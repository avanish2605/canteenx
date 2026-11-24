from django.urls import path
from .views import CartView, AddToCartView, CartItemUpdateView

urlpatterns = [
    path('', CartView.as_view(), name='cart_detail'),
    path('add/', AddToCartView.as_view(), name='cart_add'),
    path('items/<int:item_id>/', CartItemUpdateView.as_view(), name='cart_item_update'),
]
