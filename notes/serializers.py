from rest_framework import serializers
from .models import Note
from django.contrib.auth import get_user_model

User = get_user_model()

class NoteSerializer(serializers.ModelSerializer):
    user_username = serializers.SlugRelatedField(
        source='user',
        slug_field='username',
        read_only=True        
    )

    class Meta:
        model = Note
        fields = ['id', 'user', 'user_username', 'content', 'is_important', 'created_at', 'updated_at']
        read_only_fields = ['user', 'user_username', 'created_at', 'updated_at']