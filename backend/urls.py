from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
    path('termdecondition/', include('termdecondition.urls')),
    path('category/', include('ProfileCategory.urls')),
    path('items/', include('ProfileItem.urls')),
    path('domains/', include('ProfileDomain.urls')),
    path('', include('profiles.urls')),
    path('', include('goals.urls')),
    path('', include('notes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
