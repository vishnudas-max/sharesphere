from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from django.contrib.auth.models import User
from .models import Notification
from .serializer import NotificationSerializer
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        count_only = request.query_params.get('count', None)
        if count_only is not None:
            unread_count = Notification.objects.filter(Q(target_user=user) & Q(is_read=False)).count()
            return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)
        
        notifications = Notification.objects.filter(target_user=user).order_by('-time_triggered')
        grouped_notifications = {}
        n=[]
        for notification in notifications:
            date_str = notification.time_triggered.strftime('%m/%d/%Y')
            if date_str not in grouped_notifications:
                grouped_notifications[date_str] = []
            grouped_notifications[date_str].append(NotificationSerializer(notification).data)
        return Response(grouped_notifications, status=status.HTTP_200_OK)

    def post(self,request):
        user = request.user
        notifications = Notification.objects.filter(Q(target_user = user) & Q(is_read=False))

        for notification in notifications:
            notification.is_read = True
            notification.save()

        return Response({'message':'is_read status updated'},status=status.HTTP_200_OK)

class GetUnreadNotificationCount:
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request):
        user = request.user
        notifications = Notification.objects.filter(Q(target_user = user) & Q(is_read=False))