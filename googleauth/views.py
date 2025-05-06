from .services import get_user_data
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login
from rest_framework.views import APIView
from .serializers import AuthSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from userside.serializers import get_tokens_for_user
from rest_framework import status
import random,string

User = get_user_model()


# views that handle 'localhost://8000/api/auth/login/google/'
class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        print('here---')
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        validated_data = auth_serializer.validated_data
        user_data = get_user_data(validated_data)
        if(user_data['status']==False):
            redirect_url = f"{settings.BASE_APP_URL}?message='Something went wrong, Try again later...'"
            return redirect(redirect_url)
        try:
            user = User.objects.get(email=user_data['email'])
            if(user.is_active == False):
                redirect_url = f"{settings.BASE_APP_URL}?message='This account in no longer accessible'"
                return redirect(redirect_url)
            tokens = get_tokens_for_user(user)
            redirect_url = f"{settings.BASE_APP_URL}?access={tokens['access']}&refresh={tokens['refresh']}"
            return redirect(redirect_url)
        except:
            first_name = user_data['first_name']
            last_name = user_data['last_name']
            base_username = f"{first_name}.{last_name}".lower()

            # Generate a unique username
            username = base_username
            while User.objects.filter(username=username).exists():
                unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                username = f"{base_username}.{unique_suffix}"

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=user_data['email'],
                username=username
            )
            tokens = get_tokens_for_user(user)
            redirect_url = f"{settings.BASE_APP_URL}?access={tokens['access']}&refresh={tokens['refresh']}"
            return redirect(redirect_url)

       