from django.contrib.auth import get_user_model  # Add this import at the top
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
User = get_user_model()
from django.utils import timezone
from datetime import timedelta
import uuid

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'user_type', 'accepte_conditions','user_type','bio']
        extra_kwargs = {
            'password': {'required': False, 'write_only': True},
            'bio': {'required': False, 'allow_null': True},
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)


    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'confirm_password',
                  'user_type', 'accepte_conditions','bio']

    def validate(self, data):
        # Password matching validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")

        # User type validation
        valid_types = [choice[0] for choice in CustomUser.USER_TYPE_CHOICES]
        if 'user_type' in data and data['user_type'] not in valid_types:
            raise serializers.ValidationError({
                'user_type': f"Must be one of: {', '.join(valid_types)}"
            })

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'other'),
            accepte_conditions=validated_data['accepte_conditions']
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Must include both email and password.")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        token, created = Token.objects.get_or_create(user=user)

        return {
            "user": {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "token": token.key
            }
        }


