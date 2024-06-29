from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, GetRandomUsersSerializer,ProfileDetailSeializer,get_tokens_for_user
import pyotp
import time
from .models import Regotp, CustomUser
import time
from .tasks import send_mail_to,send_sms_to
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
import random
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import string
import hashlib

# Create your views here.


def hash_otp( otp):
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()  # Hash the OTP using SHA-256
        return hashed_otp

class RegisterView(APIView):

    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=4))
        return otp

    def post(self, request):

        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            otp= self.generate_otp()
            hashedotp = hash_otp(otp)
            email = data['email']
            phone_number = data['phone_number']
            message = f"""
                        SHARESPHERE,
                           Your OTP for Verification {otp}
                    """
            title = "OTP VERIFICATION"
            # sending mail-
            send_mail_to.delay(message=message, mail=email)
            send_sms_to.delay(phone_number,otp)
            obj, created = Regotp.objects.update_or_create(
                email=email,
                defaults={
                    'secret': hashedotp,
                    'user_data': data
                }
            )
            return Response({'status': True, 'message': 'OTP sent', 'email': email,'phone_number':phone_number}, status=status.HTTP_200_OK)

            # saving the otp-
        return Response({'status': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RegisterConfirm(APIView):
    def post(self, request):
        otp = request.data['otp']
        email = request.data['email']
        try:
            obj = Regotp.objects.values('secret', 'user_data', 'otp_time').get(email=email)
            originalotp = obj['secret']
            user_data = obj['user_data']
        except:
            return Response({'status': False, 'message': 'request time out'}, status=status.HTTP_400_BAD_REQUEST)
        
        hashedotp =hash_otp(otp)
        is_valid = originalotp == hashedotp
        if is_valid:
            current_time = timezone.now()
            time_difference = current_time - obj['otp_time']
            if time_difference > timedelta(minutes=1):
                return Response({'status': False, 'message': 'Otp time out'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = RegisterSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                Regotp.objects.get(email=email).delete()
                return Response({'status': True, 'message': 'user created '}, status=status.HTTP_201_CREATED)
        else:
            current_time = timezone.now()
            time_difference = current_time - obj['otp_time']
            if time_difference > timedelta(minutes=1):
                return Response({'status': False, 'message': 'Otp time out'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': False, 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class ResendOtpView(APIView):

    def post(self, request):
        try:
            email = request.data['email']
            phone_number = request.data['phone_number']
            obj = Regotp.objects.get(email=email)
        except:
            return Response({'status': False, 'message': 'Request time out'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = ''.join(random.choices(string.digits, k=4))
        hashedotp = hash_otp(otp)
        Regotp.objects.filter(email=email).update(otp_time=timezone.now(),secret=hashedotp)
        message = f"""
                        SHARESPHERE,
                           Your OTP for Verification {otp}
                    """
        title = "OTP VERIFICATION"
        # sending mail-
        send_mail_to.delay(message=message, mail=email)
        send_sms_to.delay(phone_number,otp)

        return Response({'status': True, 'message': 'OTP send', 'email': email}, status=status.HTTP_200_OK)


class FollowAndFollowingView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, username):
        user = request.user
        user_to_follow = get_object_or_404(CustomUser, username=username)

        if user_to_follow == user:
            return Response({'detail': 'You cannot follow youself!'}, status=status.HTTP_400_BAD_REQUEST)

        if user_to_follow in user.following.all():
            user.following.remove(user_to_follow)
            user_to_follow.followers.remove(user)
            following_Status = False
        else:
            user.following.add(user_to_follow)
            user_to_follow.followers.add(user)
            following_Status = True

        return Response({'following_Status': following_Status}, status=status.HTTP_200_OK)

    def get(self, request, username=None):
        user = request.user
        following = user.following.all().count()
        follwers = user.followers.all().count()
        print(follwers)
        print(following)
        return Response(status=status.HTTP_200_OK)

# view for getting radom users--
class getRandomUser(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request):
        users = CustomUser.objects.filter(Q(is_superuser=False) & Q(is_active=True)).exclude(username=request.user.username).order_by('?')[:5]
        serializer = GetRandomUsersSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)


# view for getting user-profile detailes--
class GetUserProfile(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request,id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        serializer = ProfileDetailSeializer(user, context={'request': request})
        return Response(serializer.data)


class LoginView(APIView):
    def post(self,request):
        username = request.data['username']
        password = request.data['password']
        # if(not CustomUser.objects.filter(phone_number=username).exists()):
        #     return Response('invalid PhoneNumber')
        # print(username)
        user = authenticate(username=username,password=password)
        if user is None:
            return Response('Invalid Username or passsword',status=status.HTTP_400_BAD_REQUEST)
        
        # refresh = RefreshToken.for_user(user)
        tokens = get_tokens_for_user(user)
        return Response(tokens,status=status.HTTP_200_OK)
        

        