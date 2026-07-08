"""merge migration heads

Revision ID: 39e7a565867a
Revises: b44d4ca973af, cc52ad35bc74
Create Date: 2026-07-08 03:33:53.375605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39e7a565867a'
down_revision: Union[str, Sequence[str], None] = ('b44d4ca973af', 'cc52ad35bc74')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
