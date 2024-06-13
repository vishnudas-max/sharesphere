from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userside.models import CustomUser,Posts
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count, F
from django.db.models.functions import ExtractWeekDay
from rest_framework import viewsets
from .serializers import AdminUserSerializer
from rest_framework.pagination import PageNumberPagination
# Create your views here.


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 7  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserVerificatinCount(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request):
        verified = CustomUser.objects.filter(is_verified=True).count()
        non_verified = CustomUser.objects.filter(is_verified=False).count()
        print(verified,non_verified)
        return Response({'verified':verified,'non_verified':non_verified},status=status.HTTP_200_OK)
    

class PostCountByDay(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request):

        postobj = Posts.objects.annotate(day_of_week = ExtractWeekDay('uploadDate')).values('day_of_week').annotate(count=Count('id')).order_by('day_of_week')
        print(postobj)
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        counts_by_day = {days[entry['day_of_week'] - 1]: entry['count'] for entry in postobj}
        # Ensure all days are represented
        for day in days:
            if day not in counts_by_day:
                counts_by_day[day] = 0

        return Response(counts_by_day,status=status.HTTP_200_OK)
    
class getTotalDetailes(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request):
        total_post = Posts.objects.all().count()
        total_users = CustomUser.objects.filter(is_superuser = False).count()

        return Response({'total_users':total_users,'total_post':total_post},status=status.HTTP_200_OK)
    

class GeUsers(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        queryset = queryset.filter(is_superuser = False)
        queryset = queryset.annotate(post_count=Count('userPosts'))
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)