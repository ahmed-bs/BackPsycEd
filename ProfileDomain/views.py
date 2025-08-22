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
        try:
            domain = get_object_or_404(ProfileDomain, pk=pk)
            profile = domain.profile_category.profile

            if not self._check_edit_permission(profile, request.user):
                return Response(
                    {'error': 'You are not authorized to update this domain'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Prepare update data with current values as fallback
            update_data = {
                'name': getattr(domain, 'name', ''),
                'name_ar': getattr(domain, 'name_ar', ''),
                'description': getattr(domain, 'description', ''),
                'description_ar': getattr(domain, 'description_ar', ''),
            }

            # Update with new values from request
            if 'name' in request.data:
                update_data['name'] = request.data['name'].strip()
            if 'name_ar' in request.data:
                update_data['name_ar'] = request.data['name_ar'].strip()
            if 'description' in request.data:
                update_data['description'] = request.data['description'].strip()
            if 'description_ar' in request.data:
                update_data['description_ar'] = request.data['description_ar'].strip()

            # Apply automatic translation for name and description
            fields_to_translate = ['name', 'description']
            update_data = translation_service.auto_translate_fields(update_data, fields_to_translate)

            # Update domain fields
            for field, value in update_data.items():
                setattr(domain, field, value)
            
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
