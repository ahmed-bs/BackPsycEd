from rest_framework import serializers
from ProfileItem.models import ProfileItem

class ProfileItemSerializer(serializers.ModelSerializer):
    profile_domain_name = serializers.CharField(source='profile_domain.name', read_only=True)
    profile_category_name = serializers.CharField(source='profile_domain.profile_category.name', read_only=True)

    class Meta:
        model = ProfileItem
        fields = ['id', 'name', 'name_ar', 'description', 'description_ar', 'etat', 'profile_domain', 'profile_domain_name', 'profile_category_name', 'commentaire', 'commentaire_ar']