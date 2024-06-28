from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Posts
from post.serializers import UserDetailsSerializer
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh['is_admin'] = user.is_superuser
    refresh['username'] = user.username

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         token['username'] = user.username
#         token['is_admin'] = user.is_superuser
 
#         return token

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField()

    def validate(self,data):
        if data['username']:
            if CustomUser.objects.filter(username = data['username']).exists():
                raise serializers.ValidationError('Username already in use!')
        if data['email']:
            if CustomUser.objects.filter(email = data['email']).exists():
                raise serializers.ValidationError('Email already in use !')
        if data['phone_number']:
            if CustomUser.objects.filter(phone_number = data['phone_number']).exists():
                raise serializers.ValidationError('Phone already in use !')
        return data

    def create(self,validated_data):
        print(validated_data)
        user = CustomUser.objects.create(first_name =validated_data['first_name'],
                                         last_name = validated_data['last_name'],
                                         username = validated_data['username'],
                                         email=validated_data['email'],
                                         phone_number = validated_data['phone_number'])
        
        user.set_password(validated_data['password'])
        user.save()

        return validated_data


# serializer to set add follwing and followers-
class FollowFollwersSerializer(serializers.Serializer):
    userID = serializers.IntegerField()


# serializer for getching 5 random user's for suggetions--
class GetRandomUsersSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id','username','profile_pic','is_following']

    def get_is_following(self,obj):
        user = self.context['request'].user
        return obj in user.following.all()



# serializer for serializing post data-
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id','contend']


# serializer for getting user profile detailes--
class ProfileDetailSeializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_pic', 'bio', 'created_date', 'is_active', 'is_admin', 'is_verified', 'post_count', 'followers_count', 'following_count', 
                  'posts','is_following','following','followers']

    def get_post_count(self, obj):
        return obj.userPosts.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_is_following(self,obj):
        user = self.context['request'].user
        return obj in user.following.all()
    
    def get_following(self,obj):
        user = self.context['request'].user
        users =user.following.all()
        return UserDetailsSerializer(users,many=True).data
    
    def get_followers(self,obj):
        user = self.context['request'].user
        users =user.followers.all()
        return UserDetailsSerializer(users,many=True).data
    
    def get_posts(self,obj):
        posts= obj.userPosts.filter(is_deleted=False)
        return PostSerializer(posts,many = True).data
    
