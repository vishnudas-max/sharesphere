from channels.generic.websocket import AsyncWebsocketConsumer
import json
from userside.models import CustomUser
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user(self, id):
        try:
            user = CustomUser.objects.get(id=id)
            return user
        except CustomUser.DoesNotExist:
            return 'no user found'

    @database_sync_to_async
    def save_notification(self,invoked_user, user, message, notification_type):
        print('hello')
        try:
            Notification.objects.create(
                invoked_user=invoked_user,
                target_user=user,
                message=message,
                notification_type=notification_type
            )
            print('hello')
        except Exception as e:
            print(e)

    @database_sync_to_async
    def get_pending_notifications(self, user_id):
        print('getting')
        return Notification.objects.filter(target_user_id=user_id, is_send=False)

    @database_sync_to_async
    def mark_notification_as_send(self, notification):
        notification.is_send = True
        notification.save()

    async def connect(self):
        invoked_user = self.scope['user']
        # Ensure user is authenticated
        if not invoked_user or invoked_user.is_anonymous:
            await self.close()
        else:
            # Get the ID of the user to chat with from the URL
            target_user_id = self.scope['url_route']['kwargs']['id']
            self.room_group_name = f"from_{invoked_user.id}_to_{target_user_id}"

            print(self.room_group_name)

            # Add the user to the channel group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()

            self.send_pending_notifications(target_user_id)

    async def disconnect(self, code):
        # Notifying the group that the user has gone offline
        print('disconnected')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                data = json.loads(text_data)
                message = data.get('message')
                notification_type = data.get('notification_type')
                
                if message:
                    invoked_user_instance = self.scope['user']
                    invoked_user =invoked_user_instance.username
                    target_user_id = self.scope['url_route']['kwargs']['id']
                    user = await self.get_user(target_user_id)
                    await self.save_notification(invoked_user_instance, user, message, notification_type)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_notification",
                            "message": message,
                            "invoked_user": invoked_user,
                            "target_user": user.username,
                            "notification_type": notification_type,
                        }
                    )
        except json.JSONDecodeError:
            # Handle the case where text_data is not valid JSON
            pass
        except Exception as e:
            # Handle other exceptions if necessary
            pass

    async def send_notification(self, event):
        notification_type = event.get('notification_type')
        message = event.get('message')
        invoked_user = event.get('invoked_user')
        target_user = event.get('target_user')

        print(f"invokeduser={invoked_user} message={message} targetuser={target_user} type={notification_type}")

        if message:
            await self.send(text_data=json.dumps({
                "type": "send_notification",
                "message": message,
                "invoked_user": invoked_user,
                "target_user": target_user,
                "notification_type": notification_type,
            }))

    async def send_pending_notifications(self, target_user_id):
        print('sending....')
        pending_notifications = await self.get_pending_notifications(target_user_id)
        print('after')
        for notification in pending_notifications:
            await self.send(text_data=json.dumps({
                "type": "send_notification",
                "message": notification.message,
                "invoked_user": notification.invoked_user.username,
                "target_user": notification.target_user.username,
                "notification_type": notification.notification_type,
            }))
            await self.mark_notification_as_send(notification)
         