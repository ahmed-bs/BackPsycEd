from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import *
from .serializers import *
from datetime import date
from django.utils.timezone import now
from profiles.models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from categories.models import DefaultCategory
from categories.serializers import DefaultCategorySerializer
def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

class AllDefaultCategoriesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = DefaultCategory.objects.all()
        serializer = DefaultCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class DefaultCategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, profile_id):
        profile = Profile.objects.get(pk=profile_id, parent=request.user)
        age = calculate_age(profile.birth_date)
        age_type = 'petit_enfant' if age < 6 else 'grand_enfant'
        copied_codes = UserCategory.objects.filter(owner=request.user).values_list('code', flat=True)
        base_codes = [code.split('_')[0] for code in copied_codes]
        categories = DefaultCategory.objects.filter(age_type=age_type).exclude(code__in=base_codes)
        serializer = DefaultCategorySerializer(categories, many=True)
        return Response(serializer.data)

class ListDefaultCategoriesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        categories = DefaultCategory.objects.all()
        serializer = DefaultCategorySerializer(categories, many=True)
        return Response(serializer.data)
class DefaultCategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, category_id):
        category = DefaultCategory.objects.get(pk=category_id)
        domains = DefaultDomain.objects.filter(category=category).prefetch_related('items')
        data = {
            'category': DefaultCategorySerializer(category).data,
            'domains': [
                {
                    'domain': DefaultDomainSerializer(domain).data,
                    'items': DefaultItemSerializer(domain.items.all(), many=True).data
                }
                for domain in domains
            ]
        }
        return Response(data)


class CopyCategoryToUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        category_id = request.data.get('category_id')
        category_code = request.data.get('category_code')
        profile_id = request.data.get('profile_id')

        if not profile_id or (not category_id and not category_code):
            return Response({'error': 'Vous devez fournir category_id ou category_code et profile_id.'}, status=400)

        try:
            profile = Profile.objects.get(pk=profile_id, parent=request.user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profil non trouvé ou non autorisé'}, status=403)

        try:
            if category_id:
                default_cat = DefaultCategory.objects.get(pk=category_id)
            else:
                default_cat = DefaultCategory.objects.get(code=category_code)
        except DefaultCategory.DoesNotExist:
            return Response({'error': 'Catégorie non trouvée'}, status=404)

        copy_code = f"{default_cat.code}_{request.user.id}"
        if UserCategory.objects.filter(code=copy_code, owner=request.user).exists():
            return Response({'error': 'Cette catégorie a déjà été copiée.'}, status=400)

        user_cat = UserCategory.objects.create(
            code=copy_code,
            title=default_cat.title,
            created_date=now().date(),
            items_count=default_cat.items_count,
            domains_count=default_cat.domains_count,
            owner=request.user
        )

        for domain in DefaultDomain.objects.filter(category=default_cat):
            user_domain = UserDomain.objects.create(
                code=f"{domain.code}_{request.user.id}",
                title=domain.title,
                description=domain.description,
                category=user_cat
            )
            for item in domain.items.all():
                user_item = UserItem.objects.create(
                    code=f"{item.code}_{request.user.id}",
                    title=item.title,
                    description=item.description
                )
                user_domain.items.add(user_item)

        profile.category = user_cat
        profile.save()

        return Response({
            'message': f'Catégorie {default_cat.code} copiée et liée avec succès au profil {profile.first_name}',
            'user_category_code': user_cat.code
        }, status=201)

class UpdateUserCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('user_category_code')
        title = request.data.get('title')
        domains_data = request.data.get('domains', [])

        if not code:
            return Response({'error': 'Code de la catégorie requis.'}, status=400)

        try:
            user_cat = UserCategory.objects.get(code=code, owner=request.user)
        except UserCategory.DoesNotExist:
            return Response({'error': 'Catégorie personnalisée non trouvée'}, status=404)

        if title:
            user_cat.title = title
            user_cat.save()

        for domain_data in domains_data:
            try:
                user_domain = UserDomain.objects.get(id=domain_data['id'], category=user_cat)
                user_domain.title = domain_data.get('title', user_domain.title)
                user_domain.save()

                for item_data in domain_data.get('items', []):
                    try:
                        user_item = UserItem.objects.get(id=item_data['id'])
                        user_item.title = item_data.get('title', user_item.title)
                        user_item.description = item_data.get('description', user_item.description)
                        user_item.save()
                    except UserItem.DoesNotExist:
                        continue
            except UserDomain.DoesNotExist:
                continue

        return Response({'message': 'Catégorie personnalisée mise à jour avec succès'}, status=200)

class UserCategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, profile_id):
        profile = Profile.objects.get(pk=profile_id, parent=request.user)
        category = profile.category
        domains = UserDomain.objects.filter(category=category).prefetch_related('items')
        data = {
            'category': UserCategorySerializer(category).data,
            'domains': [
                {
                    'domain': UserDomainSerializer(domain).data,
                    'items': UserItemSerializer(domain.items.all(), many=True).data
                }
                for domain in domains
            ]
        }
        return Response(data)
