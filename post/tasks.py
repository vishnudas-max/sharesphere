from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from notification.signals import user_commented,post_liked
from userside.models import CustomUser,Posts

@shared_task(bind=True)
def send_comment_notification(self, userID, postID):
    try:
        commented_user = CustomUser.objects.get(id=userID)
        post = Posts.objects.get(id=postID)
    except ObjectDoesNotExist as e:
        return str(e)
    user_commented.send(sender=self.__class__, commented_user=commented_user, owner_of_post=post.userID,post=post)
    return "COMMENT notification sent"


@shared_task(bind=True)
def send_like_notification(self, user_id, post_id):
    try:
        liked_user = CustomUser.objects.get(id=user_id)
        post = Posts.objects.get(id=post_id)
    except ObjectDoesNotExist as e:
        return str(e)

    post_liked.send(sender=self.__class__, liked_user=liked_user, owner_of_post=post.userID,post=post)
    return "notification sent"