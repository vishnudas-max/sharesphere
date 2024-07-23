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
from django.db.models import OuterRef, Subquery, DateTimeField, BooleanField, Value
from django.db.models.functions import Coalesce
# Create your views here.

class GetUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self, request):
        user = request.user
        print('helloooooo')

        # Get following users and blocked users
        following_users = user.following.all()
        blocked_users = user.blocked_users.all()

        # Annotate with the latest message time and blocked status
        latest_message_time = Chat.objects.filter(
            room__users=OuterRef('pk')
        ).order_by('-message_time').values('message_time')[:1]

        # Annotate following users with latest message time and blocked status
        filtered_following_users = following_users.annotate(
            last_message_time=Coalesce(Subquery(latest_message_time, output_field=DateTimeField()), None),
            is_blocked=Value(False, output_field=BooleanField())
        )

        # Get chat users
        chat_rooms = Room.objects.filter(users=user)
        chat_users = CustomUser.objects.filter(chatRooms__in=chat_rooms).exclude(id=user.id).distinct()

        # Annotate chat users with latest message time and blocked status
        filtered_chat_users = chat_users.annotate(
            last_message_time=Coalesce(Subquery(latest_message_time, output_field=DateTimeField()), None),
            is_blocked=Value(False, output_field=BooleanField())
        )

        # Combine annotated users
        filtered_users = filtered_following_users.union(filtered_chat_users)

        # Annotate blocked users by the current user
        blocked_users_annotated = blocked_users.annotate(
            last_message_time=Coalesce(Subquery(latest_message_time, output_field=DateTimeField()), None),
            is_blocked=Value(True, output_field=BooleanField())
        )

        # Combine all users including those blocked by the current user
        all_users = filtered_users.union(blocked_users_annotated)

        # Sort users by is_blocked (blocked users last) and last_message_time in descending order
        sorted_users = all_users.order_by('is_blocked', '-last_message_time')

        # Serialize the users
        serializer = UserSerializer(sorted_users, many=True, context={'user': request.user.id})
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
