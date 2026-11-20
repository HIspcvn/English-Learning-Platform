"""Add learner biographies and persisted command receipts."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0004_learner_settings"
down_revision = "0003_secure_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("bio", sa.String(500)))
    op.create_table(
        "idempotency_records",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("operation_id", sa.Text(), primary_key=True),
        sa.Column("idem_key", sa.String(128), primary_key=True),
        sa.Column("body_hash", sa.LargeBinary(), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=False),
        sa.Column("response_body", JSONB(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "octet_length(body_hash) = 32", name="ck_idempotency_records_hash_length"
        ),
    )
    op.create_index("ix_idempotency_records_expires_at", "idempotency_records", ["expires_at"])


def downgrade() -> None:
    op.drop_table("idempotency_records")
    op.drop_column("user_profiles", "bio")
