from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import  SharedProfilePermission
from ProfileCategory.models import ProfileCategory
from ProfileDomain.models import  ProfileDomain
from profiles.serializers import  ProfileDomainSerializer
from rest_framework import status, viewsets




class ProfileDomainViewSet(viewsets.ViewSet):
    def get_queryset(self):
        # Handle the nested case for categories/2/domains/
        if 'categories_id' in self.kwargs:
            return self.queryset.filter(category_id=self.kwargs['categories_id'])
        return self.queryset
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
            category_id = request.query_params.get('category_id')
            print(f"Profile ID this is where to look: {category_id}")
            category = get_object_or_404(ProfileCategory, pk=category_id)
            profile = category.profile

            if not self._check_view_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to view domains for this category'},
                    status=status.HTTP_403_FORBIDDEN
                )

            domains = ProfileDomain.objects.filter(profile_category=category)
            serializer = ProfileDomainSerializer(domains, many=True)
            return Response(
                {'message': 'Domains retrieved successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            category_id = request.query_params.get('category_id')
            print(f"Profile ID this is where to look: {category_id}")
            category = get_object_or_404(ProfileCategory, pk=category_id)
            profile = category.profile

            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to create a domain for this category'},
                    status=status.HTTP_403_FORBIDDEN
                )

            required_fields = ['name']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields: {", ".join(required_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            domain_data = {
                'profile_category': category,
                'name': request.data['name'],
                'description': request.data.get('description', ''),
            }

            domain = ProfileDomain.objects.create(**domain_data)
            serializer = ProfileDomainSerializer(domain)
            return Response(
                {'message': 'Domain created successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            domain = get_object_or_404(ProfileDomain, pk=pk)
            profile = domain.profile_category.profile

            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this domain'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if 'name' in request.data:
                domain.name = request.data['name']
            if 'description' in request.data:
                domain.description = request.data['description']
            domain.save()

            serializer = ProfileDomainSerializer(domain)
            return Response(
                {'message': 'Domain updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            domain = get_object_or_404(ProfileDomain, pk=pk)
            profile = domain.profile_category.profile

            if not self._check_delete_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to delete this domain'},
                    status=status.HTTP_403_FORBIDDEN
                )

            domain.delete()
            return Response(
                {'message': 'Domain deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
