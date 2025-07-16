from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Goal, SubObjective
from .serializers import GoalSerializer, SubObjectiveSerializer
from profiles.models import Profile, SharedProfilePermission
from rest_framework import serializers

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

        serializer.save(profile=profile)

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