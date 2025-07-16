from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Strategy
from .serializers import StrategySerializer
from profiles.models import Profile, SharedProfilePermission
from authentification.models import CustomUser

from .permissions import IsAuthenticatedAndProfileRelated, IsStrategyAuthor

class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedAndProfileRelated, IsStrategyAuthor]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Strategy.objects.none()

        owned_profile_ids = []

        shared_profile_ids = SharedProfilePermission.objects.filter(
            shared_with=user
        ).values_list('profile__id', flat=True)

        allowed_profile_ids = list(set(list(owned_profile_ids) + list(shared_profile_ids)))

        queryset = Strategy.objects.filter(profile__id__in=allowed_profile_ids)
        profile_id_param = self.request.query_params.get('profile_id', None)
        if profile_id_param is not None:
            try:
                profile_id = int(profile_id_param)
                if profile_id in allowed_profile_ids:
                    queryset = queryset.filter(profile__id=profile_id)
                else:
                    return Strategy.objects.none()
            except ValueError:
                return Strategy.objects.none()

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required to create a strategy."})

        profile_id = self.request.data.get('profile')
        if not profile_id:
            raise serializers.ValidationError({"profile": "Profile ID is required for a new strategy."})

        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"profile": "Profile not found."})

        has_edit_permission_on_profile = SharedProfilePermission.objects.filter(
            profile=profile,
            shared_with=user,
            permissions='edit'
        ).exists()

        if not has_edit_permission_on_profile:
            raise serializers.ValidationError({"detail": "You do not have permission to add strategies to this profile."})

        serializer.save(author=user, profile=profile)