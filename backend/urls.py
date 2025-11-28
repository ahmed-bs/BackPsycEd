from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API routes with /api/ prefix
    path('api/authentification/', include('authentification.urls')),
    path('api/termdecondition/', include('termdecondition.urls')),
    path('api/category/', include('ProfileCategory.urls')),
    path('api/items/', include('ProfileItem.urls')),
    path('api/domains/', include('ProfileDomain.urls')),
    path('api/', include('profiles.urls')),
    path('api/', include('goals.urls')),
    path('api/', include('notes.urls')),
    path('api/', include('strategies.urls')),
    # Legacy routes without /api/ prefix (for backward compatibility)
    path('authentification/', include('authentification.urls')),
    path('termdecondition/', include('termdecondition.urls')),
    path('category/', include('ProfileCategory.urls')),
    path('items/', include('ProfileItem.urls')),
    path('domains/', include('ProfileDomain.urls')),
    path('', include('profiles.urls')),
    path('', include('goals.urls')),
    path('', include('notes.urls')),
    path('', include('strategies.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
