from django.db import models
from userside.models import CustomUser,Posts
# Create your models here.


class PostLike(models.Model):
    userID = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='likedpost')
    postID = models.ForeignKey(Posts,on_delete=models.CASCADE,related_name='postlikes')



class Comments(models.Model):
    userID = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='usercomments')
    postID = models.ForeignKey(Posts,on_delete=models.CASCADE,related_name='postcomments')
    comment = models.TextField()
    comment_time = models.TimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='replies')

    def __str__(self):
        return self.comment[:20]
