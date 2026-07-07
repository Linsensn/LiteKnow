"""resolve multiple heads

Revision ID: a760ad1f27e8
Revises: 06fd2880d87c, d406220988bf
Create Date: 2026-07-07 02:04:32.814368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a760ad1f27e8'
down_revision: Union[str, Sequence[str], None] = ('06fd2880d87c', 'd406220988bf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
