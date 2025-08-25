from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from profiles.models import  SharedProfilePermission
from ProfileCategory.models import ProfileCategory
from ProfileDomain.models import  ProfileDomain
from profiles.serializers import  ProfileDomainSerializer
from rest_framework import status, viewsets
from django.db.models import Q, Count, F
from rest_framework.decorators import action
from .translation_utils import translation_service


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
    @action(detail=False, methods=['get'], url_path='specific-items')
    def list_domains_with_specific_items(self, request):
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

            # Get domains with at least one item where etat != 'NON_COTE'
            # and not all items are 'ACQUIS'
            domains = ProfileDomain.objects.filter(
                profile_category=category,
                items__etat__in=['ACQUIS', 'PARTIEL', 'NON_ACQUIS']  # At least one item not NON_COTE
            ).annotate(
                total_items=Count('items'),
                acquis_items=Count('items', filter=Q(items__etat='ACQUIS'))
            ).filter(
                total_items__gt=0,  # Ensure domain has items
                acquis_items__lt=F('total_items')  # Not all items are ACQUIS
            ).distinct()

            serializer = ProfileDomainSerializer(domains, many=True)
            return Response(
                {
                    'message': 'Domains with specific item states retrieved successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

            # Check if at least one of name or name_ar is provided
            name = request.data.get('name', '').strip()
            name_ar = request.data.get('name_ar', '').strip()
            
            if not name and not name_ar:
                return Response(
                    {'error': 'Either name or name_ar must be provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare domain data with translation
            domain_data = {
                'profile_category': category,
                'name': name,
                'name_ar': name_ar,
                'description': request.data.get('description', '').strip(),
                'description_ar': request.data.get('description_ar', '').strip(),
            }

            # Apply automatic translation for name and description
            fields_to_translate = ['name', 'description']
            domain_data = translation_service.auto_translate_fields(domain_data, fields_to_translate)

            domain = ProfileDomain.objects.create(**domain_data)
            serializer = ProfileDomainSerializer(domain)
            return Response(
                {'message': 'Domain created successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        print(f"UPDATE method called with pk: {pk}")
        print(f"Request method: {request.method}")
        print(f"Request data: {request.data}")
        try:
            domain = get_object_or_404(ProfileDomain, pk=pk)
            profile = domain.profile_category.profile
            print(f"Found domain: {domain.id}, profile: {profile.id}")
            
            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this domain'},
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
                    if new_name != domain.name:
                        update_data['name'] = new_name
                        changed_fields.append('name')
                    else:
                        update_data['name'] = domain.name
                else:
                    # If None is sent, keep the existing value
                    update_data['name'] = domain.name
            else:
                update_data['name'] = domain.name
                
            if 'name_ar' in request.data:
                new_name_ar = request.data['name_ar']
                if new_name_ar is not None:
                    new_name_ar = new_name_ar.strip()
                    if new_name_ar != (domain.name_ar or ''):
                        update_data['name_ar'] = new_name_ar
                        changed_fields.append('name_ar')
                    else:
                        update_data['name_ar'] = domain.name_ar or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['name_ar'] = domain.name_ar or ''
            else:
                update_data['name_ar'] = domain.name_ar or ''
            
            # Check for changes in description fields
            if 'description' in request.data:
                new_description = request.data['description']
                if new_description is not None:
                    new_description = new_description.strip()
                    if new_description != (domain.description or ''):
                        update_data['description'] = new_description
                        changed_fields.append('description')
                    else:
                        update_data['description'] = domain.description or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['description'] = domain.description or ''
            else:
                update_data['description'] = domain.description or ''
                
            if 'description_ar' in request.data:
                new_description_ar = request.data['description_ar']
                if new_description_ar is not None:
                    new_description_ar = new_description_ar.strip()
                    if new_description_ar != (domain.description_ar or ''):
                        update_data['description_ar'] = new_description_ar
                        changed_fields.append('description_ar')
                    else:
                        update_data['description_ar'] = domain.description_ar or ''
                else:
                    # If None is sent, keep the existing value
                    update_data['description_ar'] = domain.description_ar or ''
            else:
                update_data['description_ar'] = domain.description_ar or ''

            print(f"Changed fields: {changed_fields}")
            print(f"Before translation: {update_data}")

            # Apply smart translation based on changes
            fields_to_translate = ['name', 'description']
            translated_data = translation_service.smart_translate_fields(update_data, fields_to_translate, changed_fields)
            print(f"After translation: {translated_data}")

            # Update the domain object with translated data
            domain.name = translated_data['name']
            domain.name_ar = translated_data['name_ar']
            domain.description = translated_data['description']
            domain.description_ar = translated_data['description_ar']
            
            domain.save()
            print(f"Domain saved with ID: {domain.id}")

            serializer = ProfileDomainSerializer(domain)
            return Response(
                {'message': 'Domain updated successfully', 'data': serializer.data},
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
