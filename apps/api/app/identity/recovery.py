from datetime import timedelta
from hmac import compare_digest
from typing import TypeGuard

from sqlalchemy import Engine, select, update
from sqlalchemy.orm import Session

from app.identity.models import RESET_PURPOSE, AuthSession, AuthToken, User
from app.identity.service import (
    digest_token,
    hash_password,
    issue_mail_proof,
    lock_current_proof,
    retire_delivery,
    supersede_proof,
    utc_now,
)

RESET_TTL = timedelta(minutes=30)


def _can_recover(user: User | None) -> TypeGuard[User]:
    return (
        user is not None
        and user.status == "active"
        and user.verified_at is not None
        and user.deleted_at is None
    )


def request_password_reset(engine: Engine, email: str, key: bytes, key_id: str) -> None:
    with Session(engine) as session, session.begin():
        user = session.scalar(
            select(User).where(User.email_norm == email.lower()).with_for_update()
        )
        if not _can_recover(user):
            return
        current = lock_current_proof(session, user.id, RESET_PURPOSE)
        now = utc_now()
        if current is not None:
            supersede_proof(session, current, now)
        issue_mail_proof(session, user, now, key, key_id, purpose=RESET_PURPOSE, ttl=RESET_TTL)


def reset_password(engine: Engine, token: str, password: str) -> bool:
    digest = digest_token(token)
    with Session(engine) as session, session.begin():
        user_id = session.scalar(
            select(AuthToken.user_id).where(
                AuthToken.token_digest == digest, AuthToken.purpose == RESET_PURPOSE
            )
        )
        if user_id is None:
            return False
        user = session.get(User, user_id, with_for_update=True)
        if not _can_recover(user):
            return False
        proof = lock_current_proof(session, user_id, RESET_PURPOSE)
        now = utc_now()
        if (
            proof is None
            or not compare_digest(proof.token_digest, digest)
            or proof.expires_at <= now
        ):
            return False

        proof.consumed_at = now
        user.password_hash = hash_password(password)
        session.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        retire_delivery(session, proof.id)
        return True
