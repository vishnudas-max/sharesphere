from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Notification(models.Model):
   
    invoked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoked_notifications')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_notifications')
    notification_type = models.CharField(max_length=50)
    time_triggered = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    is_send = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_notification_type_display()} from {self.invoked_user.username} to {self.target_user.username}"