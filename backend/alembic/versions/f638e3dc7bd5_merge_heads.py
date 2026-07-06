"""merge heads

Revision ID: f638e3dc7bd5
Revises: 700a65a98d34, f21472a159ff
Create Date: 2026-07-06 02:19:34.337352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f638e3dc7bd5'
down_revision: Union[str, Sequence[str], None] = ('700a65a98d34', 'f21472a159ff')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
