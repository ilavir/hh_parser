from math import ceil
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa

from app import app, db
from app.functions import (get_database_files, get_employer_by_id, get_vacancies,
                           get_vacancy_by_id, get_vacancy_relation_status_list,
                           change_vacancy_relation_status, change_vacancy_relation_notes, change_vacancy_relation_conversation_content, change_vacancy_relation_favorite,
                           change_employer_relation_notes)
from app.hh_auth import check_hh_auth
from app.forms import LoginForm, RegistrationForm
from app.models import User

import os

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    db_files = get_database_files()
    selected_db = request.args.get('db', db_files[0] if db_files else None)

    if not selected_db:
        return 'No databases found.'
    elif selected_db not in db_files:
        return 'No database found.'

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    relation_status_list = get_vacancy_relation_status_list(selected_db)
    vacancies, total_vacancies = get_vacancies(
        selected_db, offset=offset, per_page=per_page)
    pagination = {'page': page, 'per_page': per_page,
                  'total': total_vacancies, 'pages': ceil(total_vacancies / per_page)}

    return render_template('index.html', db_files=db_files, selected_db=selected_db,
                           vacancies=vacancies, pagination=pagination, status_list=relation_status_list)


@app.route('/vacancy/<hh_id>', methods=['POST', 'GET'])
def vacancy_detail(hh_id):
    db_files = get_database_files()
    selected_db = request.args.get('db', None)

    if not selected_db:
        return 'No database name specified.'
    elif selected_db not in db_files:
        return 'No database found.'

    page_source = request.args.get('page_source', 1)

    vacancy_id = request.form.get('vacancy_id', None)
    notes_content = request.form.get('notes_content', None)
    conversation_content = request.form.get('conversation_content', None)

    if notes_content is not None:
        change_vacancy_relation_notes(selected_db, vacancy_id, notes_content)

    if conversation_content is not None:
        change_vacancy_relation_conversation_content(
            selected_db, vacancy_id, conversation_content)

    vacancy = get_vacancy_by_id(selected_db, hh_id)

    if not vacancy:
        return "Vacancy not found", 404

    relation_status_list = get_vacancy_relation_status_list(selected_db)

    return render_template('vacancy.html', vacancy=vacancy, selected_db=selected_db, status_list=relation_status_list, page_source=page_source)


@app.route('/employer/<hh_id>', methods=['POST', 'GET'])
def employer_detail(hh_id):
    db_files = get_database_files()
    selected_db = request.args.get('db', None)

    if not selected_db:
        return 'No database name specified.'
    elif selected_db not in db_files:
        return 'No database found.'

    vacancy_source = request.args.get('vacancy_hh_id', None)
    page_source = request.args.get('page_source', 1)

    employer_id = request.form.get('employer_id', None)
    notes_content = request.form.get('notes_content', None)

    if notes_content is not None:
        change_employer_relation_notes(selected_db, employer_id, notes_content)

    employer, industries = get_employer_by_id(selected_db, hh_id)

    if not employer:
        return "Employer not found", 404

    return render_template('employer.html', employer=employer, selected_db=selected_db, industries=industries, vacancy_source=vacancy_source, page_source=page_source)


@app.route('/update_content', methods=['POST'])
def update_content():
    selected_db = request.form.get('db')
    vacancy_id = request.form.get('vacancy_id', None)
    relation_status = request.form.get('relation_status', None)
    relation_favorite = request.form.get('favorite', None)

    if vacancy_id and relation_favorite:
        change_vacancy_relation_favorite(
            selected_db, vacancy_id, relation_favorite)

    if vacancy_id and relation_status:
        change_vacancy_relation_status(
            selected_db, vacancy_id, relation_status)

    return 'Good'


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = 1
    hh_authorized, access_token, refresh_token = check_hh_auth(user_id)
    hh_authorization = {'hh_authorized': hh_authorized,
                        'access_token': access_token, 'refresh_token': refresh_token}

    return render_template('profile.html', hh_authorization=hh_authorization)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')

            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        flash(f'User {user.username} successfuly logged in.')

        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('user', username=user.username)

        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    tokens = {
        'access_token': 'sdfsd6776sdf',
        'refresh_token': 'efg443dssd7k'
    }

    return render_template('user.html', user=user, tokens=tokens)