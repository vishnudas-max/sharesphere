from rest_framework import serializers
from userside.models import CustomUser,UserReports



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