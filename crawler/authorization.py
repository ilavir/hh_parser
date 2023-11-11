import requests
import json

def get_tokens():

    # Replace with your HeadHunter API credentials
    client_id = 'VM85UJBT6TL3S8ESS9QDIRG2CHPNSTV9OCNQF6CBBS2T4RH0B5IVKV2UGV0I1CIK'
    client_secret = 'M8NOENCSJOCEV3DVCKMS6V0VR8B25GB9SDN4UDLH4I3PQMAQ7F273349HI59VIV3'
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

    tokens = {'access_token': access_token, 'refresh_token': refresh_token}
    with open(filename, 'w') as file:
        json.dump(tokens, file)
    print(f'Tokens saved to {filename}')

access_token, refresh_token = get_tokens()

if access_token and refresh_token:
    save_tokens_to_file(access_token, refresh_token)
else:
    print("Tokens not available. Check for errors.")