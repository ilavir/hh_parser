"""dictionary professional roles added

Revision ID: 8cf87bd676af
Revises: 1e7d3486c45f
Create Date: 2024-02-12 01:07:35.615373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cf87bd676af'
down_revision = '1e7d3486c45f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dict_professional_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hh_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hh_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dict_professional_roles')
    # ### end Alembic commands ###
