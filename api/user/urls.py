from django.urls import path,include
from userside import views as user
from post import views as post
from story import views as story
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from post.views import PostsViewSet,PostLikeViewSet

router = DefaultRouter()
router.register(r'posts', PostsViewSet)
router.register(r'postlike', PostLikeViewSet)

urlpatterns = [
    path('register/',user.RegisterView.as_view(),name='register'),
    path('register/confirm/',user.RegisterConfirm.as_view()),
    path('register/resendotp/',user.ResendOtpView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('post/',post.PostCreateUpdate.as_view()),
    path('get/user/liked/posts/',post.UserLikedPosts.as_view()),
    path('post/comment/<int:id>/',post.CommentView.as_view()),
    path('follow/<str:username>',user.FollowAndFollowingView.as_view()),
    path('suggested/users/',user.getRandomUser.as_view()),
    path('user/profile/detailes/<int:id>/',user.GetUserProfile.as_view()),
    path('user/story/',story.addStoryView.as_view())
]
