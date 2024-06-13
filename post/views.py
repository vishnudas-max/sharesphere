from django.shortcuts import render
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import postCreateSeializer,PostsSerializer,PostLikeserializer,CommentSerializer,CommentCreateSerializer
from userside.models import Posts,CustomUser
from rest_framework.views import APIView
from .models import PostLike,Comments
from django.db.models import Count

# Create your views here.

# view for fetching all post,user's posts and deleting post--
class PostsViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

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
        query_set = queryset.filter(is_deleted=False).annotate(likes_count = Count('postlikes')) #annotating counnt of totallikes ussing reverse forignkey relation
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
    permission_classes =[IsAuthenticated]
    
    def post(self,request):
        data = request.data
        serializer = postCreateSeializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request):
        data = request.data
        obj = Posts.objects.get(id = data['id'])
        serializer = PostsSerializer(obj,data=data,partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':True,'message':'Post Updated'},status=status.HTTP_200_OK)
        return Response({'status':False},serializer.errors,status=status.HTTP_400_BAD_REQUEST)


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
            return Response({'detail': 'Post liked successfully'}, status=status.HTTP_201_CREATED)



# views for getting user liked posts-  
class UserLikedPosts(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
            user = request.user
            posts = PostLike.objects.filter(userID=user.id).values_list('postID')
            return Response(posts)
        


class CommentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self,request,id=None):
        data = request.data
        serializer = CommentCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, id=None):
        comments = Comments.objects.filter(postID=id, parent_comment__isnull=True).order_by('-id')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)