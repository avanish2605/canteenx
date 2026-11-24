from django.urls import path
from .views import (
    FoodCategoryListView, FoodCategoryCreateView, FoodCategoryDetailView,
    FoodItemListView, FoodItemDetailView, FoodItemCreateView,
    FoodItemUpdateView, FoodItemDeleteView, AdminFoodItemListView, AdminCategoryListView
)

urlpatterns = [
    # Public & Student
    path('categories/', FoodCategoryListView.as_view(), name='category_list'),
    path('items/', FoodItemListView.as_view(), name='food_item_list'),
    path('items/<int:pk>/', FoodItemDetailView.as_view(), name='food_item_detail'),

    # Admin Food Items
    path('admin/items/', AdminFoodItemListView.as_view(), name='admin_food_item_list'),
    path('admin/items/create/', FoodItemCreateView.as_view(), name='admin_food_item_create'),
    path('admin/items/<int:pk>/update/', FoodItemUpdateView.as_view(), name='admin_food_item_update'),
    path('admin/items/<int:pk>/delete/', FoodItemDeleteView.as_view(), name='admin_food_item_delete'),

    # Admin Categories
    path('admin/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin/categories/create/', FoodCategoryCreateView.as_view(), name='admin_category_create'),
    path('admin/categories/<int:pk>/', FoodCategoryDetailView.as_view(), name='admin_category_detail'),
]
