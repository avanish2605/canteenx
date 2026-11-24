from django.contrib import admin
from .models import FoodCategory, FoodItem


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'canteen', 'order', 'is_active', 'created_at')
    list_filter = ('canteen', 'is_active')
    search_fields = ('name', 'canteen__name')
    ordering = ('canteen', 'order', 'name')


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'canteen', 'category', 'price', 'is_veg', 'is_available', 'is_featured', 'total_orders')
    list_filter = ('canteen', 'category', 'is_veg', 'is_available', 'is_featured')
    search_fields = ('name', 'description', 'canteen__name')
    list_editable = ('price', 'is_available', 'is_featured')
    readonly_fields = ('total_orders', 'created_at', 'updated_at')
