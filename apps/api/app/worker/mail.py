import smtplib
from contextlib import closing
from dataclasses import dataclass
from datetime import timedelta
from email.message import EmailMessage
from random import uniform
from uuid import UUID, uuid4

from cryptography.exceptions import InvalidTag
from sqlalchemy import Engine, and_, delete, func, or_, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.identity.models import (
    VERIFICATION_JOB,
    VERIFICATION_PURPOSE,
    AuthMailSecret,
    AuthToken,
    Job,
    User,
)
from app.worker.secrets import decrypt_token

MAX_ATTEMPTS = 3
SMTP_TIMEOUT_SECONDS = 5
LEASE_DURATION = timedelta(minutes=1)


@dataclass(frozen=True)
class _Lease:
    job_id: UUID
    owner: str


def _verification_message(settings: Settings, recipient: str, token: str) -> EmailMessage:
    link = f"{settings.auth_public_origin}/verify#token={token}"
    message = EmailMessage()
    message["From"] = settings.smtp_sender
    message["To"] = recipient
    message["Subject"] = "Xác minh email cho English Learning Platform"
    message.set_content(
        "Chào bạn,\n\n"
        "Mở liên kết sau để xác minh email và thiết lập mật khẩu. "
        "Liên kết có hiệu lực trong 24 giờ và chỉ dùng được một lần.\n\n"
        f"{link}\n\n"
        "Nếu bạn không yêu cầu tạo tài khoản, hãy bỏ qua thư này.\n"
    )

    return message


def _terminal(session: Session, job: Job, status: str, error_code: str | None = None) -> None:
    job.status = status
    job.lease_owner = None
    job.lease_until = None
    job.last_error_code = error_code
    session.execute(delete(AuthMailSecret).where(AuthMailSecret.job_id == job.id))


def _claim(session: Session) -> tuple[bool, _Lease | None]:
    # Expired payloads are eligible for cleanup even during retry backoff or a lease.
    now = session.scalar(select(func.clock_timestamp()))
    row = session.execute(
        select(Job, AuthMailSecret.expires_at)
        .outerjoin(AuthMailSecret, AuthMailSecret.job_id == Job.id)
        .where(
            Job.kind == VERIFICATION_JOB,
            Job.status.in_(("queued", "running")),
            or_(
                AuthMailSecret.job_id.is_(None),
                AuthMailSecret.expires_at <= now,
                and_(Job.status == "queued", Job.available_at <= now),
                and_(Job.status == "running", Job.lease_until <= now),
            ),
        )
        .order_by(Job.available_at, Job.id)
        .limit(1)
        .with_for_update(skip_locked=True, of=Job)
    ).one_or_none()
    if row is None:
        return False, None

    job, expires_at = row
    if expires_at is None or expires_at <= now:
        _terminal(session, job, "cancelled")
        return True, None
    if job.attempts >= MAX_ATTEMPTS:
        _terminal(session, job, "failed", "LEASE_EXPIRED")
        return True, None

    lease = _Lease(job.id, str(uuid4()))
    job.attempts += 1
    job.status = "running"
    job.lease_owner = lease.owner
    job.lease_until = now + LEASE_DURATION
    return True, lease


def _current_delivery(engine: Engine, lease: _Lease) -> tuple[str, AuthMailSecret] | None:
    with Session(engine) as session:
        row = session.execute(
            select(User.email, AuthMailSecret)
            .join(AuthMailSecret, AuthMailSecret.user_id == User.id)
            .join(AuthToken, AuthToken.id == AuthMailSecret.token_id)
            .join(Job, Job.id == AuthMailSecret.job_id)
            .where(
                Job.id == lease.job_id,
                Job.status == "running",
                Job.lease_owner == lease.owner,
                Job.lease_until > func.clock_timestamp(),
                User.status == "pending",
                User.deleted_at.is_(None),
                AuthToken.user_id == AuthMailSecret.user_id,
                AuthToken.purpose == VERIFICATION_PURPOSE,
                AuthMailSecret.purpose == AuthToken.purpose,
                AuthMailSecret.expires_at == AuthToken.expires_at,
                AuthToken.expires_at > func.clock_timestamp(),
                AuthToken.consumed_at.is_(None),
                AuthToken.superseded_at.is_(None),
            )
        ).one_or_none()
    if row is None:
        return None
    recipient, secret = row
    return recipient, secret


