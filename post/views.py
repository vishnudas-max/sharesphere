from django.shortcuts import render
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import postCreateSeializer, PostsSerializer, PostLikeserializer, CommentSerializer, CommentCreateSerializer, ExploreSerializer, ExploreUserSerializer
from userside.models import Posts, CustomUser
from rest_framework.views import APIView
from .models import PostLike, Comments, PostReports
from django.db.models import Count
from .tasks import send_comment_notification, send_like_notification
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# Create your views here.


class CustomPagination(PageNumberPagination):
    page_size = 4  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaginationForExplore(PageNumberPagination):
    page_size = 6  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaginationForUsers(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

# view for fetching all post,user's posts and deleting post--


class PostsViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    pagination_class = CustomPagination

    def get_serializer(self, *args, **kwargs):
        # Pass 'request.user' to the serializer context
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request_user'] = self.request.user
        return context

    @action(detail=False, methods=['get'], url_path='user-post/(?P<user_id>[^/.]+)')
    def user_posts(self, request, user_id=None):
        posts = Posts.objects.filter(userID=user_id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        query_set = queryset.filter(
            is_deleted=False, userID__is_active=True
        ).annotate(
            likes_count=Count('postlikes')
        ).order_by('-uploadDate', '-updatedDate')

        if user.is_verified == False:
            query_set = query_set.filter(
                Q(userID__in=user.following.all()) | Q(userID=user))

        # annotating counnt of totallikes ussing reverse forignkey relation
        return query_set

    # deleting post-
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# view for creation and updation of posts-
class PostCreateUpdate(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = postCreateSeializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        data = request.data
        obj = Posts.objects.get(id=data['id'])
        print(data)
        serializer = postCreateSeializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'status': False}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# view for liking post -
class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeserializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    # creating a post action to toggle between like and removing like--
    @action(detail=True, methods=['post'], url_path='toggle-like')
    def toggle_like(self, request, pk=None):
        post = Posts.objects.get(pk=pk)
        user = request.user
        try:
            post_like = PostLike.objects.get(postID=post, userID=user)
            post_like.delete()
            return Response({'detail': 'Post like removed'}, status=status.HTTP_204_NO_CONTENT)

        except PostLike.DoesNotExist:
            PostLike.objects.create(postID=post, userID=user)
            if post.userID.id != user.id:
                send_like_notification.delay(user_id=user.id, post_id=post.id)
            return Response({'detail': 'Post liked successfully'}, status=status.HTTP_201_CREATED)


# views for getting user liked posts-
class UserLikedPosts(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        posts = PostLike.objects.filter(userID=user.id).values_list('postID')
        return Response(posts)


class CommentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        data = request.data
        postID = data['postID']
        user = request.user
        post = Posts.objects.get(id=postID)
        serializer = CommentCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # giving notification sending to celery-
            if user.id != post.userID.id:
                send_comment_notification.delay(userID=user.id, postID=postID)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id=None):
        comments = Comments.objects.filter(
            postID=id, parent_comment__isnull=True).order_by('-id')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id=None):
        try:
            comment = Comments.objects.get(id=id)
        except Comments.DoesNotExist:
            return Response({"message": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the author of the comment or has permission to delete
        if comment.userID != request.user:
            return Response({"message": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id=None):
        try:
            comment = Comments.objects.get(id=id)
        except Comments.DoesNotExist:
            return Response({"message": "Comment not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is the author of the comment
        if comment.userID != request.user:
            return Response({"message": "You do not have permission to edit this comment."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = CommentCreateSerializer(comment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# reporting post---
class ReportPost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reported_by = request.user
        report_reason = request.data['report_reason']
        reported_post = request.data['reported_post']
        if PostReports.objects.filter(reported_by=reported_by.id,reported_post=reported_post).exists():
            return Response({'detail': 'You have already reported this Post.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Posts.objects.get(id=reported_post)
            report = PostReports.objects.create(reported_by=reported_by,
                                                reported_post=post,
                                                report_reason=report_reason)
            return Response('Post Reported', status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response('Something Wend wrong', status=status.HTTP_400_BAD_REQUEST)


class ExploreView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Posts.objects.all()
    serializer_class = ExploreSerializer
    pagination_class = PaginationForExplore

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        queryset = queryset.filter(is_deleted=False, userID__is_active=True).annotate(  likes_count=Count('postlikes')).order_by('-likes_count')
        if user.is_verified == False:
            queryset = queryset.filter(Q(userID__in=user.following.all()) | Q(userID=user))
        return queryset


class ExploreUserSearch(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.filter(is_superuser=False).all()
    serializer_class = ExploreUserSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        return queryset
