from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, GetRandomUsersSerializer, ProfileDetailSeializer, get_tokens_for_user, UserReportSerializer,RequestVerificationSeializer,GetverificationDetailes,UserSerializer
import pyotp
import time
from .models import Regotp, CustomUser
import time
from .tasks import send_mail_to, send_sms_to ,send_follow_notification
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
from rest_framework_simplejwt.views import TokenRefreshView
from .signals import user_followed, user_unfollowed


# Create your views here.


def hash_otp(otp):
    # Hash the OTP using SHA-256
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
    return hashed_otp

def generate_otp():
        otp = ''.join(random.choices(string.digits, k=4))
        return otp

class RegisterView(APIView):

   

    def post(self, request):

        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            otp = generate_otp()
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
            send_sms_to.delay(phone_number, otp)
            obj, created = Regotp.objects.update_or_create(
                email=email,
                defaults={
                    'secret': hashedotp,
                    'user_data': data
                }
            )
            return Response({'status': True, 'message': 'OTP sent', 'email': email, 'phone_number': phone_number}, status=status.HTTP_200_OK)

            # saving the otp-
        return Response({'status': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RegisterConfirm(APIView):
    def post(self, request):
        otp = request.data['otp']
        email = request.data['email']
        try:
            obj = Regotp.objects.values(
                'secret', 'user_data', 'otp_time').get(email=email)
            originalotp = obj['secret']
            user_data = obj['user_data']
        except:
            return Response({'status': False, 'message': 'request time out'}, status=status.HTTP_400_BAD_REQUEST)

        hashedotp = hash_otp(otp)
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
        Regotp.objects.filter(email=email).update(
            otp_time=timezone.now(), secret=hashedotp)
        message = f"""
                        SHARESPHERE,
                           Your OTP for Verification {otp}
                    """
        title = "OTP VERIFICATION"
        # sending mail-
        send_mail_to.delay(message=message, mail=email)
        send_sms_to.delay(phone_number, otp)

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
            print('follwoing')
            user_unfollowed.send(sender=self.__class__, follower=user, followed=user_to_follow)
        else:
            user.following.add(user_to_follow)
            user_to_follow.followers.add(user)
            following_Status = True
            user_followed.send(sender=self.__class__, follower=user, followed=user_to_follow)
            send_follow_notification.delay(follower_id=user.id, followed_id=user_to_follow.id)
            # follow_notification.send(sender=self.__class__,follower=user,followed=user_to_follow)

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

    def get(self, request):
        users = CustomUser.objects.filter(Q(is_superuser=False) & Q(
            is_active=True)).exclude(username=request.user.username).order_by('?')[:5]
        serializer = GetRandomUsersSerializer(
            users, many=True, context={'request': request})
        return Response(serializer.data)


# view for getting user-profile detailes--
class GetUserProfile(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        serializer = ProfileDetailSeializer(user, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response( 'something went wrong!', status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        print(data)
        if 'username' in data:
            if CustomUser.objects.filter(username = data['username']).exclude(id=id):
                return Response('username already in use', status=status.HTTP_400_BAD_REQUEST)
        serializer = ProfileDetailSeializer(user, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response('something went wrong!', status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            return Response('Invalid Username or passsword', status=status.HTTP_400_BAD_REQUEST)
        if user.is_active == False:
            return Response('This Account is no longer accessible', status=status.HTTP_400_BAD_REQUEST)
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
   def post(self, request, *args, **kwargs):
        try:
            refresh = request.data['refresh']
        except KeyError:
            return Response({'error': 'Refresh token not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the refresh token
            refresh_token = RefreshToken(refresh)
            user_id = refresh_token.payload.get('user_id')

            # Fetch user from database
            user = CustomUser.objects.get(id=user_id)

            # Check if user is active
            if not user.is_active:
                return Response({'error': 'User account is not active.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate new access token
            access_token = refresh_token.access_token

            return Response({'access': str(access_token)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Reportuser(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data.copy()
        data['reported_by'] = request.user.id
        print(data)
        serializer = UserReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response('Report Succes', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def patch(self,request):
        try:
            password = request.data['password']
            user = request.user
            user.set_password(password)
            user.save()

            return Response('Password Updated',status=status.HTTP_200_OK)
        except:
            return Response('something went wrong ',status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request):
        try:
            user=request.user
            user.is_active=False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response('something went wrong!',status=status.HTTP_400_BAD_REQUEST)
            

class RequestVerification(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self,request):
        data = request.data
        serializer = RequestVerificationSeializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response('Request Send',status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        user = request.user
        try:
            verification_obj = user.verificationData
            if verification_obj and verification_obj.plan_choosed and verification_obj.expiry_date < timezone.now():
                    user.is_verified = False
                    user.save()

                    verification_obj.is_subscribed = False
                    verification_obj.plan_choosed = None
                    verification_obj.amount_paid = None
                    verification_obj.subscribed_date = None
                    verification_obj.save()
        except:
            pass
        serializer = GetverificationDetailes(user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    


# sending otp for forgot password --
class ForgotPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email)
        try:
            user = CustomUser.objects.get(email=email)
            otp = generate_otp()
            hashedotp = hash_otp(otp)
            message = f"""
                SHARESPHERE,
                Your OTP for Verification {otp}
            """
            title = "OTP VERIFICATION"
            # sending mail-
            send_mail_to.delay(message=message, mail=email)
            obj, created = Regotp.objects.update_or_create(
                email=email,
                defaults={
                    'secret': hashedotp,
                    'user_data':{}
                }
            )
            return Response({'status': True, 'message': 'OTP sent', 'email': email}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'status': False, 'message': 'There is no matching account found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'status': False, 'message': 'An error occurred'}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOtp_for_ForgotPassword(APIView):

    def post(self, request):
        otp = request.data['otp']
        email = request.data['email']
        try:
            otp_instance =Regotp.objects.get(email=email)
            originalotp = otp_instance.secret
            otp_time =otp_instance.otp_time
        except:
            return Response({'status': False, 'message': 'request time out'}, status=status.HTTP_400_BAD_REQUEST)

        hashedotp = hash_otp(otp)
        is_valid = originalotp == hashedotp
        if is_valid:
            current_time = timezone.now()
            time_difference = current_time - otp_time
            if time_difference > timedelta(minutes=1):
                return Response({'status': False, 'message': 'Otp time out'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp_instance.delete()
            return Response({'status': True, 'message':'otp validattion success'}, status=status.HTTP_200_OK)
        
        else:
            current_time = timezone.now()
            time_difference = current_time - otp_time
            if time_difference > timedelta(minutes=1):
                return Response({'status': False, 'message': 'Otp time out'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': False, 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request):
        try:
            password = request.data['password']
            email = request.data['email']
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.save()

            return Response('Password Updated',status=status.HTTP_200_OK)
        except:
            return Response('something went wrong ',status=status.HTTP_400_BAD_REQUEST)
        
class ForgotPasswordResendOtpView(APIView):

    def post(self, request):
        try:
            email = request.data['email']
            otp_intance = Regotp.objects.get(email=email)
        except:
            return Response({'status': False, 'message': 'Request time out'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()
        hashedotp = hash_otp(otp)
        Regotp.objects.filter(email=email).update(
            otp_time=timezone.now(), secret=hashedotp)
        message = f"""
                        SHARESPHERE,
                           Your OTP for Verification {otp}
                    """
        title = "OTP VERIFICATION"
        # sending mail-
        send_mail_to.delay(message=message, mail=email)
        return Response({'status': True, 'message': 'OTP send', 'email': email}, status=status.HTTP_200_OK)
    

class BlockUserView(APIView):
    authentication_classes =[JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request,userID=None):
        user=request.user
        blocked_users = user.blocked_users.all()
        serializer = UserSerializer(blocked_users,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)


    def post(self,request):
        userID = request.data.get('userID')
        user = request.user
        try:
            user_to_block = CustomUser.objects.get(id=userID)
            if user_to_block == user:
                return Response("You cannot block yourself.", status=status.HTTP_400_BAD_REQUEST)

            if user_to_block in user.blocked_users.all():
                return Response(f"You have already blocked {user_to_block.username}.", status=status.HTTP_400_BAD_REQUEST)

            user.blocked_users.add(user_to_block)
            return Response(f"You have successfully blocked {user_to_block.username}.", status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response("User not found.", status=status.HTTP_404_NOT_FOUND)
    
    def patch(self,request):
        userID = request.data.get('userID')
        user = request.user
        try:
            user_to_block = CustomUser.objects.get(id=userID)
            if user_to_block in user.blocked_users.all():
                user.blocked_users.remove(user_to_block)

            return Response({'status':True,'message':f"{user_to_block.username} has been removed from block list"},status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response("User not found.", status=status.HTTP_404_NOT_FOUND)


