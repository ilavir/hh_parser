from datetime import datetime, timezone
from typing import Optional
import json
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app, db, login
from app.hh_api import check_hh_authorization, hh_employer_get
from app.hh_dicts import DictArea, DictEmployerType, DictEmployment, DictExperience, DictIndustries, DictProfessionalRoles, DictSchedule, DictVacancyType
from typing import List
from typing import Dict

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
        
    def save_from_hh(self, employer_json):
        if not self.if_exists():
             # *temporary* Make a list for professional_roles
            industries = []
            for industry in employer_json['industries']:
                industry_id = DictIndustries.query.filter_by(hh_id=industry['id']).first()
                industries.append(industry_id.id)

            db.session.add(self)
            self.name=employer_json['name']
            self.description=employer_json['description']
            self.site_url=employer_json['site_url'] if employer_json['site_url'] else None
            self.trusted=employer_json['trusted']
            self.industries=json.dumps(industries) if industries else None
            self.alternate_url=employer_json['alternate_url']
            self.area = db.session.scalar(sa.select(DictArea).where(DictArea.hh_id == employer_json['area']['id']))
            self.type = db.session.scalar(sa.select(DictEmployerType).where(DictEmployerType.hh_id == employer_json['type']))

        return self


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
    snippet: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
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
    #relation: so.WriteOnlyMapped['VacancyRelation'] = so.relationship(secondary='vacancy_relation')

    def __repr__(self):
        return f'<Vacancy (ID: {self.id}) "{self.hh_id}: {self.name}">'
    
    def if_exists(self):
        query = sa.select(Vacancy).where(Vacancy.hh_id == self.hh_id)
        return db.session.scalar(query) is not None
    
    def get(self):
        query = sa.select(Vacancy).where(Vacancy.hh_id == self.hh_id)
        return db.session.scalar(query)
    
    def save_from_hh(self, vacancy_json):
        if not self.if_exists():
            # Vacancy JSON refactoring. Format date to UTC timezone
            published_at_obj = datetime.strptime(vacancy_json['published_at'], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
            initial_created_at_obj = datetime.strptime(vacancy_json['initial_created_at'], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
            # *temporary* Make a list for professional_roles
            professional_roles = []
            for role in vacancy_json['professional_roles']:
                role_id = DictProfessionalRoles.query.filter_by(hh_id=role['id']).first()
                professional_roles.append(role_id.id)

            db.session.add(self)
            self.name=vacancy_json['name']
            self.archived=vacancy_json['archived']
            self.salary=json.dumps(vacancy_json['salary']) if vacancy_json['salary'] else None
            self.address=json.dumps(vacancy_json['address'], ensure_ascii=False) if vacancy_json['address'] else None
            self.contacts=json.dumps(vacancy_json['contacts'], ensure_ascii=False) if vacancy_json['contacts'] else None
            self.description = vacancy_json['description'] if vacancy_json['description'] else None
            self.key_skills=json.dumps(vacancy_json['key_skills'], ensure_ascii=False) if vacancy_json['key_skills'] else None
            self.professional_roles=json.dumps(professional_roles) if professional_roles else None
            self.area = db.session.scalar(sa.select(DictArea).where(DictArea.hh_id == vacancy_json['area']['id']))
            self.employment = db.session.scalar(sa.select(DictEmployment).where(DictEmployment.hh_id == vacancy_json['employment']['id']))
            self.experience = db.session.scalar(sa.select(DictExperience).where(DictExperience.hh_id == vacancy_json['experience']['id']))
            self.schedule = db.session.scalar(sa.select(DictSchedule).where(DictSchedule.hh_id == vacancy_json['schedule']['id']))
            self.type = db.session.scalar(sa.select(DictVacancyType).where(DictVacancyType.hh_id == vacancy_json['type']['id']))
            self.alternate_url=vacancy_json['alternate_url']
            self.published_at=published_at_obj
            self.initial_created_at=initial_created_at_obj

        return self
    
    def update_from_hh(self, vacancy_json):
        if self.if_exists():
            self.updated_at = datetime.now(timezone.utc)
            # Vacancy JSON refactoring. Format date to UTC timezone
            published_at_obj = datetime.strptime(vacancy_json['published_at'], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
            self.published_at=published_at_obj
            self.name=vacancy_json['name']
            self.archived=vacancy_json['archived']
            self.salary=json.dumps(vacancy_json['salary']) if vacancy_json['salary'] else None
            self.address=json.dumps(vacancy_json['address'], ensure_ascii=False) if vacancy_json['address'] else None
            self.contacts=json.dumps(vacancy_json['contacts'], ensure_ascii=False) if vacancy_json['contacts'] else None
            self.description = vacancy_json['description'] if vacancy_json['description'] else None

        return self

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


class DictRelationStatus(db.Model):
    id: so.Mapped[str] = so.mapped_column(sa.String(64), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), unique=True)

    relations: so.Mapped['VacancyRelation'] = so.relationship(back_populates='status')
    
    def __repr__(self):
        return f'<DictRelationStatus "{self.id}: {self.name}">'
    

def init_relation_status():
    for status in [('new', 'Новые'), ('applied', 'Откликнулся'), ('interview', 'Интервью'), ('rejected', 'Отказ'), ('offer', 'Оффер'), ('unsuitable', 'Не подходит'), ('archived', 'Архив')]:
        new_item = DictRelationStatus(id=status[0], name=status[1])
        db.session.add(new_item)

    db.session.commit()
    print('Relation Status dictionary created.')


class VacancyRelation(db.Model):
    #id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), primary_key=True)
    vacancy_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Vacancy.id), primary_key=True)
    hidden: so.Mapped[bool] = so.mapped_column(default=False, nullable=False)
    favorite: so.Mapped[bool] = so.mapped_column(default=False, nullable=False)
    relation_status_id: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(DictRelationStatus.id, name='fk_relation_status_id'))
    hh_relations: so.Mapped[Optional[List[Dict]]] = so.mapped_column(sa.JSON)

    status: so.Mapped[DictRelationStatus] = so.relationship(back_populates='relations')

    def __repr__(self):
        return f'<Relation "{self.user_id}: {self.vacancy_id}">'
    

def get_relation(user_id, vacancy_hh_id):
    user_alias = so.aliased(User)
    vacancy_alias = so.aliased(Vacancy)
    query = sa.select(VacancyRelation) \
            .join(user_alias, VacancyRelation.user_id == user_alias.id) \
            .join(vacancy_alias, VacancyRelation.vacancy_id == vacancy_alias.id) \
            .where(user_alias.id == user_id, vacancy_alias.hh_id == vacancy_hh_id)
    return db.session.scalar(query)