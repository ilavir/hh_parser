import sqlite3
import csv
import json
import os
from datetime import datetime

today_date = datetime.now()

# Database filename input without extension (.db)
database_filename = input('Enter database filename (without extension .db): ')

# Specify the CSV file name
csv_file = 'export/' + database_filename + '_' + today_date.strftime('%d%m%Y') + '.csv'

# Specify the database file name
database_filename = 'db/' + database_filename + '.db'

# Check if database file exists
if not os.path.exists(database_filename):
    print('Database does not exist.')
    exit()

# Function for choosing a header template (column names)
def output_header(template_number):
    match template_number:
        case '0':
            header = ['#', 'Дата', 'ID', 'Вакансия', 'Работодатель', 'Зарплата', 'График', 'Адрес', 'Контактное лицо', 'E-mail', 'Телефоны']
        case _:
            print('You have entered invalid template number.')
            exit()
    return header

# Function for choosing row template
def output_template(template_number):
    match template_number:
        case '0':
            template = [
                row[0],
                date_formatted,
                row[2],
                row[3],
                row[4],
                salary_formatted,
                row[6],
                address_formatted,
                contacts_formatted_name,
                contacts_formatted_email,
                contacts_formatted_phones
            ]
        case _:
            print('You have entered invalid template number')
            exit()
    return template
    
# Template number input for headers and row columns for export
template_number = input('Enter template number for .csv export ("0" by default): ')
if len(template_number) < 1:
    template_number = '0'

# Connect to the SQLite database
conn = sqlite3.connect(database_filename)
cursor = conn.cursor()

# Full query to database for returning all possible data
cursor.execute('''SELECT vacancy.vacancy_id,
                         vacancy.published_at,
                         vacancy.hh_id,
                         vacancy.name,
                         employer.name,
                         vacancy.salary,
                         schedule.name,
                         vacancy.address,
                         vacancy.contacts
               FROM vacancy JOIN employer ON vacancy.employer_id = employer.employer_id JOIN schedule ON vacancy.schedule_id = schedule.schedule_id
               ''')
rows = cursor.fetchall()

# Write the data to a CSV file
with open(csv_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Select a header (column names) template
    header = output_header(template_number)
    # Write the header (column names)
    csv_writer.writerow(header)
    #print([description[0] for description in cursor.description])
    #csv_writer.writerow([description[0] for description in cursor.description])
    
    # Write the rows
    #csv_writer.writerows(rows)

    for row in rows:
        # Convert UNIX timestamp from DB to DD/MM/YYYY format for Date column
        dt_object = datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S%z')
        date_formatted = dt_object.strftime('%d/%m/%Y')

        # If there are salary in JSON file, make a column Salary from it
        json_salary = json.loads(row[5])
        if json_salary:
            salary_formatted = (("от " + str(json_salary['from']) if json_salary['from'] else "") + (" до " + str(json_salary['to']) if json_salary['to'] else "") + (" гросс" if json_salary['gross'] else "")).strip()
        else:
            salary_formatted = None

        json_address = json.loads(row[7])
        if json_address:
            address_formatted = json_address['raw']
            if json_address['metro']:
                address_formatted += ", метро: " + json_address['metro']['station_name']
        else:
            address_formatted = None

        # If there are contacts in JSON, split it to Name, Email and Phones columns
        json_contacts = json.loads(row[8])
        if json_contacts:
            if json_contacts['name']:
                contacts_formatted_name = json_contacts['name']
            else:
                contacts_formatted_name = None
            if json_contacts['email']:
                contacts_formatted_email = json_contacts['email']
            else:
                contacts_formatted_email = None
            if json_contacts['phones']:
                contacts_phones = []
                for phone in json_contacts['phones']:
                    contacts_phones.append(f"+{phone['country']}({phone['city']}){phone['number']}")
                contacts_formatted_phones = ", ".join(contacts_phones)
            else:
                contacts_formatted_phones = None
        else:
            continue
            contacts_formatted_name = None
            contacts_formatted_email = None
            contacts_formatted_phones = None

        # Select a columns template
        formatted_row = output_template(template_number)

        # Insert formatted row into .csv file
        csv_writer.writerow(formatted_row)

# Close the database connection
cursor.close()
conn.close()

print(f'Data has been exported to {csv_file}')