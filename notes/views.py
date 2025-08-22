from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer
from django.shortcuts import get_object_or_404
import datetime
from profiles.models import Profile, SharedProfilePermission
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .translation_utils import translation_service

User = get_user_model()

class IsProfilePermitted(permissions.BasePermission):
    """
    Custom permission to ensure user has appropriate permissions (view/edit/delete)
    for the profile associated with the note.
    Superusers have full access.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            profile_id = request.data.get('profile_id')
            if not profile_id:
                raise permissions.PermissionDenied({"detail": "Profile ID is required for creating a note."})
            
            try:
                profile = Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                raise permissions.PermissionDenied({"detail": "Profile not found."})

            if request.user.is_superuser:
                return True
            
            return SharedProfilePermission.objects.filter(
                profile=profile,
                shared_with=request.user,
                permissions='edit'
            ).exists()
        
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if not obj.profile:
            return False

        if request.method in permissions.SAFE_METHODS:
            return SharedProfilePermission.objects.filter(
                profile=obj.profile,
                shared_with=request.user,
                permissions__in=['view', 'edit', 'share', 'delete']
            ).exists()
        else:
            required_permission_for_action = 'edit'
            if request.method == 'DELETE':
                required_permission_for_action = 'delete'
            
            return SharedProfilePermission.objects.filter(
                profile=obj.profile,
                shared_with=request.user,
                permissions=required_permission_for_action
            ).exists()

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfilePermitted]

    def get_queryset(self):
        user = self.request.user
        queryset = Note.objects.all().prefetch_related('profile', 'author')

        if user.is_superuser:
            return queryset

        profile_id_param = self.request.query_params.get('profile_id')

        if profile_id_param:
            try:
                requested_profile_id = int(profile_id_param)
            except ValueError:
                return Note.objects.none()

            has_permission = SharedProfilePermission.objects.filter(
                profile__id=requested_profile_id,
                shared_with=user,
                permissions__in=['view', 'edit', 'share', 'delete']
            ).exists()

            if has_permission:
                queryset = queryset.filter(profile__id=requested_profile_id)
            else:
                return Note.objects.none()
        else:
            accessible_profile_ids = SharedProfilePermission.objects.filter(
                shared_with=user,
                permissions__in=['view', 'edit', 'share', 'delete']
            ).values_list('profile__id', flat=True)
            
            queryset = queryset.filter(profile__id__in=accessible_profile_ids)

        search_query = self.request.query_params.get('search', None)
        if search_query is not None:
            queryset = queryset.filter(content__icontains=search_query)

        important_filter = self.request.query_params.get('important', None)
        if important_filter is not None:
            if important_filter.lower() == 'true':
                queryset = queryset.filter(is_important=True)
            elif important_filter.lower() == 'false':
                queryset = queryset.filter(is_important=False)

        start_date_str = self.request.query_params.get('start_date', None)
        end_date_str = self.request.query_params.get('end_date', None)

        if start_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_date)
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_date)
            except ValueError:
                pass
        
        author_username = self.request.query_params.get('author_username', None)
        if author_username:
            try:
                author_user = User.objects.get(username__iexact=author_username)
                queryset = queryset.filter(author=author_user)
            except User.DoesNotExist:
                queryset = queryset.none()

        return queryset.order_by('-created_at').distinct()

    def perform_create(self, serializer):
        profile_id = self.request.data.get('profile_id')
        if not profile_id:
            raise serializers.ValidationError({"profile_id": "This field is required to create a note."})
        
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
                raise permissions.PermissionDenied("You do not have permission to add notes to this profile.")

        # Get the validated data
        validated_data = serializer.validated_data
        
        # Prepare note data with translation
        note_data = {
            'content': validated_data.get('content', '').strip(),
            'content_ar': validated_data.get('content_ar', '').strip(),
        }

        # Apply automatic translation for content
        fields_to_translate = ['content']
        note_data = translation_service.auto_translate_fields(note_data, fields_to_translate)

        # Save the note with translated data
        note = serializer.save(
            profile=profile, 
            author=self.request.user,
            content=note_data['content'],
            content_ar=note_data['content_ar']
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        
        # Get the validated data
        validated_data = serializer.validated_data
        
        # Prepare update data
        update_data = {}
        if 'content' in validated_data:
            update_data['content'] = validated_data['content'].strip()
        if 'content_ar' in validated_data:
            update_data['content_ar'] = validated_data['content_ar'].strip()

        # Apply automatic translation for updated fields
        fields_to_translate = []
        if 'content' in update_data or 'content_ar' in update_data:
            fields_to_translate.append('content')

        if fields_to_translate:
            # Get current values and merge with updates
            current_data = {
                'content': instance.content,
                'content_ar': instance.content_ar or '',
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
        instance.delete()