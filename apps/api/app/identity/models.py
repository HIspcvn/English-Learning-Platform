from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

VERIFICATION_PURPOSE = "verify_email"
VERIFICATION_JOB = "auth.verify_email"
RESET_PURPOSE = "reset_password"
RESET_JOB = "auth.reset_password"
AUTH_MAIL_JOB_BY_PURPOSE = {VERIFICATION_PURPOSE: VERIFICATION_JOB, RESET_PURPOSE: RESET_JOB}


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email_norm", name="uq_users_email_norm"),
        CheckConstraint(
            "(status = 'pending' AND password_hash IS NULL AND verified_at IS NULL) OR "
            "(status = 'active' AND password_hash IS NOT NULL AND verified_at IS NOT NULL) OR "
            "status = 'deactivated'",
            name="ck_users_status_credentials",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(254))
    email_norm: Mapped[str] = mapped_column(String(254))
    status: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str | None] = mapped_column(Text)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    display_name: Mapped[str] = mapped_column(String(80))
    bio: Mapped[str | None] = mapped_column(String(500))


class LearningPreferences(Base):
    __tablename__ = "learning_preferences"
    __table_args__ = (
        CheckConstraint("locale IN ('vi', 'en')", name="ck_learning_preferences_locale"),
        CheckConstraint(
            "current_cefr IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="ck_learning_preferences_current_cefr",
        ),
        CheckConstraint(
            "default_accent IN ('uk', 'us', 'system')",
            name="ck_learning_preferences_default_accent",
        ),
        CheckConstraint("revision > 0", name="ck_learning_preferences_revision"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(2), server_default="vi")
    timezone: Mapped[str] = mapped_column(Text)
    current_cefr: Mapped[str] = mapped_column(String(2))
    target_kind: Mapped[str | None] = mapped_column(Text)
    target_code: Mapped[str | None] = mapped_column(Text)
    exam_date: Mapped[date | None]
    default_accent: Mapped[str] = mapped_column(Text, server_default="system")
    ai_opt_in: Mapped[bool] = mapped_column(server_default=text("false"))
    social_opt_in: Mapped[bool] = mapped_column(server_default=text("false"))
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revision: Mapped[int] = mapped_column(server_default=text("1"))


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        CheckConstraint("octet_length(body_hash) = 32", name="ck_idempotency_records_hash_length"),
        Index("ix_idempotency_records_expires_at", "expires_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    operation_id: Mapped[str] = mapped_column(Text, primary_key=True)
    idem_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    body_hash: Mapped[bytes] = mapped_column(LargeBinary)
    response_status: Mapped[int]
    response_body: Mapped[dict[str, object]] = mapped_column(JSONB)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        UniqueConstraint("token_digest", name="uq_auth_sessions_token_digest"),
        CheckConstraint("octet_length(token_digest) = 32", name="ck_auth_sessions_digest_length"),
        CheckConstraint(
            "octet_length(csrf_secret) = 32", name="ck_auth_sessions_csrf_secret_length"
        ),
        Index("ix_auth_sessions_user_id_revoked_at", "user_id", "revoked_at"),
        Index("ix_auth_sessions_expires_at", "expires_at"),
        Index("ix_auth_sessions_last_seen_at", "last_seen_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_digest: Mapped[bytes] = mapped_column(LargeBinary)
    csrf_secret: Mapped[bytes] = mapped_column(LargeBinary)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reauthenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuthToken(Base):
    __tablename__ = "auth_tokens"
    __table_args__ = (
        UniqueConstraint("token_digest", name="uq_auth_tokens_token_digest"),
        CheckConstraint("octet_length(token_digest) = 32", name="ck_auth_tokens_digest_length"),
        Index("ix_auth_tokens_user_id", "user_id"),
        Index("ix_auth_tokens_expires_at", "expires_at"),
        Index(
            "uq_auth_tokens_open_user_purpose",
            "user_id",
            "purpose",
            unique=True,
            postgresql_where=text("consumed_at IS NULL AND superseded_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(Text)
    token_digest: Mapped[bytes] = mapped_column(LargeBinary)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("kind", "dedupe_key", name="uq_jobs_kind_dedupe_key"),
        CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')",
            name="ck_jobs_status",
        ),
        CheckConstraint("attempts >= 0", name="ck_jobs_attempts_nonnegative"),
        Index("ix_jobs_status_available_at", "status", "available_at"),
        Index("ix_jobs_lease_until", "lease_until"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    kind: Mapped[str] = mapped_column(Text)
    dedupe_key: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(server_default=text("0"))
    payload: Mapped[dict[str, str]] = mapped_column(JSONB)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_owner: Mapped[str | None] = mapped_column(Text)
    last_error_code: Mapped[str | None] = mapped_column(Text)


class AuthMailSecret(Base):
    __tablename__ = "auth_mail_secrets"
    __table_args__ = (
        UniqueConstraint("token_id", name="uq_auth_mail_secrets_token_id"),
        Index("ix_auth_mail_secrets_user_id", "user_id"),
        Index("ix_auth_mail_secrets_expires_at", "expires_at"),
    )

    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_id: Mapped[UUID] = mapped_column(ForeignKey("auth_tokens.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(Text)
    token_ciphertext: Mapped[bytes] = mapped_column(LargeBinary)
    nonce: Mapped[bytes] = mapped_column(LargeBinary)
    kms_key_id: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuthRateLimit(Base):
    __tablename__ = "auth_rate_limits"
    __table_args__ = (
        CheckConstraint("count > 0", name="ck_auth_rate_limits_count_positive"),
        Index("ix_auth_rate_limits_expires_at", "expires_at"),
    )

    key: Mapped[UUID] = mapped_column(primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    count: Mapped[int]
