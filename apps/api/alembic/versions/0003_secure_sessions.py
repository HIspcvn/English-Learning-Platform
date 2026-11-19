"""Add secure auth sessions and the preferences read model."""

import sqlalchemy as sa
from alembic import op

revision = "0003_secure_sessions"
down_revision = "0002_email_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_preferences",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("locale", sa.String(2), server_default="vi", nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False),
        sa.Column("current_cefr", sa.String(2), nullable=False),
        sa.Column("target_kind", sa.Text()),
        sa.Column("target_code", sa.Text()),
        sa.Column("exam_date", sa.Date()),
        sa.Column("default_accent", sa.Text(), server_default="system", nullable=False),
        sa.Column("ai_opt_in", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("social_opt_in", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("onboarding_completed_at", sa.DateTime(timezone=True)),
        sa.Column("revision", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint("locale IN ('vi', 'en')", name="ck_learning_preferences_locale"),
        sa.CheckConstraint(
            "current_cefr IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="ck_learning_preferences_current_cefr",
        ),
        sa.CheckConstraint(
            "default_accent IN ('uk', 'us', 'system')",
            name="ck_learning_preferences_default_accent",
        ),
        sa.CheckConstraint("revision > 0", name="ck_learning_preferences_revision"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("token_digest", sa.LargeBinary(), nullable=False),
        sa.Column("csrf_secret", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reauthenticated_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("token_digest", name="uq_auth_sessions_token_digest"),
        sa.CheckConstraint(
            "octet_length(token_digest) = 32", name="ck_auth_sessions_digest_length"
        ),
        sa.CheckConstraint(
            "octet_length(csrf_secret) = 32", name="ck_auth_sessions_csrf_secret_length"
        ),
    )
    op.create_index(
        "ix_auth_sessions_user_id_revoked_at", "auth_sessions", ["user_id", "revoked_at"]
    )
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_index("ix_auth_sessions_last_seen_at", "auth_sessions", ["last_seen_at"])


def downgrade() -> None:
    op.drop_table("auth_sessions")
    op.drop_table("learning_preferences")
