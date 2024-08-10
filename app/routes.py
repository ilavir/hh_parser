from math import ceil
from datetime import datetime, timezone
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import any_
import json
import ast

from app import app, db
from app.functions import (get_database_files, get_employer_by_id, get_vacancies,
                           get_vacancy_by_id, get_vacancy_relation_status_list,
                           change_vacancy_relation_status, change_vacancy_relation_notes, change_vacancy_relation_conversation_content, change_vacancy_relation_favorite,
                           change_employer_relation_notes)
from app.hh_api import get_hh_authorization_code, get_hh_tokens, refresh_hh_tokens, hh_search_vacancies, hh_vacancy_get, hh_employer_get
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SearchForm, EmptyForm
from app.models import User, Vacancy, get_vacancy, Employer, get_employer, VacancyRelation, get_relation, DictRelationStatus
from app.hh_dicts import DictProfessionalRoles, DictIndustries
import re


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/')
def index():

    return redirect(url_for('search'))


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

            user.check_hh_auth()
            session['hh_auth'] = user.hh_auth
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

    if text:
        params = {
            'text': text,
            'page': page,
            'per_page': per_page,
            'area': area,
            'period': period,
            'order_by': 'publication_time'
        }
        # Get vacancies list from HH API
        response = hh_search_vacancies(params, current_user)
        vacancies_json = response.json()

        # Vacancy JSON refactoring
        for item in vacancies_json['items']:

            # Get vacancy relations from DB
            if current_user.is_authenticated:
                vacancy_relation = get_relation(current_user.id, int(item['id']))

                if vacancy_relation:
                    item['custom_in_db'] = True
                    item['custom_hidden'] = vacancy_relation.hidden

            # Format date for displaying in search results
            datetime_obj = datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
            item['published_at'] = datetime_obj.strftime("%d-%m-%Y")

            remove_tags = re.compile('<.*?>')
            if item['snippet']['requirement']:
                item['snippet']['requirement'] = re.sub(remove_tags, '', item['snippet']['requirement'])
            if item['snippet']['responsibility']:
                item['snippet']['responsibility'] = re.sub(remove_tags, '', item['snippet']['responsibility'])
    else:
        vacancies_json = None
        params = None

    return render_template('search.html', form=form, empty_form=empty_form, page=page, vacancies=vacancies_json, params=params, user=current_user)


@app.route('/employer/<employer_hh_id>')
def employer_detail(employer_hh_id):
    # Get Vacancy from DB or create
    employer = get_employer(employer_hh_id)
    app.logger.debug(f'employer_detail(): Employer in DB: {employer}')

    if not employer:
        app.logger.debug('employer_detail(): Employer not in DB')
        employer = Employer(hh_id=employer_hh_id)
        employer = employer_save(employer)
        if employer == 404:
            return '404 Error: Employer not found', 404
    else:
        employer = employer_update(employer)

    db.session.commit()

    ## Render employer details page
    # Get industry ID's from Dictionary and convert them to list of names for displaying in employer details
    industries = []
    industries_json = json.loads(employer.industries) if employer.industries else None
    if industries_json is not None:
        for industry in industries_json:
            industry_name = DictIndustries.query.filter_by(id=industry).first()
            industries.append(industry_name.name)
    employer.industries_json = industries

    return render_template('employer.html', employer=employer)


def employer_save(employer):
    employer_response = hh_employer_get(employer.hh_id, current_user)

    if employer_response.status_code == 404:
        app.logger.debug('employer_save(): Employer not found')

        return 404

    employer_json = employer_response.json()

    employer.save_from_hh(employer_json)
    app.logger.debug(f'employer_save(): Employer added to DB: {employer}')

    return employer

def employer_update(employer):

    return employer


