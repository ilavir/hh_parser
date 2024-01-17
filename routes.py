from math import ceil
from flask import render_template, request
from app import app
from functions import (get_database_files, get_employer_by_id, get_vacancies,
                       get_vacancy_by_id, get_vacancy_relation_status_list,
                       change_vacancy_relation_status, change_vacancy_relation_notes, change_vacancy_relation_conversation_content, change_vacancy_relation_favorite,
                       change_employer_relation_notes)


@app.route('/', methods = ['POST', 'GET'])
def index():
    db_files = get_database_files()

    selected_db = request.args.get('db', db_files[0] if db_files else None)
        
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    relation_status_list = get_vacancy_relation_status_list(selected_db)
    vacancies, total_vacancies = get_vacancies(selected_db, offset=offset, per_page=per_page)
    pagination = {'page': page, 'per_page': per_page,
                  'total': total_vacancies, 'pages': ceil(total_vacancies / per_page)}

    return render_template('index.html', db_files=db_files, selected_db=selected_db,
                           vacancies=vacancies, pagination=pagination, status_list=relation_status_list)


@app.route('/vacancy/<hh_id>', methods = ['POST', 'GET'])
def vacancy_detail(hh_id):
    selected_db = request.args.get('db')
    page_source = request.args.get('page_source', 1)

    vacancy_id = request.form.get('vacancy_id', None)
    notes_content = request.form.get('notes_content', None)
    conversation_content = request.form.get('conversation_content', None)

    if notes_content is not None:
        change_vacancy_relation_notes(selected_db, vacancy_id, notes_content)

    if conversation_content is not None:
        change_vacancy_relation_conversation_content(selected_db, vacancy_id, conversation_content)

    vacancy = get_vacancy_by_id(selected_db, hh_id)

    if not vacancy:
        return "Vacancy not found", 404

    relation_status_list = get_vacancy_relation_status_list(selected_db)

    return render_template('vacancy.html', vacancy=vacancy, selected_db=selected_db, status_list=relation_status_list, page_source=page_source)


@app.route('/employer/<hh_id>', methods = ['POST', 'GET'])
def employer_detail(hh_id):
    selected_db = request.args.get('db')
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


@app.route('/update_content', methods = ['POST'])
def update_content():
    selected_db = request.form.get('db')
    vacancy_id = request.form.get('vacancy_id', None)
    relation_status = request.form.get('relation_status', None)
    relation_favorite = request.form.get('favorite', None)

    if vacancy_id and relation_favorite:
        change_vacancy_relation_favorite(selected_db, vacancy_id, relation_favorite)

    print(selected_db, vacancy_id, relation_status)

    if vacancy_id and relation_status:
        change_vacancy_relation_status(selected_db, vacancy_id, relation_status)

    return 'Good'