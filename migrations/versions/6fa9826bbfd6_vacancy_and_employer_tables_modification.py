"""vacancy and employer tables modification

Revision ID: 6fa9826bbfd6
Revises: 071cd2d3f34f
Create Date: 2024-02-10 14:42:56.883066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fa9826bbfd6'
down_revision = '071cd2d3f34f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employer_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('employment', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('schedule', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('experience', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('salary', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('type', sa.String(), nullable=True))
        batch_op.alter_column('alternate_url',
               existing_type=sa.VARCHAR(length=256),
               type_=sa.String(length=128),
               existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_vacancy_employer_id'), ['employer_id'], unique=False)
        batch_op.create_foreign_key('fk_vacancy_employer_id', 'employer', ['employer_id'], ['id'])
        batch_op.drop_column('employer')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employer', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('fk_vacancy_employer_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_vacancy_employer_id'))
        batch_op.alter_column('alternate_url',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=256),
               existing_nullable=True)
        batch_op.drop_column('type')
        batch_op.drop_column('salary')
        batch_op.drop_column('experience')
        batch_op.drop_column('schedule')
        batch_op.drop_column('employment')
        batch_op.drop_column('archived')
        batch_op.drop_column('employer_id')

    # ### end Alembic commands ###
