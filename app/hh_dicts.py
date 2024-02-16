from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
import requests
from app import app, db
#from app.models import Vacancy


class DictArea(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    parent_id: so.Mapped[Optional[int]] = so.mapped_column()
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    #vacancies: so.Mapped['Vacancy'] = so.relationship(backref='area')

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

class DictEmployerType(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'


class DictEmployment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    #vacancies: so.Mapped['Vacancy'] = so.relationship(back_populates='employment')

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

class DictExperience(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    #vacancies: so.Mapped['Vacancy'] = so.relationship(back_populates='experience')

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

class DictIndustries(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    parent_id: so.Mapped[Optional[int]] = so.mapped_column()
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

class DictProfessionalRoles(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    parent_id: so.Mapped[Optional[int]] = so.mapped_column()
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

class DictSchedule(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    #vacancies: so.Mapped['Vacancy'] = so.relationship(back_populates='schedule')

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

class DictVacancyType(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    #vacancies: so.Mapped['Vacancy'] = so.relationship(back_populates='type')

    def __repr__(self):
        return f'{self.hh_id}: {self.name}'
    

def init_dicts():
    init_area()
    init_employer_type()
    init_employment()
    init_experience()
    init_industries()
    init_professional_roles()
    init_schedule()
    init_vacancy_type()


def init_area():
    api_url = 'https://api.hh.ru/areas/'
    data = requests.get(api_url).json()

    init_area_recursive(data)

    db.session.commit()
    print('Area dictionary created.')

def init_area_recursive(data):
    for item in data:
        hh_id = item['id']
        parent_id = item['parent_id']
        name = item['name']

        # check if current area already exists in DB
        exists = db.session.scalar(sa.select(DictArea).where(DictArea.hh_id == hh_id))

        if not exists:
            new_item = DictArea(hh_id=hh_id, parent_id=parent_id, name=name)
            db.session.add(new_item)

        if item['areas']:
            init_area_recursive(item['areas'])


def init_employer_type():
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['employer_type']:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictEmployerType).where(DictEmployerType.hh_id == hh_id))
        if not exists:
            new_item = DictEmployerType(hh_id=hh_id, name=name)
            db.session.add(new_item)

    db.session.commit()
    print('Employer Type dictionary created.')


def init_employment():
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['employment']:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictEmployment).where(DictEmployment.hh_id == hh_id))
        if not exists:
            new_item = DictEmployment(hh_id=hh_id, name=name)
            db.session.add(new_item)

    db.session.commit()
    print('Employment dictionary created.')


def init_experience():
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['experience']:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictExperience).where(DictExperience.hh_id == hh_id))
        if not exists:
            new_item = DictExperience(hh_id=hh_id, name=name)
            db.session.add(new_item)

    db.session.commit()
    print('Experience dictionary created.')


def init_industries():
    api_url = 'https://api.hh.ru/industries'
    data = requests.get(api_url).json()

    init_industries_recursive(data)

    db.session.commit()
    print('Industries dictionary created.')


def init_industries_recursive(data, parent_id=None):
    for item in data:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictIndustries).where(DictIndustries.hh_id == hh_id))

        if not exists:
            new_item = DictIndustries(hh_id=hh_id, parent_id=parent_id, name=name)
            db.session.add(new_item)

        if item.get('industries'):
            init_industries_recursive(item['industries'], parent_id=hh_id)


def init_professional_roles():
    api_url = 'https://api.hh.ru/professional_roles'
    data = requests.get(api_url).json()['categories']

    init_professional_roles_recursive(data)

    db.session.commit()
    print('Professional Roles dictionary created.')


def init_professional_roles_recursive(data, parent_id=None):
    for item in data:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictProfessionalRoles).where(DictProfessionalRoles.hh_id == hh_id))

        if not exists:
            new_item = DictProfessionalRoles(hh_id=hh_id, parent_id=parent_id, name=name)
            db.session.add(new_item)

        if item.get('roles'):
            init_professional_roles_recursive(item['roles'], parent_id=hh_id)


def init_schedule():
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['schedule']:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictSchedule).where(DictSchedule.hh_id == hh_id))
        if not exists:
            new_item = DictSchedule(hh_id=hh_id, name=name)
            db.session.add(new_item)

    db.session.commit()
    print('Schedule dictionary created.')


def init_vacancy_type():
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['vacancy_type']:
        hh_id = item['id']
        name = item['name']

        exists = db.session.scalar(sa.select(DictVacancyType).where(DictVacancyType.hh_id == hh_id))
        if not exists:
            new_item = DictVacancyType(hh_id=hh_id, name=name)
            db.session.add(new_item)

    db.session.commit()
    print('Vacancy Type dictionary created.')


if __name__ == '__main__':
    init_dicts()