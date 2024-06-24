from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .serializers import UserSerializer
from .models import Room
from userside.models import CustomUser
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


        serializer = UserSerializer(all_users,many = True,context={'user': user.id})
        return Response(serializer.data)