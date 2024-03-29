from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app, db, login
from app.hh_api import check_hh_authorization
from app.hh_dicts import DictArea, DictEmployerType, DictEmployment, DictExperience, DictIndustries, DictProfessionalRoles, DictSchedule, DictVacancyType

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    access_token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    refresh_token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    registration_date: so.Mapped[Optional[datetime]] = so.mapped_column(default=datetime.utcnow)
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=datetime.utcnow)

    vacancies: so.WriteOnlyMapped['Vacancy'] = so.relationship(secondary='vacancy_relation',
                                                               #primaryjoin=('vacancy_relation.c.user_id' == id),
                                                               backref='users')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def check_hh_auth(self):
        self.hh_auth = check_hh_authorization(self.access_token)
        return self.hh_auth
    

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Employer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    site_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    trusted: so.Mapped[Optional[bool]] = so.mapped_column()
    type_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictEmployerType.id, name='fk_employer_type_id'), index=True) # dict
    area_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(DictArea.id, name='fk_employer_area_id'), index=True) # dict
    industries: so.Mapped[Optional[str]] = so.mapped_column() # *temporary* # dict
    alternate_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(default=datetime.utcnow)

    area: so.Mapped[DictArea] = so.relationship(backref='employers')
    type: so.Mapped[DictEmployerType] = so.relationship(backref='employers')
    vacancies: so.WriteOnlyMapped['Vacancy'] = so.relationship(back_populates='employer')

    def __repr__(self):
        return f'<Employer (ID: {self.id}) "{self.hh_id}: {self.name}">'
    
    def if_exists(self):
        query = sa.select(Employer).where(Employer.hh_id == self.hh_id)
        return db.session.scalar(query) is not None
    
    def get(self):
        query = sa.select(Employer).where(Employer.hh_id == self.hh_id)
        return db.session.scalar(query)
    
    # Format Employer for saving in DB
    def save(self):
        if not self.if_exists():
            db.session.add(self)
            self.area = db.session.scalar(sa.select(DictArea).where(DictArea.hh_id == self.area_id))
            self.type = db.session.scalar(sa.select(DictEmployerType).where(DictEmployerType.hh_id == self.type_id))
            app.logger.debug(f'Employer (ID: {self.id}) "{self.hh_id}: {self.name}" added to database.')
            return True
        else:
            app.logger.debug(f'Employer (ID: {self.id}) "{self.hh_id}: {self.name}" already exists.')
            return False


# Get Employer object by employer hh_id
def get_employer(hh_id):
    query = sa.select(Employer).where(Employer.hh_id == hh_id)
    return db.session.scalar(query)


