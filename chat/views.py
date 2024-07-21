from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .serializers import UserSerializer
from .models import Room
from userside.models import CustomUser
from .models import Chat
from rest_framework import status
# Create your views here.

class GetUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self,request):
        user =request.user
        print('helloooooo')
        following_users = user.following.all()


        chat_rooms = Room.objects.filter(users=user)
        chat_users = CustomUser.objects.filter(chatRooms__in=chat_rooms).exclude(id=user.id).distinct()

        all_users = following_users.union(chat_users)
        blocked_users = user.blocked_users.all()
        filtered_users = all_users.difference(blocked_users)
        serializer = UserSerializer(filtered_users,many = True,context={'user': user.id})
        return Response(serializer.data)
    
    def post(self,request):
        room_id = request.data.get('room_id')
        if not room_id:
            return Response({"error": "Room ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        Chat.objects.filter(room=room).update(is_read=True)

        return Response({"message": "All messages marked as read"}, status=status.HTTP_200_OK)
    

class GetrommChats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self,request,roomID):
         try:
            chats = Chat.objects.filter(room=roomID).order_by('message_time')
            chatdata = [
               {
                   "message": chat.message,
                   "sender_id": chat.sender.id,
                   "sender_username": chat.sender.username,
                   "time": chat.formatted_message_time,
                   "is_read": chat.is_read
               }
               for chat in chats
            ]

            return Response({'chats':chatdata},status=status.HTTP_200_OK)
         except:
             return Response('something went wrong',status=status.HTTP_400_BAD_REQUEST)
