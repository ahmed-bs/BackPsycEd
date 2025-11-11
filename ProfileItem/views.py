from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
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
                    'commentaire': item['commentaire'],
                    'commentaire_ar': item['commentaire_ar'],
                    'isPeu': item.get('isPeu', False),
                    'done': item.get('done', False),
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
                'commentaire': request.data.get('commentaire', '').strip(),
                'commentaire_ar': request.data.get('commentaire_ar', '').strip(),
                'etat': request.data.get('etat', 'NON_COTE'),
            }

            # Apply automatic translation for name, description, and commentaire
            fields_to_translate = ['name', 'description', 'commentaire']
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
        print(f"UPDATE method called with pk: {pk}")
        print(f"Request method: {request.method}")
        print(f"Request data: {request.data}")
        try:
            item = get_object_or_404(ProfileItem, pk=pk)
            profile = item.profile_domain.profile_category.profile
            print(f"Found item: {item.id}, profile: {profile.id}")
            
            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this item'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Prepare update data and track changes
            update_data = {}
            changed_fields = []
            
            # Check for changes in name fields
            if 'name' in request.data:
                new_name = request.data['name']
                if new_name is not None:
                    new_name = new_name.strip()
                    if new_name != item.name:
                        update_data['name'] = new_name
                        changed_fields.append('name')
                    else:
                        update_data['name'] = item.name
                else:
                    # If None is sent, keep the existing value
                    update_data['name'] = item.name
            else:
                update_data['name'] = item.name
                
            if 'name_ar' in request.data:
                new_name_ar = request.data['name_ar']
                if new_name_ar is not None:
                    new_name_ar = new_name_ar.strip()
                    if new_name_ar != (item.name_ar or ''):
                        update_data['name_ar'] = new_name_ar
                        changed_fields.append('name_ar')
                    else:
                        update_data['name_ar'] = item.name_ar or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['name_ar'] = item.name_ar or ''
            else:
                update_data['name_ar'] = item.name_ar or ''
            
            # Check for changes in description fields
            if 'description' in request.data:
                new_description = request.data['description']
                if new_description is not None:
                    new_description = new_description.strip()
                    if new_description != (item.description or ''):
                        update_data['description'] = new_description
                        changed_fields.append('description')
                    else:
                        update_data['description'] = item.description or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['description'] = item.description or ''
            else:
                update_data['description'] = item.description or ''
                
            if 'description_ar' in request.data:
                new_description_ar = request.data['description_ar']
                if new_description_ar is not None:
                    new_description_ar = new_description_ar.strip()
                    if new_description_ar != (item.description_ar or ''):
                        update_data['description_ar'] = new_description_ar
                        changed_fields.append('description_ar')
                    else:
                        update_data['description_ar'] = item.description_ar or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['description_ar'] = item.description_ar or ''
            else:
                update_data['description_ar'] = item.description_ar or ''
            
            # Check for changes in commentaire fields
            if 'commentaire' in request.data:
                new_commentaire = request.data['commentaire']
                if new_commentaire is not None:
                    new_commentaire = new_commentaire.strip()
                    if new_commentaire != (item.commentaire or ''):
                        update_data['commentaire'] = new_commentaire
                        changed_fields.append('commentaire')
                    else:
                        update_data['commentaire'] = item.commentaire or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['commentaire'] = item.commentaire or ''
            else:
                update_data['commentaire'] = item.commentaire or ''
                
            if 'commentaire_ar' in request.data:
                new_commentaire_ar = request.data['commentaire_ar']
                if new_commentaire_ar is not None:
                    new_commentaire_ar = new_commentaire_ar.strip()
                    if new_commentaire_ar != (item.commentaire_ar or ''):
                        update_data['commentaire_ar'] = new_commentaire_ar
                        changed_fields.append('commentaire_ar')
                    else:
                        update_data['commentaire_ar'] = item.commentaire_ar or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['commentaire_ar'] = item.commentaire_ar or ''
            else:
                update_data['commentaire_ar'] = item.commentaire_ar or ''

            print(f"Changed fields: {changed_fields}")
            print(f"Before translation: {update_data}")

            # Apply smart translation based on changes
            fields_to_translate = ['name', 'description', 'commentaire']
            translated_data = translation_service.smart_translate_fields(update_data, fields_to_translate, changed_fields)
            print(f"After translation: {translated_data}")

            # Update the item object with translated data
            item.name = translated_data['name']
            item.name_ar = translated_data['name_ar']
            item.description = translated_data['description']
            item.description_ar = translated_data['description_ar']
            item.commentaire = translated_data['commentaire']
            item.commentaire_ar = translated_data['commentaire_ar']

            if 'etat' in request.data:
                etat = request.data['etat']
                if etat not in [choice[0] for choice in ProfileItem.ETAT_CHOICES]:
                    return Response(
                        {'error': 'Invalid etat. Must be one of: ACQUIS, PARTIEL, NON_ACQUIS, NON_COTE'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.etat = etat
            
            # Handle isPeu field
            if 'isPeu' in request.data:
                item.isPeu = bool(request.data['isPeu'])
            
            # Handle done field
            if 'done' in request.data:
                item.done = bool(request.data['done'])
            
            item.is_modified = True
            item.save()
            print(f"Item saved with ID: {item.id}")

            serializer = ProfileItemSerializer(item)
            return Response(
                {'message': 'Item updated successfully', 'data': serializer.data},
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

    @action(detail=True, methods=['patch', 'put'], url_path='toggle-ispeu')
    def toggle_ispeu(self, request, pk=None):
        """
        Toggle the isPeu field for a ProfileItem.
        Accepts a boolean value in the request body or toggles the current value.
        """
        try:
            item = get_object_or_404(ProfileItem, pk=pk)
            profile = item.profile_domain.profile_category.profile
            
            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this item'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # If isPeu is provided in request, use it; otherwise toggle
            if 'isPeu' in request.data:
                item.isPeu = bool(request.data['isPeu'])
            else:
                # Toggle the current value
                item.isPeu = not item.isPeu
            
            item.is_modified = True
            item.save()
            
            serializer = ProfileItemSerializer(item)
            return Response(
                {
                    'message': 'isPeu updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )