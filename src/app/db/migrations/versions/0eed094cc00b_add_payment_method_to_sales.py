"""add payment_method to sales

Revision ID: 0ee0bd94cc0
Revises: 378043ba77c0
Create Date: 2026-02-10 21:02:57.291277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0eed094cc00b"
down_revision: Union[str, None] = "XXXXXXXXXXXX"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("sales", sa.Column("payment_method", sa.String(length=20), server_default="cash", nullable=False))

def downgrade() -> None:
    op.drop_column("sales", "payment_method")