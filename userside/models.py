
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .manager import CustomUserManager
from django.core.validators import RegexValidator


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits and contain no letters or special characters."
            )
        ]
    )
    profile_pic = models.ImageField(
        upload_to='profilepics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='user_followers', blank=True)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='user_followwing', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email', 'password']

    def __str__(self):
        return self.username


class Regotp(models.Model):
    email = models.EmailField(null=False, unique=True)
    secret = models.CharField(max_length=200, null=False)
    user_data = models.JSONField()
    otp_time = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.otp_time = timezone.now()
        super(Regotp, self).save(*args, **kwargs)


class Meta:
    constraints = [
        models.UniqueConstraint(
            name='unique_nonnull_field',
            fields=['unique_field'],
            condition=models.Q(unique_field__isnull=False),
        )
    ]


class Posts(models.Model):
    userID = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='userPosts')
    caption = models.TextField(null=False)
    contend = models.ImageField(upload_to='postImages/')
    uploadDate = models.DateTimeField(auto_now_add=True, null=True)
    updatedDate = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def formatted_uploadDate(self):
        if self.uploadDate:
            return self.uploadDate.strftime('%Y-%m-%d %H:%M:%S')
        return None


class UserReports(models.Model):
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reported_users')
    reported_user = models.ForeignKey( CustomUser, on_delete=models.CASCADE, related_name='allreports')
    report_reason = models.TextField(null=False)
    action_took = models.BooleanField(default=False)
    reported_time = models.DateTimeField(auto_now_add=True)



class Verification(models.Model):


    userID = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='verificationData')
    document = models.ImageField(upload_to='verificationDocs/')
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    plan_choosed = models.CharField(max_length=50,null=True,blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    subscribed_date = models.DateTimeField(null=True, blank=True)
    requested_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.userID.username} - {self.plan_choosed}"