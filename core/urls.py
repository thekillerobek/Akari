from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from core import settings
from django.conf.urls import handler404 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('manga.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'manga.views.handler404'