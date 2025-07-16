from rest_framework import serializers
from .models import Strategy
from profiles.models import Profile
from authentification.models import CustomUser

class StrategySerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    profile_name = serializers.CharField(source='profile.__str__', read_only=True)

    class Meta:
        model = Strategy
        fields = [
            'id', 'profile', 'profile_name',
            'author', 'author_username',    
            'title', 'description', 'status', 'responsible',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'author_username', 'profile_name', 'created_at', 'updated_at']

    def validate_profile(self, value):
        if not Profile.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Profile with this ID does not exist.")
        return value