@app.route('/vacancy/<vacancy_hh_id>', methods=['GET', 'POST'])
def vacancy_detail(vacancy_hh_id):
    vacancy_snippet = request.form.get('vacancy_snippet', None)

    # Get Vacancy from DB or create
    vacancy = get_vacancy(vacancy_hh_id)
    app.logger.debug(f'vacancy_detail(): Vacancy in DB: {vacancy}')

    if not vacancy:
        app.logger.debug('vacancy_detail(): Vacancy not in DB')
        vacancy = Vacancy(hh_id=vacancy_hh_id)
        vacancy = vacancy_save(vacancy, vacancy_snippet)
        if vacancy == 404:
            return '404 Error: Vacancy not found', 404
    else:
        # vacancy = vacancy_update(vacancy)
        pass

    db.session.commit()

    if current_user.is_authenticated:
        # Get vacancy relation from DB
        relation = get_relation(current_user.id, int(vacancy.hh_id))
    else:
        relation = None

    ## Render vacancy details page
    # Convert strings to JSON for displaying in vacancy details
    vacancy.salary_json = json.loads(vacancy.salary) if vacancy.salary else None
    vacancy.address_json = json.loads(vacancy.address) if vacancy.address else None
    vacancy.contacts_json = json.loads(vacancy.contacts) if vacancy.contacts else None
    vacancy.key_skills_json = json.loads(vacancy.key_skills) if vacancy.key_skills else None
    # Format date for displaying in vacancy details
    vacancy.published_at_formatted = vacancy.published_at.strftime("%d-%m-%Y")

    # Get professional roles ID's from Dictionary and convert them to list of names for displaying in vacancy details
    professional_roles = []
    professional_roles_json = json.loads(vacancy.professional_roles) if vacancy.professional_roles else None
    for role in professional_roles_json:
        role_name = DictProfessionalRoles.query.filter_by(id=role).first()
        professional_roles.append(role_name.name)
    vacancy.professional_roles_json = professional_roles

    form = EmptyForm()

    return render_template('vacancy.html', vacancy=vacancy, user=current_user, relation=relation, form=form)


def vacancy_save(vacancy, vacancy_snippet=None):
    vacancy_response = hh_vacancy_get(vacancy.hh_id, current_user)

    if vacancy_response.status_code == 404:
        app.logger.debug('vacancy_save(): Vacancy not found')

        return 404

    vacancy_json = vacancy_response.json()

    if 'employer' in vacancy_json and 'id' in vacancy_json['employer']:
        # Get Employer from DB or create
        employer = get_employer(vacancy_json['employer']['id'])
        app.logger.debug(f'vacancy_save(): Employer in DB: {employer}')

        if not employer:
            app.logger.debug('vacancy_save(): Employer not in DB')
            employer = Employer(hh_id=vacancy_json['employer']['id'])
            employer = employer_save(employer)
        else:
            employer = employer_update(employer)
    else:
        employer = None

    # vacancy = Vacancy(hh_id=vacancy_json['id'])
    try:
        vacancy_snippet_json = json.loads(vacancy_snippet) if vacancy_snippet else None
    except ValueError as e:
        vacancy_snippet_json = ast.literal_eval(vacancy_snippet) if vacancy_snippet else None
    vacancy.snippet = json.dumps(vacancy_snippet_json, ensure_ascii=False) if vacancy_snippet_json else None
    vacancy.employer = employer
    vacancy.save_from_hh(vacancy_json)
    vacancy.relations = vacancy_json.get('relations', None)
    app.logger.debug(f'vacancy_save(): Vacancy added to DB: {vacancy}')

    return vacancy

