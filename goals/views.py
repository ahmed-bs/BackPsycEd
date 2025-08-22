from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Goal, SubObjective
from .serializers import GoalSerializer, SubObjectiveSerializer
from profiles.models import Profile, SharedProfilePermission
from rest_framework import serializers
from .translation_utils import translation_service

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Goal.objects.all().prefetch_related('sub_objectives', 'profile')

        if user.is_superuser:
            return queryset
        
        profile_id_param = self.request.query_params.get('profile_id')

        if profile_id_param:
            try:
                requested_profile_id = int(profile_id_param)
            except ValueError:
                return Goal.objects.none()
            
            has_permission = SharedProfilePermission.objects.filter(
                profile__id=requested_profile_id,
                shared_with=user,
                permissions__in=['view', 'edit', 'share', 'delete']
            ).exists()

            if has_permission:
                queryset = queryset.filter(profile__id=requested_profile_id)
            else:
                return Goal.objects.none() 
        else:
            accessible_profile_ids = SharedProfilePermission.objects.filter(
                shared_with=user, 
                permissions__in=['view', 'edit', 'share', 'delete']
            ).values_list('profile__id', flat=True)
            
            queryset = queryset.filter(profile__id__in=accessible_profile_ids)
            
        return queryset.distinct()

    def perform_create(self, serializer):
        profile_id = self.request.data.get('profile_id')
        if not profile_id:
            raise serializers.ValidationError({"profile_id": "This field is required to create a goal."})
        
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"profile_id": "Profile not found."})

        if not self.request.user.is_superuser:
            has_edit_permission = SharedProfilePermission.objects.filter(
                profile=profile,
                shared_with=self.request.user,
                permissions='edit'
            ).exists()
            if not has_edit_permission:
                raise permissions.PermissionDenied("You do not have permission to add goals to this profile.")

        # Get the validated data
        validated_data = serializer.validated_data
        
        # Prepare goal data with translation
        goal_data = {
            'title': validated_data.get('title', '').strip(),
            'title_ar': validated_data.get('title_ar', '').strip(),
            'description': validated_data.get('description', '').strip(),
            'description_ar': validated_data.get('description_ar', '').strip(),
        }

        # Apply automatic translation for title and description
        fields_to_translate = ['title', 'description']
        goal_data = translation_service.auto_translate_fields(goal_data, fields_to_translate)

        # Save the goal with translated data
        goal = serializer.save(
            profile=profile,
            title=goal_data['title'],
            title_ar=goal_data['title_ar'],
            description=goal_data['description'],
            description_ar=goal_data['description_ar']
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if not self.request.user.is_superuser:
            has_edit_permission = SharedProfilePermission.objects.filter(
                profile=instance.profile,
                shared_with=self.request.user,
                permissions='edit'
            ).exists()
            if not has_edit_permission:
                raise permissions.PermissionDenied("You do not have permission to edit goals for this profile.")
        
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

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            has_delete_permission = SharedProfilePermission.objects.filter(
                profile=instance.profile,
                shared_with=self.request.user,
                permissions='delete'
            ).exists()
            if not has_delete_permission:
                raise permissions.PermissionDenied("You do not have permission to delete goals for this profile.")
        instance.delete()