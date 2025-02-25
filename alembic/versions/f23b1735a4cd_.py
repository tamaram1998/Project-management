"""empty message

Revision ID: f23b1735a4cd
Revises:
Create Date: 2024-06-12 20:29:29.647269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f23b1735a4cd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_project_participants_id'), 'project_participants', ['id'], unique=False)
    op.alter_column('projects', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('projects', 'description',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.create_index(op.f('ix_projects_description'), 'projects', ['description'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_project_id'), 'projects', ['project_id'], unique=False)
    op.alter_column('users', 'login',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_login'), 'users', ['login'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_login'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.alter_column('users', 'login',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_index(op.f('ix_projects_project_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_description'), table_name='projects')
    op.alter_column('projects', 'description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('projects', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_index(op.f('ix_project_participants_id'), table_name='project_participants')
    # ### end Alembic commands ###
