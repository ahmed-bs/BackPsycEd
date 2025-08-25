from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import  SharedProfilePermission
from ProfileItem.models import ProfileItem
from ProfileDomain.models import ProfileDomain
from profiles.serializers import  ProfileItemSerializer
from rest_framework import status, viewsets
from .translation_utils import translation_service

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

    def list(self, request):
        try:
            domain_id = request.query_params.get('domain_id')
            domain = get_object_or_404(ProfileDomain, pk=domain_id)
            profile = domain.profile_category.profile

            if not self._check_view_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to view items for this domain'},
                    status=status.HTTP_403_FORBIDDEN
                )

            items = ProfileItem.objects.filter(profile_domain=domain)
            serializer = ProfileItemSerializer(items, many=True)
        
            # Customize response to include domain and category names with all _ar fields
            response_data = [
                {
                    'id': item['id'],
                    'name': item['name'],
                    'name_ar': item['name_ar'],
                    'description': item['description'],
                    'description_ar': item['description_ar'],
                    'etat': item['etat'],
                    'profile_domain_name': domain.name,
                    'profile_domain_name_ar': domain.name_ar,
                    'profile_category_name': domain.profile_category.name,
                    'profile_category_name_ar': domain.profile_category.name_ar,
                    'comentaire': item['comentaire'],
                    'commentaire_ar': item['commentaire_ar'],
                }
                for item in serializer.data
            ]
            
            return Response(
                {'message': 'Items retrieved successfully', 'data': response_data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create(self, request):
        try:
            domain_id = request.query_params.get('domain_id')
            print(f"Profile ID this is where to look: {domain_id}")
            domain = get_object_or_404(ProfileDomain, pk=domain_id)
            profile = domain.profile_category.profile

            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to create an item for this domain'},
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

            # Prepare item data with translation
            item_data = {
                'profile_domain': domain,
                'name': name,
                'name_ar': name_ar,
                'description': request.data.get('description', '').strip(),
                'description_ar': request.data.get('description_ar', '').strip(),
                'comentaire': request.data.get('comentaire', '').strip(),
                'commentaire_ar': request.data.get('commentaire_ar', '').strip(),
                'etat': request.data.get('etat', 'NON_COTE'),
            }

            # Apply automatic translation for name, description, and comentaire
            fields_to_translate = ['name', 'description', 'comentaire']
            item_data = translation_service.auto_translate_fields(item_data, fields_to_translate)

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
            if 'comentaire' in request.data:
                update_data['comentaire'] = request.data['comentaire'].strip()
            if 'commentaire_ar' in request.data:
                update_data['commentaire_ar'] = request.data['commentaire_ar'].strip()

            # Apply automatic translation for updated fields
            fields_to_translate = []
            if 'name' in update_data or 'name_ar' in update_data:
                fields_to_translate.append('name')
            if 'description' in update_data or 'description_ar' in update_data:
                fields_to_translate.append('description')
            if 'comentaire' in update_data or 'commentaire_ar' in update_data:
                fields_to_translate.append('comentaire')

            if fields_to_translate:
                # Get current values and merge with updates
                current_data = {
                    'name': item.name,
                    'name_ar': item.name_ar or '',
                    'description': item.description or '',
                    'description_ar': item.description_ar or '',
                    'comentaire': item.comentaire or '',
                    'commentaire_ar': item.commentaire_ar or '',
                }
                current_data.update(update_data)
                
                # Apply translation
                translated_data = translation_service.auto_translate_fields(current_data, fields_to_translate)
                
                # Update item with translated data
                for field in fields_to_translate:
                    setattr(item, field, translated_data[field])
                    setattr(item, f"{field}_ar", translated_data[f"{field}_ar"])

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