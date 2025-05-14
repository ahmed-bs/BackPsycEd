from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import Profile, SharedProfilePermission
from profiles.serializers import ProfileCategorySerializer
from rest_framework import status, viewsets
from ProfileCategory.models import ProfileCategory





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

            required_fields = ['name']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields:{"name": ", ".join(required_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category_data = {
                'profile': profile,
                'name': request.data['name'],
                'description': request.data.get('description', ''),
            }

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

            if 'name' in request.data:
                category.name = request.data['name']
            if 'description' in request.data:
                category.description = request.data['description']
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
