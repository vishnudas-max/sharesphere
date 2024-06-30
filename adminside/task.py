from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind = True)
def send_mail_to(self, message, mail):
    try:
        send_mail(
                    "Account Removal Notification",
                    message,
                    "fluxbeatauth@gmail.com",
                    [mail],
                    fail_silently=False,
                )
        return "done"
    except:
        return "failed"