# questions/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)

urlpatterns = router.urls