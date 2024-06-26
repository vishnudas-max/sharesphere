

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routes import websocket_urlpatterns
from notification.routes import websocket_urlpatterns as notification_router
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat.channel_middleware import JwtAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharesphere.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": JwtAuthMiddleware(AuthMiddlewareStack(URLRouter( websocket_urlpatterns + notification_router)))

        
})
