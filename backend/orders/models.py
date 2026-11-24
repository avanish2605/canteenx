import random
import uuid
from django.db import models
from django.utils import timezone


def generate_order_number():
    today = timezone.now().strftime('%Y%m%d')
    while True:
        token = uuid.uuid4().hex[:6].upper()
        candidate = f"CX-{today}-{token}"
        if not Order.objects.filter(order_number=candidate).exists():
            return candidate


def generate_pickup_pin():
    while True:
        pin = f"{random.randint(1000, 9999)}"
        # Optionally ensure it's not colliding with active orders
        if not Order.objects.filter(pickup_pin=pin, status__in=['placed', 'accepted', 'preparing', 'ready']).exists():
            return pin


class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Order Placed'),
        ('accepted', 'Order Accepted'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash at Counter'),
        ('online', 'Online Payment'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='orders')
    canteen = models.ForeignKey('canteens.Canteen', on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    pickup_pin = models.CharField(max_length=6, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    estimated_prep_minutes = models.PositiveIntegerField(null=True, blank=True)
    estimated_ready_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)  # 1 to 5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        if not self.pickup_pin:
            self.pickup_pin = generate_pickup_pin()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} (PIN: {self.pickup_pin})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('menu.FoodItem', on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=200)   # snapshot at order time
    item_price = models.DecimalField(max_digits=8, decimal_places=2)  # snapshot
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.item_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.item_name} in {self.order.order_number}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.order.order_number}"
