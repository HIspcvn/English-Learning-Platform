from dataclasses import dataclass, field
from datetime import datetime, timedelta
from secrets import token_bytes
from uuid import UUID, uuid4

from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import Engine, delete, or_, select, update
from sqlalchemy.orm import Session

from app.identity.models import AuthSession, LearningPreferences, User, UserProfile
from app.identity.schemas import UserView
from app.identity.service import digest_token, hash_password, new_token, password_hasher, utc_now

HARD_TTL = timedelta(days=30)
IDLE_TTL = timedelta(days=14)
ACTIVITY_INTERVAL = timedelta(minutes=5)
_DUMMY_PASSWORD_HASH = hash_password(new_token())


@dataclass(frozen=True)
class SessionIdentity:
    id: UUID
    csrf_secret: bytes = field(repr=False)
    user: UserView


def _user_view(id_: UUID, display_name: str, preferences: LearningPreferences | None) -> UserView:
    return UserView(
        id=id_,
        display_name=display_name,
        locale=preferences.locale if preferences else "vi",
        timezone=preferences.timezone if preferences else "UTC",
        roles=["learner"],
        verified=True,
        onboarding_completed=preferences is not None
        and preferences.onboarding_completed_at is not None,
    )


def _active_session(now: datetime):
    return (
        AuthSession.revoked_at.is_(None),
        AuthSession.expires_at > now,
        AuthSession.last_seen_at > now - IDLE_TTL,
    )


def _active_user():
    return (User.status == "active", User.deleted_at.is_(None), User.verified_at.is_not(None))


def load_session(engine: Engine, token: str, *, touch: bool = False) -> SessionIdentity | None:
    now = utc_now()
    with Session(engine) as session, session.begin():
        row = session.execute(
            select(AuthSession, UserProfile.display_name, LearningPreferences)
            .join(User, User.id == AuthSession.user_id)
            .join(UserProfile, UserProfile.user_id == User.id)
            .outerjoin(LearningPreferences, LearningPreferences.user_id == User.id)
            .where(
                AuthSession.token_digest == digest_token(token),
                *_active_session(now),
                *_active_user(),
            )
        ).one_or_none()
        if row is None:
            return None
        auth, display_name, preferences = row
        update_before = now - ACTIVITY_INTERVAL
        if touch and auth.last_seen_at <= update_before:
            updated = session.execute(
                update(AuthSession)
                .where(
                    AuthSession.id == auth.id,
                    *_active_session(now),
                    AuthSession.last_seen_at <= update_before,
                )
                .values(last_seen_at=now)
            )
            if not updated.rowcount:
                # A concurrent refresh may have won, or this session was revoked meanwhile.
                if (
                    session.scalar(
                        select(AuthSession.id).where(
                            AuthSession.id == auth.id, *_active_session(now)
                        )
                    )
                    is None
                ):
                    return None
        return SessionIdentity(
            auth.id, auth.csrf_secret, _user_view(auth.user_id, display_name, preferences)
        )


def lock_active_learner(session: Session, identity: SessionIdentity) -> bool:
    # Follow password reset's user-first lock order before holding the session through a write.
    user_id = session.scalar(
        select(User.id).where(User.id == identity.user.id, *_active_user()).with_for_update()
    )
    if user_id is None:
        return False
    return (
        session.scalar(
            select(AuthSession.id)
            .where(
                AuthSession.id == identity.id,
                AuthSession.user_id == user_id,
                *_active_session(utc_now()),
            )
            .with_for_update()
        )
        is not None
    )


def _valid_credentials(password: str, encoded: str | None) -> bool:
    usable = encoded is not None and encoded.startswith("$argon2id$")
    try:
        return (
            password_hasher.verify(encoded if usable else _DUMMY_PASSWORD_HASH, password) and usable
        )
    except (InvalidHashError, VerificationError):
        return False


def revoke_session(session: Session, session_id: UUID, now: datetime) -> None:
    session.execute(
        update(AuthSession)
        .where(AuthSession.id == session_id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )


def login_account(
    engine: Engine, email: str, password: str, previous_session_id: UUID | None
) -> tuple[str, SessionIdentity] | None:
    with Session(engine) as session:
        candidate = session.execute(
            select(User.id, User.password_hash).where(
                User.email_norm == email.lower(), *_active_user()
            )
        ).one_or_none()
    if (
        not _valid_credentials(password, candidate.password_hash if candidate else None)
        or candidate is None
    ):
        return None

    with Session(engine) as session, session.begin():
        # Reset uses the same user lock. A hash verified before reset must not mint a new session after it.
        user_id = session.scalar(
            select(User.id)
            .where(
                User.id == candidate.id,
                User.password_hash == candidate.password_hash,
                *_active_user(),
            )
            .with_for_update()
        )
        if user_id is None:
            return None
        profile = session.get(UserProfile, user_id)
        if profile is None:
            return None
        preferences = session.get(LearningPreferences, user_id)
        now = utc_now()
        if previous_session_id is not None:
            revoke_session(session, previous_session_id, now)

        token = new_token()
        auth = AuthSession(
            id=uuid4(),
            user_id=user_id,
            token_digest=digest_token(token),
            csrf_secret=token_bytes(32),
            expires_at=now + HARD_TTL,
            last_seen_at=now,
        )
        session.add(auth)
        identity = SessionIdentity(
            auth.id, auth.csrf_secret, _user_view(user_id, profile.display_name, preferences)
        )
        return token, identity


def logout_session(engine: Engine, session_id: UUID) -> None:
    with Session(engine) as session, session.begin():
        revoke_session(session, session_id, utc_now())


def retire_expired_sessions(engine: Engine) -> None:
    now = utc_now()
    expired = (
        select(AuthSession.id)
        .where(or_(AuthSession.expires_at <= now, AuthSession.last_seen_at <= now - IDLE_TTL))
        .order_by(AuthSession.expires_at, AuthSession.id)
        .limit(100)
        .with_for_update(skip_locked=True)
    )
    with engine.begin() as connection:
        connection.execute(delete(AuthSession).where(AuthSession.id.in_(expired)))
