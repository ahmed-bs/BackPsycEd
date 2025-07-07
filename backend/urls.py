from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
    path('termdecondition/', include('termdecondition.urls')),
    path('category/', include('ProfileCategory.urls')),
    path('items/', include('ProfileItem.urls')),
    path('domains/', include('ProfileDomain.urls')),
    path('', include('profiles.urls')),

     # --- NEW PATH FOR GOALS ---
    path('', include('goals.urls')),
    
    # --- NEW PATH FOR NOTES ---
    path('', include('notes.urls'))
]
