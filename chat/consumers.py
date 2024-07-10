from channels.generic.websocket import AsyncWebsocketConsumer
import json
from userside.models import CustomUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
import jwt
from .models import Room, Chat


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def save_chat_message(self, room, sender, message):
        print('hello')
        chat = Chat.objects.create(room=room, sender=sender, message=message)
        return chat

    # to get room--
    @database_sync_to_async
    def get_room(self, id):

        room = Room.objects.get(id=id)
        return room

    # to get user--
    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    # @database_sync_to_async
    # def get_all_messages(self, roomID):
    #     chats = Chat.objects.filter(room=roomID).order_by('message_time')
    #     return [
    #         {
    #             "message": chat.message,
    #             "sender_id": chat.sender.id,
    #             "sender_username": chat.sender.username,
    #             "time": chat.formatted_message_time,
    #             "is_read": chat.is_read
    #         }
    #         for chat in chats
    #     ]

    # to check if room exists else create room---
    @database_sync_to_async
    def get_or_create_room(self, request_user, target_user):
        room = Room.objects.filter(users=request_user).filter(
            users=target_user).first()
        if not room:
            room = Room.objects.create()
            room.users.add(request_user, target_user)
        return room

    async def connect(self):
        request_user = self.scope['user']

        # Ensure user is authenticated
        if not request_user or request_user.is_anonymous:
            await self.close()
        else:
            # Get the ID of the user to chat with from the URL
            chat_with_user_id = self.scope['url_route']['kwargs']['id']

            # Fetch the chat_with_user object asynchronously
            chat_with_user = await self.get_user(chat_with_user_id)

            # Create a room name based on user IDs
            room = await self.get_or_create_room(request_user, chat_with_user)

            self.room_group_name = f"chat_{room.id}"

            print(self.room_group_name)

            # Add the user to the channel group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()

            self.roomID = room.id
            await self.send(text_data=json.dumps({
                "type": "send_room_id",
                "roomID": self.roomID
            }))

    async def disconnect(self, code):

        # notifying the group that the user has gone offline--
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_offline',
                'username': self.scope['user'].username
            }
        )

        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                data = json.loads(text_data)
                message = data.get('message')
                event_type = data.get('type')

                if message and event_type == 'chat_message':
                    request_user = self.scope['user']
                    room_id = int(self.room_group_name.split('_')[1])
                    print(f"roomid{room_id}")

                    room = await self.get_room(room_id)

                    chat_message = await self.save_chat_message(room, request_user, message)
                    print('message saved', chat_message)

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": message,
                            "sender_id": chat_message.sender.id,
                            "sender_username": chat_message.sender.username,
                            "time": chat_message.formatted_message_time,
                            "is_read": chat_message.is_read
                        }
                    )
                elif event_type == 'user_typing':
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_typing',
                            'username': self.scope['user'].username
                        }

                    )

                elif event_type == 'user_online':
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_online',
                            'username': self.scope['user'].username
                        }
                    )

        except json.JSONDecodeError:
            # Handle the case where text_data is not valid JSON
            pass
        except Exception as e:
            # Handle other exceptions if necessary
            pass

    async def chat_message(self, event):

        message = event.get('message')
        sender_id = event.get('sender_id')
        sender_username = event.get('sender_username')
        time = event.get('time')
        is_read = event.get('is_read')
        print(message, sender_id, sender_username, time, is_read)
        if message:
            await self.send(text_data=json.dumps({
                "type": "chat_message",
                "message": message,
                "sender_id": sender_id,
                "sender_username": sender_username,
                "time": time,
                "is_read": is_read
            }))

        else:
            # Handle the missing or invalid 'message' key
            pass

    async def user_typing(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'username': username
        }))

    async def user_online(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'user_online',
            'username': username
        }))

    async def user_offline(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'user_offline',
            'username': username
        }))

    # to save message into databaase--


class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'videocall'
        self.room_group_name = f'call_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        roomID = data['roomID']
        targetUser = data['targetUser']
        print(data)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_message',
                'roomID': roomID,
                'targetUser': targetUser
            }
        )

    async def call_message(self, event):
        roomID = event['roomID']
        targetuser = event['targetUser']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_message',
            'roomID': roomID,
            'targetUser': targetuser
        }))
