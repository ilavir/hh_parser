import requests
from flask import flash
from urllib.parse import urlencode, urljoin
from app import app


def check_hh_authorization(access_token):
    app.logger.info('Checking HH.ru OAuth Status...')

    if access_token:
        headers = {
            'user-agent': 'api-test',
            'authorization': 'Bearer ' + access_token,
        }

        response = requests.get('https://api.hh.ru/me', headers=headers)

        if response.status_code == 200:
            app.logger.info(f"--- HH.ru API OAuth Status: {response.status_code} OK ---")
            return True
        else:
            app.logger.warning(f"--- HH.ru API OAuth Status: {response.status_code} ERROR ---")
            app.logger.warning(response.text)
            flash('You are not authorized in HH.ru API. Please, try to refresh or update tokens from your profile.')
    else:
        app.logger.warning('No ACCESS_TOKEN found.')
        flash('No Access Token found. Please, get new tokens from your profile.')

    return False


def refresh_hh_tokens(current_refresh_token):
    app.logger.info('Making a refresh tokens request to HH.ru API...')

    # Step 2: Exchange authorization code for access token
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'refresh_token',
        'refresh_token': current_refresh_token
    }
    token_response = requests.post(token_url, data=token_data)

    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')
        refresh_token = token_response.json().get('refresh_token')
        app.logger.info(f'Access Token: {access_token}')
        app.logger.info(f'Refresh Token: {refresh_token}')
    else:
        app.logger.warning(f'Failed to obtain tokens. Status code: {token_response.status_code}')
        app.logger.warning(token_response.text)
        access_token = None
        refresh_token = None

    return access_token, refresh_token

def get_hh_authorization_code():
    app.logger.info('Making a request to HH.ru API for authorization code...')

    # Replace with your HeadHunter API credentials
    client_id = app.config['HH_CLIENT_ID']
    self_uri = app.config['SELF_URL']
    hh_redirect_uri = urljoin(self_uri, 'hh_auth')  # If you've specified it during app registration
    state = 'your_state'  # Optional, used to prevent CSRF attacks

    # Step 1: Obtain authorization code
    authorization_url = 'https://hh.ru/oauth/authorize'
    authorization_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': hh_redirect_uri,
        'state': state  # Optional
    }

    endpoint_url = urljoin(authorization_url, '?' + urlencode(authorization_params))

    return endpoint_url


def get_hh_tokens(authorization_code):
    app.logger.info('Getting tokens from HH.ru API...')

    # Replace with your HeadHunter API credentials
    client_id = app.config['HH_CLIENT_ID']
    client_secret = app.config['HH_CLIENT_SECRET']
    self_uri = app.config['SELF_URL']
    hh_redirect_uri = urljoin(self_uri, 'hh_auth')  # If you've specified it during app registration

    # Step 2: Exchange authorization code for access token
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': hh_redirect_uri,
        'code': authorization_code
    }

    token_response = requests.post(token_url, data=token_data)

    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')
        refresh_token = token_response.json().get('refresh_token')
        app.logger.info(f'Access Token: {access_token}')
        app.logger.info(f'Refresh Token: {refresh_token}')
    else:
        app.logger.warning(f'Failed to obtain tokens. Status code: {token_response.status_code}')
        app.logger.warning(token_response.text)
        access_token = None
        refresh_token = None

    return access_token, refresh_token


def hh_search_vacancies(params, user):
    api_url = 'https://api.hh.ru/vacancies'
    headers = {'user-agent': 'test-api'}
    app.logger.info(f'Starting vacancies search (headers = {headers}, params = {params})...')

    if user.is_authenticated:
        access_token = user.access_token
        headers['authorization'] = 'Bearer ' + access_token
        response = requests.get(api_url, params=params, headers=headers)
        app.logger.info(f'Response Status Code: {response.status_code}')

        if response.status_code == 200:
            return response
        if response.status_code == 403:
            flash(f'ERROR! Bad request. Please, recheck HH Oauth Status in your profile.')
            app.logger.warning(f'Bad request. Error message: {response.json()}')
            del headers['authorization']

    response = requests.get(api_url, params=params, headers=headers)
    app.logger.info(f'Response Status Code: {response.status_code}')

    return response


def hh_vacancy_get(hh_id, user):
    api_url = 'https://api.hh.ru/vacancies/' + str(hh_id)
    headers = {'user-agent': 'test-api'}
    app.logger.info(f'Retrieving vacancy details...')

    if user.is_authenticated:
        access_token = user.access_token
        headers['authorization'] = 'Bearer ' + access_token
        response = requests.get(api_url, headers=headers)
        app.logger.info(f'Response Status Code: {response.status_code}')

        if response.status_code == 200:
            return response
        if response.status_code == 403:
            flash(f'ERROR! Bad request. Please, recheck HH Oauth Status in your profile.')
            app.logger.warning(f'Bad request. Error message: {response.json()}')
            del headers['authorization']

    response = requests.get(api_url, headers=headers)
    app.logger.info(f'Response Status Code: {response.status_code}')

    return response


def hh_employer_get(hh_id, user):
    api_url = 'https://api.hh.ru/employers/' + str(hh_id)
    headers = {'user-agent': 'test-api'}
    app.logger.info(f'Retrieving employer details...')

    if user.is_authenticated:
        access_token = user.access_token
        headers['authorization'] = 'Bearer ' + access_token
        response = requests.get(api_url, headers=headers)
        app.logger.info(f'Response Status Code: {response.status_code}')

        if response.status_code == 200:
            return response
        if response.status_code == 403:
            flash(f'ERROR! Bad request. Please, recheck HH Oauth Status in your profile.')
            app.logger.warning(f'Bad request. Error message: {response.json()}')
            del headers['authorization']

    response = requests.get(api_url, headers=headers)
    app.logger.info(f'Response Status Code: {response.status_code}')

    return response