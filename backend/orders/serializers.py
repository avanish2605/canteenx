from rest_framework import serializers
from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'item_name', 'item_price', 'quantity', 'subtotal']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'method', 'status', 'transaction_id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_mobile = serializers.CharField(source='student.mobile', read_only=True)
    student_enrollment = serializers.SerializerMethodField()
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'pickup_pin', 'student', 'student_name',
                  'student_email', 'student_mobile', 'student_enrollment',
                  'canteen', 'canteen_name', 'status', 'status_display', 'payment_method', 'payment_status',
                  'subtotal', 'tax_amount', 'total_amount', 'special_instructions',
                  'cancellation_reason', 'estimated_prep_minutes', 'estimated_ready_at',
                  'rating', 'review', 'items', 'payment',
                  'created_at', 'updated_at']

    def get_student_enrollment(self, obj):
        profile = getattr(obj.student, 'student_profile', None)
        return profile.enrollment_number if profile else 'EN2024CS001'


class OrderCreateSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=['cash', 'online'], default='cash')
    special_instructions = serializers.CharField(required=False, allow_blank=True, default='')


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[c[0] for c in Order.STATUS_CHOICES])
    cancellation_reason = serializers.CharField(required=False, allow_blank=True, default='')
    estimated_prep_minutes = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=180
    )


class OrderRateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review = serializers.CharField(required=False, allow_blank=True, default='')


class VerifyOrderPinSerializer(serializers.Serializer):
    pickup_pin = serializers.CharField(max_length=6)
