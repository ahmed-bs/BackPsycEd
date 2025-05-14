from rest_framework.routers import DefaultRouter
from ProfileCategory.views import ProfileCategoryViewSet
router = DefaultRouter()
router.register(r'categories', ProfileCategoryViewSet , basename='category')

urlpatterns = router.urls