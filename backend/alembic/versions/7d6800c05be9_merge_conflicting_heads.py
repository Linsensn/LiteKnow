"""merge conflicting heads

Revision ID: 7d6800c05be9
Revises: 24781aa87fd2, 667fd4feaac7
Create Date: 2026-07-05 08:37:33.931469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d6800c05be9'
down_revision: Union[str, Sequence[str], None] = ('24781aa87fd2', '667fd4feaac7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
