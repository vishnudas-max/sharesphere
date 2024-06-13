from django.urls import path,include
from  chat import views as chat

urlpatterns = [
    path('users/',chat.GetUsers.as_view()),
    
]
