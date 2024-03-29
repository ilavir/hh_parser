"""vacancy model foreign keys updated

Revision ID: 0b5efabcffd8
Revises: c6ee32663112
Create Date: 2024-02-12 02:07:47.216347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b5efabcffd8'
down_revision = 'c6ee32663112'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.alter_column('employment',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('experience',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('professional_roles',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('schedule',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_vacancy_area'), ['area'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_employment'), ['employment'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_experience'), ['experience'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_professional_roles'), ['professional_roles'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_schedule'), ['schedule'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_type'), ['type'], unique=False)
        batch_op.create_foreign_key('fk_vacancy_employment_id', 'dict_employment', ['employment'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_experience_id', 'dict_experience', ['experience'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_type_id', 'dict_vacancy_type', ['type'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_schedule_id', 'dict_schedule', ['schedule'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_professional_roles_id', 'dict_professional_roles', ['professional_roles'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_area_id', 'dict_area', ['area'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.drop_constraint('fk_vacancy_area_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_professional_roles_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_schedule_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_type_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_experience_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_employment_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_vacancy_type'))
        batch_op.drop_index(batch_op.f('ix_vacancy_schedule'))
        batch_op.drop_index(batch_op.f('ix_vacancy_professional_roles'))
        batch_op.drop_index(batch_op.f('ix_vacancy_experience'))
        batch_op.drop_index(batch_op.f('ix_vacancy_employment'))
        batch_op.drop_index(batch_op.f('ix_vacancy_area'))
        batch_op.alter_column('type',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('schedule',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('professional_roles',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('experience',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('employment',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    # ### end Alembic commands ###
