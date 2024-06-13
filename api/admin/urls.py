from django.urls import path,include
from adminside import views

from rest_framework.routers import DefaultRouter
from adminside.views import GeUsers

router = DefaultRouter()
router.register(r'users', GeUsers)

urlpatterns = [
    path('user/verification-status/',views.UserVerificatinCount.as_view()),
    path('postperday/',views.PostCountByDay.as_view()),
    path('postuser/overview/',views.getTotalDetailes.as_view()),
    path('', include(router.urls)),
   
]
