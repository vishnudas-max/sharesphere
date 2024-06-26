from channels.generic.websocket import AsyncWebsocketConsumer
import json
from userside.models import CustomUser
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_username(self,id):
         try:
            obj = CustomUser.objects.get(id=id)
            return obj.username
         except:
              return 'no user found'
         
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
    
    async def disconnect(self, code):
        
        # notifying the group that the user has gone offline--
        print('disconnected')
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
               
    async def receive(self, text_data=None, bytes_data=None):
         try:
            if text_data:
                data = json.loads(text_data)
                message = data.get('message')
                notification_type = data.get('notification_type')
                type = data.get('type')
                
                if message:
                    invoked_user = self.scope['user'].username
                    target_user_id = self.scope['url_route']['kwargs']['id']
                    target_username = self.get_username(target_user_id)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_notification",
                            "message": message,
                            "invoked_user": invoked_user ,
                            "target_user": target_username,
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
        invoked_user= event.get('invoked_user')
        target_user = event.get('target_user')
       
        print(f"invokeduser={invoked_user} message={message} targetuser={target_user} type={notification_type}")
        if message:
            await self.send(text_data=json.dumps({
                "type": "send_notification",
                "message": message,
                "invoked_user": invoked_user ,
                "target_user": target_user,
                "notification_type": notification_type,
            }))

        else:
            # Handle the missing or invalid 'message' key
            pass
         