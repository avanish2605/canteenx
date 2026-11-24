from rest_framework import serializers
from .models import FoodCategory, FoodItem


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ['id', 'canteen', 'name', 'description', 'image', 'is_active', 'order', 'created_at']
        read_only_fields = ['canteen']


class FoodItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)

    class Meta:
        model = FoodItem
        fields = ['id', 'canteen', 'canteen_name', 'category', 'category_name',
                  'name', 'description', 'price', 'image', 'is_veg', 'is_available',
                  'is_featured', 'preparation_time', 'stock_quantity', 'total_orders',
                  'created_at', 'updated_at']
        read_only_fields = ['canteen']


class FoodItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)

    class Meta:
        model = FoodItem
        fields = ['id', 'canteen', 'canteen_name', 'name', 'description', 'price', 'image', 'is_veg',
                  'is_available', 'is_featured', 'preparation_time',
                  'stock_quantity', 'category', 'category_name']
