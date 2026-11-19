import base64
import secrets
import smtplib
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from threading import Event
from unittest.mock import Mock
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidTag
from sqlalchemy.orm import Session

from app.config import Settings
from app.identity import service
from app.identity.models import (
    VERIFICATION_JOB,
    VERIFICATION_PURPOSE,
    AuthMailSecret,
    AuthToken,
    Job,
    User,
)
from app.worker import mail
from app.worker.secrets import decrypt_token, encrypt_token

TEST_KEY = bytes(range(32))
TEST_EMAIL = "worker@example.test"


@pytest.fixture
def settings():
    return Settings(
        database_url="postgresql+psycopg://test@127.0.0.1/test",
        auth_mail_key=base64.urlsafe_b64encode(TEST_KEY).decode("ascii"),
        auth_mail_key_id="test-key",
        auth_public_origin="http://localhost:3000",
    )


@pytest.fixture
def smtp_connection(monkeypatch):
    smtp = Mock(spec=smtplib.SMTP)
    smtp.connect.return_value = 220, b"Ready"
    monkeypatch.setattr(smtplib, "SMTP", Mock(return_value=smtp))
    return smtp


def test_delivery_secret_binds_token_and_context():
    token = secrets.token_urlsafe(32)
    context = {
        "user_id": uuid4(),
        "token_id": uuid4(),
        "purpose": VERIFICATION_PURPOSE,
        "expires_at": datetime.now(UTC) + timedelta(hours=24),
    }
    ciphertext, nonce = encrypt_token(TEST_KEY, token, **context)

    assert len(nonce) == 12
    assert token.encode() not in ciphertext
    assert decrypt_token(TEST_KEY, ciphertext, nonce, **context) == token
    assert encrypt_token(TEST_KEY, token, **context)[1] != nonce

    mismatches = {
        "user_id": uuid4(),
        "token_id": uuid4(),
        "purpose": "reset_password",
        "expires_at": context["expires_at"] + timedelta(seconds=1),
    }
    for field, value in mismatches.items():
        with pytest.raises(InvalidTag):
            decrypt_token(TEST_KEY, ciphertext, nonce, **(context | {field: value}))

    altered = bytes([ciphertext[0] ^ 1]) + ciphertext[1:]
    with pytest.raises(InvalidTag):
        decrypt_token(TEST_KEY, altered, nonce, **context)


@pytest.fixture
def queued_proof(identity_engine, settings):
    user_id, token_id, job_id = uuid4(), uuid4(), uuid4()
    token = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    context = {
        "user_id": user_id,
        "token_id": token_id,
        "purpose": VERIFICATION_PURPOSE,
        "expires_at": now + timedelta(hours=24),
    }
    ciphertext, nonce = encrypt_token(TEST_KEY, token, **context)

    with Session(identity_engine) as session, session.begin():
        session.add(User(id=user_id, email=TEST_EMAIL, email_norm=TEST_EMAIL, status="pending"))
        session.flush()
        session.add_all(
            [
                AuthToken(
                    id=token_id,
                    user_id=user_id,
                    purpose=VERIFICATION_PURPOSE,
                    token_digest=sha256(token.encode()).digest(),
                    expires_at=context["expires_at"],
                ),
                Job(
                    id=job_id,
                    kind=VERIFICATION_JOB,
                    dedupe_key=str(token_id),
                    payload={
                        "user_id": str(user_id),
                        "token_id": str(token_id),
                        "purpose": VERIFICATION_PURPOSE,
                    },
                    status="queued",
                    attempts=0,
                    available_at=now - timedelta(seconds=1),
                ),
            ]
        )
        session.flush()
        session.add(
            AuthMailSecret(
                job_id=job_id,
                token_ciphertext=ciphertext,
                nonce=nonce,
                kms_key_id=settings.auth_mail_key_id,
                **context,
            )
        )
    return job_id, token_id


