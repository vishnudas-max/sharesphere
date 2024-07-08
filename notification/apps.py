from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        from . import signals,handlers
        signals.user_followed.connect(handlers.send_follow_notification)
        signals.user_commented.connect(handlers.send_comment_notification)
        signals.post_liked.connect(handlers.send_post_like_notification)
