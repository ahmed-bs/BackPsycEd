from rest_framework import serializers
from .models import Category, Domain, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'code', 'title', 'description']


class DomainSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Domain
        fields = ['id', 'code', 'title', 'description', 'category', 'items']


class CategorySerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'code', 'title', 'created_date', 'items_count', 'domains_count', 'domains']
