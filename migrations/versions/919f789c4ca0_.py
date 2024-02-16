"""empty message

Revision ID: 919f789c4ca0
Revises: 6ab066d00ef4
Create Date: 2024-02-11 00:32:50.660893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '919f789c4ca0'
down_revision = '6ab066d00ef4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vacancy_relation',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('vacancy_id', sa.Integer(), nullable=False),
    sa.Column('hidden', sa.Boolean(), nullable=False),
    sa.Column('relations', sa.String(length=256), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['vacancy_id'], ['vacancy.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'vacancy_id')
    )
    op.drop_table('users_vacancies')
    with op.batch_alter_table('employer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trusted', sa.Boolean(), nullable=True))

    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('contacts', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('professional_roles', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('initial_created_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DATETIME(), nullable=True))
        batch_op.drop_column('initial_created_at')
        batch_op.drop_column('professional_roles')
        batch_op.drop_column('contacts')
        batch_op.drop_column('address')

    with op.batch_alter_table('employer', schema=None) as batch_op:
        batch_op.drop_column('trusted')

    op.create_table('users_vacancies',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('vacancy_id', sa.INTEGER(), nullable=False),
    sa.Column('hidden', sa.BOOLEAN(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['vacancy_id'], ['vacancy.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'vacancy_id')
    )
    op.drop_table('vacancy_relation')
    # ### end Alembic commands ###