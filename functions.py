import json
import os
import sqlite3
from datetime import datetime


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
        employer.hh_id AS employer_hh_id, employer.name AS employer_name, vacancy.published_at, vacancy.snippet,
        vacancy_relation.favorite, vacancy_relation.vacancy_relation_status_id, vacancy.vacancy_id
        FROM vacancy
        JOIN area ON vacancy.area_id = area.area_id
        JOIN schedule ON vacancy.schedule_id = schedule.schedule_id
        JOIN employer ON vacancy.employer_id = employer.employer_id
        LEFT JOIN vacancy_relation ON vacancy.vacancy_id = vacancy_relation.vacancy_id
        ORDER BY vacancy.published_at DESC
        LIMIT ? OFFSET ?;
    """
    cursor.execute(query, (per_page, offset))
    vacancies = cursor.fetchall()

    # Count total vacancies
    cursor.execute("SELECT COUNT(*) FROM vacancy")
    total_vacancies = cursor.fetchone()[0]

    conn.close()

    # Convertions
    for i, vacancy in enumerate(vacancies):
        dt_object = datetime.strptime(vacancy[7], "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = dt_object.strftime("%d.%m.%Y")
        vacancies[i] = vacancy[:4] + (json.loads(vacancy[4]),) + vacancy[5:7] + (
            formatted_date,) + (json.loads(vacancy[8]),) + vacancy[9:]

    return vacancies, total_vacancies


def get_vacancy_relation_status_list(selected_db):
    conn, cursor = db_connect(selected_db)

    query = """SELECT * FROM vacancy_relation_status"""
    cursor.execute(query)
    relation_status_list = cursor.fetchall()

    conn.close()

    return relation_status_list


def change_vacancy_relation_status(selected_db, vacancy_id, relation_status):
    conn, cursor = db_connect(selected_db)

    if relation_status == 'None':
        relation_status = None

    query = """INSERT OR IGNORE INTO vacancy_relation (vacancy_id, vacancy_relation_status_id) VALUES (?, ?)"""
    cursor.execute(query, (vacancy_id, relation_status))

    query = """UPDATE vacancy_relation SET vacancy_relation_status_id = ? WHERE vacancy_id = ?"""
    cursor.execute(query, (relation_status, vacancy_id))

    conn.commit()
    conn.close()


def get_vacancy_by_id(selected_db, vacancy_id):
    conn, cursor = db_connect(selected_db)
    query = """
        SELECT vacancy_id, vacancy.hh_id, vacancy.url, vacancy.alternate_url, vacancy.name, archived, published_at,
        vacancy_type.name, salary, experience.name, schedule.name, vacancy_description, vacancy_skills, professional_roles.name,
        employer.hh_id, employment.name, employer.name, employer.alternate_url, area.name, address, contacts
        FROM vacancy
        JOIN vacancy_type ON vacancy.type_id = vacancy_type.type_id
        JOIN experience ON vacancy.experience_id = experience.experience_id
        JOIN schedule ON vacancy.schedule_id = schedule.schedule_id
        JOIN professional_roles ON vacancy.professional_roles_id = professional_roles.professional_roles_id
        JOIN employer ON vacancy.employer_id = employer.employer_id
        JOIN employment ON vacancy.employment_id = employment.employment_id
        JOIN area ON vacancy.area_id = area.area_id
        WHERE vacancy.hh_id = ?
    """
    cursor.execute(query, (vacancy_id,))
    vacancy = cursor.fetchone()

    # Convertions
    dt_object = datetime.strptime(vacancy[6], "%Y-%m-%dT%H:%M:%S%z")
    formatted_date = dt_object.strftime("%d.%m.%Y")
    vacancy = vacancy[:6] + (formatted_date,) + (vacancy[7],) + (json.loads(vacancy[8]),) + vacancy[9:12] + (
        json.loads(vacancy[12]),) + vacancy[13:19] + (json.loads(vacancy[19]),) + (json.loads(vacancy[20]),)

    conn.close()

    return vacancy


def get_employer_by_id(selected_db, vacancy_id):
    conn, cursor = db_connect(selected_db)
    query = """
        SELECT employer.*, area.name, employer_type.name
        FROM employer
        JOIN area ON employer.area = area.area_id
        JOIN employer_type ON employer.type = employer_type.employer_type_id
        WHERE employer.hh_id = ?
    """
    cursor.execute(query, (vacancy_id,))
    employer = cursor.fetchone()

    # Convertions
    employer = employer[:11] + (json.loads(employer[11]),) + employer[12:]

    # Retrieve industries from database if they are exist
    if employer[11]:
        industries_list = []

        for industry in employer[11]:
            query = """
                SELECT industries.name
                FROM industries
                WHERE industries_id = ?
            """
            cursor.execute(query, (industry,))
            industries_list.append(cursor.fetchone()[0])

        industries = '; '.join(industries_list)
    else:
        industries = None

    conn.close()

    return employer, industries