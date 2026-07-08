"""merge migration heads

Revision ID: cb1ff872a02e
Revises: 39e7a565867a, bf9422c1f57f
Create Date: 2026-07-08 07:04:09.127866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb1ff872a02e'
down_revision: Union[str, Sequence[str], None] = ('39e7a565867a', 'bf9422c1f57f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
