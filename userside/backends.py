from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

class PhoneOrUsernameBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            return None

        # Check if username is a valid phone number
        if User.objects.filter(phone_number=username).exists():
            user = User.objects.get(phone_number=username)
        else:
            # Check if username is a valid username
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                return None

        # Verify the password
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
