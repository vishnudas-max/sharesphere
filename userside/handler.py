from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .signals import user_followed,user_unfollowed

def send_follow_notification(sender,follower,followed, **kwargs):
    channel_layer = get_channel_layer()
    message = f"{follower.username} is following you"
    print(message)
    async_to_sync(channel_layer.group_send)(
        f"follow_{followed.id}",
        {
            'type' : 'follow_message',
            'message' : 1
        }

    )

def send_unfollow_notification(sender, follower, followed, **kwargs):
    channel_layer = get_channel_layer()
    message = f"{follower.username} has unfollowed you."
    async_to_sync(channel_layer.group_send)(
        f"follow_{followed.id}",
        {
            'type': 'follow_message',
            'message': -1
        }
    )