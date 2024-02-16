"""vacancy_relation table

Revision ID: 9b053768ce88
Revises: 139f48da0645
Create Date: 2024-02-11 14:10:26.910221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b053768ce88'
down_revision = '139f48da0645'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy_relation', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy_relation', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###
