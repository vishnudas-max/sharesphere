from celery import shared_task
from django.core.mail import send_mail
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from notification.signals import user_followed,verification_request,verificaton_success,verfication_expired
from .models import CustomUser,Posts


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
    



@shared_task(bind=True)
def send_follow_notification(self, follower_id, followed_id):
    try:
        follower = CustomUser.objects.get(id=follower_id)
        followed = CustomUser.objects.get(id=followed_id)
    except ObjectDoesNotExist as e:
        return str(e)
    user_followed.send(sender=self.__class__, follower=follower, followed=followed)
    return "FOLLOW notification sent"

@shared_task(bind=True)
def send_request_verification_notification(self,userID):
    try:
        user = CustomUser.objects.get(id=userID)
    except ObjectDoesNotExist as e:
        return str(e)
    verification_request.send(sender=self.__class__, user=user)
    return "verification  notification sent"

# task for sending sigal after verification succcsss-
@shared_task(bind=True)
def send_verification_success_notification(self,userID):
    try:
        user = CustomUser.objects.get(id=userID)
    except ObjectDoesNotExist as e:
        return str(e)
    verificaton_success.send(sender=self.__class__, user=user)
    return "verification success  notification sent"

# task for sending signals after verification is expired--
@shared_task(bind=True)
def send_verification_expired_notification(self,userID):
    try:
        user = CustomUser.objects.get(id=userID)
    except ObjectDoesNotExist as e:
        return str(e)
    verfication_expired.send(sender=self.__class__, user=user)
    return "verification expired  notification sent"

