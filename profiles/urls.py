from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ShareChildProfileView, CreateChildProfileView , ProfilesByParentView

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profiles')  # crée /profiles/

urlpatterns = [
    # 🌱 CRUD des profils avec ViewSet
    path('', include(router.urls)),
    path('profiles/by-parent/<int:parent_id>/', ProfilesByParentView.as_view(), name='profiles-by-parent'),
    path('my-children/', ProfileViewSet.as_view({'get': 'list_children'}), name='list-children'),
    # 👶 Création des enfants depuis un parent connecté
    path('create-children/', CreateChildProfileView.as_view(), name='create-children'),

    # 📤 POST : Partager un profil enfant (Parent X → Parent Y)
    path('share-profile/<int:child_profile_id>/', ShareChildProfileView.as_view(), name='share-child-profile'),

    # 👁️ GET : Lire un profil partagé
    path('shared-child-profile/<int:profile_id>/', ShareChildProfileView.as_view(), name='get-child-profile'),

    # ✏️ PUT : Mettre à jour un profil partagé (si autorisé)
    path('shared-child-profile/<int:profile_id>/update/', ShareChildProfileView.as_view(), name='update-child-profile'),

    # ❌ DELETE : Supprimer un partage de profil (si autorisé)
    path('share-profile/<int:share_id>/delete/', ShareChildProfileView.as_view(), name='delete-share'),
]
