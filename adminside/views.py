from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userside.models import CustomUser,Posts,UserReports
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count, F
from django.db.models.functions import ExtractWeekDay
from rest_framework import viewsets
from .serializers import AdminUserSerializer,GetReportSerializer,AdminPostSeializer,VerificationSerializer
from rest_framework.pagination import PageNumberPagination
from .task import send_mail_to
from post.models import PostReports
from userside.models import Verification
from rest_framework.decorators import action
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
        show_deactivated = self.request.query_params.get('show_deactivated', 'false').lower() in ['true', '1', 'yes']

        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        queryset = queryset.filter(is_superuser=False)

        if show_deactivated == True:
            queryset = queryset.filter(is_active = False)
        else:
            queryset = queryset.filter(is_active = True)

        queryset = queryset.annotate(
            post_count=Count('userPosts'),
            report_count=Count('allreports',distinct=True) 
        )
        
    
        queryset = queryset.order_by('-report_count')
        return queryset
    
    
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        total_report = instance.allreports.all().count()
        last_two_reports = instance.allreports.order_by('-reported_time')[:2].values_list('report_reason', flat=True)
        last_two_reports_text = "\n".join(f"- {reason}" for reason in last_two_reports)
        message = f"""
        Dear {instance.username},

            We regret to inform you that your account on sharesphere has been removed due to repeated violations of our community guidelines. Your account has been reported a total of {total_report} times.

            The reasons for the last two reports against your account are as follows:
            {last_two_reports_text}

            We take the integrity and safety of our community very seriously, and multiple reports indicate that your behavior has been repeatedly found to be inappropriate.

            If you believe this decision has been made in error or if you have any questions, please contact +919207069066.

            Thank you for your understanding.

        Sincerely,
        Sharesphere Support Team
        """
        
        email = instance.email
        send_mail_to.delay(message,email)
        instance.save()
        all_reports = instance.allreports.all()

        # updating report status--
        for report in all_reports:
            report.action_took = True
            report.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class GerUserReports(APIView):    
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]
    def get(self,request,id):
        reports = UserReports.objects.filter(reported_user = id)
        serializer = GetReportSerializer(reports,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


# view to get posts in admin side--
class GetPosts(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]
    queryset = Posts.objects.all()
    serializer_class = AdminPostSeializer
    pagination_class = StandardResultsSetPagination


    def get_queryset(self):
        queryset = super().get_queryset()
        show_deleted = self.request.query_params.get('show_deleted', 'false').lower() in ['true', '1', 'yes']

        if show_deleted == True:
            queryset = queryset.filter(is_deleted = True)
        else:
            queryset = queryset.filter(is_deleted = False)

        queryset = queryset.annotate(
            report_count=Count('all_post_reports')
        )

        queryset = queryset.order_by('-report_count')
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        reports = instance.all_post_reports.all()
        for report in reports:
            report.action_took = True
            report.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class GetPostReprts(APIView):    
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]
    def get(self,request,id):
        reports = PostReports.objects.filter(reported_post= id)
        serializer = GetReportSerializer(reports,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class GetVerificationRequets(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    pagination_class = StandardResultsSetPagination


    def get_queryset(self):
        queryset = super().get_queryset()
        show_accepted = self.request.query_params.get('accepted', 'false').lower() in ['true', '1', 'yes']
        show_rejected = self.request.query_params.get('rejected', 'false').lower() in ['true', '1' ,'yes']
        print(show_accepted,show_rejected)
        if show_accepted == True:
            queryset = queryset.filter(is_accepted = True)
        elif show_rejected == True:
            queryset = queryset.filter(is_rejected = True)
        else:
            queryset = queryset.filter(Q(is_accepted= False) & Q(is_rejected =False))
        return queryset

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        verification = self.get_object()
        print(verification)
        verification.is_accepted = True
        verification.save()
        return Response({'status': 'verification accepted'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        verification = self.get_object()
        verification.is_rejected = True
        verification.save()
        return Response({'status': 'verification rejected'}, status=status.HTTP_200_OK)
