from rest_framework import serializers
from profiles.models import Profile
from ProfileCategory.models import ProfileCategory
from ProfileDomain.models import ProfileDomain
from ProfileItem.models import ProfileItem


class ProfileItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileItem
        fields = ['id', 'name', 'name_ar', 'description', 'description_ar', 'etat', 'is_modified', 'modified_at', 'comentaire', 'commentaire_ar']
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
        fields = ['id', 'name', 'name_ar', 'description', 'description_ar', 'item_count', 'acquis_percentage', 'start_date', 'last_evaluation_date', 'items']
        read_only_fields = ['id', 'item_count', 'acquis_percentage', 'start_date', 'last_evaluation_date']