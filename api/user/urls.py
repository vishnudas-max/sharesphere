from django.urls import path,include
from userside import views as user
from post import views as post
from story import views as story
from googleauth import views as google
from notification import views as notification
from chat import views as chat

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from post.views import PostsViewSet,PostLikeViewSet,ExploreView,ExploreUserSearch

router = DefaultRouter()
router.register(r'posts', PostsViewSet,basename='posts')
router.register(r'postlike', PostLikeViewSet,basename='postlike')
router.register(r'explore', ExploreView,basename='explore')
router.register(r'exploreusers',ExploreUserSearch,basename='exploreusers')

urlpatterns = [
    path('register/',user.RegisterView.as_view(),name='register'),
    path('login/',user.LoginView.as_view(),name='register'),
    path('register/confirm/',user.RegisterConfirm.as_view()),
    path('register/resendotp/',user.ResendOtpView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', user.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('post/',post.PostCreateUpdate.as_view()),
    path('get/user/liked/posts/',post.UserLikedPosts.as_view()),
    path('post/comment/<int:id>/',post.CommentView.as_view()),
    path('follow/<str:username>',user.FollowAndFollowingView.as_view()),
    path('suggested/users/',user.getRandomUser.as_view()),
    path('user/profile/detailes/<int:id>/',user.GetUserProfile.as_view()),
    path('user/story/',story.addStoryView.as_view()),
    path('auth/login/google/',google.GoogleLoginApi.as_view()),
    path('report/',user.Reportuser.as_view()),
    path('report/post/',post.ReportPost.as_view()),
    path('add/user/tostory/view/<int:storyID>/',story.AddViewers.as_view()),
    path('user/notifications/',notification.UserNotificationsView.as_view()),
    path('get/all/chats/<int:roomID>/',chat.GetrommChats.as_view()),
    path('user/account/sercurity/',user.ChangePassword.as_view()),
    path('verify/account/',user.RequestVerification.as_view()),
    path('forgot/password/verification/',user.ForgotPassword.as_view()),
    path('forgot/password/verification/otp/',user.VerifyOtp_for_ForgotPassword.as_view()),
    path('forgot/password/verification/otp/resend/',user.ForgotPasswordResendOtpView.as_view()),
    path('block/user/',user.BlockUserView.as_view())

]
