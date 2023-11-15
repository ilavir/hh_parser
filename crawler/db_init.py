import requests
import sqlite3
import os

def initialize_database():

    # Database filename input without extension (.db)
    database_filename = input('Enter database filename (without extension .db): ')
    if len(database_filename) < 1:
        database_filename = 'db/test.db' # database filename by default
    else:
        database_filename = 'db/' + database_filename + '.db'

    # Check if database file exists
    if not os.path.exists(database_filename):
        print('Database does not exist.')
        create_file = input('Create database? (Y/n): ')
        if create_file == 'Y':
            # Connect to database and create/update dictionaries
            conn = sqlite3.connect(database_filename)
            cursor = conn.cursor()
            print('Creating database...')
            create_database(conn, cursor)
            update_dictionaries(conn, cursor)
            print('All dictionaries successfuly updated.')
            print('Database successfuly created.')
        else:
            print('Goodbye.')
            exit()
    elif os.path.exists(database_filename) and __name__ == '__main__':
        print('Database already exists.')
        update_file = input('Update database dictionaries? (Y/n): ')
        if update_file == 'Y':
            # Connect to database and create/update dictionaries
            conn = sqlite3.connect(database_filename)
            cursor = conn.cursor()
            create_database(conn, cursor)
            update_dictionaries(conn, cursor)
            print('All dictionaries successfuly updated.')
        else:
            print('Goodbye.')
            exit()
    else:
        # Connect to database
        conn = sqlite3.connect(database_filename)
        cursor = conn.cursor()
    
    return conn, cursor

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

def area_dict_update(conn, cursor, parent_id=16):

    api_url = 'https://api.hh.ru/areas/'
    data = requests.get(api_url + str(parent_id)).json()

    print('Dictionary "area" updating...')

    hh_id = data['id']
    parent_id = data['parent_id']
    name = data['name']

    # check if current area already exists in DB
    cursor.execute('SELECT * FROM area WHERE hh_id = ?', (hh_id,))
    if_exists = cursor.fetchone()

    if not if_exists:
        cursor.execute('INSERT INTO area (hh_id, parent_id, name) VALUES (?, ?, ?)', (hh_id, parent_id, name))

    if data['areas']:
        for item in data['areas']:
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

    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    print('Dictionary "vacancy_type" updating...')

    for item in data['vacancy_type']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM vacancy_type WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO vacancy_type (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def experience_dict_update(conn, cursor):

    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    print('Dictionary "experience" updating...')

    for item in data['experience']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM experience WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO experience (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def schedule_dict_update(conn, cursor):

    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    print('Dictionary "schedule" updating...')

    for item in data['schedule']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM schedule WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO schedule (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def employment_dict_update(conn, cursor):

    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    print('Dictionary "employment" updating...')

    for item in data['employment']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM employment WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO employment (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def professional_roles_dict_update(conn, cursor):

    api_url = 'https://api.hh.ru/professional_roles'
    data = requests.get(api_url).json()

    print('Dictionary "professional_roles" updating...')

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

    api_url = 'https://api.hh.ru/dictionaries'
    data = requests.get(api_url).json()

    print('Dictionary "employer_type" updating...')

    for item in data['employer_type']:
        hh_id = item['id']
        name = item['name']

        cursor.execute('SELECT * FROM employer_type WHERE hh_id = ?', (hh_id,))
        if_exists = cursor.fetchone()

        if not if_exists:
            cursor.execute('INSERT INTO employer_type (hh_id, name) VALUES (?, ?)', (hh_id, name))
            
    conn.commit()

def industries_dict_update(conn, cursor):

    api_url = 'https://api.hh.ru/industries'
    data = requests.get(api_url).json()

    print('Dictionary "industries" updating...')

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
    experience_table_create(conn, cursor)
    schedule_table_create(conn, cursor)
    employment_table_create(conn, cursor)
    professional_roles_table_create(conn, cursor)
    employer_type_table_create(conn, cursor)
    industries_table_create(conn, cursor)

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