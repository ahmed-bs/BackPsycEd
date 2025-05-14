from rest_framework.routers import DefaultRouter
from  ProfileItem.views import ProfileItemViewSet
router = DefaultRouter()
router.register(r'items', ProfileItemViewSet , basename='item')

urlpatterns = router.urls