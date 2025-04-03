from django.urls import path
from .views import TermdeConditionListCreateView, TermdeConditionDetailView

urlpatterns = [
    path('terms/', TermdeConditionListCreateView.as_view(), name='terms-list-create'),
    path('terms/<int:pk>/', TermdeConditionDetailView.as_view(), name='terms-detail'),
]
