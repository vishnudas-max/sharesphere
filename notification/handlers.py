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
    
def send_verification_request_notification(sender,user,**kwargs):
    channel_layer = get_channel_layer()
    message =f"Your request for verifcation was succesfull . You will get response within 24 hours."
    async_to_sync(channel_layer.group_send)(
        f"notification_{user.id}",{
            'type' : 'notification',
            'message':message
        }
    )
    print('verification_notification_send_--------------------------------------')
    Notification.objects.create(invoked_user=user,
                                target_user=user,
                                notification_type='verification',
                                message = message)
    
def send_verification_request_response_notification(sender,invokedUser,user,adminresponse,**kwargs):
    channel_layer = get_channel_layer()
    if adminresponse:
        message = "✅ Your request for verification has been approved. You can now choose and purchase a plan to get verified."
    else:
        message = "❌ Your request for verification has been rejected. You can apply again after one month."

    async_to_sync(channel_layer.group_send)(
        f"notification_{user.id}",{
            'type' : 'notification',
            'message':message
        }
    )
    print('verification_notification_send_--------------------------------------')
    Notification.objects.create(invoked_user=invokedUser,
                                target_user=user,
                                notification_type='verification',
                                message = message)

def send_account_verified_notification(sender,user,**kwargs):
    channel_layer = get_channel_layer()
    message = "✔️ Your account has now been verified. Enjoy the features!"
    async_to_sync(channel_layer.group_send)(
        f"notification_{user.id}",{
            'type' : 'notification',
            'message':message
        }
    )
    Notification.objects.create(invoked_user=user,
                                target_user=user,
                                notification_type='verification',
                                message = message)
    
def send_verification_plan_expired_notification(sender,user,**kwargs):
    channel_layer = get_channel_layer()
    message = "⏳ Your verification plan has expired. Renew the plan to continue using the features!"
    async_to_sync(channel_layer.group_send)(
        f"notification_{user.id}",{
            'type' : 'notification',
            'message':message
        }
    )
    Notification.objects.create(invoked_user=user,
                                target_user=user,
                                notification_type='verification',
                                message = message)
    
def send_message_recived_notification(sender,user,**kwargs):
    channel_layer = get_channel_layer()
    message = "message recived"
    async_to_sync(channel_layer.group_send)(
        f"notification_{user.id}",{
            'type' : 'chat_notification',
            'message':message
        }
    )
