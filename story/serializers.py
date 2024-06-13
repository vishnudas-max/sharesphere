from rest_framework import serializers
from .models import Story
from userside.models import CustomUser


class StorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Story
        fields = ['id', 'content', 'userID', 'is_deleted']

class GetStoriesSerializer(serializers.ModelSerializer):
    # stories = StorySerializer(source='userStories', many=True, read_only=True)
    stories = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_pic', 'stories']

    def get_stories(self,obj):
        stories= obj.userStories.filter(is_deleted=False)
        return StorySerializer(stories,many=True).data