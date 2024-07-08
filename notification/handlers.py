from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .signals import user_followed,user_commented,post_liked
from .models import Notification

def send_follow_notification(sender,follower,followed, **kwargs):
    channel_layer = get_channel_layer()
    message = f"{follower.username} started following you."
    print(message)
    async_to_sync(channel_layer.group_send)(
        f"notification_{followed.id}",
        {
            'type' : 'notification',
            'message' : message
        }

    )
    Notification.objects.create(invoked_user=follower,
                                target_user=followed,
                                notification_type='follow',
                                message = message)

def send_comment_notification(sender, commented_user, owner_of_post,post ,**kwargs):
    channel_layer = get_channel_layer()
    message = f"{commented_user.username} commented on your post."
    async_to_sync(channel_layer.group_send)(
        f"notification_{owner_of_post.id}",
        {
            'type': 'notification',
            'message': message
        }
    )
    obj=Notification.objects.create(invoked_user=commented_user,
                                target_user=owner_of_post,
                                postID = post,
                                notification_type='comment',
                                message = message)
    print(obj)

def send_post_like_notification(sender, liked_user, owner_of_post,post, **kwargs):
    channel_layer = get_channel_layer()
    message = f"{liked_user.username} liked your post."
    async_to_sync(channel_layer.group_send)(
        f"notification_{owner_of_post.id}",
        {
            'type': 'notification',
            'message': message
        }
    )
    Notification.objects.create(invoked_user=liked_user,
                                target_user=owner_of_post,
                                postID = post,
                                notification_type='like',
                                message = message)