@pytest.mark.integration
def test_smtp_timeout_retries_then_succeeds(
    identity_engine, settings, queued_proof, monkeypatch, caplog
):
    job_id, token_id = queued_proof
    deliveries = []

    with socket.create_server(("127.0.0.1", 0)) as listener:
        # The TCP connection opens but the listener never sends the SMTP greeting.
        timed_out_settings = settings.model_copy(
            update={"smtp_host": "127.0.0.1", "smtp_port": listener.getsockname()[1]}
        )
        monkeypatch.setattr(mail, "SMTP_TIMEOUT_SECONDS", 0.2)
        assert mail.deliver_one(identity_engine, timed_out_settings)

    with Session(identity_engine) as session, session.begin():
        job = session.get(Job, job_id)
        assert (job.status, job.attempts, job.last_error_code) == ("queued", 1, "SMTP_TIMEOUT")
        assert job.lease_owner is None
        assert job.available_at > datetime.now(UTC)
        assert session.get(AuthMailSecret, job_id) is not None
        job.available_at = datetime.now(UTC) - timedelta(seconds=1)

    class LocalSMTP:
        def __init__(self, *, local_hostname, timeout):
            assert local_hostname
            assert timeout > 0

        def connect(self, host, port):
            assert host == settings.smtp_host
            assert port == settings.smtp_port
            return 220, b"Ready"

        def ehlo_or_helo_if_needed(self):
            pass

        def send_message(self, message):
            deliveries.append(message)

        def close(self):
            pass

    monkeypatch.setattr(smtplib, "SMTP", LocalSMTP)

    assert mail.deliver_one(identity_engine, settings)
    with Session(identity_engine) as session:
        job = session.get(Job, job_id)
        assert (job.status, job.attempts, job.last_error_code) == ("succeeded", 2, None)
        assert session.get(AuthMailSecret, job_id) is None
        assert len(deliveries) == 1
        message = deliveries[0]
        assert str(message["To"]) == TEST_EMAIL
        assert "Xác minh" in str(message["Subject"])
        link_prefix = f"{settings.auth_public_origin}/verify#token="
        link = next(line for line in message.get_content().splitlines() if link_prefix in line)
        assert link.startswith(link_prefix)
        token = link.removeprefix(link_prefix)
        assert sha256(token.encode()).digest() == session.get(AuthToken, token_id).token_digest
        assert not any(value in caplog.text for value in (token, TEST_EMAIL))


@pytest.mark.integration
def test_bounded_attempts_clean_up_failed_delivery(
    identity_engine, settings, queued_proof, monkeypatch
):
    job_id, _ = queued_proof

    def timeout(*_args, **_kwargs):
        raise TimeoutError("SMTP timed out")

    monkeypatch.setattr(smtplib, "SMTP", timeout)
    for attempt in range(1, 4):
        assert mail.deliver_one(identity_engine, settings)
        with Session(identity_engine) as session, session.begin():
            job = session.get(Job, job_id)
            assert job.attempts == attempt
            job.available_at = datetime.now(UTC) - timedelta(seconds=1)

    assert not mail.deliver_one(identity_engine, settings)
    with Session(identity_engine) as session:
        job = session.get(Job, job_id)
        assert (job.status, job.last_error_code) == ("failed", "SMTP_TIMEOUT")
        assert job.lease_owner is None
        assert session.get(AuthMailSecret, job_id) is None


@pytest.mark.integration
@pytest.mark.parametrize("state", ["superseded", "expired"])
def test_stale_job_is_cancelled_without_smtp(
    state, identity_engine, settings, queued_proof, monkeypatch
):
    job_id, token_id = queued_proof
    now = datetime.now(UTC)
    monkeypatch.setattr(
        smtplib, "SMTP", lambda *_args, **_kwargs: pytest.fail("Unexpected SMTP I/O")
    )

    with Session(identity_engine) as session, session.begin():
        proof = session.get(AuthToken, token_id)
        if state == "superseded":
            proof.superseded_at = now
        else:
            proof.expires_at = now - timedelta(seconds=1)
            session.get(AuthMailSecret, job_id).expires_at = proof.expires_at
            session.get(Job, job_id).available_at = now + timedelta(minutes=5)

    assert mail.deliver_one(identity_engine, settings)
    with Session(identity_engine) as session:
        assert session.get(Job, job_id).status == "cancelled"
        assert session.get(AuthMailSecret, job_id) is None


