import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema

pytestmark = pytest.mark.integration


@pytest.fixture
def clean_schema(monkeypatch):
    configured_url = os.environ.get("TEST_DATABASE_URL")
    if not configured_url:
        pytest.skip("Set TEST_DATABASE_URL to run the PostgreSQL integration test")

    schema = f"s00_{uuid4().hex}"
    base_engine = create_engine(configured_url)
    with base_engine.begin() as connection:
        connection.execute(CreateSchema(schema))

    # A private search path keeps all fixture migrations isolated from application data.
    url = make_url(configured_url).update_query_dict({"options": f"-csearch_path={schema}"})
    scoped_engine = create_engine(url)
    monkeypatch.setenv("DATABASE_URL", url.render_as_string(hide_password=False))

    try:
        yield scoped_engine
    finally:
        scoped_engine.dispose()
        with base_engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        base_engine.dispose()


def test_readiness_tracks_clean_upgrade_revision_mismatch_and_downgrade(clean_schema):
    from app.main import app

    migrations = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with TestClient(app) as client:
        assert inspect(clean_schema).get_table_names() == []
        assert client.get("/health/ready").status_code == 503

        command.upgrade(migrations, "head")
        command.check(migrations)
        assert inspect(clean_schema).get_table_names() == ["alembic_version"]
        ready = client.get("/health/ready")
        assert ready.status_code == 200
        assert ready.json() == {"status": "ready"}

        with clean_schema.begin() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            connection.execute(text("UPDATE alembic_version SET version_num = 'other_revision'"))
        assert client.get("/health/ready").status_code == 503
        assert client.get("/health/live").status_code == 200

        with clean_schema.begin() as connection:
            connection.execute(
                text("UPDATE alembic_version SET version_num = :revision"), {"revision": revision}
            )
        command.downgrade(migrations, "base")
        assert client.get("/health/ready").status_code == 503
