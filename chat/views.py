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
from django.db.models import OuterRef, Subquery, DateTimeField, IntegerField,Case,When, Value
from django.db.models.functions import Coalesce
from notification.signals import message_recived
# Create your views here.

class GetUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get following users
        following_users = user.following.all()

        # Subquery to get the latest message time for users in chat rooms
        latest_message_time_subquery = Chat.objects.filter(
            room__users=OuterRef('pk')
        ).order_by('-message_time').values('message_time')[:1]

        # Annotate following users with latest message time and a flag for sorting
        filtered_following_users = following_users.annotate(
            last_message_time=Coalesce(Subquery(latest_message_time_subquery, output_field=DateTimeField()), None)
        ).annotate(
            message_time_flag=Case(
                When(last_message_time__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )

        # Get chat users
        chat_rooms = Room.objects.filter(users=user)
        chat_users = CustomUser.objects.filter(chatRooms__in=chat_rooms).exclude(id=user.id).distinct()

        # Annotate chat users with latest message time and a flag for sorting
        filtered_chat_users = chat_users.annotate(
            last_message_time=Coalesce(Subquery(latest_message_time_subquery, output_field=DateTimeField()), None)
        ).annotate(
            message_time_flag=Case(
                When(last_message_time__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )

        # Combine annotated users
        combined_users = filtered_following_users.union(filtered_chat_users)

        # Sort users by message_time_flag (to place users with no message time at the end) and last_message_time in descending order
        sorted_users = combined_users.order_by('message_time_flag', '-last_message_time')

        # Serialize the users
        serializer = UserSerializer(sorted_users, many=True, context={'user': request.user.id})
        return Response(serializer.data)
      
    
    def post(self, request):
        room_id = request.data.get('room_id')
        user = request.user  # Get the current user
        if not room_id:
            return Response({"error": "Room ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        chats = Chat.objects.filter(room=room,is_read=False).exclude(sender=user).order_by('-message_time').update(is_read=True)
        message_recived.send(sender=self.__class__,user=user)
        return Response({"message": "All messages marked as read"}, status=status.HTTP_200_OK)

class GetrommChats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self,request,roomID):
         try:
            user =  request.user
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

class GetUnreadMessageCount(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self,request):
            user = request.user
            rooms = Room.objects.filter(users=user)
            unread_messages_count = Chat.objects.filter(room__in=rooms,is_read=False).exclude(sender=user).count()
            return Response({"message_count": unread_messages_count})