@pytest.mark.integration
def test_worker_claim_is_committed_and_exclusive(
    identity_engine, settings, queued_proof, smtp_connection
):
    job_id, _ = queued_proof
    sending = Event()
    finish = Event()

    def send_message(*_args, **_kwargs):
        assert not sending.is_set()
        sending.set()
        assert finish.wait(timeout=5)

    smtp_connection.send_message.side_effect = send_message
    with ThreadPoolExecutor(max_workers=1) as pool:
        delivered = pool.submit(mail.deliver_one, identity_engine, settings)
        try:
            assert sending.wait(timeout=5)
            with Session(identity_engine) as session:
                job = session.get(Job, job_id)
                assert (job.status, job.attempts) == ("running", 1)
                assert job.lease_owner
            assert not mail.deliver_one(identity_engine, settings)
        finally:
            finish.set()
        assert delivered.result(timeout=5)


@pytest.mark.integration
def test_resend_during_smtp_handshake_prevents_stale_message(
    identity_engine, settings, queued_proof, smtp_connection, monkeypatch
):
    job_id, token_id = queued_proof
    future = datetime.now(UTC) + timedelta(seconds=61)
    monkeypatch.setattr(service, "utc_now", lambda: future)

    def connect(_host, _port):
        service.request_verification(
            identity_engine, TEST_EMAIL, TEST_KEY, settings.auth_mail_key_id, register=False
        )
        return 220, b"Ready"

    smtp_connection.connect.side_effect = connect
    assert mail.deliver_one(identity_engine, settings)

    smtp_connection.connect.assert_called_once()
    smtp_connection.send_message.assert_not_called()
    with Session(identity_engine) as session:
        assert session.get(AuthToken, token_id).superseded_at is not None
        assert session.get(Job, job_id).status == "cancelled"
        assert session.get(AuthMailSecret, job_id) is None


@pytest.mark.integration
def test_permanent_smtp_rejection_cleans_up_without_retry(
    identity_engine, settings, queued_proof, smtp_connection
):
    job_id, _ = queued_proof
    smtp_connection.send_message.side_effect = smtplib.SMTPDataError(550, b"Synthetic rejection")

    assert mail.deliver_one(identity_engine, settings)
    assert not mail.deliver_one(identity_engine, settings)
    with Session(identity_engine) as session:
        job = session.get(Job, job_id)
        assert (job.status, job.attempts, job.last_error_code) == ("failed", 1, "SMTP_REJECTED")
        assert session.get(AuthMailSecret, job_id) is None


@pytest.mark.integration
def test_dead_lease_at_attempt_limit_is_terminal(
    identity_engine, settings, queued_proof, monkeypatch
):
    job_id, _ = queued_proof
    monkeypatch.setattr(
        smtplib, "SMTP", lambda *_args, **_kwargs: pytest.fail("Unexpected SMTP I/O")
    )
    with Session(identity_engine) as session, session.begin():
        job = session.get(Job, job_id)
        job.status = "running"
        job.attempts = 3
        job.lease_owner = "abandoned-worker"
        job.lease_until = datetime.now(UTC) - timedelta(seconds=1)

    assert mail.deliver_one(identity_engine, settings)
    with Session(identity_engine) as session:
        job = session.get(Job, job_id)
        assert (job.status, job.attempts, job.last_error_code) == ("failed", 3, "LEASE_EXPIRED")
        assert session.get(AuthMailSecret, job_id) is None
