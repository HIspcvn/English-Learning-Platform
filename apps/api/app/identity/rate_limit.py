from datetime import UTC, datetime, timedelta
from math import ceil
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import Engine, case, delete, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.identity.models import AuthRateLimit

WINDOW = timedelta(minutes=15)
EMAIL_LIMIT = 5
EMAIL_IP_LIMIT = 20
VERIFY_IP_LIMIT = 10


def charge(session: Session, scope: str, value: str, limit: int, now: datetime) -> int | None:
    key = uuid5(NAMESPACE_URL, f"elp:auth-rate:{scope}\0{value}")
    expired = AuthRateLimit.expires_at <= now
    expiry = now + WINDOW
    updated = session.scalar(
        insert(AuthRateLimit)
        .values(key=key, expires_at=expiry, count=1)
        .on_conflict_do_update(
            index_elements=[AuthRateLimit.key],
            set_={
                "expires_at": case((expired, expiry), else_=AuthRateLimit.expires_at),
                "count": case((expired, 1), else_=AuthRateLimit.count + 1),
            },
            where=or_(expired, AuthRateLimit.count < limit),
        )
        .returning(AuthRateLimit.expires_at)
    )
    if updated is not None:
        return None
    expires_at = session.scalar(select(AuthRateLimit.expires_at).where(AuthRateLimit.key == key))
    return max(1, ceil((expires_at - now).total_seconds()))


def retry_after(engine: Engine, peer: str, email: str | None = None) -> int | None:
    now = datetime.now(UTC)
    expired_keys = (
        select(AuthRateLimit.key)
        .where(AuthRateLimit.expires_at <= now)
        .order_by(AuthRateLimit.expires_at, AuthRateLimit.key)
        .limit(50)
        .with_for_update(skip_locked=True)
    )
    # Release cleanup locks before acquiring request-specific counters.
    with engine.begin() as connection:
        connection.execute(delete(AuthRateLimit).where(AuthRateLimit.key.in_(expired_keys)))
    with Session(engine) as session, session.begin():
        if email is None:
            return charge(session, "verify:ip", peer, VERIFY_IP_LIMIT, now)
        ip_retry = charge(session, "verification-mail:ip", peer, EMAIL_IP_LIMIT, now)
        if ip_retry is not None:
            return ip_retry
        return charge(session, "verification-mail:email", email.lower(), EMAIL_LIMIT, now)
