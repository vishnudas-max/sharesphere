from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind = True)
def send_mail_to(self, message, mail):
    send_mail(
                    "OTP VERIFICATION",
                    message,
                    "fluxbeatauth@gmail.com",
                    [mail],
                    fail_silently=False,
                )
    return "done"