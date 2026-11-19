"""Add the email identity lifecycle and durable verification mail queue."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002_email_identity"
down_revision = "0001_sprint_00_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("email_norm", sa.String(254), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text()),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("email_norm", name="uq_users_email_norm"),
        sa.CheckConstraint(
            "(status = 'pending' AND password_hash IS NULL AND verified_at IS NULL) OR "
            "(status = 'active' AND password_hash IS NOT NULL AND verified_at IS NOT NULL) OR "
            "status = 'deactivated'",
            name="ck_users_status_credentials",
        ),
    )
    op.create_table(
        "user_profiles",
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("display_name", sa.String(80), nullable=False),
    )
    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("token_digest", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("superseded_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("token_digest", name="uq_auth_tokens_token_digest"),
        sa.CheckConstraint("octet_length(token_digest) = 32", name="ck_auth_tokens_digest_length"),
    )
    op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"])
    op.create_index("ix_auth_tokens_expires_at", "auth_tokens", ["expires_at"])
    op.create_index(
        "uq_auth_tokens_open_user_purpose",
        "auth_tokens",
        ["user_id", "purpose"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL AND superseded_at IS NULL"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("dedupe_key", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
        sa.Column("lease_owner", sa.Text()),
        sa.Column("last_error_code", sa.Text()),
        sa.UniqueConstraint("kind", "dedupe_key", name="uq_jobs_kind_dedupe_key"),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')",
            name="ck_jobs_status",
        ),
        sa.CheckConstraint("attempts >= 0", name="ck_jobs_attempts_nonnegative"),
    )
    op.create_index("ix_jobs_status_available_at", "jobs", ["status", "available_at"])
    op.create_index("ix_jobs_lease_until", "jobs", ["lease_until"])
    op.create_table(
        "auth_mail_secrets",
        sa.Column(
            "job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "token_id",
            sa.Uuid(),
            sa.ForeignKey("auth_tokens.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("token_ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("nonce", sa.LargeBinary(), nullable=False),
        sa.Column("kms_key_id", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("token_id", name="uq_auth_mail_secrets_token_id"),
    )
    op.create_index("ix_auth_mail_secrets_user_id", "auth_mail_secrets", ["user_id"])
    op.create_index("ix_auth_mail_secrets_expires_at", "auth_mail_secrets", ["expires_at"])
    op.create_table(
        "auth_rate_limits",
        sa.Column("key", sa.Uuid(), primary_key=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.CheckConstraint("count > 0", name="ck_auth_rate_limits_count_positive"),
    )
    op.create_index("ix_auth_rate_limits_expires_at", "auth_rate_limits", ["expires_at"])


def downgrade() -> None:
    op.drop_table("auth_mail_secrets")
    op.drop_table("jobs")
    op.drop_table("auth_tokens")
    op.drop_table("user_profiles")
    op.drop_table("users")
    op.drop_table("auth_rate_limits")
