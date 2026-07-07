"""merge multiple heads

Revision ID: 06fd2880d87c
Revises: f21472a159ff, f90191510143
Create Date: 2026-07-07 01:46:38.418167

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06fd2880d87c'
down_revision: Union[str, Sequence[str], None] = ('f21472a159ff', 'f90191510143')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
