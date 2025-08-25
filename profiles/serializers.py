# profiles/serializers.py
from rest_framework import serializers
from profiles.models import Profile
from ProfileCategory.models import ProfileCategory
from ProfileDomain.models import ProfileDomain
from ProfileItem.models import ProfileItem


class ProfileItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileItem
        fields = ['id', 'name', 'name_ar', 'description', 'description_ar', 'etat', 'is_modified', 'modified_at', 'commentaire', 'commentaire_ar']
        read_only_fields = ['id', 'is_modified', 'modified_at']

    def validate_etat(self, value):
        valid_etats = [choice[0] for choice in ProfileItem.ETAT_CHOICES]
        if value not in valid_etats:
            raise serializers.ValidationError("Invalid etat. Must be one of: ACQUIS, PARTIEL, NON_ACQUIS, NON_COTE")
        return value


class ProfileDomainSerializer(serializers.ModelSerializer):
    items = ProfileItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProfileDomain
        fields = ['id', 'name', 'name_ar', 'description', 'description_ar', 'item_count', 'acquis_percentage', 'items']
        read_only_fields = ['id', 'item_count', 'acquis_percentage']


class ProfileCategorySerializer(serializers.ModelSerializer):
    # domains = ProfileDomainSerializer(many=True, read_only=True)
    domains_count = serializers.IntegerField(read_only=True)
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProfileCategory
        fields = ['id', 'name', 'name_ar', 'description', 'description_ar', 'domains_count','created_at', 'items_count']
        read_only_fields = ['id', 'domains_count', 'items_count']

class ProfileSerializer(serializers.ModelSerializer):
    categories = ProfileCategorySerializer(many=True, read_only=True)
    associated_users = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'  # Ensure 'image' is included

    def get_associated_users(self, obj):
        return [user.username for user in obj.associated_users]