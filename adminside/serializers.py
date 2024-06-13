from rest_framework import serializers
from userside.models import CustomUser


class AdminUserSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'is_active', 'profile_pic', 'post_count']