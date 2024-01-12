from flask import Flask, render_template, request
import sqlite3
import json
import os
from math import ceil
from datetime import datetime

# generate typical flask application code
app = Flask(__name__)


def get_database_files():
    db_path = 'db/'

    return [f for f in os.listdir(db_path) if f.endswith('.db')]


def db_connect(selected_db):
    conn = sqlite3.connect(f'db/{selected_db}')
    cursor = conn.cursor()

    return conn, cursor


def get_vacancies(selected_db, offset=0, per_page=20):
    conn, cursor = db_connect(selected_db)
    query = """
        SELECT vacancy.hh_id, vacancy.name AS vacancy_name, area.name AS area_name, schedule.name AS schedule_name, vacancy.salary,
        employer.hh_id AS employer_hh_id, employer.name AS employer_name, vacancy.published_at, vacancy.snippet
        FROM vacancy
        JOIN area ON vacancy.area_id = area.area_id
        JOIN schedule ON vacancy.schedule_id = schedule.schedule_id
        JOIN employer ON vacancy.employer_id = employer.employer_id
        ORDER BY vacancy.published_at DESC
        LIMIT ? OFFSET ?;
    """
    cursor.execute(query, (per_page, offset))
    vacancies = cursor.fetchall()

    # Count total vacancies
    cursor.execute("SELECT COUNT(*) FROM vacancy")
    total_vacancies = cursor.fetchone()[0]

    conn.close()

    # Convert salary strings to dictionaries
    for i, vacancy in enumerate(vacancies):
        dt_object = datetime.strptime(vacancy[7], "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = dt_object.strftime("%d.%m.%Y")
        vacancies[i] = vacancy[:4] + (json.loads(vacancy[4]),) + vacancy[5:7] + (formatted_date,) + (json.loads(vacancy[8]),) + vacancy[9:]

    return vacancies, total_vacancies


def get_vacancy_by_id(selected_db, vacancy_id):
    conn, cursor = db_connect(selected_db)
    query = """
        SELECT vacancy.hh_id, vacancy.name, area.name, schedule.name, vacancy.salary,
        employer.hh_id, employer.name FROM vacancy JOIN area ON vacancy.area_id = area.area_id
        JOIN schedule ON vacancy.schedule_id = schedule.schedule_id JOIN employer ON vacancy.employer_id = employer.employer_id
        WHERE vacancy.hh_id = ?
    """
    cursor.execute(query, (vacancy_id,))
    vacancy = cursor.fetchone()

    # Convert salary string to dictionary
    if vacancy and vacancy[4]:
        vacancy = vacancy[:4] + (json.loads(vacancy[4]),) + vacancy[5:]

    conn.close()

    return vacancy


@app.route('/')
def index():
    db_files = get_database_files()
    selected_db = request.args.get('db', db_files[0] if db_files else None)

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    vacancies, total_vacancies = get_vacancies(selected_db, offset=offset, per_page=per_page)
    print(total_vacancies)
    pagination = {'page': page, 'per_page': per_page, 'total': total_vacancies, 'pages': ceil(total_vacancies / per_page)}

    return render_template('index.html', db_files=db_files, selected_db=selected_db, vacancies=vacancies, pagination=pagination)


@app.route('/vacancy/<hh_id>')
def vacancy_detail(hh_id):
    selected_db = request.args.get('db')
    vacancy = get_vacancy_by_id(selected_db, hh_id)

    if not vacancy:
        return "Vacancy not found", 404

    return render_template('vacancy.html', vacancy=vacancy)


if __name__ == '__main__':
    app.run(debug=True)
