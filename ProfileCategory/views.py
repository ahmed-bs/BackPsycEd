from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import Profile, SharedProfilePermission
from profiles.serializers import ProfileCategorySerializer
from rest_framework import status, viewsets
from ProfileCategory.models import ProfileCategory
from .translation_utils import translation_service





class ProfileCategoryViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _check_view_permission(self, profile, user):
        if user.is_superuser:
            return True
        return SharedProfilePermission.objects.filter(
            profile=profile, shared_with=user, permissions='view'
        ).exists()

    def _check_edit_permission(self, profile, user):
        if user.is_superuser:
            return True
        return SharedProfilePermission.objects.filter(
            profile=profile, shared_with=user, permissions='edit'
        ).exists()

    def _check_delete_permission(self, profile, user):
        if user.is_superuser:
            return True
        return SharedProfilePermission.objects.filter(
            profile=profile, shared_with=user, permissions='delete'
        ).exists()

    def list(self, request):
        try:
            profile_id = request.query_params.get('profile_id')
            print(f"Profile ID this is where to look: {profile_id}")
            profile = get_object_or_404(Profile, pk=profile_id)

            if not self._check_view_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to view categories for this profile'},
                    status=status.HTTP_403_FORBIDDEN
                )

            categories = ProfileCategory.objects.filter(profile=profile)
            serializer = ProfileCategorySerializer(categories, many=True)
            return Response(
                {'message': 'Categories retrieved successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        try:
            category = get_object_or_404(ProfileCategory, pk=pk)
            if not self._check_view_permission(category.profile, request.user):
                return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            serializer = ProfileCategorySerializer(category)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request ):
        profile_id = request.query_params.get('profile_id')
        print(f"Profile ID this is where to look: {profile_id}")
        profile_id = int(profile_id) if profile_id else None
        try:
            profile = get_object_or_404(Profile, pk=profile_id)
            print(f"Profile ID: {profile_id}")
            print(f"Profile: {profile}")
            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to create a category for this profile'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if at least one of name or name_ar is provided
            name = request.data.get('name', '').strip()
            name_ar = request.data.get('name_ar', '').strip()
            
            if not name and not name_ar:
                return Response(
                    {'error': 'Either name or name_ar must be provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare category data with translation
            category_data = {
                'profile': profile,
                'name': name,
                'name_ar': name_ar,
                'description': request.data.get('description', '').strip(),
                'description_ar': request.data.get('description_ar', '').strip(),
            }

            # Apply automatic translation for name and description
            fields_to_translate = ['name', 'description']
            category_data = translation_service.auto_translate_fields(category_data, fields_to_translate)

            category = ProfileCategory.objects.create(**category_data)
            serializer = ProfileCategorySerializer(category)
            return Response(
                {'message': 'Category created successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        print(f"Profile ID this is where to look: {pk}")
        pk = int(pk) if pk else None
        try:
            category = get_object_or_404(ProfileCategory, pk=pk)
            profile = category.profile
            print(f"Profile ID: {profile.id}")
            print(f"Category ID: {category.id}")
            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this category'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Prepare update data
            update_data = {}
            if 'name' in request.data:
                update_data['name'] = request.data['name'].strip()
            if 'name_ar' in request.data:
                update_data['name_ar'] = request.data['name_ar'].strip()
            if 'description' in request.data:
                update_data['description'] = request.data['description'].strip()
            if 'description_ar' in request.data:
                update_data['description_ar'] = request.data['description_ar'].strip()

            # Apply automatic translation for updated fields
            fields_to_translate = []
            if 'name' in update_data or 'name_ar' in update_data:
                fields_to_translate.append('name')
            if 'description' in update_data or 'description_ar' in update_data:
                fields_to_translate.append('description')

            if fields_to_translate:
                # Get current values and merge with updates
                current_data = {
                    'name': category.name,
                    'name_ar': category.name_ar or '',
                    'description': category.description or '',
                    'description_ar': category.description_ar or '',
                }
                current_data.update(update_data)
                
                # Apply translation
                translated_data = translation_service.auto_translate_fields(current_data, fields_to_translate)
                
                # Update category with translated data
                for field in fields_to_translate:
                    setattr(category, field, translated_data[field])
                    setattr(category, f"{field}_ar", translated_data[f"{field}_ar"])

            category.save()

            serializer = ProfileCategorySerializer(category)
            return Response(
                {'message': 'Category updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            category = get_object_or_404(ProfileCategory, pk=pk)
            profile = category.profile

            if not self._check_delete_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to delete this category'},
                    status=status.HTTP_403_FORBIDDEN
                )

            category.delete()
            return Response(
                {'message': 'Category deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
