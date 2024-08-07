
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('api.user.urls')),
    path('api/admin/',include('api.admin.urls')),
    path('api/chat/',include('api.chatapi.urls')),
    path('api/razorpay/',include('api.razorpay.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)