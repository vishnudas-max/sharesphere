from rest_framework import serializers
from .models import Notification
from userside.models import Posts,CustomUser

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id','contend']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','profile_pic']


class NotificationSerializer(serializers.ModelSerializer):
    postID = serializers.SerializerMethodField(read_only = True)
    is_following = serializers.SerializerMethodField(read_only = True)
    invoked_user = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Notification
        fields = ['id','invoked_user','target_user','postID','notfication_date','message','notification_type','is_following','is_read']
    
    def get_postID(self, obj):
       if obj.postID:
           return PostSerializer(obj.postID).data
       else:
           return None
       
    def get_is_following(self,obj):
        followings = obj.target_user.following.all()
        return obj.invoked_user in followings
    
    def get_invoked_user(self, obj):
        return UserSerializer(obj.invoked_user).data
    
    