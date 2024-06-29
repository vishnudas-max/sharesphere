from celery import shared_task
from django.core.mail import send_mail
import requests
from django.conf import settings


apikey = settings.TWO_FACTOR_API_KEY

@shared_task(bind = True)
def send_mail_to(self, message, mail):
    try:
        send_mail(
                    "OTP VERIFICATION",
                    message,
                    "fluxbeatauth@gmail.com",
                    [mail],
                    fail_silently=False,
                )
        return "done"
    except:
        return "failed"
    
@shared_task(bind = True)
def send_sms_to(self,phone_number,otp):
    try:
        url = f"https://2factor.in/API/V1/{apikey}/SMS/+91{phone_number}/{otp}/OTP1"
        payload={}
        headers = {}
        print(url)
        response = requests.request("GET", url, headers=headers, data=payload)

        return "done"
    except:
        return "failed"