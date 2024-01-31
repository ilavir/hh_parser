#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv, find_dotenv, set_key

load_dotenv()

def get_tokens():

    # Replace with your HeadHunter API credentials
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redirect_uri = 'http://localhost/auth'  # If you've specified it during app registration
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

def save_tokens_to_file(access_token, refresh_token, filename='tokens.json'):

    '''tokens = {'access_token': access_token, 'refresh_token': refresh_token}
    with open(filename, 'w') as file:
        json.dump(tokens, file)'''
    # Find the .env file in the current directory
    dotenv_path = find_dotenv()

    # Set or update a key-value pair in the .env file
    set_key(dotenv_path, "ACCESS_TOKEN", access_token)
    set_key(dotenv_path, "REFRESH_TOKEN", refresh_token)
    print(f'Tokens saved to .env')

access_token, refresh_token = get_tokens()

if access_token and refresh_token:
    save_tokens_to_file(access_token, refresh_token)
else:
    print("Tokens not available. Check for errors.")