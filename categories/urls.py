from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, DomainViewSet, ItemViewSet, create_domain_with_items

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-with-items/', create_domain_with_items, name='create-domain-with-items'),
]
