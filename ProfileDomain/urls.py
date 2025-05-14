from rest_framework.routers import DefaultRouter
from ProfileDomain.views import ProfileDomainViewSet
router = DefaultRouter()
router.register(r'domains', ProfileDomainViewSet , basename='domain')

urlpatterns = router.urls