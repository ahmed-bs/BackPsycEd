from rest_framework import serializers
from .models import Note
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class NoteSerializer(serializers.ModelSerializer):
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        source='profile',
        write_only=True,
        required=True
    )
    profile = ProfileSerializer(read_only=True)

    author_username = serializers.SlugRelatedField(
        source='author',
        slug_field='username',
        read_only=True        
    )

    class Meta:
        model = Note
        fields = [
            'id', 'profile_id', 'profile', 'author_username', 'content', 
            'is_important', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile', 'author_username']