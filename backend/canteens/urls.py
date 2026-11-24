from django.urls import path
from .views import (
    CanteenListView, CanteenDetailView, CanteenCreateView, CanteenUpdateView
)

urlpatterns = [
    path('', CanteenListView.as_view(), name='canteen_list'),
    path('<int:pk>/', CanteenDetailView.as_view(), name='canteen_detail'),
    path('create/', CanteenCreateView.as_view(), name='canteen_create'),
    path('<int:pk>/update/', CanteenUpdateView.as_view(), name='canteen_update'),
]
