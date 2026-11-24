from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'subtotal')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('student', 'canteen', 'updated_at')
    list_filter = ('canteen',)
    search_fields = ('student__email', 'student__full_name')
    inlines = [CartItemInline]
    readonly_fields = ('updated_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'food_item', 'quantity', 'created_at')
    search_fields = ('cart__student__email', 'food_item__name')
