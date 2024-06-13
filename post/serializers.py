from rest_framework import serializers
from userside.models import CustomUser,Posts
from .models import PostLike,Comments

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
    class Meta:
        model = Posts
        fields = ['id','userID', 'caption', 'contend', 'uploadDate', 'updatedDate', 'is_deleted', 'likes_count','liked_users','comment_count','is_following']

    def get_is_following(self,obj):
        user = self.context['request_user']
        currentUser =CustomUser.objects.get(username=user)
        if obj.userID == currentUser:
            return True
        else:
            return obj.userID in currentUser.following.all()
        

    def get_comment_count(self,obj):
        return obj.postcomments.all().count()

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
    class Meta:
        model = Comments
        fields = ['id','userID','postID','comment','comment_time']

# serializers for getting comments with replies--
class CommentSerializer(serializers.ModelSerializer):
    userID = UserDetailsSerializer(read_only =True)
    replies = ReplySerializer(many = True,read_only = True)
    class Meta:
        model = Comments
        fields = ['id','userID','postID','comment','comment_time','parent_comment','replies']