"""empty message

Revision ID: 071cd2d3f34f
Revises: aab72385ae3e
Create Date: 2024-02-09 00:00:43.065382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '071cd2d3f34f'
down_revision = 'aab72385ae3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('area', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('employer', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('alternate_url', sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column('published_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('published_at')
        batch_op.drop_column('alternate_url')
        batch_op.drop_column('employer')
        batch_op.drop_column('area')

    # ### end Alembic commands ###
