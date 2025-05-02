from rest_framework import serializers
from .models import ProfileCategory, ProfileDomain, ProfileItem
from template_data.serializers import TemplateCategorySerializer, TemplateDomainSerializer, TemplateItemSerializer

class ProfileItemSerializer(serializers.ModelSerializer):
    template_item = TemplateItemSerializer(read_only=True)

    class Meta:
        model = ProfileItem
        fields = ['id', 'name', 'description', 'is_modified', 'modified_at', 'etat', 'template_item']

class ProfileDomainSerializer(serializers.ModelSerializer):
    template_domain = TemplateDomainSerializer(read_only=True)
    items = ProfileItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProfileDomain
        fields = ['id', 'name', 'description', 'template_domain', 'items', 'item_count', 'acquis_percentage']

class ProfileCategorySerializer(serializers.ModelSerializer):
    template_category = TemplateCategorySerializer(read_only=True)
    domains = ProfileDomainSerializer(many=True, read_only=True)

    class Meta:
        model = ProfileCategory
        fields = ['id', 'name', 'description', 'template_category', 'domains']