"""merge_final_two_heads

Revision ID: c5bc5b53cb68
Revises: a760ad1f27e8, f638e3dc7bd5
Create Date: 2026-07-07 02:34:59.565159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5bc5b53cb68'
down_revision: Union[str, Sequence[str], None] = ('a760ad1f27e8', 'f638e3dc7bd5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
