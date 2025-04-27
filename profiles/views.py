from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import uuid

from .models import Profile, ProfileShare
from .serializers import ProfileSerializer, ProfileShareSerializer

CustomUser = get_user_model()


def parse_bool(value):
    return str(value).lower() in ['true', '1', 'yes']


from rest_framework.decorators import action

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # For regular profile creation
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Profile.objects.all().select_related('parent')

        if user.is_parent():
            # Parent ne voit que ses propres enfants
            return queryset.filter(parent=user)

        # Admin voit tous les profils enfants (ceux avec un parent)
        return queryset.filter(parent__isnull=False)

    @action(detail=False, methods=['get'], url_path='by-parent/(?P<parent_id>\d+)')
    def profiles_by_parent(self, request, parent_id=None):
        """
        Retrieve all profiles associated with a specific parent ID.
        """
        # Check if the requester is authorized (e.g., admin or the parent themselves)
        if not request.user.is_staff and str(request.user.id) != parent_id:
            return Response(
                {"error": "You are not authorized to view these profiles"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            parent = CustomUser.objects.get(id=parent_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Parent not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        profiles = Profile.objects.filter(parent=parent)
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# class ProfileViewSet(viewsets.ModelViewSet):
    # queryset = Profile.objects.all()
    # serializer_class = ProfileSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

 

    # @action(detail=False, methods=['get'], url_path='my-children')
    # def my_children(self, request):
    #     """
    #     Endpoint spécial pour Postman - Liste des enfants du parent connecté
    #     """
    #     if not request.user.is_parent():
    #         return Response(
    #             {"error": "Seuls les parents peuvent accéder à cette liste"},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

    #     children = Profile.objects.filter(parent=request.user)
    #     serializer = self.get_serializer(children, many=True)
    #     return Response(serializer.data)

    # @action(detail=False, methods=['get'], url_path='my-children')
    # def list_children(self, request):
    #     """
    #     List all child profiles for the authenticated parent
    #     """
    #     # Verify user is a parent
    #     if request.user.user_type != CustomUser.PARENT:
    #         return Response(
    #             {'error': 'Only parent users can access this endpoint.'},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

    #     children = self.get_queryset()
    #     serializer = self.get_serializer(children, many=True)
    #     return Response(serializer.data)




class ShareChildProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def has_permission_or_group(self, user, perm_codename=None, group_name=None):
        if perm_codename and user.has_perm(f"yourappname.{perm_codename}"):
            return True
        if group_name and user.groups.filter(name=group_name).exists():
            return True
        return False

    def get_child_profile(self, profile_id):
        try:
            return Profile.objects.get(id=profile_id, is_parent=False)
        except Profile.DoesNotExist:
            return None

    def get_profile_share(self, share_id):
        try:
            return ProfileShare.objects.get(id=share_id)
        except ProfileShare.DoesNotExist:
            return None

    def get(self, request, child_profile_id):
        requester_profile = Profile.objects.filter(user=request.user).first()
        child_profile = self.get_child_profile(child_profile_id)

        if not child_profile:
            return Response({'error': 'Profil non trouvé.'}, status=404)

        if child_profile.parent == requester_profile:
            serializer = ProfileSerializer(child_profile)
            return Response(serializer.data)

        try:
            share = ProfileShare.objects.get(profile=child_profile, shared_with=requester_profile)
            if not share.can_read:
                return Response({'error': 'Vous n\'avez pas la permission de lecture.'}, status=403)
        except ProfileShare.DoesNotExist:
            return Response({'error': 'Profil non partagé avec vous.'}, status=403)

        serializer = ProfileSerializer(child_profile)
        return Response(serializer.data)

    class ShareChildProfileView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def post(self, request, child_profile_id):

            try:
                # Vérifier que l'enfant existe et appartient au parent connecté
                child_profile = Profile.objects.get(
                    id=child_profile_id,
                    parent=request.user  # Seul le parent propriétaire peut partager
                )
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profil enfant non trouvé ou non autorisé'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Vérifier le parent avec qui partager
            shared_with_parent_id = request.data.get('shared_with_parent_id')
            if not shared_with_parent_id:
                return Response(
                    {'error': 'ID du parent destinataire requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                shared_with_parent = CustomUser.objects.get(
                    id=shared_with_parent_id,
                    user_type=CustomUser.PARENT  # Vérifier que c'est bien un parent
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': 'Parent destinataire non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Vérifier que le partage n'existe pas déjà
            if ProfileShare.objects.filter(
                    profile=child_profile,
                    shared_with__parent=shared_with_parent
            ).exists():
                return Response(
                    {'error': 'Ce profil est déjà partagé avec ce parent'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Trouver le profil du parent destinataire
            try:
                shared_with_profile = Profile.objects.get(parent=shared_with_parent)
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profil du parent destinataire non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Créer le partage
            profile_share = ProfileShare.objects.create(
                profile=child_profile,
                shared_with=shared_with_profile,
                can_read=request.data.get('can_read', False),
                can_write=request.data.get('can_write', False),
                can_update=request.data.get('can_update', False),
                can_delete=request.data.get('can_delete', False)
            )

            serializer = ProfileShareSerializer(profile_share)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    def put(self, request, profile_id):
        # Récupérer le profil enfant
        profile = self.get_child_profile(profile_id)
        if not profile:
            return Response({'error': 'Profil non trouvé.'}, status=404)

        #  Récupérer le profil du demandeur (parent connecté)
        requester_profile = Profile.objects.filter(user=request.user).first()

        #  Cas 1 : Le parent direct du profil
        if profile.parent == requester_profile:
            pass  # autorisé

        #  Cas 2 : Profil partagé → vérifier can_write
        else:
            try:
                share = ProfileShare.objects.get(profile=profile, shared_with=requester_profile)
                if not share.can_write:
                    return Response({'error': "Vous n'avez pas la permission d'écriture."}, status=403)
            except ProfileShare.DoesNotExist:
                return Response({'error': 'Profil non partagé avec vous.'}, status=403)

        # 🛠️ Mise à jour autorisée
        profile.name = request.data.get('name', profile.name)
        profile.age = request.data.get('age', profile.age)
        profile.save()

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=200)

    def delete(self, request, share_id):
        profile_share = self.get_profile_share(share_id)

        if not self.has_permission_or_group(request.user, perm_codename='can_delete_shared_profile',
                                            group_name='can_delete_profiles'):
            return Response({'error': 'Permission refusée pour supprimer ce partage.'}, status=403)

        profile_share.delete()
        return Response({'message': 'Profile share deleted successfully.'}, status=204)


class CreateChildProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a child profile with proper parent assignment
        """
        try:
            if not request.user.is_parent():
                return Response(
                    {'error': 'Only parent users can create child profiles'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Ensure required fields are present
            required_fields = ['first_name', 'last_name', 'birth_date']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields: {", ".join(required_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the child profile with parent relationship
            child_profile = Profile.objects.create(
                parent=request.user,  # This ensures parent_id is set
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                birth_date=request.data['birth_date'],
                diagnosis=request.data.get('diagnosis', ''),
                notes=request.data.get('notes', ''),
                is_active=True
            )

            serializer = ProfileSerializer(child_profile)
            return Response(
                {
                    'message': 'Child profile created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ProfilesByParentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, parent_id):
        """
        Retrieve all profiles associated with a specific parent ID.
        """
        # Check if the requester is authorized (e.g., admin or the parent themselves)
        if not request.user.is_staff and str(request.user.id) != parent_id:
            return Response(
                {"error": "You are not authorized to view these profiles"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            parent = CustomUser.objects.get(id=parent_id, user_type=CustomUser.PARENT)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Parent not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        profiles = Profile.objects.filter(parent=parent)
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)