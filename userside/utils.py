# utils/twofactor.py
import requests
from django.conf import settings


apikey = settings.TWO_FACTOR_API_KEY


def send_otp(phone_number,otp):
    url = f"https://2factor.in/API/V1/{apikey}/SMS/+91{phone_number}/{otp}/OTP1"
    payload={}
    headers = {}
    print(url)
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
