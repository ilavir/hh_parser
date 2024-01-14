import requests
import sqlite3
import os

def initialize_database():
    database_directory = 'db'

    # Create a database directory if it does not exist
    if not os.path.exists(database_directory):
        os.makedirs(database_directory)

    # Database name input without extension (.db)
    database_name = input('Enter database name: ')

    # Check if database name is empty
    if len(database_name) < 1:
        database_name = 'test.db' # database filename by default
    else:
        if not database_name.endswith('.db'):
            database_name += '.db' # add .db extension if not present
    
    # Full database filename with directory
    database_filename = os.path.join(database_directory, database_name)

    # Check if database file exists
    if not os.path.exists(database_filename):
        print('Database does not exist.')
        create_file = input('Create database? (Y/n): ')

        if create_file.lower() == 'y':
            # Connect to database and create/update dictionaries
            conn = sqlite3.connect(database_filename)
            cursor = conn.cursor()
            print('Creating database...')
            create_database(conn, cursor)
            print('Database successfuly created.')
            print('Updating dictionaries...')
            update_dictionaries(conn, cursor)
            print('Dictionaries successfuly updated.')
        else:
            print('Goodbye.')
            exit()
            
    elif os.path.exists(database_filename):
        print('Database already exists.')
        update_file = input('Update database? (Y/n): ')
        # Connect to database
        conn = sqlite3.connect(database_filename)
        cursor = conn.cursor()

        if update_file.lower() == 'y':
            # Create/update dictionaries
            print('Creating database...')
            create_database(conn, cursor)
            print('Database successfuly created.')
            print('Updating dictionaries...')
            update_dictionaries(conn, cursor)
            print('Dictionaries successfuly updated.')
    
    return conn, cursor


def vacancies_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancy (
            vacancy_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id INTEGER UNIQUE,
            name TEXT,
            area_id TEXT,
            salary TEXT,
            type_id TEXT,
            address TEXT,
            contacts TEXT,
            professional_roles_id INTEGER,
            experience_id TEXT,
            schedule_id TEXT,
            employment_id TEXT,
            snippet TEXT,
            vacancy_description TEXT,
            vacancy_skills TEXT,
            url TEXT,
            alternate_url TEXT,
            archived BOOLEAN,
            published_at DATETIME,
            employer_id INTEGER
        )
    ''')
    conn.commit()

def employers_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employer (
            employer_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id INTEGER UNIQUE,
            name TEXT,
            description TEXT,
            site_url TEXT,
            url TEXT,
            alternate_url TEXT,
            vacancies_url TEXT,
            trusted BOOLEAN,
            area TEXT,
            type TEXT,
            industries TEXT
        )
    ''')
    conn.commit()


def vacancy_relation_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancy_relation (
            vacancy_relation_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            vacancy_id INTEGER NOT NULL UNIQUE,
            favorite BOOLEAN,
            vacancy_relation_status_id INTEGER,
            notes TEXT,
            cover_letter TEXT
        )
    ''')
    conn.commit()


def vacancy_relation_status_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancy_relation_status (
        vacancy_relation_status_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE
        )
    ''')

    relation_status_list = ['Откликнулся', 'Ответили', 'Тестовое задание', 'Собеседование', 'Отказ', 'Не подхожу', 'Не интересно']

    for status in relation_status_list:
        cursor.execute('INSERT OR IGNORE INTO vacancy_relation_status (name) VALUES (?)', (status,))

    conn.commit()


def area_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS area (
            area_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id INTEGER,
            parent_id INTEGER,
            name TEXT
        )
    ''')
    conn.commit()

def vacancy_type_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancy_type (
            type_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id TEXT,
            name TEXT
        )
    ''')
    conn.commit()

def experience_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experience (
            experience_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id TEXT,
            name TEXT
        )
    ''')
    conn.commit()

def schedule_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            schedule_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id TEXT,
            name TEXT
        )
    ''')
    conn.commit()

def employment_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employment (
            employment_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id TEXT,
            name TEXT
        )
    ''')
    conn.commit()

def professional_roles_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professional_roles (
            professional_roles_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id INTEGER,
            parent_id INTEGER,
            name TEXT
        )
    ''')
    conn.commit()

def employer_type_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employer_type (
            employer_type_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id INTEGER,
            name TEXT
        )
    ''')
    conn.commit()

def industries_table_create(conn, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS industries (
            industries_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            hh_id INTEGER,
            parent_id INTEGER,
            name TEXT
        )
    ''')
    conn.commit()

