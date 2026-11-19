from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import Uuid, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.identity.models import VERIFICATION_PURPOSE, AuthToken, User

pytestmark = pytest.mark.integration


def test_readiness_tracks_clean_upgrade_revision_mismatch_and_downgrade(clean_schema, migrations):
    from app.main import app

    with TestClient(app) as client:
        assert inspect(clean_schema).get_table_names() == []
        assert client.get("/health/ready").status_code == 503

        command.upgrade(migrations, "0001_sprint_00_baseline")
        assert inspect(clean_schema).get_table_names() == ["alembic_version"]
        assert client.get("/health/ready").status_code == 503

        command.upgrade(migrations, "head")
        command.check(migrations)
        inspector = inspect(clean_schema)
        product_tables = {
            "auth_mail_secrets",
            "auth_rate_limits",
            "auth_sessions",
            "auth_tokens",
            "jobs",
            "learning_preferences",
            "user_profiles",
            "users",
        }
        assert set(inspector.get_table_names()) == {"alembic_version", *product_tables}
        for table in product_tables:
            primary_key = inspector.get_pk_constraint(table)["constrained_columns"]
            [column] = [
                item for item in inspector.get_columns(table) if item["name"] in primary_key
            ]
            assert isinstance(column["type"], Uuid)
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
        command.downgrade(migrations, "0001_sprint_00_baseline")
        assert inspect(clean_schema).get_table_names() == ["alembic_version"]
        assert client.get("/health/ready").status_code == 503

        command.downgrade(migrations, "base")
        with clean_schema.connect() as connection:
            assert (
                connection.execute(text("SELECT count(*) FROM alembic_version")).scalar_one() == 0
            )


@pytest.mark.parametrize(
    ("status", "password_hash"), [("pending", "synthetic-hash"), ("active", None)]
)
def test_migration_enforces_account_credentials(identity_engine, status, password_hash):
    email = "identity@example.test"
    with Session(identity_engine) as session, pytest.raises(IntegrityError) as error:
        session.add(User(email=email, email_norm=email, status=status, password_hash=password_hash))
        session.flush()

    assert error.value.orig.diag.constraint_name == "ck_users_status_credentials"


def test_migration_enforces_one_open_proof_per_user_and_purpose(identity_engine):
    now = datetime.now(UTC)
    user_id = uuid4()
    email = "identity@example.test"
    first_id = uuid4()
    proof = {
        "user_id": user_id,
        "purpose": VERIFICATION_PURPOSE,
        "expires_at": now + timedelta(hours=24),
    }

    with Session(identity_engine) as session, session.begin():
        session.add(User(id=user_id, email=email, email_norm=email, status="pending"))
        session.flush()
        session.add(AuthToken(id=first_id, token_digest=bytes(32), **proof))

    with Session(identity_engine) as session, pytest.raises(IntegrityError) as error:
        session.add(AuthToken(token_digest=bytes(range(32)), **proof))
        session.flush()

    assert error.value.orig.diag.constraint_name == "uq_auth_tokens_open_user_purpose"

    with Session(identity_engine) as session, session.begin():
        session.get_one(AuthToken, first_id).superseded_at = now
        session.flush()
        session.add(AuthToken(token_digest=bytes(range(32)), **proof))
