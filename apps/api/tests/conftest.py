import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema


@pytest.fixture
def migrations():
    return Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))


@pytest.fixture
def clean_schema(monkeypatch):
    configured_url = os.environ.get("TEST_DATABASE_URL")
    if not configured_url:
        pytest.skip("Set TEST_DATABASE_URL to run the PostgreSQL integration test")

    schema = f"elp_test_{uuid4().hex}"
    base_engine = create_engine(configured_url, hide_parameters=True)
    with base_engine.begin() as connection:
        connection.execute(CreateSchema(schema))

    # A private search path keeps all fixture migrations isolated from application data.
    url = make_url(configured_url).update_query_dict({"options": f"-csearch_path={schema}"})
    scoped_engine = create_engine(url, hide_parameters=True)
    monkeypatch.setenv("DATABASE_URL", url.render_as_string(hide_password=False))

    try:
        yield scoped_engine
    finally:
        scoped_engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))
        finally:
            base_engine.dispose()


@pytest.fixture
def identity_engine(clean_schema, migrations):
    command.upgrade(migrations, "head")
    return clean_schema
