from django.urls import path,include
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserInfoView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    VerifyOldPasswordView,
    PasswordResetWithOldPasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserInfoView.as_view(), name='user-info'),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    path('verify-old-password/', VerifyOldPasswordView.as_view()),
    path('password-reset-with-old/', PasswordResetWithOldPasswordView.as_view()),
]
