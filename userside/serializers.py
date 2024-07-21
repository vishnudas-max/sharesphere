from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Posts,UserReports,Verification
from post.serializers import UserDetailsSerializer
from rest_framework_simplejwt.tokens import RefreshToken ,TokenError



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh['is_admin'] = user.is_superuser
    refresh['username'] = user.username


    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# # class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
# #     @classmethod
# #     def get_token(cls, user):
# #         token = super().get_token(user)

# #         token['username'] = user.username
# #         token['is_admin'] = user.is_superuser
 
# #         return token


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
    post_count = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
    posts = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)
    following = serializers.SerializerMethodField(read_only=True)
    followers = serializers.SerializerMethodField(read_only=True)
    is_currentUser_verified = serializers.SerializerMethodField(read_only =True)
    

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_pic', 'bio', 'created_date', 'is_active', 'is_admin', 'is_verified', 'post_count', 'followers_count', 'following_count', 
                  'posts','is_following','following','followers','is_currentUser_verified']
      
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
    
    def get_is_currentUser_verified(self,obj):
        user = self.context['request'].user
        return user.is_verified
    

class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReports
        fields = ['reported_by','reported_user','report_reason']




class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs['refresh']

        try:
            # Decode the refresh token
            refresh_token = RefreshToken(refresh)
            data = {'refresh': str(refresh), 'access': str(refresh_token.access_token)}
            user_id = refresh_token.payload.get('user_id')
            
            # Fetch user from database
            user = CustomUser.objects.get(id=user_id)

            if not user.is_active:
                raise serializers.ValidationError('User account is not active.')

            return data

        except TokenError as e:
            raise serializers.ValidationError(str(e))


class RequestVerificationSeializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['userID','document']


class VerficationSerializer(serializers.ModelSerializer):
    class Meta:
        model =Verification
        fields = '__all__'
        exlude = ['userID','docuement']

class GetverificationDetailes(serializers.ModelSerializer):
    is_requested=serializers.SerializerMethodField(read_only=True)
    verification_detailes = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = CustomUser
        fields =['id','username','profile_pic','is_requested','verification_detailes','is_verified']

    def get_is_requested(self,obj):
        if Verification.objects.filter(userID=obj.id).exists():
            return True
        else:
            return False
        
    def get_verification_detailes(self,obj):
       try:
           verification_obj = obj.verificationData
           return VerficationSerializer(verification_obj).data
       except:
           return None



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields =['id','username','profile_pic']