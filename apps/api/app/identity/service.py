from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from sqlalchemy import Engine, delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.identity.models import (
    VERIFICATION_JOB,
    VERIFICATION_PURPOSE,
    AuthMailSecret,
    AuthToken,
    Job,
    User,
    UserProfile,
)
from app.worker.secrets import encrypt_token

VERIFICATION_TTL = timedelta(hours=24)
RESEND_COOLDOWN = timedelta(seconds=60)
password_hasher = PasswordHasher()


def utc_now() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def new_token() -> str:
    return token_urlsafe(32)


def digest_token(token: str) -> bytes:
    return sha256(token.encode()).digest()


def retire_delivery(session: Session, token_id: UUID) -> None:
    session.execute(
        update(Job)
        .where(
            Job.kind == VERIFICATION_JOB,
            Job.dedupe_key == str(token_id),
            Job.status.in_(("queued", "running")),
        )
        .values(status="cancelled", lease_until=None, lease_owner=None)
    )
    session.execute(delete(AuthMailSecret).where(AuthMailSecret.token_id == token_id))


def issue_verification(
    session: Session, user: User, now: datetime, key: bytes, key_id: str
) -> None:
    token = new_token()
    token_id, job_id = uuid4(), uuid4()
    expires_at = now + VERIFICATION_TTL
    ciphertext, nonce = encrypt_token(
        key,
        token,
        user_id=user.id,
        token_id=token_id,
        purpose=VERIFICATION_PURPOSE,
        expires_at=expires_at,
    )
    session.add_all(
        (
            AuthToken(
                id=token_id,
                user_id=user.id,
                purpose=VERIFICATION_PURPOSE,
                token_digest=digest_token(token),
                expires_at=expires_at,
            ),
            Job(
                id=job_id,
                kind=VERIFICATION_JOB,
                dedupe_key=str(token_id),
                status="queued",
                attempts=0,
                payload={
                    "user_id": str(user.id),
                    "token_id": str(token_id),
                    "purpose": VERIFICATION_PURPOSE,
                },
                available_at=now,
            ),
        )
    )
    session.flush()
    session.add(
        AuthMailSecret(
            job_id=job_id,
            user_id=user.id,
            token_id=token_id,
            purpose=VERIFICATION_PURPOSE,
            token_ciphertext=ciphertext,
            nonce=nonce,
            kms_key_id=key_id,
            expires_at=expires_at,
        )
    )


def request_verification(
    engine: Engine, email: str, key: bytes, key_id: str, *, register: bool
) -> None:
    email_norm = email.lower()
    with Session(engine) as session, session.begin():
        if register:
            user_id = session.scalar(
                insert(User)
                .values(id=uuid4(), email=email, email_norm=email_norm, status="pending")
                .on_conflict_do_nothing(index_elements=[User.email_norm])
                .returning(User.id)
            )
            if user_id is None:
                return

        user = session.scalar(select(User).where(User.email_norm == email_norm).with_for_update())
        if user is None or user.status != "pending" or user.deleted_at is not None:
            return

        current = session.scalar(
            select(AuthToken)
            .where(
                AuthToken.user_id == user.id,
                AuthToken.purpose == VERIFICATION_PURPOSE,
                AuthToken.consumed_at.is_(None),
                AuthToken.superseded_at.is_(None),
            )
            .with_for_update()
        )
        now = utc_now()
        if current is not None:
            if now < current.expires_at - VERIFICATION_TTL + RESEND_COOLDOWN:
                return
            current.superseded_at = now
            retire_delivery(session, current.id)
            session.flush()
        issue_verification(session, user, now, key, key_id)


def verify_account(engine: Engine, token: str, password: str, display_name: str) -> bool:
    digest = digest_token(token)
    with Session(engine) as session, session.begin():
        user_id = session.scalar(select(AuthToken.user_id).where(AuthToken.token_digest == digest))
        if user_id is None:
            return False
        user = session.get(User, user_id, with_for_update=True)
        if user is None or user.status != "pending" or user.deleted_at is not None:
            return False

        proof = session.scalar(
            select(AuthToken)
            .where(AuthToken.user_id == user_id, AuthToken.token_digest == digest)
            .with_for_update()
        )
        now = utc_now()
        if (
            proof is None
            or proof.purpose != VERIFICATION_PURPOSE
            or proof.consumed_at is not None
            or proof.superseded_at is not None
            or proof.expires_at <= now
        ):
            return False

        proof.consumed_at = now
        user.password_hash = hash_password(password)
        user.status = "active"
        user.verified_at = now
        session.add(UserProfile(user_id=user.id, display_name=display_name))
        retire_delivery(session, proof.id)
        return True
