from rest_framework import serializers
from .models import TemplateCategory, TemplateDomain, TemplateItem

class TemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateItem
        fields = ['id', 'name', 'description', 'code']

class TemplateDomainSerializer(serializers.ModelSerializer):
    items = TemplateItemSerializer(many=True, read_only=True)

    class Meta:
        model = TemplateDomain
        fields = ['id', 'name', 'description', 'level', 'items']

class TemplateCategorySerializer(serializers.ModelSerializer):
    domains = TemplateDomainSerializer(many=True, read_only=True)

    class Meta:
        model = TemplateCategory
        fields = ['id', 'name', 'description', 'domains']