from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        from . import signals,handlers
        signals.user_followed.connect(handlers.send_follow_notification)
        signals.user_commented.connect(handlers.send_comment_notification)
        signals.post_liked.connect(handlers.send_post_like_notification)
        signals.verification_request.connect(handlers.send_verification_request_notification)
        signals.verification_response.connect(handlers.send_verification_request_response_notification)
        signals.verificaton_success.connect(handlers.send_account_verified_notification)
        signals.verfication_expired.connect(handlers.send_verification_plan_expired_notification)
