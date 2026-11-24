from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_name', 'item_price', 'quantity', 'subtotal', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'student', 'canteen', 'pickup_pin', 
        'status', 'payment_method', 'payment_status', 
        'total_amount', 'rating', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'payment_status', 'canteen', 'created_at')
    search_fields = ('order_number', 'pickup_pin', 'student__email', 'student__full_name', 'canteen__name')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('order_number', 'pickup_pin', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item_name', 'item_price', 'quantity', 'subtotal', 'created_at')
    search_fields = ('order__order_number', 'item_name')
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
