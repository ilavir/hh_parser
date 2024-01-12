#!/usr/bin/env python

import requests
import json
import argparse
import os
from dotenv import load_dotenv
from db_init import initialize_database

#from authorization import get_token

def authorization():
    
    load_dotenv()

    access_token = os.getenv('ACCESS_TOKEN')
    refresh_token = os.getenv('REFRESH_TOKEN')

    headers = {
        'user-agent': 'api-test',
        'authorization': 'Bearer ' + access_token,
    }

    auth = requests.get('https://api.hh.ru/me', headers=headers)
    
    if auth.status_code == 200:
        print(f"--- Status: {auth.status_code} OK ---")
    else:
        print(f"--- ERROR {auth.status_code} ---")
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        proceed = input('Do you want to proceed without authorization? (Y/n): ')

        if proceed.lower() == 'y':
            headers = {}
        else:
            print('Goodbye.')
            exit()
            
    return headers

# return parameters for API function call
def get_parameters(args_description, args_employer):
    api_url = 'https://api.hh.ru/vacancies'

    params = {
        'order_by': 'publication_time',
        'area': 1002,
        'per_page': 100
    }

    params['text'] = input('Enter search query: ')

    while True:
        param_type = input('Enter parameter type ("text" for search query; press "Enter" to skip): ')
        if len(param_type) < 1:
            break
        param_value = input('Enter parameter value: ')
        params[param_type] = param_value
    
    #if args_description == True or args_employer == True:
    #    params['per_page'] = 10

    return params, api_url

# Get argument -d (--description) from script start
def args_desc_func(args_description, vacancy_hh_id):

    if args_description == True:
        vacancy_api_url = 'https://api.hh.ru/vacancies/' + vacancy_hh_id
        vacancy = requests.get(vacancy_api_url).json()
        vacancy_description = vacancy['description']
        vacancy_skills = vacancy['key_skills']
    else:
        vacancy_description = None
        vacancy_skills = None

    return vacancy_description, vacancy_skills

# Get argument -e (--employer) from script start
def args_employer_func(cursor, args_employer, employer_hh_id):

    if args_employer == True:
        employer_api_url = 'https://api.hh.ru/employers/' + employer_hh_id
        employer = requests.get(employer_api_url).json()
        employer_description = employer['description']
        employer_site_url = employer['site_url']
        cursor.execute('SELECT area_id FROM area WHERE hh_id = ?', (employer['area']['id'],))
        cursor_current = cursor.fetchone()

        if cursor_current:
            employer_area = cursor_current[0]
        else:
            employer_area = 'Other'

        cursor.execute('SELECT employer_type_id FROM employer_type WHERE hh_id = ?', (employer['type'],))
        employer_type = cursor.fetchone()[0]

        if employer['industries']:
            employer_industries = []
            for industry in employer['industries']:
                cursor.execute('SELECT industries_id FROM industries WHERE hh_id = ?', (industry['id'],))
                employer_industry = cursor.fetchone()[0]
                employer_industries.append(employer_industry)
        else:
            employer_industries = None

    else:
        employer_description = None
        employer_site_url = None
        employer_area = None
        employer_type = None
        employer_industries = None

    return employer_description, employer_site_url, employer_area, employer_type, employer_industries

