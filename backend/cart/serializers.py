from rest_framework import serializers
from .models import Cart, CartItem
from menu.serializers import FoodItemListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    food_item_detail = FoodItemListSerializer(source='food_item', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'food_item', 'food_item_detail', 'quantity', 'subtotal', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'canteen', 'canteen_name', 'items', 'total', 'item_count', 'updated_at']

    def get_total(self, obj):
        return sum(item.subtotal for item in obj.items.all())

    def get_item_count(self, obj):
        return obj.items.count()


class AddToCartSerializer(serializers.Serializer):
    food_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_food_item_id(self, value):
        from menu.models import FoodItem
        try:
            item = FoodItem.objects.get(id=value)
        except FoodItem.DoesNotExist:
            raise serializers.ValidationError("Food item not found.")
        if not item.is_available:
            raise serializers.ValidationError("This item is currently unavailable.")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)
