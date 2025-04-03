# answers/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AnswerViewSet

router = DefaultRouter()
router.register(r'answers', AnswerViewSet)

urlpatterns = router.urls