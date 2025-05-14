# In profiles/serializers.py
from rest_framework import serializers
from profiles.models import Profile
from ProfileCategory.models import ProfileCategory
from ProfileDomain.models import ProfileDomain
from ProfileItem.models import ProfileItem
class ProfileItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileItem
        fields = ['id', 'name', 'description', 'etat', 'commentaire', 'is_modified', 'modified_at', 'template_item']
        read_only_fields = ['id', 'is_modified', 'modified_at']

    def validate_etat(self, value):
        valid_etats = [choice[0] for choice in ProfileItem.ETAT_CHOICES]
        if value not in valid_etats:
            raise serializers.ValidationError("Invalid etat. Must be one of: ACQUIS, PARTIEL, NON_ACQUIS, NON_COTE")
        return value

# ... (other serializers remain unchanged)
class ProfileDomainSerializer(serializers.ModelSerializer):
    items = ProfileItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProfileDomain
        fields = ['id', 'name', 'description', 'item_count', 'acquis_percentage', 'template_domain', 'items']
        read_only_fields = ['id', 'item_count', 'acquis_percentage']

class ProfileCategorySerializer(serializers.ModelSerializer):
    domains = ProfileDomainSerializer(many=True, read_only=True)

    class Meta:
        model = ProfileCategory
        fields = ['id', 'name', 'description', 'template_category', 'domains']
        read_only_fields = ['id']

class ProfileSerializer(serializers.ModelSerializer):
    categories = ProfileCategorySerializer(many=True, read_only=True)
    associated_users = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'category', 'first_name', 'last_name', 'birth_date', 'diagnosis', 'notes',
            'evaluation_score', 'objectives', 'progress', 'recommended_strategies', 'image_url',
            'created_at', 'is_active', 'bio', 'gender', 'associated_users', 'categories'
        ]

    def get_associated_users(self, obj):
        return [user.username for user in obj.associated_users]