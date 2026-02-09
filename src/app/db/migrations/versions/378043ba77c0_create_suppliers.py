"""create suppliers

Revision ID: 378043ba77c0
Revises: 4ebbfaa1fcb4
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "378043ba77c0"
down_revision = "4ebbfaa1fcb4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("document", sa.String(length=30), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("suppliers")
