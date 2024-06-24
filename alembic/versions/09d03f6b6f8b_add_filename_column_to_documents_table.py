"""Add filename column to documents table

Revision ID: 09d03f6b6f8b
Revises: e94c4a00339c
Create Date: 2024-06-19 21:39:44.005612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09d03f6b6f8b'
down_revision: Union[str, None] = 'e94c4a00339c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('filename', sa.String(), nullable=True))
    op.drop_index('ix_users_login', table_name='users')
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.create_index('ix_users_login', 'users', ['username'], unique=True)
    op.drop_column('documents', 'filename')
    # ### end Alembic commands ###