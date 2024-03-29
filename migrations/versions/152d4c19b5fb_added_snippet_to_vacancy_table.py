"""added snippet to vacancy table

Revision ID: 152d4c19b5fb
Revises: 6174243e5519
Create Date: 2024-02-14 11:26:37.587428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '152d4c19b5fb'
down_revision = '6174243e5519'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('snippet', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.drop_column('snippet')

    # ### end Alembic commands ###
