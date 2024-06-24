import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async

User = get_user_model()

class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract the token from the query parameters
        query_string = scope['query_string'].decode()
        query_params = dict(qc.split('=') for qc in query_string.split('&'))
        token = query_params.get('token')

        # Ensure the token is provided
        if token:
            try:
                validated_token = AccessToken(token)
                scope['user'] = await self.get_user(validated_token['user_id'])
            except jwt.ExpiredSignatureError:
                # Token has expired
                scope['user'] = None
            except jwt.InvalidTokenError:
                # Token is invalid
                scope['user'] = None
        else:
            scope['user'] = None

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
