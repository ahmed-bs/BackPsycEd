from rest_framework import serializers
from .models import *


class DefaultItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultItem
        fields = '__all__'


class DefaultDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultDomain
        fields = '__all__'


class DefaultCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultCategory
        fields = '__all__'


class UserItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserItem
        fields = '__all__'


class UserDomainSerializer(serializers.ModelSerializer):
    items = UserItemSerializer(many=True, read_only=True)

    class Meta:
        model = UserDomain
        fields = '__all__'


class UserCategorySerializer(serializers.ModelSerializer):
    domains = UserDomainSerializer(many=True, read_only=True)

    class Meta:
        model = UserCategory
        fields = '__all__'

