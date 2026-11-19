from datetime import datetime
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
