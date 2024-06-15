#!/usr/bin/env python3

import requests
import json
import os
import sqlite3
from dotenv import load_dotenv, find_dotenv, set_key

load_dotenv()

def db_connect(selected_db):
    conn = sqlite3.connect(f'db/{selected_db}')
    cursor = conn.cursor()

    return conn, cursor


def get_tokens_from_db(user_id):
    conn, cursor = db_connect('test.db')
    query = 'SELECT access_token, refresh_token FROM user WHERE user_id = ?'
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    access_token = result[0]
    refresh_token = result[1]

    conn.close()

    return access_token, refresh_token


def check_hh_auth(user_id):
    auth_status = False
    access_token, refresh_token = get_tokens_from_db(user_id)

    if access_token and refresh_token:
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")

        headers = {
            'user-agent': 'api-test',
            'authorization': 'Bearer ' + access_token,
        }

        auth = requests.get('https://api.hh.ru/me', headers=headers)

        if auth.status_code == 200:
            print(f"--- HH.ru API OAuth Status: {auth.status_code} OK ---")
            auth_status = True
        else:
            print(f"--- HH.ru API OAuth Status: {auth.status_code} ERROR ---")

    else:
        print('ERROR: No Access and Refresh Tokens found.')

    return auth_status, access_token, refresh_token

def get_tokens():

    # Replace with your HeadHunter API credentials
    client_id = os.getenv('HH_CLIENT_ID')
    client_secret = os.getenv('HH_CLIENT_SECRET')
    print(client_id, client_secret)
    redirect_uri = 'http://localhost:5000/auth'  # If you've specified it during app registration
    state = 'your_state'  # Optional, used to prevent CSRF attacks

    # Step 1: Obtain authorization code
    authorization_url = 'https://hh.ru/oauth/authorize'
    authorization_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state  # Optional
    }

    #authorization_response = requests.get(authorization_url, params=authorization_params)
    print('Open next URL in browser and input Authorization Code below:')
    print(authorization_url + "?response_type=" + authorization_params['response_type'] + "&client_id=" + authorization_params['client_id'])

    # Open next link in web-browser to get Access Token and Refresh Token:
    '''
      https://hh.ru/oauth/authorize?
      response_type=code&
      client_id={client_id}&
      state={state}&
      redirect_uri={redirect_uri}
    '''

    # After opening this URL in a web browser, the user will be redirected to your redirect_uri with the code as a query parameter.
    # Extract the code from the redirected URL, e.g., 'http://your_redirect_uri?code=authorization_code'
    authorization_code = input("Enter the authorization code from the redirected URL: ")

    # Step 2: Exchange authorization code for access token
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': authorization_code
    }

    token_response = requests.post(token_url, data=token_data)

    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')
        refresh_token = token_response.json().get('refresh_token')
        print(f'Access Token: {access_token}')
        print(f'Refresh Token: {refresh_token}')
    else:
        print(f'Failed to obtain access token. Status code: {token_response.status_code}')
        print(token_response.text)
        exit()

    return access_token, refresh_token


def save_token_to_db(user_id, access_token, refresh_token):

    return

def save_tokens_to_file(access_token, refresh_token, filename='tokens.json'):

    '''tokens = {'access_token': access_token, 'refresh_token': refresh_token}
    with open(filename, 'w') as file:
        json.dump(tokens, file)'''
    # Find the .env file in the current directory
    dotenv_path = find_dotenv()

    # Set or update a key-value pair in the .env file
    set_key(dotenv_path, "ACCESS_TOKEN", access_token)
    set_key(dotenv_path, "REFRESH_TOKEN", refresh_token)

    return f'Tokens saved to .env'


if __name__ == '__main__':
    access_token, refresh_token = get_tokens()

    if access_token and refresh_token:
        save_tokens_to_file(access_token, refresh_token)
    else:
        print("Tokens not available. Check for errors.")

    #print(check_hh_auth(1))