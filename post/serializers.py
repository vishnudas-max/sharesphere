from rest_framework import serializers
from userside.models import CustomUser,Posts
from .models import PostLike,Comments
from django.utils.timesince import timesince
from django.utils import timezone

# serializer to serializer user data-
class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','profile_pic']

# serializer to serializer liked users-
class PostLikeserializer(serializers.ModelSerializer):
    userID = UserDetailsSerializer(read_only = True)
    class Meta:
        model = PostLike
        fields = ['userID']

# serililzer to get post data with likecount and likes users' data-
class PostsSerializer(serializers.ModelSerializer):
    userID = UserDetailsSerializer(read_only=True)
    likes_count =serializers.IntegerField(read_only = True)
    liked_users = PostLikeserializer(source = 'postlikes' , many = True ,read_only = True)  #getting seialized data of users' who liked the post-
    comment_count = serializers.SerializerMethodField(read_only = True)
    is_following = serializers.SerializerMethodField(read_only = True)
    formatted_uploadDate = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Posts
        fields = ['id','userID', 'caption', 'contend', 'uploadDate', 'updatedDate', 'is_deleted', 'likes_count','liked_users','comment_count','is_following','formatted_uploadDate']

    def get_is_following(self,obj):
        user = self.context['request_user']
        currentUser =CustomUser.objects.get(username=user)
        if obj.userID == currentUser:
            return True
        else:
            return obj.userID in currentUser.following.all()
        

    def get_comment_count(self,obj):
        return obj.postcomments.all().count()
    
    def get_formatted_uploadDate(self, obj):
        return obj.formatted_uploadDate

# serializer for creation and updation of posts--
class postCreateSeializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['userID','caption','contend']


# serializer for getting user liked posts--
class GetLikedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields =['postID']


# serializer for creating comments--
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'userID', 'postID', 'comment', 'comment_time', 'parent_comment']

# serializer for comment reply-
class ReplySerializer(serializers.ModelSerializer):
    userID = UserDetailsSerializer(read_only = True)
    time_ago = serializers.SerializerMethodField()
    reply_to = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Comments
        fields = ['id','userID','postID','comment','comment_time','time_ago','reply_to']

    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.comment_time

        if diff.days >= 1:
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds} seconds ago"
    
    def get_reply_to(self,obj):
        if obj.parent_comment:
            return obj.parent_comment.userID.username
        return None
    
# serializers for getting comments with replies--
class CommentSerializer(serializers.ModelSerializer):
    userID = UserDetailsSerializer(read_only =True)
    replies = ReplySerializer(many = True,read_only = True)
    time_ago = serializers.SerializerMethodField()
    class Meta:
        model = Comments
        fields = ['id','userID','postID','comment','comment_time','parent_comment','replies','time_ago']

    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.comment_time

        if diff.days >= 1:
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds} seconds ago"