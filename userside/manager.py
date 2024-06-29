from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, phone_number, username, email=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        email = self.normalize_email(email) if email else None
        user = self.model(phone_number=phone_number, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, username, email, password, **extra_fields)