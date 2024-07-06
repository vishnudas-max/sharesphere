from django.apps import AppConfig

class UsersideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userside'

    def ready(self):
        from . import signals,handler
        signals.user_followed.connect(handler.send_follow_notification)
        signals.user_unfollowed.connect(handler.send_unfollow_notification)
       