def vacancy_update(vacancy, vacancy_snippet=None):
    vacancy_response = hh_vacancy_get(vacancy.hh_id, current_user)

    if vacancy_response.status_code == 404:
        app.logger.debug('vacancy_update(): Vacancy not found')
        flash(f'WARNING! {vacancy} was deleted from HH.')
        return vacancy_response

    vacancy_json = vacancy_response.json()
    # try:
    #     vacancy_snippet_json = json.loads(vacancy_snippet) if vacancy_snippet else None
    # except ValueError as e:
    #     vacancy_snippet_json = ast.literal_eval(vacancy_snippet) if vacancy_snippet else None
    # vacancy.snippet = json.dumps(vacancy_snippet_json, ensure_ascii=False) if vacancy_snippet_json else None
    vacancy.update_from_hh(vacancy_json)
    vacancy.relations = vacancy_json.get('relations', None)
    app.logger.debug(f'vacancy_update(): Vacancy updated: {vacancy}')

    return vacancy


@app.route('/vacancy/_status_update', methods=['POST'])
def vacancy_status_update():
    form = EmptyForm()

    if form.validate_on_submit():
        new_status = request.form.get('status_update', None)
        vacancy_hh_id = request.form.get('vacancy_hh_id', None)
        if vacancy_hh_id == None:
            return 'Error! Vacancy ID not found.'

        # Get Vacancy from DB
        vacancy = get_vacancy(vacancy_hh_id)
        if not vacancy:
            return 'Error! Vacancy not found.'

        # Create relation
        if current_user.is_authenticated:
            # Get vacancy relation from DB
            relation = get_relation(current_user.id, int(vacancy_hh_id))

            if not relation:
                app.logger.debug('New relation')
                relation = VacancyRelation(user_id=current_user.id, vacancy_id=vacancy.id)
                db.session.add(relation)
            else:
                app.logger.debug('Existing relation')

            relation_status_list = db.session.scalars(DictRelationStatus.query).all()
            relation_status_id_list = [result.id for result in relation_status_list]

            if new_status in relation_status_id_list:
                relation.relation_status_id = new_status
                app.logger.debug(f'RelationStatus updated to {new_status}')

        db.session.commit()

    else:
        # Redirect if form not validated
        return 'Form not validated', 500

    return redirect(url_for('vacancy_detail', vacancy_hh_id=vacancy_hh_id))


@app.route('/vacancy/_save', methods=['POST'])
def vacancy_save_or_update():
    form = EmptyForm()

    if form.validate_on_submit():
        vacancy_hh_id = request.form.get('vacancy_hh_id', None, str)
        vacancy_snippet = request.form.get('vacancy_snippet', None)

        # Get Vacancy from DB or create
        vacancy = get_vacancy(vacancy_hh_id)
        app.logger.debug(f'vacancy_save_or_update(): Vacancy in DB: {vacancy}')

        if not vacancy:
            app.logger.debug('vacancy_save_or_update(): Vacancy not in DB')
            vacancy = Vacancy(hh_id=vacancy_hh_id)
            vacancy = vacancy_save(vacancy, vacancy_snippet)
            if type(vacancy) is not Vacancy:
                return '404 Error: Vacancy not found', 404
        else:
            vacancy = vacancy_update(vacancy, vacancy_snippet)
            if type(vacancy) is not Vacancy:
                return '404 Error: Vacancy not found', 404

        # Create relation
        if current_user.is_authenticated:
            # Get vacancy relation from DB
            relation = get_relation(current_user.id, int(vacancy_hh_id))

            if not relation:
                app.logger.debug('New relation')
                relation = VacancyRelation(user_id=current_user.id, vacancy_id=vacancy.id, relation_status_id='new')
                db.session.add(relation)
            else:
                app.logger.debug('Existing relation')

            relation.hh_relations = vacancy.relations
            app.logger.debug(relation)

            # Actions to "Save", "Hide", "Unhide" buttons clicked
            action = request.form.get('action')

            if action == 'hide_unhide':
                if relation.hidden == True or relation is None:
                    relation.hidden = False
                    button_text = 'Скрыть'  # New text for the button
                    button_class = 'btn-secondary'  # New class for the button
                    background_class1 = None  # New background class for the button container tr
                    background_class2 = None  # Optional Secondary backround class for the button container tr
                    app.logger.debug('unhide')
                else:
                    relation.hidden = True
                    button_text = 'Показать'
                    button_class = 'btn-outline-secondary'
                    background_class1 = 'bg-light'
                    background_class2 = None
                    app.logger.debug('hide')
            if action == 'save':
                button_text = 'Обновить'
                button_class = 'btn-success'
                background_class1 = None  # New background class for the button container tr
                background_class2 = None  # Optional Secondary backround class for the button container tr
                app.logger.debug('save')
        else:
            relation = None

        db.session.commit()

        # Make a response for JS when clicked "Save", "Hide", "Unhide" buttons
        if action == 'hide_unhide' or action == 'save':
            return jsonify({'buttonText': button_text, 'buttonClass': button_class, 'backgroundClass1': background_class1, 'backgroundClass2': background_class2})
    else:
        # Redirect if form not validated
        return 'Form not validated', 500

    return 'ok'


