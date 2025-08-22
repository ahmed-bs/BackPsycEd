from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Strategy
from .serializers import StrategySerializer
from profiles.models import Profile, SharedProfilePermission
from authentification.models import CustomUser

from .permissions import IsAuthenticatedAndProfileRelated, IsStrategyAuthor
from .translation_utils import translation_service

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

        # Get the validated data
        validated_data = serializer.validated_data
        
        # Prepare strategy data with translation
        strategy_data = {
            'title': validated_data.get('title', '').strip(),
            'title_ar': validated_data.get('title_ar', '').strip(),
            'description': validated_data.get('description', '').strip(),
            'description_ar': validated_data.get('description_ar', '').strip(),
        }

        # Apply automatic translation for title and description
        fields_to_translate = ['title', 'description']
        strategy_data = translation_service.auto_translate_fields(strategy_data, fields_to_translate)

        # Save the strategy with translated data
        strategy = serializer.save(
            author=user, 
            profile=profile,
            title=strategy_data['title'],
            title_ar=strategy_data['title_ar'],
            description=strategy_data['description'],
            description_ar=strategy_data['description_ar']
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        
        # Get the validated data
        validated_data = serializer.validated_data
        
        # Prepare update data
        update_data = {}
        if 'title' in validated_data:
            update_data['title'] = validated_data['title'].strip()
        if 'title_ar' in validated_data:
            update_data['title_ar'] = validated_data['title_ar'].strip()
        if 'description' in validated_data:
            update_data['description'] = validated_data['description'].strip()
        if 'description_ar' in validated_data:
            update_data['description_ar'] = validated_data['description_ar'].strip()

        # Apply automatic translation for updated fields
        fields_to_translate = []
        if 'title' in update_data or 'title_ar' in update_data:
            fields_to_translate.append('title')
        if 'description' in update_data or 'description_ar' in update_data:
            fields_to_translate.append('description')

        if fields_to_translate:
            # Get current values and merge with updates
            current_data = {
                'title': instance.title,
                'title_ar': instance.title_ar or '',
                'description': instance.description,
                'description_ar': instance.description_ar or '',
            }
            current_data.update(update_data)
            
            # Apply translation
            translated_data = translation_service.auto_translate_fields(current_data, fields_to_translate)
            
            # Update instance with translated data
            for field in fields_to_translate:
                setattr(instance, field, translated_data[field])
                setattr(instance, f"{field}_ar", translated_data[f"{field}_ar"])

        serializer.save()