from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
    path('termdecondition/', include('termdecondition.urls')),
    path('', include('profiles.urls')),
    path('', include('categories.urls')),
    path('goals/', include('goals.urls')),
    path('questions/', include('questions.urls')),
    path('answers/', include('answers.urls')),
]
