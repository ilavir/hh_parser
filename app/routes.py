from math import ceil
from datetime import datetime, timezone
from flask import render_template, request, flash, redirect, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
import json

from app import app, db
from app.functions import (get_database_files, get_employer_by_id, get_vacancies,
                           get_vacancy_by_id, get_vacancy_relation_status_list,
                           change_vacancy_relation_status, change_vacancy_relation_notes, change_vacancy_relation_conversation_content, change_vacancy_relation_favorite,
                           change_employer_relation_notes)
from app.hh_api import get_hh_authorization_code, get_hh_tokens, refresh_hh_tokens, hh_search_vacancies, hh_vacancy_get
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SearchForm, EmptyForm
from app.models import User, Vacancy


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


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
        user.check_hh_auth()
        session['hh_auth'] = user.hh_auth

        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('user', username=current_user.username)

        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('hh_auth', None)
    logout_user()

    return redirect(url_for('login'))


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
    
    try:
        hh_auth = session['hh_auth']
    except:
        hh_auth = False

    return render_template('profile.html', user=user, hh_auth=hh_auth)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')

        return redirect(url_for('user', username=current_user.username))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@app.route('/hh_auth', methods=['GET'])
@login_required
def hh_auth():
    action = request.args.get('action', None)
    error = request.args.get('error', None)
    authorization_code = request.args.get('code', None)

    user = db.session.scalar(sa.select(User).where(User.id == current_user.id))

    if error:
        flash(f'ERROR! Failed to obtain tokens. Tokens are not updated. Error message: {error}')
        app.logger.warning(f'Failed to obtain tokens. Tokens are not updated. Error message: {error}')

        return redirect(url_for('user', username=current_user.username))

    if authorization_code:
        access_token, refresh_token = get_hh_tokens(authorization_code)

        if access_token and refresh_token:
            user.access_token = access_token
            user.refresh_token = refresh_token
            db.session.commit()
            app.logger.info('New tokens are obtained and updated.')
            flash('SUCCESS! New tokens are obtained and updated.')

            user.check_hh_auth()
            session['hh_auth'] = user.hh_auth

        else:
            flash('ERROR! Failed to obtain tokens. Tokens are not updated.')

        return redirect(url_for('user', username=current_user.username))
    
    if action == 'check_status':
        
        user.check_hh_auth()
        session['hh_auth'] = user.hh_auth

        return redirect(url_for('user', username=current_user.username))
    
    elif action == 'refresh_tokens':
        current_refresh_token = user.refresh_token
        access_token, refresh_token = refresh_hh_tokens(current_refresh_token)

        if access_token and refresh_token:
            user.access_token = access_token
            user.refresh_token = refresh_token
            db.session.commit()
            app.logger.info('New tokens are obtained and updated.')
            flash('SUCCESS! New tokens are obtained and updated.')
        else:
            flash(f'ERROR! Failed to obtain tokens. Tokens are not updated.')
            app.logger.error(f'Failed to obtain tokens. Tokens are not updated.')

        return redirect(url_for('user', username=current_user.username))

    elif action == 'get_tokens':
        oauth_url = get_hh_authorization_code()
        
        return redirect(oauth_url)
    
    return redirect(url_for('user', username=current_user.username))


@app.route('/search', methods=['GET', 'POST'])
def search():
    page = request.args.get('page', 0, type=int)
    text = request.args.get('text', None)
    per_page = request.args.get('per_page', 10)
    area = request.args.get('area', 16)
    period = request.args.get('period', None)

    form = SearchForm()
    empty_form = EmptyForm()
    
    params = {
        'text': text,
        'page': page,
        'per_page': per_page,
        'area': area,
        'period': period,
        'order_by': 'publication_time'
    }
    respond_json = hh_search_vacancies(params)

    # Format date
    for item in respond_json['items']:
        datetime_obj = datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%S%z")
        item['published_at'] = datetime_obj.strftime("%d-%m-%Y")

    return render_template('search.html', form=form, empty_form=empty_form, page=page, vacancies=respond_json, params=params)


@app.route('/vacancy/_save', methods=['GET', 'POST'])
def vacancy_save():
    hh_id = request.form.get('vacancy_hh_id', None, str)

    vacancy_json = hh_vacancy_get(hh_id)
    vacancy = Vacancy(hh_id=vacancy_json['id'], name=vacancy_json['name'])
    vacancy.save()
    print(vacancy)

    return 'Vacancy saved.'