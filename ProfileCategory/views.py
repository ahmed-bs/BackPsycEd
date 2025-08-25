from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import Profile, SharedProfilePermission
from profiles.serializers import ProfileCategorySerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from ProfileCategory.models import ProfileCategory
from .translation_utils import translation_service





class ProfileCategoryViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def debug_urls(self, request):
        """
        Debug endpoint to show available URLs and methods
        """
        return Response({
            'message': 'ProfileCategory ViewSet URLs',
            'available_endpoints': {
                'list': 'GET /category/categories/',
                'create': 'POST /category/categories/',
                'retrieve': 'GET /category/categories/{id}/',
                'update': 'PUT /category/categories/{id}/',
                'partial_update': 'PATCH /category/categories/{id}/',
                'destroy': 'DELETE /category/categories/{id}/',
            },
            'current_request': {
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.query_params),
                'data': request.data if hasattr(request, 'data') else None
            }
        })

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
        print("CREATE method called")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        print(f"Request data: {request.data}")
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
            print(f"Category created with ID: {category.id}")
            serializer = ProfileCategorySerializer(category)
            return Response(
                {'message': 'Category created successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        print(f"UPDATE method called with pk: {pk}")
        print(f"Request method: {request.method}")
        print(f"Request data: {request.data}")
        try:
            category = get_object_or_404(ProfileCategory, pk=pk)
            profile = category.profile
            print(f"Found category: {category.id}, profile: {profile.id}")
            
            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this category'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Prepare update data and track changes
            update_data = {}
            changed_fields = []
            
            # Check for changes in name fields
            if 'name' in request.data:
                new_name = request.data['name'].strip()
                if new_name != category.name:
                    update_data['name'] = new_name
                    changed_fields.append('name')
                else:
                    update_data['name'] = category.name
            else:
                update_data['name'] = category.name
                
            if 'name_ar' in request.data:
                new_name_ar = request.data['name_ar'].strip()
                if new_name_ar != (category.name_ar or ''):
                    update_data['name_ar'] = new_name_ar
                    changed_fields.append('name_ar')
                else:
                    update_data['name_ar'] = category.name_ar or ''
            else:
                update_data['name_ar'] = category.name_ar or ''
            
            # Check for changes in description fields
            if 'description' in request.data:
                new_description = request.data['description'].strip()
                if new_description != (category.description or ''):
                    update_data['description'] = new_description
                    changed_fields.append('description')
                else:
                    update_data['description'] = category.description or ''
            else:
                update_data['description'] = category.description or ''
                
            if 'description_ar' in request.data:
                new_description_ar = request.data['description_ar'].strip()
                if new_description_ar != (category.description_ar or ''):
                    update_data['description_ar'] = new_description_ar
                    changed_fields.append('description_ar')
                else:
                    update_data['description_ar'] = category.description_ar or ''
            else:
                update_data['description_ar'] = category.description_ar or ''

            print(f"Changed fields: {changed_fields}")
            print(f"Before translation: {update_data}")

            # Apply smart translation based on changes
            fields_to_translate = ['name', 'description']
            translated_data = translation_service.smart_translate_fields(update_data, fields_to_translate, changed_fields)
            print(f"After translation: {translated_data}")

            # Update the category object with translated data
            category.name = translated_data['name']
            category.name_ar = translated_data['name_ar']
            category.description = translated_data['description']
            category.description_ar = translated_data['description_ar']
            
            category.save()
            print(f"Category saved with ID: {category.id}")

            serializer = ProfileCategorySerializer(category)
            return Response(
                {'message': 'Category updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        """
        Handle PATCH requests for partial updates
        """
        return self.update(request, pk)

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
