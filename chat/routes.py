from django.urls import path
from .consumers import ChatConsumer,CallConsumer
websocket_urlpatterns=[
    path('ws/chat/<int:id>/',ChatConsumer.as_asgi()),
    path('ws/call/',CallConsumer.as_asgi())
]