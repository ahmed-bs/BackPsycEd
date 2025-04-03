# profiles/serializers.py
from rest_framework import serializers
from .models import Profile,ProfileShare

class ProfileShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileShare
        fields = ('id', 'profile', 'shared_with', 'can_read', 'can_write', 'can_update', 'can_delete')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

        extra_kwargs = {
            'bio': {'required': False, 'allow_null': True},
            'parent': {'read_only': True},
            'diagnosis': {'required': False, 'allow_null': True}
        }

