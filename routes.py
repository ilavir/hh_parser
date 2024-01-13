from math import ceil
from flask import render_template, request
from app import app
from functions import (get_database_files, get_employer_by_id, get_vacancies,
                       get_vacancy_by_id)


@app.route('/')
def index():
    db_files = get_database_files()
    selected_db = request.args.get('db', db_files[0] if db_files else None)

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    vacancies, total_vacancies = get_vacancies(
        selected_db, offset=offset, per_page=per_page)
    pagination = {'page': page, 'per_page': per_page,
                  'total': total_vacancies, 'pages': ceil(total_vacancies / per_page)}

    return render_template('index.html', db_files=db_files, selected_db=selected_db, vacancies=vacancies, pagination=pagination)


@app.route('/vacancy/<hh_id>')
def vacancy_detail(hh_id):
    selected_db = request.args.get('db')
    vacancy = get_vacancy_by_id(selected_db, hh_id)

    if not vacancy:
        return "Vacancy not found", 404

    return render_template('vacancy.html', vacancy=vacancy, selected_db=selected_db)


@app.route('/employer/<hh_id>')
def employer_detail(hh_id):
    selected_db = request.args.get('db')
    employer, industries = get_employer_by_id(selected_db, hh_id)

    if not employer:
        return "Employer not found", 404

    return render_template('employer.html', employer=employer, industries=industries)
