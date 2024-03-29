"""professional_roles table to string

Revision ID: b0057c87f77b
Revises: 310594c49663
Create Date: 2024-02-14 13:12:24.572602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0057c87f77b'
down_revision = '310594c49663'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('professional_roles', sa.String(), nullable=True))
        batch_op.drop_index('ix_vacancy_professional_roles_id')
        batch_op.drop_constraint('fk_vacancy_professional_roles_id', type_='foreignkey')
        batch_op.drop_column('professional_roles_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('professional_roles_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_vacancy_professional_roles_id', 'dict_professional_roles', ['professional_roles_id'], ['id'])
        batch_op.create_index('ix_vacancy_professional_roles_id', ['professional_roles_id'], unique=False)
        batch_op.drop_column('professional_roles')

    # ### end Alembic commands ###
