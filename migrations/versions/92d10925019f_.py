"""empty message

Revision ID: 92d10925019f
Revises: c223865c23e2
Create Date: 2018-12-13 22:57:22.459845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92d10925019f'
down_revision = 'c223865c23e2'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('event', 'target', existing_type=sa.VARCHAR(), nullable=True)


def downgrade():
    event = sa.table('event', sa.column('target'))
    op.execute(event.update().values(target=''))
    op.alter_column('event', 'target', existing_type=sa.VARCHAR(), nullable=False, )
