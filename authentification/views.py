from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
CustomUser = get_user_model()
from .serializers import *
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission personnalisée :
    - Accès complet pour les admins
    - Les utilisateurs normaux ne peuvent accéder qu'à leur propre profil
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user

class UserListCreateView(generics.ListCreateAPIView):
    """Endpoint pour :
    - GET : Liste tous les utilisateurs (admin seulement)
    - POST : Création d'un nouvel utilisateur"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Seulement pour les admins

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Seuls les administrateurs peuvent créer des utilisateurs")
        serializer.save()

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint pour :
    - GET : Détails d'un utilisateur
    - PATCH : Mise à jour partielle
    - PUT : Mise à jour complète
    - DELETE : Suppression"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_object(self):
        user = super().get_object()
        if not (self.request.user.is_staff or user == self.request.user):
            raise PermissionDenied("Vous n'avez pas la permission d'accéder à ce profil")
        return user

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Seuls les administrateurs peuvent supprimer des comptes")
        instance.delete()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        request.data.setdefault('bio', None)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    # Either remove lookup_field (default is 'pk') or set it to 'id':
    lookup_field = 'pk'  # This matches your URL pattern

    def get_object(self):
        user = super().get_object()
        # Ensure users can only update their own profile unless admin
        if not (self.request.user.is_staff or self.request.user == user):
            raise permissions.PermissionDenied("You can only update your own profile")
        return user



@api_view(['POST'])
@permission_classes([AllowAny])  # Décorateur correctement placé
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        })
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]  # Ensure token authentication is enforced
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "Logged out successfully"}, status=200)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)
        
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Update current user's profile"""
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True  # Allows partial updates
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class VerifyOldPasswordView(APIView):
    """
    POST /api/auth/verify-old-password/
    {
        "username": "rabeb",
        "old_password": "ancienMotDePasse"
    }
    """

    def post(self, request):
        username = request.data.get('username')
        old_password = request.data.get('old_password')

        if not username or not old_password:
            return Response(
                {"error": "Username et ancien mot de passe requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)

            if user.check_password(old_password):
                # Si l'ancien mot de passe est correct
                return Response({
                    "verified": True,
                    "message": "Ancien mot de passe correct"
                })
            else:
                return Response({
                    "verified": False,
                    "message": "Ancien mot de passe incorrect"
                }, status=status.HTTP_403_FORBIDDEN)

        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )


class PasswordResetWithOldPasswordView(APIView):
    """
    POST /api/auth/password-reset-with-old/
    {
        "username": "rabeb",
        "old_password": "ancienMotDePasse",
        "new_password": "nouveauMotDePasse"
    }
    """

    def post(self, request):
        username = request.data.get('username')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        # Validation basique
        if not all([username, old_password, new_password]):
            return Response(
                {"error": "Tous les champs sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)

            # Vérification ancien mot de passe
            if not user.check_password(old_password):
                return Response({
                    "error": "Ancien mot de passe incorrect",
                    "security_question": user.security_question
                }, status=status.HTTP_403_FORBIDDEN)

            # Changement du mot de passe
            user.set_password(new_password)
            user.save()

            return Response({
                "success": True,
                "message": "Mot de passe mis à jour avec succès"
            })

        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