def _permanent_smtp_rejection(error: OSError) -> bool:
    if isinstance(error, smtplib.SMTPRecipientsRefused):
        return bool(error.recipients) and all(
            500 <= code < 600 for code, _ in error.recipients.values()
        )
    return isinstance(error, smtplib.SMTPResponseException) and 500 <= error.smtp_code < 600


def _deliver(
    engine: Engine, settings: Settings, key: bytes, lease: _Lease
) -> tuple[str, str | None]:
    if _current_delivery(engine, lease) is None:
        return "cancelled", None

    try:
        # Close directly so a missing QUIT reply cannot retry an accepted message.
        with closing(
            smtplib.SMTP(local_hostname="elp-worker.local", timeout=SMTP_TIMEOUT_SECONDS)
        ) as smtp:
            status, greeting = smtp.connect(settings.smtp_host, settings.smtp_port)
            if status != 220:
                raise smtplib.SMTPConnectError(status, greeting)
            smtp.ehlo_or_helo_if_needed()

            # Resend or verify can retire the proof during the SMTP handshake.
            delivery = _current_delivery(engine, lease)
            if delivery is None:
                return "cancelled", None
            recipient, secret = delivery
            if secret.kms_key_id != settings.auth_mail_key_id:
                return "failed", "MAIL_KEY_UNAVAILABLE"
            try:
                token = decrypt_token(
                    key,
                    secret.token_ciphertext,
                    secret.nonce,
                    user_id=secret.user_id,
                    token_id=secret.token_id,
                    purpose=secret.purpose,
                    expires_at=secret.expires_at,
                )
            except (InvalidTag, ValueError):
                return "failed", "INVALID_MAIL_SECRET"
            smtp.send_message(_verification_message(settings, recipient, token))
    except OSError as error:
        if isinstance(error, TimeoutError) or isinstance(error.__context__, TimeoutError):
            return "queued", "SMTP_TIMEOUT"
        if _permanent_smtp_rejection(error):
            return "failed", "SMTP_REJECTED"
        return "queued", "SMTP_FAILURE"
    return "succeeded", None


def _finalize(session: Session, lease: _Lease, status: str, error_code: str | None) -> None:
    job = session.scalar(
        select(Job)
        .where(Job.id == lease.job_id, Job.status == "running", Job.lease_owner == lease.owner)
        .with_for_update()
    )
    if job is None:
        return
    if status == "queued" and job.attempts < MAX_ATTEMPTS:
        retry_delay = timedelta(seconds=15 * 2 ** (job.attempts - 1) * uniform(1, 1.25))
        job.available_at = session.scalar(select(func.clock_timestamp())) + retry_delay
        job.status = "queued"
        job.lease_owner = None
        job.lease_until = None
        job.last_error_code = error_code
    else:
        _terminal(session, job, "failed" if status == "queued" else status, error_code)


def deliver_one(engine: Engine, settings: Settings) -> bool:
    """Process one due verification mail job, including terminal cleanup."""
    key = settings.auth_mail_key_bytes
    if key is None:
        raise ValueError("AUTH_MAIL_KEY is required by the verification mail worker")
    with Session(engine) as session, session.begin():
        processed, lease = _claim(session)
    if lease is not None:
        status, error_code = _deliver(engine, settings, key, lease)
        with Session(engine) as session, session.begin():
            _finalize(session, lease, status, error_code)
    return processed
