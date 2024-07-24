from rest_framework import serializers
from userside.models import CustomUser,UserReports,Posts
from post.models import PostReports
from userside.models import Verification



class AdminUserSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(read_only=True)
    report_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email','is_active', 'profile_pic', 'post_count', 'report_count']

class GetReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.SerializerMethodField()
    class Meta:
        model = UserReports
        fields = ['reported_by','report_reason']
    def get_reported_by(self,obj):
        return obj.reported_by.username
    
class AdminPostSeializer(serializers.ModelSerializer):
    report_count = serializers.IntegerField(read_only=True)
    username = serializers.SerializerMethodField(read_only = True)
    total_likes = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Posts
        fields = ['id','caption','contend','uploadDate','updatedDate','is_deleted','username','total_likes','report_count']

    def get_username(self,obj):
        return obj.userID.username
    
    def get_total_likes(self,obj):
        return obj.postlikes.all().count()
    
class GetPostReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.SerializerMethodField()
    class Meta:
        model = PostReports
        fields = ['reported_by','report_reason']
    def get_reported_by(self,obj):
        return obj.reported_by.username
    
# serializer for getting verfication request--
class VerificationSerializer(serializers.ModelSerializer):

    userID = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Verification
        fields = ['id','userID','document_type','document_number','is_accepted','is_rejected']

    def get_userID(self,obj):
        user=CustomUser.objects.get(id=obj.userID.id)
        return user.username