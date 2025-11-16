from django.urls import path
from rest_framework.routers import DefaultRouter
from ProfileItem.views import ProfileItemViewSet, list_peu_items_view

router = DefaultRouter()
router.register(r'items', ProfileItemViewSet, basename='item')

# Add custom URL for items-peu endpoint
urlpatterns = router.urls + [
    path('items-peu/', list_peu_items_view, name='item-list-peu-items'),
]