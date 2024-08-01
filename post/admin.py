from django.contrib import admin
from .models import PostLike,Comments,PostReports
# Register your models here.

admin.site.register(PostLike)
admin.site.register(Comments)
admin.site.register(PostReports)