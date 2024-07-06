from django.urls import path
from .consumers import FollowConsumer 
websocket_urlpatterns=[
    path('ws/follow/',FollowConsumer.as_asgi())
]