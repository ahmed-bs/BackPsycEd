from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
    path('termdecondition/', include('termdecondition.urls')),
    path('', include('profiles.urls')),
]
