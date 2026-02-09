"""merge heads

Revision ID: 4ebbfaa1fcb4
Revises: 0001a1b2c3d4, 87fc548207dd
Create Date: 2026-02-07 22:44:15.402162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4ebbfaa1fcb4'
down_revision: Union[str, None] = ('0001a1b2c3d4', '87fc548207dd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
