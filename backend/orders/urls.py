from django.urls import path
from .views import (
    OrderCreateView, StudentOrderListView, StudentOrderDetailView,
    CanteenOrderListView, OrderStatusUpdateView, CancelOrderView,
    RateOrderView, VerifyOrderPinView
)

urlpatterns = [
    # Student
    path('', StudentOrderListView.as_view(), name='student_order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', StudentOrderDetailView.as_view(), name='student_order_detail'),
    path('<int:order_id>/cancel/', CancelOrderView.as_view(), name='student_order_cancel'),
    path('<int:order_id>/rate/', RateOrderView.as_view(), name='order_rate'),

    # Admin
    path('admin/orders/', CanteenOrderListView.as_view(), name='canteen_order_list'),
    path('admin/orders/<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('admin/verify-pin/', VerifyOrderPinView.as_view(), name='order_verify_pin'),
]
