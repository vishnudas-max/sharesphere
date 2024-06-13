from django.shortcuts import render
from rest_framework.views import APIView
from userside.models import CustomUser
from .models import Story
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import StorySerializer, GetStoriesSerializer
from rest_framework import status
from .tasks import delete_story
from django.db.models import Q,Count
# Create your views here.


class addStoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        serializer = StorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            storyID = serializer.data['id']
            delete_story.apply_async((storyID,), countdown=60 * 60)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user

        # Filter following users with active stories and include the user itself
        # filter by checking if the user stories count is greaterthan 0 with active stories
        following_with_stories = user.following.filter(is_active=True).annotate(has_stories=Count('userStories', filter=Q(userStories__is_deleted=False))).filter(has_stories__gt=0)

        # collecting all from the above filtering along with current user--
        all_users = CustomUser.objects.filter(
            Q(id__in=following_with_stories.values_list(
                'id', flat=True)) | Q(id=user.id)
        )



        serializer = GetStoriesSerializer(all_users, many=True)
        return Response(serializer.data)
