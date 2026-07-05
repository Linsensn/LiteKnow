"""resolve merge conflict

Revision ID: 700a65a98d34
Revises: 077c4236872b, dca608c143c0
Create Date: 2026-07-05 14:26:05.027501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '700a65a98d34'
down_revision: Union[str, Sequence[str], None] = ('077c4236872b', 'dca608c143c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
