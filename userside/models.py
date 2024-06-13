
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils import timezone
from .manager import CustomUserManager

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to='profilepics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    following = models.ManyToManyField('self', symmetrical=False, related_name='user_followers', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='user_followwing', blank=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','password']

    def __str__(self):
        return self.username
    
   
class Regotp(models.Model):
    email = models.EmailField(null=False,unique=True)
    secret = models.CharField(max_length=200,null=False)
    user_data = models.JSONField()
    otp_time = models.DateTimeField(null=True)

    def save(self,*args, **kwargs):
        self.otp_time = timezone.now()
        super(Regotp, self).save(*args, **kwargs)

class Posts(models.Model):
    userID = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='userPosts')
    caption = models.TextField(null=False)
    contend = models.ImageField(upload_to='postImages/')
    uploadDate = models.DateTimeField(auto_now_add=True,null=True)
    updatedDate = models.DateTimeField(auto_now=True,null=True)
    is_deleted = models.BooleanField(default= False)


