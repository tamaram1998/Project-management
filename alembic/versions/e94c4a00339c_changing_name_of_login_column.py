"""Changing name of login column

Revision ID: e94c4a00339c
Revises: a2b43ca74131
Create Date: 2024-06-17 21:43:28.097962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e94c4a00339c'
down_revision: Union[str, None] = 'a2b43ca74131'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
