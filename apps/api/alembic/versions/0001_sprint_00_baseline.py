"""Establish Alembic history before the first product schema migration."""

revision = "0001_sprint_00_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Record the baseline revision without creating product tables."""


def downgrade() -> None:
    """Return to the revision-free Alembic state."""
