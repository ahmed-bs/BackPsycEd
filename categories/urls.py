# Exemple dans categories/urls.py
from django.urls import path
from .views import (
    DefaultCategoryListView,
    DefaultCategoryDetailView,
    CopyCategoryToUserView,
    UserCategoryDetailView,
    AllDefaultCategoriesView,
    UpdateUserCategoryView,
    ListDefaultCategoriesView
)

urlpatterns = [
    path('categories/standards/', ListDefaultCategoriesView.as_view(), name='list-default-categories'),
    path('categories/update-copy/', UpdateUserCategoryView.as_view(), name='update-user-category'),
    path('categories/', AllDefaultCategoriesView.as_view(), name='all-default-categories'),
    path('categories/<int:profile_id>/', DefaultCategoryListView.as_view()),
    path('categories/view/<int:category_id>/', DefaultCategoryDetailView.as_view()),
    path('categories/copy/', CopyCategoryToUserView.as_view()),
    path('profiles/<int:profile_id>/category/', UserCategoryDetailView.as_view()),
 

]
