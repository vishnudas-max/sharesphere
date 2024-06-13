from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .serializers import UserSerializer
# Create your views here.

class GetUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self,request):
        user =request.user
        print('hello')
        all_users =user.following.all()
        serializer = UserSerializer(all_users,many = True)
        return Response(serializer.data)