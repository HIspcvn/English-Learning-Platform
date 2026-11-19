from base64 import urlsafe_b64encode
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier

import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select, update
from sqlalchemy.orm import Session

from app.identity import service
from app.identity.models import AuthMailSecret, AuthRateLimit, AuthToken, Job, User, UserProfile
from app.main import app

ORIGIN = "http://127.0.0.1:3000"
AUTH = "/api/v1/auth"
EMAIL = "learner@example.com"
PASSWORD = "synthetic learner password"
pytestmark = pytest.mark.integration


@pytest.fixture
def auth_client(identity_engine, monkeypatch):
    monkeypatch.setenv("AUTH_PUBLIC_ORIGIN", ORIGIN)
    monkeypatch.setenv("AUTH_MAIL_KEY", urlsafe_b64encode(bytes(32)).decode())
    with TestClient(app, base_url=ORIGIN) as client:
        bootstrap = client.get(f"{AUTH}/session")
        assert bootstrap.json()["user"] is None
        client.headers.update({"Origin": ORIGIN, "X-CSRF-Token": bootstrap.json()["csrf_token"]})
        yield client


@pytest.fixture
def issued_tokens(monkeypatch):
    tokens = []
    generate = service.new_token

    def capture():
        token = generate()
        tokens.append(token)
        return token

    monkeypatch.setattr(service, "new_token", capture)
    return tokens


def verify(client, token):
    return client.post(
        f"{AUTH}/verify", json={"token": token, "password": PASSWORD, "display_name": " Learner "}
    )


def count(session, model):
    return session.scalar(select(func.count()).select_from(model))


def test_register_verify_and_protect_active_account(auth_client, identity_engine, issued_tokens):
    registered = auth_client.post(f"{AUTH}/register", json={"email": EMAIL})
    duplicate = auth_client.post(f"{AUTH}/register", json={"email": EMAIL.upper()})
    assert registered.status_code == duplicate.status_code == 202
    assert registered.json() == duplicate.json() == {"accepted": True}
    assert registered.headers["cache-control"] == "no-store"
    assert len(issued_tokens) == 1

    token = issued_tokens[0]
    with Session(identity_engine) as session:
        user = session.scalar(select(User))
        proof = session.scalar(select(AuthToken))
        job = session.scalar(select(Job))
        secret = session.scalar(select(AuthMailSecret))
        assert count(session, User) == 1
        assert user.status == "pending" and user.password_hash is None and user.verified_at is None
        assert count(session, UserProfile) == 0
        assert proof.token_digest == service.digest_token(token)
        assert token not in str(job.payload) and EMAIL not in str(job.payload)
        assert secret.token_ciphertext != token.encode()
        assert secret.job_id == job.id and secret.token_id == proof.id

    activated = verify(auth_client, token)
    assert activated.status_code == 204 and activated.content == b""
    assert "set-cookie" not in activated.headers
    assert verify(auth_client, token).status_code == 410
    assert verify(auth_client, "unknown-proof").status_code == 410
    with Session(identity_engine) as session:
        user = session.scalar(select(User))
        password_hash = user.password_hash
        assert user.status == "active" and user.verified_at is not None
        assert PasswordHasher().verify(password_hash, PASSWORD)
        assert session.scalar(select(UserProfile)).display_name == "Learner"
        assert session.scalar(select(AuthToken)).consumed_at is not None
        assert count(session, AuthMailSecret) == 0

    assert auth_client.post(f"{AUTH}/register", json={"email": EMAIL}).json() == registered.json()
    assert (
        auth_client.post(f"{AUTH}/verification/resend", json={"email": EMAIL}).json()
        == registered.json()
    )
    with Session(identity_engine) as session:
        assert session.scalar(select(User)).password_hash == password_hash
        assert session.scalar(select(UserProfile)).display_name == "Learner"
        assert count(session, Job) == 1


def test_resend_cooldown_and_superseded_or_expired_token(
    auth_client, identity_engine, issued_tokens, monkeypatch
):
    clock = datetime.now(UTC)
    monkeypatch.setattr(service, "utc_now", lambda: clock)
    assert auth_client.post(f"{AUTH}/register", json={"email": EMAIL}).status_code == 202
    assert auth_client.post(f"{AUTH}/verification/resend", json={"email": EMAIL}).status_code == 202
    assert len(issued_tokens) == 1

    clock += timedelta(seconds=60)
    assert auth_client.post(f"{AUTH}/verification/resend", json={"email": EMAIL}).status_code == 202
    assert len(issued_tokens) == 2
    stale = verify(auth_client, issued_tokens[0])
    assert stale.status_code == 410
    assert stale.headers["content-type"] == "application/problem+json"
    assert issued_tokens[0] not in stale.text
    with Session(identity_engine) as session:
        jobs = {job.status for job in session.scalars(select(Job))}
        assert jobs == {"cancelled", "queued"}
        assert count(session, AuthMailSecret) == 1

    clock += timedelta(hours=24)
    assert verify(auth_client, issued_tokens[1]).status_code == 410
    with Session(identity_engine) as session:
        assert session.scalar(select(User)).password_hash is None


