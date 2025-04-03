from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Category, Domain, Item
from .serializers import CategorySerializer, DomainSerializer, ItemSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def create_domain_with_items(request):
    data = request.data
    category_id = data.get("category")

    if not category_id:
        return Response({"error": "category is required"}, status=400)

    domain = Domain.objects.create(
        code=data.get("code"),
        title=data.get("title"),
        description=data.get("description"),
        category_id=category_id
    )

    items_data = data.get("items", [])
    for item in items_data:
        new_item = Item.objects.create(
            code=item["code"],
            title=item["title"],
            description=item["description"]
        )
        domain.items.add(new_item)

    serializer = DomainSerializer(domain)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