class Vacancy(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128))
    updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(default=datetime.utcnow)
    archived: so.Mapped[Optional[bool]] = so.mapped_column()
    employer_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(Employer.id, name='fk_vacancy_employer_id'), index=True)
    salary: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    address: so.Mapped[Optional[str]] = so.mapped_column()
    contacts: so.Mapped[Optional[str]] = so.mapped_column()
    snippet: so.Mapped[Optional[str]] = so.mapped_column()
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    key_skills: so.Mapped[Optional[str]] = so.mapped_column()
    professional_roles: so.Mapped[Optional[str]] = so.mapped_column() # *temporary* # dict
    #professional_roles_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictProfessionalRoles.id, name='fk_vacancy_professional_roles_id'), index=True) # dict
    area_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(DictArea.id, name='fk_vacancy_area_id'), index=True) # dict
    employment_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictEmployment.id, name='fk_vacancy_employment_id'), index=True) # dict
    experience_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictExperience.id, name='fk_vacancy_experience_id'), index=True) # dict
    schedule_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictSchedule.id, name='fk_vacancy_schedule_id'), index=True) # dict
    type_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictVacancyType.id, name='fk_vacancy_type_id'), index=True) # dict
    alternate_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    published_at: so.Mapped[Optional[datetime]] = so.mapped_column()
    initial_created_at: so.Mapped[Optional[datetime]] = so.mapped_column()
    employer: so.Mapped[Employer] = so.relationship(back_populates='vacancies')
    area: so.Mapped[DictArea] = so.relationship(backref='vacancies')
    employment: so.Mapped[DictEmployment] = so.relationship(backref='vacancies')
    experience: so.Mapped[DictExperience] = so.relationship(backref='vacancies')
    schedule: so.Mapped[DictSchedule] = so.relationship(backref='vacancies')
    type: so.Mapped[DictVacancyType] = so.relationship(backref='vacancies')

    def __repr__(self):
        return f'<Vacancy (ID: {self.id}) "{self.hh_id}: {self.name}">'
    
    def if_exists(self):
        query = sa.select(Vacancy).where(Vacancy.hh_id == self.hh_id)
        return db.session.scalar(query) is not None
    
    def get(self):
        query = sa.select(Vacancy).where(Vacancy.hh_id == self.hh_id)
        return db.session.scalar(query)
    
    # Format Vacancy for saving in DB
    def save(self):
        db.session.add(self)
        self.area = db.session.scalar(sa.select(DictArea).where(DictArea.hh_id == self.area_id))
        self.employment = db.session.scalar(sa.select(DictEmployment).where(DictEmployment.hh_id == self.employment_id))
        self.experience = db.session.scalar(sa.select(DictExperience).where(DictExperience.hh_id == self.experience_id))
        self.schedule = db.session.scalar(sa.select(DictSchedule).where(DictSchedule.hh_id == self.schedule_id))
        self.type = db.session.scalar(sa.select(DictVacancyType).where(DictVacancyType.hh_id == self.type_id))
        app.logger.debug(f'Vacancy (ID: {self.id}) "{self.hh_id}: {self.name}" added to database.')

    def save_or_update(self, employer, user, relation):
        app.logger.debug(self)
        app.logger.debug(employer)
        app.logger.debug(user)
        app.logger.debug(relation)

        # Create new Vacancy if not exists
        if not self.if_exists():
            app.logger.debug('Adding vacancy...')
            
            # Create new Employer if not exists
            if not employer.if_exists():
                app.logger.debug('Adding employer...')
                employer.save()
                self.employer = employer
            # Update Employer if exists
            else:
                self.employer = employer
                app.logger.debug('Existing employer.')

            self.save()
            app.logger.debug(self)
            if user not in self.users and user.is_authenticated:
                relation.vacancy_id = self.id
                db.session.add(relation)
            app.logger.debug(relation)

        # Update Vacancy if exists
        else:
            app.logger.debug('Existing vacancy.')
            if user not in self.users and user.is_authenticated:
                relation.vacancy_id = self.id
                db.session.add(relation)

        db.session.commit()

        return f'Vacancy (ID: {self.id}) "{self.hh_id}: {self.name}" added or updated. \
                Employer (ID: {employer.id}) "{employer.hh_id}: {employer.name}" added or updated. \
                Relation {relation} added or updated.'
    
    #def add_user(self, user):
    #    if user not in self.users:
    #        self.users.append(user)
    #        #db.session.add(self)
    #        app.logger.debug(f'User "{user.id}" added to vacancy "{self.id}".')

# Get Vacancy object by vacancy hh_id
def get_vacancy(hh_id):
    query = sa.select(Vacancy).where(Vacancy.hh_id == hh_id)
    return db.session.scalar(query)


class VacancyRelation(db.Model):
    #id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), primary_key=True)
    vacancy_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Vacancy.id), primary_key=True)
    hidden: so.Mapped[bool] = so.mapped_column(default=False, nullable=False)
    relations: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    def __repr__(self):
        return f'<Relation "{self.user_id}: {self.vacancy_id}">'
    
    #def update(self):

def get_relation(user_id, vacancy_hh_id):
    user_alias = so.aliased(User)
    vacancy_alias = so.aliased(Vacancy)
    query = sa.select(VacancyRelation) \
            .join(user_alias, VacancyRelation.user_id == user_alias.id) \
            .join(vacancy_alias, VacancyRelation.vacancy_id == vacancy_alias.id) \
            .where(user_alias.id == user_id, vacancy_alias.hh_id == vacancy_hh_id)
    return db.session.scalar(query)