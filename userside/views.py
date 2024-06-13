from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, GetRandomUsersSerializer,ProfileDetailSeializer
import pyotp
import time
from .models import Regotp, CustomUser
import time
from .tasks import send_mail_to
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
import random
# Create your views here.


class RegisterView(APIView):

    def generate_otp(self):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=120, digits=4)
        otp = totp.now()
        return otp, secret

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            request.session['userdata'] = data
            otp, secret = self.generate_otp()
            email = data['email']
            message = f"""
                        SHARESPHERE,
                           Your OTP for Verification {otp}
                    """
            title = "OTP VERIFICATION"
            # sending mail-
            send_mail_to.delay(message=message, mail=email)
            # saving the otp-
            obj, created = Regotp.objects.update_or_create(
                email=email,
                defaults={
                    'secret': secret,
                    'user_data': data
                }
            )

            return Response({'status': True, 'message': 'OTP sent', 'email': email}, status=status.HTTP_200_OK)

        return Response({'status': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RegisterConfirm(APIView):

    def post(self, request):
        otp = request.data['otp']
        email = request.data['email']
        try:
            obj = Regotp.objects.values(
                'secret', 'user_data', 'otp_time').get(email=email)
            secret = obj['secret']
            user_data = obj['user_data']
            totp = pyotp.TOTP(secret, interval=120, digits=4)
            is_valid = totp.verify(otp)
            print(is_valid)
        except:
            return Response({'status': False, 'message': 'request time out'}, status=status.HTTP_400_BAD_REQUEST)

        if is_valid:
            serializer = RegisterSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                Regotp.objects.get(email=email).delete()
                return Response({'status': True, 'message': 'user created '}, status=status.HTTP_201_CREATED)
        else:
            current_time = timezone.now()
            time_difference = current_time - obj['otp_time']
            if time_difference > timedelta(minutes=2):
                return Response({'status': False, 'message': 'Otp time out'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': False, 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class ResendOtpView(APIView):

    def post(self, request):
        try:
            email = request.data['email']
            obj = Regotp.objects.get(email=email)
            secret = obj.secret
        except:
            return Response({'status': False, 'message': 'Request time out'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(secret, interval=120, digits=4)
        otp = totp.now()
        Regotp.objects.filter(email=email).update(otp_time=timezone.now())
        message = f"""
                        SHARESPHERE,
                           Your OTP for Verification {otp}
                    """
        title = "OTP VERIFICATION"
        # sending mail-
        send_mail_to.delay(message=message, mail=email)

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
