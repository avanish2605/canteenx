from rest_framework import serializers
from .models import Canteen


class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = ['id', 'name', 'description', 'location', 'image',
                  'is_active', 'opening_time', 'closing_time', 'created_at']


class CanteenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = ['id', 'name', 'description', 'location', 'image', 'is_active',
                  'opening_time', 'closing_time']
