"""vacancy table updated

Revision ID: 6174243e5519
Revises: 0b5efabcffd8
Create Date: 2024-02-13 22:28:40.694727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6174243e5519'
down_revision = '0b5efabcffd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('area_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('employment_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('experience_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('professional_roles_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('schedule_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('type_id', sa.Integer(), nullable=True))
        batch_op.drop_index('ix_vacancy_area')
        batch_op.drop_index('ix_vacancy_employment')
        batch_op.drop_index('ix_vacancy_experience')
        batch_op.drop_index('ix_vacancy_professional_roles')
        batch_op.drop_index('ix_vacancy_schedule')
        batch_op.drop_index('ix_vacancy_type')
        batch_op.create_index(batch_op.f('ix_vacancy_area_id'), ['area_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_employment_id'), ['employment_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_experience_id'), ['experience_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_professional_roles_id'), ['professional_roles_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_schedule_id'), ['schedule_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_vacancy_type_id'), ['type_id'], unique=False)
        batch_op.drop_constraint('fk_vacancy_area_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_professional_roles_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_experience_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_employment_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_schedule_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_type_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_vacancy_experience_id', 'dict_experience', ['experience_id'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_schedule_id', 'dict_schedule', ['schedule_id'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_type_id', 'dict_vacancy_type', ['type_id'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_employment_id', 'dict_employment', ['employment_id'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_area_id', 'dict_area', ['area_id'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_professional_roles_id', 'dict_professional_roles', ['professional_roles_id'], ['id'])
        batch_op.drop_column('experience')
        batch_op.drop_column('employment')
        batch_op.drop_column('type')
        batch_op.drop_column('schedule')
        batch_op.drop_column('area')
        batch_op.drop_column('professional_roles')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacancy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('professional_roles', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('area', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('schedule', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('type', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('employment', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('experience', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('fk_vacancy_professional_roles_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_area_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_employment_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_type_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_schedule_id', type_='foreignkey')
        batch_op.drop_constraint('fk_vacancy_experience_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_vacancy_type_id', 'dict_vacancy_type', ['type'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_schedule_id', 'dict_schedule', ['schedule'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_employment_id', 'dict_employment', ['employment'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_experience_id', 'dict_experience', ['experience'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_professional_roles_id', 'dict_professional_roles', ['professional_roles'], ['id'])
        batch_op.create_foreign_key('fk_vacancy_area_id', 'dict_area', ['area'], ['id'])
        batch_op.drop_index(batch_op.f('ix_vacancy_type_id'))
        batch_op.drop_index(batch_op.f('ix_vacancy_schedule_id'))
        batch_op.drop_index(batch_op.f('ix_vacancy_professional_roles_id'))
        batch_op.drop_index(batch_op.f('ix_vacancy_experience_id'))
        batch_op.drop_index(batch_op.f('ix_vacancy_employment_id'))
        batch_op.drop_index(batch_op.f('ix_vacancy_area_id'))
        batch_op.create_index('ix_vacancy_type', ['type'], unique=False)
        batch_op.create_index('ix_vacancy_schedule', ['schedule'], unique=False)
        batch_op.create_index('ix_vacancy_professional_roles', ['professional_roles'], unique=False)
        batch_op.create_index('ix_vacancy_experience', ['experience'], unique=False)
        batch_op.create_index('ix_vacancy_employment', ['employment'], unique=False)
        batch_op.create_index('ix_vacancy_area', ['area'], unique=False)
        batch_op.drop_column('type_id')
        batch_op.drop_column('schedule_id')
        batch_op.drop_column('professional_roles_id')
        batch_op.drop_column('experience_id')
        batch_op.drop_column('employment_id')
        batch_op.drop_column('area_id')

    # ### end Alembic commands ###