@app.route('/vacancy/_update_bulk', methods=['POST'])
def vacancy_update_bulk():
    checked_vacancies = request.form.getlist('checkedItems', None)
    app.logger.debug(checked_vacancies)
    relation_status = request.form.get('show', 'all', str)

    form = EmptyForm()

    if form.validate_on_submit():

        if checked_vacancies:
            for vacancy_hh_id in checked_vacancies:
                vacancy = get_vacancy(vacancy_hh_id)
                relation = get_relation(current_user.id, int(vacancy_hh_id))
                vacancy = vacancy_update(vacancy)

                if type(vacancy) is not Vacancy:
                    continue

                relation.hh_relations = vacancy.relations
                app.logger.debug(f'vacancy_update_bulk(): {vacancy} updated.')
                db.session.commit()

        return redirect(url_for('dashboard', show=relation_status))

    else:
        # Redirect if form not validated
        return 'Form not validated', 500


@app.route('/dashboard')
@login_required
def dashboard():
    relation_status = request.args.get('show', 'all', str)
    relation_hidden = request.args.get('hidden', False, bool)

    relation_status_list = db.session.scalars(DictRelationStatus.query.order_by(DictRelationStatus.listorder)).all()
    relation_status_id_list = [result.id for result in relation_status_list]

    if relation_status == 'hidden':
        vacancies = db.session.scalars(current_user.vacancies.select().where(VacancyRelation.hidden == True).order_by(Vacancy.published_at.desc())).all()
    elif relation_status == 'all':
        vacancies = db.session.scalars(current_user.vacancies.select().where(VacancyRelation.hidden == False).order_by(Vacancy.published_at.desc())).all()
    elif relation_status in relation_status_id_list:
        if not relation_hidden:
            vacancies = db.session.scalars(current_user.vacancies.select().where(VacancyRelation.hidden == False).where(VacancyRelation.relation_status_id == relation_status).order_by(Vacancy.published_at.desc())).all()
        else:
            vacancies = db.session.scalars(current_user.vacancies.select().where(VacancyRelation.relation_status_id == relation_status).order_by(Vacancy.published_at.desc())).all()
    else:
        vacancies = None

    # Format fields for vacancies rendering page
    if vacancies:
        for vacancy in vacancies:
            vacancy.salary_json = json.loads(vacancy.salary) if vacancy.salary else None
            vacancy.published_at_formatted = vacancy.published_at.strftime("%d-%m-%Y")
            vacancy.key_skills_json = json.loads(vacancy.key_skills) if vacancy.key_skills else None

            # Remove tags in description
            if vacancy.description:
                remove_tags = re.compile('<.*?>')
                vacancy.description = re.sub(remove_tags, '', vacancy.description)

            # Get vacancy relations from DB
            if current_user.is_authenticated:
                vacancy.relation = get_relation(current_user.id, int(vacancy.hh_id))

    form = EmptyForm()

    return render_template('dashboard.html', user=current_user, vacancies=vacancies, show=relation_status, form=form, relation_status_list=relation_status_list)