def area_dict_update(conn, cursor):
    print('Dictionary "area" updating...')
    api_url = 'https://api.hh.ru/areas/'
    data = requests.get(api_url).json()

    for item in data:
        hh_id = item['id']
        parent_id = item['parent_id']
        name = item['name']

        # check if current area already exists in DB
        cursor.execute('SELECT * FROM area WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO area (hh_id, parent_id, name) VALUES (?, ?, ?)', (hh_id, parent_id, name))

        if item['areas']:
            for item in item['areas']:
                hh_id = item['id']
                parent_id = item['parent_id']
                name = item['name']

                # check if current area already exists in DB
                cursor.execute('SELECT * FROM area WHERE hh_id = ?', (hh_id,))
                if_exists = cursor.fetchone()

                if not if_exists:
                    cursor.execute('INSERT INTO area (hh_id, parent_id, name) VALUES (?, ?, ?)', (hh_id, parent_id, name))

                if item['areas']:
                    for item in item['areas']:
                        hh_id = item['id']
                        parent_id = item['parent_id']
                        name = item['name']

                        # check if current area already exists in DB
                        cursor.execute('SELECT * FROM area WHERE hh_id = ?', (hh_id,))
                        if_exists = cursor.fetchone()

                        if not if_exists:
                            cursor.execute('INSERT INTO area (hh_id, parent_id, name) VALUES (?, ?, ?)', (hh_id, parent_id, name))

    conn.commit()

def vacancy_type_dict_update(conn, cursor):
    print('Dictionary "vacancy_type" updating...')
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['vacancy_type']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM vacancy_type WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO vacancy_type (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def experience_dict_update(conn, cursor):
    print('Dictionary "experience" updating...')
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['experience']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM experience WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO experience (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def schedule_dict_update(conn, cursor):
    print('Dictionary "schedule" updating...')
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['schedule']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM schedule WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO schedule (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def employment_dict_update(conn, cursor):
    print('Dictionary "employment" updating...')
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['employment']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM employment WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO employment (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def professional_roles_dict_update(conn, cursor):
    print('Dictionary "professional_roles" updating...')
    api_url = 'https://api.hh.ru/professional_roles'
    data = requests.get(api_url).json()

    for item in data['categories']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM professional_roles WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO professional_roles (hh_id, name) VALUES (?, ?)', (hh_id, name))

        if item['roles']:
            parent_id = hh_id

            for item in item['roles']:
                hh_id = item['id']
                name = item['name']

                cursor.execute('SELECT * FROM professional_roles WHERE hh_id = ?', (hh_id,))
                if_exists = cursor.fetchone()

                if not if_exists:
                    cursor.execute('INSERT INTO professional_roles (hh_id, name, parent_id) VALUES (?, ?, ?)', (hh_id, name, parent_id))
            
    conn.commit()

def employer_type_dict_update(conn, cursor):
    print('Dictionary "employer_type" updating...')
    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    for item in data['employer_type']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM employer_type WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO employer_type (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def industries_dict_update(conn, cursor):
    print('Dictionary "industries" updating...')
    api_url = 'https://api.hh.ru/industries'
    data = requests.get(api_url).json()

    for item in data:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM industries WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO industries (hh_id, name) VALUES (?, ?)', (hh_id, name))

        if item['industries']:
            parent_id = hh_id
            
            for item in item['industries']:
                hh_id = item['id']
                name = item['name']

                cursor.execute('SELECT * FROM industries WHERE hh_id = ?', (hh_id,))
                if_exists = cursor.fetchone()

                if not if_exists:
                    cursor.execute('INSERT INTO industries (hh_id, name, parent_id) VALUES (?, ?, ?)', (hh_id, name, parent_id))
            
    conn.commit()

def create_database(conn, cursor):
    area_table_create(conn, cursor)
    vacancy_type_table_create(conn, cursor)
    vacancy_relation_table_create(conn, cursor)
    vacancy_relation_status_table_create(conn, cursor)
    experience_table_create(conn, cursor)
    schedule_table_create(conn, cursor)
    employment_table_create(conn, cursor)
    professional_roles_table_create(conn, cursor)
    employer_type_table_create(conn, cursor)
    industries_table_create(conn, cursor)
    vacancies_table_create(conn, cursor)
    employers_table_create(conn, cursor)

def update_dictionaries(conn, cursor):
    area_dict_update(conn, cursor)
    vacancy_type_dict_update(conn, cursor)
    experience_dict_update(conn, cursor)
    schedule_dict_update(conn, cursor)
    employment_dict_update(conn, cursor)
    professional_roles_dict_update(conn, cursor)
    employer_type_dict_update(conn, cursor)
    industries_dict_update(conn, cursor)

if __name__ == '__main__':
    conn, cursor = initialize_database()
    cursor.close()
    conn.close()