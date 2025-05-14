from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import  SharedProfilePermission
from ProfileItem.models import ProfileItem
from ProfileDomain.models import ProfileDomain
from profiles.serializers import  ProfileItemSerializer
from rest_framework import status, viewsets

class ProfileItemViewSet(viewsets.ViewSet):
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

    def list(self, request, domain_id=None):
        try:
            domain = get_object_or_404(ProfileDomain, pk=domain_id)
            profile = domain.profile_category.profile

            if not self._check_view_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to view items for this domain'},
                    status=status.HTTP_403_FORBIDDEN
                )

            items = ProfileItem.objects.filter(profile_domain=domain)
            serializer = ProfileItemSerializer(items, many=True)
            return Response(
                {'message': 'Items retrieved successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, domain_id=None):
        try:
            domain = get_object_or_404(ProfileDomain, pk=domain_id)
            profile = domain.profile_category.profile

            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to create an item for this domain'},
                    status=status.HTTP_403_FORBIDDEN
                )

            required_fields = ['name']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {'error': f'Missing required fields: {", ".join(required_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item_data = {
                'profile_domain': domain,
                'name': request.data['name'],
                'description': request.data.get('description', ''),
                'etat': request.data.get('etat', 'NON_COTE'),
                'template_item': None
            }

            item = ProfileItem.objects.create(**item_data)
            item.profile_domain.update_metrics()
            serializer = ProfileItemSerializer(item)
            return Response(
                {'message': 'Item created successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            item = get_object_or_404(ProfileItem, pk=pk)
            profile = item.profile_domain.profile_category.profile

            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this item'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if 'name' in request.data:
                item.name = request.data['name']
            if 'description' in request.data:
                item.description = request.data['description']
            if 'etat' in request.data:
                etat = request.data['etat']
                if etat not in [choice[0] for choice in ProfileItem.ETAT_CHOICES]:
                    return Response(
                        {'error': 'Invalid etat. Must be one of: ACQUIS, PARTIEL, NON_ACQUIS, NON_COTE'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.etat = etat
            item.is_modified = True
            item.save()

            serializer = ProfileItemSerializer(item)
            return Response(
                {'message': 'Item updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            item = get_object_or_404(ProfileItem, pk=pk)
            profile = item.profile_domain.profile_category.profile

            if not self._check_delete_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to delete this item'},
                    status=status.HTTP_403_FORBIDDEN
                )

            item.delete()
            return Response(
                {'message': 'Item deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)