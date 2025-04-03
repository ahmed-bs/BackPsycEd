from rest_framework import serializers
from .models import TermdeCondition

class TermdeConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermdeCondition
        fields = '__all__'
