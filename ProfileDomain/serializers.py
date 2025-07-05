from rest_framework import serializers
from .models import ProfileDomain

class ProfileDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDomain
        fields = ['id', 'name', 'description', 'profile_category_id']