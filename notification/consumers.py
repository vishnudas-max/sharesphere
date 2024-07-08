# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        # Ensure user is authenticated
        if not self.user or self.user.is_anonymous:
            await self.close()
        else:     
             self.room_name = f"user_{self.user.id}"
             self.room_group_name = f"notification_{self.user.id}"

             await self.channel_layer.group_add(
                 self.room_group_name,
                 self.channel_name
             )

             await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        print('message recieved')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification',
                'message': message
            }
        )

    async def notification(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type':'notification',
            'message': message
        }))
