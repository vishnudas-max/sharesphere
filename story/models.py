from django.db import models
from userside.models import CustomUser
from django.utils import timezone
from datetime import timedelta
# Create your models here.


class Story(models.Model):
    content = models.ImageField(upload_to='stories/')
    userID = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='userStories')
    upload_time =models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Story by {self.user.username}'

 