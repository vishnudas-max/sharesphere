from django.db import models
from django.contrib.auth import get_user_model
from userside.models import  Posts
# Create your models here.

User = get_user_model()

class Notification(models.Model):
   
    invoked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoked_notifications')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_notifications')
    postID = models.ForeignKey(Posts,on_delete= models.CASCADE,related_name='postrelated_notifications',null=True,blank=True)
    notification_type = models.CharField(max_length=50)
    time_triggered = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_notification_type_display()} from {self.invoked_user.username} to {self.target_user.username}"
    @property
    def notfication_date(self):
        date_str = self.time_triggered.strftime('%m/%d/%Y')
        return date_str
    @property
    def notfication_time(self):
        date_str = self.time_triggered.strftime('%m-%d-%Y')
        return date_str