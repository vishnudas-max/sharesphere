from django.db import models
from userside.models import CustomUser
import pytz
# Create your models here.

class Room(models.Model):
    users = models.ManyToManyField(CustomUser, blank=True, related_name='chatRooms')

    @property
    def last_message(self):
        last_chat = self.chats.order_by('-message_time').first()
        return last_chat.message if last_chat else None

    @property
    def last_message_time(self):
        last_chat = self.chats.order_by('-message_time').first()
        return last_chat.formatted_message_time if last_chat else None

    def __str__(self):
        return f"Room with users: {', '.join(user.username for user in self.users.all())}"

class Chat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='userChats')
    message = models.TextField()
    image = models.ImageField(upload_to='chatImages/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    message_time = models.DateTimeField(auto_now_add=True)

    @property
    def formatted_message_time(self):
        india_tz = pytz.timezone('Asia/Kolkata')
        local_time = self.message_time.astimezone(india_tz)
        return local_time.strftime('%I:%M %p')

    def __str__(self):
        return f"Message from {self.sender.username} in {self.room.id}"

# class OnlinStatus(models.Model):
#     userID = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='onlineUsers')
#     is_Online = models.BooleanField(default=False)

