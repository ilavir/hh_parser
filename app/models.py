from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app, db, login
from app.hh_api import check_hh_authorization

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    access_token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    refresh_token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    registration_date: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

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


class Vacancy(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128))
    area: so.Mapped[Optional[int]] = so.mapped_column()
    employer: so.Mapped[Optional[int]] = so.mapped_column()
    alternate_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    published_at: so.Mapped[Optional[datetime]] = so.mapped_column()
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column()

    def __repr__(self):
        return f'<Vacancy {self.hh_id}: {self.name}>'
    
    def if_exists(self):
        query = sa.select(Vacancy).where(Vacancy.hh_id == self.hh_id)
        return db.session.scalar(query) is not None
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        app.logger.debug('Vacancy added to database.')

    def update(self):
        vacancy = db.session.scalar(sa.select(Vacancy).where(Vacancy.hh_id == self.hh_id))
        app.logger.debug(vacancy)
        vacancy.updated_at = datetime.now(timezone.utc)
        vacancy.area = self.area
        vacancy.employer = self.employer
        vacancy.alternate_url = self.alternate_url
        vacancy.published_at = self.published_at
        vacancy.created_at = self.created_at
        db.session.commit()
        app.logger.debug('Vacancy updated.')

    def save_or_update(self, user_id):
        if self.if_exists():
            self.update()
            return f'Vacancy {self.hh_id} updated.'
        else:
            self.save()
            return f'Vacancy {self.hh_id} added to database.'

class Employer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    hh_id: so.Mapped[int] = so.mapped_column(unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128))

    def __repr__(self):
        return f'<Employer {self.hh_id}: {self.name}>'
    

class VacancyRelation(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    vacancy_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Vacancy.id), index=True)