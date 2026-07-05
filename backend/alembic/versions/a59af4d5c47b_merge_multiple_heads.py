"""Merge multiple heads

Revision ID: a59af4d5c47b
Revises: 340f8ad93b36, 7ef9f8bee362
Create Date: 2026-07-04 09:04:46.582655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a59af4d5c47b'
down_revision: Union[str, Sequence[str], None] = ('340f8ad93b36', '7ef9f8bee362')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
