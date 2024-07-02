from django.urls import path,include
from adminside import views

from rest_framework.routers import DefaultRouter
from adminside.views import GeUsers,GetPosts

router = DefaultRouter()
router.register(r'users', GeUsers)
router.register(r'posts', GetPosts)

urlpatterns = [
    path('user/verification-status/',views.UserVerificatinCount.as_view()),
    path('postperday/',views.PostCountByDay.as_view()),
    path('postuser/overview/',views.getTotalDetailes.as_view()),
    path('', include(router.urls)),
    path('user/reports/<int:id>/',views.GerUserReports.as_view()),
    path('post/reports/<int:id>/',views.GetPostReprts.as_view())

]
