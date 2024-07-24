from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from userside.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from notification.signals import verification_response


@shared_task(bind = True)
def send_mail_to(self, message, mail,title):
    try:
        send_mail(
                    title,
                    message,
                    "fluxbeatauth@gmail.com",
                    [mail],
                    fail_silently=False,
                )
        return "done"
    except:
        return "failed"
    

@shared_task(bind=True)
def send_request_verification_response_notification(self,invokedUser,userID,adminresponse):
    try:
        invokedUser = CustomUser.objects.get(id=invokedUser)
        user = CustomUser.objects.get(id=userID)
    except ObjectDoesNotExist as e:
        return str(e)
    verification_response.send(sender=self.__class__,invokedUser=invokedUser ,user=user,adminresponse=adminresponse)
    return "verification response notification sent"
    
