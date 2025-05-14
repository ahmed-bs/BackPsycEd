from datetime import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from profiles.models import Profile, SharedProfilePermission
from .serializers import ProfileSerializer

CustomUser = get_user_model()

def parse_bool(value):
    return str(value).lower() in ['true', '1', 'yes']

class ProfileViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _calculate_category(self, birth_date):
        """Helper method to calculate autism category based on birth date."""
        current_date = datetime(2025, 5, 11).date()
        age = relativedelta(current_date, birth_date).years
        if 0 <= age <= 2:
            return 'Toddler'
        elif 3 <= age <= 12:
            return 'Young Child'
        elif 13 <= age <= 22:
            return 'Young Adult'
        else:
            raise ValueError('Age out of supported range (0-22 years).')

    def _check_view_permission(self, profile, user):
        """Check if user has view permission for the profile."""
        if user.is_superuser:
            return True
        return SharedProfilePermission.objects.filter(
            profile=profile, shared_with=user, permissions='view'
        ).exists()

    def _check_edit_permission(self, profile, user):
        """Check if user has edit permission for the profile."""
        if user.is_superuser:
            return True
        return SharedProfilePermission.objects.filter(
            profile=profile, shared_with=user, permissions='edit'
        ).exists()

    def _check_delete_permission(self, profile, user):
        """Check if user has delete permission for the profile."""
        if user.is_superuser:
            return True
        return SharedProfilePermission.objects.filter(
            profile=profile, shared_with=user, permissions='delete'
        ).exists()

    @action(detail=False, methods=['post'], url_path='create-child')
    def create_child_profile(self, request):
        try:
            required_fields = ['first_name', 'last_name', 'birth_date']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields: {", ".join(required_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            gender = request.data.get('gender')
            if gender and gender not in ['M', 'F']:
                return Response(
                    {'error': 'Invalid gender. Must be one of: M, F'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            birth_date_str = request.data['birth_date']
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid birth_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category = self._calculate_category(birth_date)

            child_profile = Profile.objects.create(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                birth_date=birth_date,
                gender=gender,
                evaluation_score=0,
                objectives=[],
                progress='En progrès',
                recommended_strategies=[],
                diagnosis=request.data.get('diagnosis', ''),
                notes=request.data.get('notes', ''),
                is_active=True,
                category=category
            )

            all_permissions = ['view', 'edit', 'share', 'delete']
            for perm in all_permissions:
                SharedProfilePermission.objects.create(
                    profile=child_profile,
                    shared_with=request.user,
                    permissions=perm
                )

            # try:
            #     assign_template_data_to_profile(child_profile)
            # except Exception as e:
            #     child_profile.delete()
            #     return Response(
            #         {'error': f'Failed to assign template data: {str(e)}'},
            #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
            #     )

            serializer = ProfileSerializer(child_profile)
            return Response(
                {'message': 'Child profile created successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def profiles_by_user(self, request, user_id):
        if not request.user.is_staff and str(request.user.id) != user_id:
            return Response(
                {"error": "You are not authorized to view these profiles"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        profiles = Profile.objects.filter(shared_with__shared_with=user).distinct()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='update')
    def update_child_profile(self, request, pk=None):
        try:
            child_profile = get_object_or_404(Profile, pk=pk)

            if not self._check_edit_permission(child_profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this profile'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if 'first_name' in request.data:
                child_profile.first_name = request.data['first_name']
            if 'last_name' in request.data:
                child_profile.last_name = request.data['last_name']
            if 'birth_date' in request.data:
                birth_date_str = request.data['birth_date']
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                    child_profile.birth_date = birth_date
                    child_profile.category = self._calculate_category(birth_date)
                except ValueError:
                    return Response(
                        {'error': 'Invalid birth_date format. Use YYYY-MM-DD.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            if 'gender' in request.data:
                gender = request.data['gender']
                if gender and gender not in ['M', 'F']:
                    return Response(
                        {'error': 'Invalid gender. Must be one of: M, F'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                child_profile.gender = gender
            if 'diagnosis' in request.data:
                child_profile.diagnosis = request.data['diagnosis']
            if 'notes' in request.data:
                child_profile.notes = request.data['notes']
            if 'is_active' in request.data:
                child_profile.is_active = parse_bool(request.data['is_active'])

            child_profile.save()
            serializer = ProfileSerializer(child_profile)
            return Response(
                {'message': 'Child profile updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='share')
    def share_child_profile(self, request, pk=None):
        try:
            profile = get_object_or_404(Profile, pk=pk)

            if not request.user.is_superuser:
                has_share_permission = SharedProfilePermission.objects.filter(
                    profile=profile,
                    shared_with=request.user,
                    permissions='share'
                ).exists()
                if not has_share_permission:
                    return Response(
                        {'error': 'You are not authorized to share this profile'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            required_fields = ['shared_with', 'permissions']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields: {", ".join(required_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shared_with = request.data['shared_with']
            try:
                shared_with_user = CustomUser.objects.get(
                    Q(email=shared_with) | Q(username=shared_with)
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': 'User with provided email or username not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            permissions = request.data['permissions']
            valid_permissions = ['view', 'edit', 'share']
            if not isinstance(permissions, list) or not all(perm in valid_permissions for perm in permissions):
                return Response(
                    {'error': 'Invalid permissions. Must be a list of "view", "edit", or "share".'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if shared_with_user == request.user:
                return Response(
                    {'error': 'Cannot share with yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for perm in permissions:
                SharedProfilePermission.objects.get_or_create(
                    profile=profile,
                    shared_with=shared_with_user,
                    permissions=perm
                )

            return Response(
                {'message': f'Profile shared successfully with {shared_with_user.username}'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_child_profile(self, request, pk=None):
        try:
            child_profile = get_object_or_404(Profile, pk=pk)

            if not self._check_delete_permission(child_profile, request.user):
                return Response(
                    {'error': 'You are not authorized to delete this profile'},
                    status=status.HTTP_403_FORBIDDEN
                )

            child_profile.delete()
            return Response(
                {'message': 'Child profile deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='list-all')
    def list_all_profiles(self, request):
        try:
            if not request.user.is_superuser:
                return Response(
                    {'error': 'Only admins can access this endpoint'},
                    status=status.HTTP_403_FORBIDDEN
                )

            profiles = Profile.objects.all()
            serializer = ProfileSerializer(profiles, many=True)
            return Response(
                {'message': 'Profiles retrieved successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='get')
    def get_by_id(self, request, pk=None):
        try:
            child_profile = get_object_or_404(Profile, pk=pk)

            if not self._check_view_permission(child_profile, request.user):
                return Response(
                    {'error': 'You are not authorized to view this profile'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ProfileSerializer(child_profile)
            return Response(
                {'message': 'Profile retrieved successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)