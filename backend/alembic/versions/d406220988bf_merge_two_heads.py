"""merge two heads

Revision ID: d406220988bf
Revises: f21472a159ff, f90191510143
Create Date: 2026-07-06 07:31:33.246297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd406220988bf'
down_revision: Union[str, Sequence[str], None] = ('f21472a159ff', 'f90191510143')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