# call API and save every vacancy and assotiated employer to database
def extract_vacancies_and_save(params, api_url, headers, args_description, args_update, args_employer, page=0, new_vacancy=0, updated_vacancy=0):

    params['page'] = page
    
    # manage KeyboardInterrupt exception
    try:
        data = requests.get(api_url, params, headers=headers)
        vacancies = data.json()
    except KeyboardInterrupt:
        print('\n\n--- Aborted by user ---')
        print(f"\n--- {new_vacancy} added, {updated_vacancy} updated ---")
        exit()

    # print total vacancies and pages on the first iteration
    if page == 0:
        print(f"\nVacancies found: {vacancies['found']}")
        print(f"Pages: {vacancies['pages']}, {vacancies['per_page']} per page")
        print(f"Parameters: {params}")

    print(f"\nPage {vacancies['page'] + 1} from {vacancies['pages']} total\n")

    for item in vacancies['items']:
        vacancy_contacts = item['contacts'] # json
        vacancy_professional_roles = item['professional_roles'] # json
        vacancy_hh_id = item['id']
        vacancy_archived = item['archived']
        vacancy_employment = item['employment']
        vacancy_name = item['name']
        vacancy_url = item['url']
        vacancy_alternate_url = item['alternate_url']
        vacancy_area = item['area'] # json
        vacancy_experience = item['experience'] # json
        vacancy_salary = item['salary'] # json
        vacancy_schedule = item['schedule'] # json
        vacancy_address = item['address'] # json
        vacancy_type = item['type'] # json
        vacancy_snippet = item['snippet'] # json
        vacancy_published_at = item['published_at']

        if vacancy_type['id'] != 'anonymous':
            employer_hh_id = item['employer']['id']
            employer_name = item['employer']['name']
            employer_trusted = item['employer']['trusted']
            employer_url = item['employer']['url']
            employer_alternate_url = item['employer']['alternate_url']
            employer_vacancies_url = item['employer']['vacancies_url']
        else:
            employer_hh_id = None
            employer_name = None

        print(f"{vacancy_hh_id} | {vacancy_name} | {employer_name}")

        # check if current vacancy already exists in DB
        cursor.execute('SELECT * FROM vacancy WHERE hh_id = ?', (vacancy_hh_id,))
        existing_vacancy = cursor.fetchone()

        # add vacancy to DB if not already exists
        if not existing_vacancy:
            # check if current employer already exists in DB
            cursor.execute(
                'SELECT employer_id FROM employer WHERE hh_id = ?', (employer_hh_id,))
            existing_employer_id = cursor.fetchone()

            if existing_employer_id:
                existing_employer_id = existing_employer_id[0]
            else:
                if vacancy_type['id'] != 'anonymous':
                    employer_description, employer_site_url, employer_area, employer_type, employer_industries = args_employer_func(cursor, args_employer, employer_hh_id)

                    cursor.execute('''
                        INSERT INTO employer (hh_id, name, trusted, url, alternate_url, vacancies_url,
                                    description, site_url, area, type, industries)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (employer_hh_id, employer_name, employer_trusted, employer_url, employer_alternate_url, employer_vacancies_url,
                          employer_description, employer_site_url, employer_area, employer_type, json.dumps(employer_industries, ensure_ascii=False)))
                    cursor.execute(
                        'SELECT employer_id FROM employer WHERE hh_id = ?', (employer_hh_id,))
                    existing_employer_id = cursor.fetchone()[0]
                else:
                    existing_employer_id = None

            cursor.execute('SELECT schedule_id FROM schedule WHERE hh_id = ?', (vacancy_schedule['id'],))
            vacancy_schedule = cursor.fetchone()[0]
            cursor.execute('SELECT employment_id FROM employment WHERE hh_id = ?', (vacancy_employment['id'],))
            vacancy_employment = cursor.fetchone()[0]
            cursor.execute('SELECT experience_id FROM experience WHERE hh_id = ?', (vacancy_experience['id'],))
            vacancy_experience = cursor.fetchone()[0]
            cursor.execute('SELECT area_id FROM area WHERE hh_id = ?', (vacancy_area['id'],))
            vacancy_area = cursor.fetchone()[0]
            cursor.execute('SELECT type_id FROM vacancy_type WHERE hh_id = ?', (vacancy_type['id'],))
            vacancy_type = cursor.fetchone()[0]
            cursor.execute('SELECT professional_roles_id FROM professional_roles WHERE hh_id = ?', (vacancy_professional_roles[0]['id'],))
            vacancy_professional_roles = cursor.fetchone()[0]
            
            vacancy_description, vacancy_skills = args_desc_func(args_description, vacancy_hh_id)

            cursor.execute('''
                INSERT INTO vacancy (hh_id, archived, employment_id, name, area_id, experience_id, url, alternate_url, salary, schedule_id,
                            address, type_id, snippet, published_at, employer_id, contacts, professional_roles_id, vacancy_description, vacancy_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (vacancy_hh_id, vacancy_archived, vacancy_employment, vacancy_name, vacancy_area, vacancy_experience, vacancy_url, vacancy_alternate_url,
                json.dumps(vacancy_salary, ensure_ascii=False), vacancy_schedule, json.dumps(vacancy_address, ensure_ascii=False),
                vacancy_type, json.dumps(vacancy_snippet, ensure_ascii=False), vacancy_published_at, existing_employer_id,
                json.dumps(vacancy_contacts, ensure_ascii=False), vacancy_professional_roles, json.dumps(vacancy_description, ensure_ascii=False),
                json.dumps(vacancy_skills, ensure_ascii=False)))


            new_vacancy += 1
        else:
            cursor.execute('''SELECT published_at FROM vacancy WHERE hh_id = ?''', (vacancy_hh_id,))
            existing_published_at = cursor.fetchone()

            if args_update == True:
                vacancy_description, vacancy_skills = args_desc_func(args_description, vacancy_hh_id)

                cursor.execute('''UPDATE vacancy SET archived = ?, name = ?, salary = ?, address = ?, snippet = ?,
                                         published_at = ?, contacts = ?, vacancy_description = ?, vacancy_skills = ? WHERE hh_id = ?
                ''', (vacancy_archived, vacancy_name, json.dumps(vacancy_salary, ensure_ascii=False), json.dumps(vacancy_address, ensure_ascii=False),
                      json.dumps(vacancy_snippet, ensure_ascii=False), vacancy_published_at, json.dumps(vacancy_contacts, ensure_ascii=False),
                      json.dumps(vacancy_description, ensure_ascii=False), json.dumps(vacancy_skills, ensure_ascii=False), vacancy_hh_id,))

                updated_vacancy += 1
            else:
                if existing_published_at[0] != vacancy_published_at:
                    cursor.execute('''UPDATE vacancy SET published_at = ?, archived = ? WHERE hh_id = ?''', (vacancy_published_at, vacancy_archived, vacancy_hh_id))
                    print(existing_published_at, vacancy_published_at)
                    updated_vacancy += 1

        conn.commit()

    # check current page. if 'page' < than total pages, start function again
    if page < vacancies['pages'] - 1:
        page += 1
        extract_vacancies_and_save(params, api_url, headers, args_description, args_update, args_employer, page, new_vacancy, updated_vacancy)
    else:
        print(f"\n--- Done --- {vacancies['found']} found, {new_vacancy} added, {updated_vacancy} updated ---")

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--description', action='store_true', help='parse including vacancy description and key skills')
    parser.add_argument('-e', '--employer', action='store_true', help='parse including employer description, industry and site_url')
    parser.add_argument('-u', '--update', action='store_true', help='update existing vacancies')
    args = parser.parse_args()

    headers = authorization()
    conn, cursor = initialize_database()
    params, api_url = get_parameters(args.description, args.employer)
    
    extract_vacancies_and_save(params, api_url, headers, args.description, args.update, args.employer)
    cursor.close()
    conn.close()