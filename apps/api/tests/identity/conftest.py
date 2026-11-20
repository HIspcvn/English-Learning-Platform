from base64 import urlsafe_b64encode
from contextlib import ExitStack
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.identity.models import AuthMailSecret, User, UserProfile
from app.identity.service import hash_password
from app.main import app
from app.worker.secrets import decrypt_token

from .helpers import MAIL_KEY, ORIGIN, PASSWORD


@pytest.fixture
def browser_factory(identity_engine, monkeypatch):
    monkeypatch.setenv("AUTH_PUBLIC_ORIGIN", ORIGIN)
    monkeypatch.setenv("AUTH_MAIL_KEY", urlsafe_b64encode(MAIL_KEY).decode("ascii"))

    with ExitStack() as stack:
        stack.enter_context(TestClient(app, base_url=ORIGIN))

        def connect() -> TestClient:
            # Share one real app lifespan with independent cookie jars.
            client = TestClient(app, base_url=ORIGIN, headers={"Origin": ORIGIN})
            stack.callback(client.close)
            return client

        yield connect


@pytest.fixture
def create_user(identity_engine):
    def create(email: str, name: str = "Learner", *, active: bool = True):
        with Session(identity_engine, expire_on_commit=False) as session, session.begin():
            user = User(
                email=email, email_norm=email.lower(), status="active" if active else "pending"
            )
            if active:
                user.password_hash = hash_password(PASSWORD)
                user.verified_at = datetime.now(UTC)
            session.add(user)
            session.flush()
            if active:
                session.add(UserProfile(user_id=user.id, display_name=name))
            return user.id

    return create


@pytest.fixture
def mail_proof(identity_engine):
    def read(user_id, purpose: str = "reset_password") -> str:
        with Session(identity_engine) as session:
            secret = session.scalars(
                select(AuthMailSecret).where(
                    AuthMailSecret.user_id == user_id, AuthMailSecret.purpose == purpose
                )
            ).one()
            return decrypt_token(
                MAIL_KEY,
                secret.token_ciphertext,
                secret.nonce,
                user_id=secret.user_id,
                token_id=secret.token_id,
                purpose=secret.purpose,
                expires_at=secret.expires_at,
            )

    return read
