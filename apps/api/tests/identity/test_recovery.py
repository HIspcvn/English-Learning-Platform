from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier, Event

import pytest
from sqlalchemy import event, select, text, update
from sqlalchemy.orm import Session

from app.identity.models import AuthMailSecret, AuthToken, Job
from app.identity.service import digest_token
from app.main import app

from .helpers import SESSION_COOKIE, assert_problem, login, mutate, replay_cookie, session_view

EMAIL = "owner@example.com"
NEW_PASSWORD = "synthetic replacement credential"
RESET_PURPOSE = "reset_password"
pytestmark = pytest.mark.integration


def forgot(client, email=EMAIL):
    response = mutate(client, "password/forgot", {"email": email})
    assert response.status_code == 202
    assert response.json() == {"accepted": True}
    assert "no-store" in response.headers["cache-control"]
    return response


def reset(client, proof, password=NEW_PASSWORD):
    return mutate(client, "password/reset", {"token": proof, "password": password})


def test_forgot_has_one_public_response_and_encrypted_delivery_only_for_active_account(
    browser_factory, create_user, identity_engine, mail_proof, caplog
):
    owner = create_user(EMAIL)
    create_user("pending@example.com", active=False)
    client = browser_factory()
    clock = datetime.now(UTC)

    responses = [
        forgot(client, email)
        for email in (EMAIL.upper(), "pending@example.com", "unknown@example.com")
    ]

    token = mail_proof(owner)
    assert all(response.content == responses[0].content for response in responses)
    with Session(identity_engine) as session:
        proof = session.scalars(select(AuthToken)).one()
        secret = session.scalars(select(AuthMailSecret)).one()
        job = session.scalars(select(Job)).one()
        assert (proof.user_id, proof.purpose, proof.token_digest) == (
            owner,
            RESET_PURPOSE,
            digest_token(token),
        )
        assert timedelta(minutes=29) <= proof.expires_at - clock <= timedelta(minutes=31)
        assert (secret.job_id, secret.token_id, secret.purpose) == (job.id, proof.id, RESET_PURPOSE)
        assert secret.token_ciphertext != token.encode("ascii")
        assert token not in str(job.payload) and EMAIL not in str(job.payload)
    assert not any(value in caplog.text for value in (token, EMAIL))


def test_expired_or_superseded_reset_proof_is_rejected(
    browser_factory, create_user, identity_engine, mail_proof
):
    owner = create_user(EMAIL)
    client = browser_factory()
    forgot(client)
    old_proof = mail_proof(owner)
    forgot(client)
    fresh_proof = mail_proof(owner)
    assert fresh_proof != old_proof
    assert_problem(reset(client, old_proof), 410, "TOKEN_UNAVAILABLE")
    with Session(identity_engine) as session:
        previous = session.scalars(
            select(AuthToken).where(AuthToken.token_digest == digest_token(old_proof))
        ).one()
        assert previous.superseded_at is not None
        assert previous.expires_at > datetime.now(UTC)
        assert not session.scalar(
            select(AuthMailSecret).where(AuthMailSecret.token_id == previous.id)
        )
    with identity_engine.begin() as connection:
        connection.execute(
            update(AuthToken)
            .where(AuthToken.token_digest == digest_token(fresh_proof))
            .values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )

    assert_problem(reset(client, fresh_proof), 410, "TOKEN_UNAVAILABLE")
    assert login(client, EMAIL).status_code == 200


def test_reset_rotates_password_and_revokes_all_owner_sessions_without_affecting_other_account(
    browser_factory, create_user, identity_engine, mail_proof
):
    owner = create_user(EMAIL)
    other_email = "other@example.com"
    other_id = create_user(other_email, "Học viên khác")
    first, second, other, guest = (browser_factory() for _ in range(4))
    assert login(first, EMAIL).status_code == 200
    assert login(second, EMAIL).status_code == 200
    assert login(other, other_email).json()["user"]["id"] == str(other_id)
    old_tokens = [client.cookies.get(SESSION_COOKIE) for client in (first, second)]
    forgot(guest)
    proof = mail_proof(owner)

    changed = reset(guest, proof)

    assert (changed.status_code, changed.content) == (204, b"")
    assert "no-store" in changed.headers["cache-control"]
    assert_problem(reset(guest, proof), 410, "TOKEN_UNAVAILABLE")
    for token in old_tokens:
        replay = browser_factory()
        replay_cookie(replay, token)
        assert session_view(replay)["user"] is None
    assert session_view(other)["user"]["id"] == str(other_id)
    assert_problem(login(first, EMAIL), 401, "INVALID_CREDENTIALS")
    assert login(first, EMAIL, NEW_PASSWORD).json()["user"]["id"] == str(owner)
    with identity_engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    "SELECT count(*) FROM auth_sessions WHERE user_id = :owner AND revoked_at IS NOT NULL"
                ),
                {"owner": owner},
            )
            == 2
        )
        assert connection.scalar(text("SELECT count(*) FROM auth_mail_secrets")) == 0


def test_concurrent_reset_changes_password_only_for_the_winning_request(
    browser_factory, create_user, mail_proof
):
    owner = create_user(EMAIL)
    first, second = browser_factory(), browser_factory()
    forgot(first)
    proof = mail_proof(owner)
    barrier = Barrier(2, timeout=10)

    def synchronize_owner_lock(_connection, _cursor, statement, *_args):
        if "FROM users" in statement and "FOR UPDATE" in statement:
            barrier.wait()

    runtime_engine = app.state.engine
    event.listen(runtime_engine, "before_cursor_execute", synchronize_owner_lock)
    passwords = (NEW_PASSWORD, "second synthetic password")
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            requests = [
                pool.submit(reset, client, proof, password)
                for client, password in zip((first, second), passwords, strict=True)
            ]
            responses = [request.result(timeout=15) for request in requests]
    finally:
        event.remove(runtime_engine, "before_cursor_execute", synchronize_owner_lock)

    assert sorted(response.status_code for response in responses) == [204, 410]
    for response, password in zip(responses, passwords, strict=True):
        attempted = login(browser_factory(), EMAIL, password)
        if response.status_code == 204:
            assert attempted.status_code == 200
        else:
            assert_problem(response, 410, "TOKEN_UNAVAILABLE")
            assert_problem(attempted, 401, "INVALID_CREDENTIALS")


def test_login_that_verified_old_password_cannot_mint_session_after_reset(
    browser_factory, create_user, identity_engine, mail_proof
):
    owner = create_user(EMAIL)
    old_login, recovery = browser_factory(), browser_factory()
    forgot(recovery)
    proof = mail_proof(owner)
    verified_old_password, reset_committed = Event(), Event()

    def pause_before_login_lock(_connection, _cursor, statement, *_args):
        if (
            "FROM users" in statement
            and "users.password_hash =" in statement
            and "FOR UPDATE" in statement
        ):
            verified_old_password.set()
            assert reset_committed.wait(timeout=10)

    runtime_engine = app.state.engine
    event.listen(runtime_engine, "before_cursor_execute", pause_before_login_lock)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending_login = pool.submit(login, old_login, EMAIL)
            try:
                assert verified_old_password.wait(timeout=10)
                assert reset(recovery, proof).status_code == 204
            finally:
                reset_committed.set()
            assert_problem(pending_login.result(timeout=10), 401, "INVALID_CREDENTIALS")
    finally:
        event.remove(runtime_engine, "before_cursor_execute", pause_before_login_lock)

    with identity_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM auth_sessions")) == 0
    assert login(old_login, EMAIL, NEW_PASSWORD).status_code == 200