def test_verify_concurrent_claims(auth_client, identity_engine, issued_tokens):
    assert auth_client.post(f"{AUTH}/register", json={"email": EMAIL}).status_code == 202
    barrier = Barrier(2, timeout=10)

    def synchronize_owner_lock(_connection, _cursor, statement, *_args):
        if "FROM users" in statement and "FOR UPDATE" in statement:
            barrier.wait()

    def claim():
        return verify(auth_client, issued_tokens[0]).status_code

    runtime_engine = app.state.engine
    event.listen(runtime_engine, "before_cursor_execute", synchronize_owner_lock)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = [pool.submit(claim) for _ in range(2)]
            assert sorted(result.result(timeout=15) for result in results) == [204, 410]
    finally:
        event.remove(runtime_engine, "before_cursor_execute", synchronize_owner_lock)
    with Session(identity_engine) as session:
        assert count(session, UserProfile) == 1


def test_register_concurrent_duplicates(auth_client, identity_engine, issued_tokens):
    barrier = Barrier(2, timeout=10)

    def register(email):
        barrier.wait()
        response = auth_client.post(f"{AUTH}/register", json={"email": email})
        return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(register, [EMAIL, EMAIL.upper()]))
    assert results == [(202, {"accepted": True})] * 2
    assert len(issued_tokens) == 1
    with Session(identity_engine) as session:
        assert all(count(session, model) == 1 for model in (User, AuthToken, Job, AuthMailSecret))


def test_mail_issue_rolls_back_pending_user(auth_client, identity_engine, monkeypatch):
    def broken_encryption(*_args, **_kwargs):
        raise RuntimeError("fixture failure")

    monkeypatch.setattr(service, "encrypt_token", broken_encryption)
    with pytest.raises(RuntimeError, match="fixture failure"):
        auth_client.post(f"{AUTH}/register", json={"email": EMAIL})

    with Session(identity_engine) as session:
        assert all(count(session, model) == 0 for model in (User, AuthToken, Job, AuthMailSecret))


def test_verify_rolls_back_token_and_credential(
    auth_client, identity_engine, issued_tokens, monkeypatch
):
    assert auth_client.post(f"{AUTH}/register", json={"email": EMAIL}).status_code == 202

    retire = service.retire_delivery

    def broken_retirement(session, token_id):
        retire(session, token_id)
        session.flush()
        raise RuntimeError("fixture failure")

    with monkeypatch.context() as patch:
        patch.setattr(service, "retire_delivery", broken_retirement)
        with pytest.raises(RuntimeError, match="fixture failure"):
            verify(auth_client, issued_tokens[0])

    with Session(identity_engine) as session:
        assert session.scalar(select(User)).status == "pending"
        assert session.scalar(select(User)).password_hash is None
        assert session.scalar(select(AuthToken)).consumed_at is None
        assert count(session, AuthMailSecret) == 1
        assert session.scalar(select(Job)).status == "queued"
    assert verify(auth_client, issued_tokens[0]).status_code == 204


@pytest.mark.parametrize(
    "header,value",
    [
        ("Origin", None),
        ("Origin", "https://invalid.example"),
        ("X-CSRF-Token", None),
        ("X-CSRF-Token", "mismatch"),
    ],
)
def test_guest_guard(auth_client, identity_engine, header, value):
    if value is None:
        del auth_client.headers[header]
    else:
        auth_client.headers[header] = value
    response = auth_client.post(f"{AUTH}/register", json={"email": EMAIL})

    assert response.status_code == 403
    with Session(identity_engine) as session:
        assert count(session, User) == count(session, AuthRateLimit) == 0


def test_guest_guard_requires_cookie(auth_client):
    auth_client.cookies.clear()
    assert auth_client.post(f"{AUTH}/register", json={"email": EMAIL}).status_code == 403


def test_email_quota_is_shared_and_does_not_depend_on_account_state(auth_client, caplog):
    for _ in range(4):
        response = auth_client.post(f"{AUTH}/verification/resend", json={"email": EMAIL})
        assert response.status_code == 202 and response.json() == {"accepted": True}
    response = auth_client.post(f"{AUTH}/register", json={"email": EMAIL.upper()})
    assert response.status_code == 202

    limited = auth_client.post(f"{AUTH}/register", json={"email": EMAIL})
    assert limited.status_code == 429
    assert 0 < int(limited.headers["retry-after"]) <= 900
    assert limited.json()["code"] == "RATE_LIMITED"
    assert EMAIL not in limited.text and EMAIL not in caplog.text


def test_verify_ip_quota_and_window_restart(auth_client, identity_engine):
    for _ in range(10):
        assert verify(auth_client, "unknown-proof").status_code == 410
    assert verify(auth_client, "unknown-proof").status_code == 429

    with identity_engine.begin() as connection:
        connection.execute(
            update(AuthRateLimit).values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
    assert verify(auth_client, "unknown-proof").status_code == 410


def test_validation_uses_problem_without_echoing_input(auth_client, caplog):
    sentinel = "fixture-sensitive-input"
    response = auth_client.post(
        f"{AUTH}/verify", json={"token": sentinel, "password": "too-short", "display_name": " "}
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.headers["content-type"] == "application/problem+json"
    assert sentinel not in response.text and sentinel not in caplog.text
