from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet

# Create a router and register the GoalViewSet
router = DefaultRouter()
router.register(r'goals', GoalViewSet)

# URL patterns
urlpatterns = [
    path('', include(router.urls)),  # Automatically includes all CRUD operations for goals
]
