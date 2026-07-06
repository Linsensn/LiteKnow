"""merge sessions softdelete and practice_mode change

Revision ID: 7e8d87fd07c6
Revises: 077c4236872b, dca608c143c0
Create Date: 2026-07-06 00:37:30.791744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e8d87fd07c6'
down_revision: Union[str, Sequence[str], None] = ('077c4236872b', 'dca608c143c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
