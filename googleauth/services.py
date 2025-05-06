from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
from typing import Dict, Any
import requests
import jwt
import logging
from django.contrib.auth import get_user_model
User = get_user_model()

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
LOGIN_URL = f'{settings.BASE_APP_URL}/api/login/'

def google_get_access_token(code: str, redirect_uri: str) -> str:

    print(f'redirect-url-----{redirect_uri}')
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data,headers=headers)

    try:
        data = response.json()
    except ValueError():
        logging.error("Token endpoint did not return json",response.text)
        return None

    if not response.ok:
        logging.error("Failed to fetch access token",data)
        return None

    access_token = data.get('access_token')

    if not access_token:
        logging.error('NO access token in response',data)
        return None
    return access_token

def google_get_user_info(access_token: str) -> Dict[str, Any]:
    print(f"access token---{access_token}")
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
         return {'status':False}


    return response.json()



def get_user_data(validated_data):
    domain = settings.BASE_API_URL
    redirect_uri = f'{domain}/api/auth/login/google/'
    print(redirect_uri)
    code = validated_data.get('code')
    error = validated_data.get('error')

    if error or not code:
        return {'status':False,'error':'missing code'}


    access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)

    if not access_token:
        return {'status':False,'error':'Count not fetch access token'}

    user_data = google_get_user_info(access_token=access_token)

    if not user_data.get('email'):
        return {'status':False,'error':'Could not fetch user info'}

    profile_data = {
        'status':True,
        'email': user_data['email'],
        'first_name': user_data.get('given_name'),
        'last_name': user_data.get('family_name'),
    }

    return profile_data