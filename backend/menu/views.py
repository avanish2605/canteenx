from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FoodCategory, FoodItem
from .serializers import FoodCategorySerializer, FoodItemSerializer, FoodItemListSerializer
from accounts.permissions import IsCanteenAdmin


class FoodCategoryListView(generics.ListAPIView):
    serializer_class = FoodCategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        canteen_id = self.request.query_params.get('canteen')
        qs = FoodCategory.objects.filter(is_active=True)
        if canteen_id:
            qs = qs.filter(canteen_id=canteen_id)
        return qs


class FoodCategoryCreateView(generics.CreateAPIView):
    serializer_class = FoodCategorySerializer
    permission_classes = [IsCanteenAdmin]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'canteen_admin':
            canteen = user.canteen_admin_profile.canteen
            serializer.save(canteen=canteen)
        else:
            from canteens.models import Canteen
            canteen_id = self.request.data.get('canteen')
            canteen = Canteen.objects.filter(id=canteen_id).first() if canteen_id else Canteen.objects.first()
            serializer.save(canteen=canteen)


class FoodCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FoodCategorySerializer
    permission_classes = [IsCanteenAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return FoodCategory.objects.all()
        elif user.role == 'canteen_admin':
            return FoodCategory.objects.filter(canteen=user.canteen_admin_profile.canteen)
        return FoodCategory.objects.none()


class FoodItemListView(generics.ListAPIView):
    serializer_class = FoodItemListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'total_orders']

    def get_queryset(self):
        qs = FoodItem.objects.filter(is_available=True).select_related('canteen', 'category')
        canteen_id = self.request.query_params.get('canteen')
        category_id = self.request.query_params.get('category')
        is_veg = self.request.query_params.get('is_veg')
        is_featured = self.request.query_params.get('is_featured')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if canteen_id:
            qs = qs.filter(canteen_id=canteen_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if is_veg is not None and is_veg != '':
            qs = qs.filter(is_veg=is_veg.lower() in ['true', '1'])
        if is_featured is not None and is_featured != '':
            qs = qs.filter(is_featured=is_featured.lower() in ['true', '1'])
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs


class FoodItemDetailView(generics.RetrieveAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [AllowAny]
    queryset = FoodItem.objects.all()


class FoodItemCreateView(generics.CreateAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [IsCanteenAdmin]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'canteen_admin':
            canteen = user.canteen_admin_profile.canteen
            serializer.save(canteen=canteen)
        else:
            from canteens.models import Canteen
            canteen_id = self.request.data.get('canteen')
            canteen = Canteen.objects.filter(id=canteen_id).first() if canteen_id else Canteen.objects.first()
            serializer.save(canteen=canteen)


class FoodItemUpdateView(generics.UpdateAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [IsCanteenAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return FoodItem.objects.all()
        elif user.role == 'canteen_admin':
            return FoodItem.objects.filter(canteen=user.canteen_admin_profile.canteen)
        return FoodItem.objects.none()


class FoodItemDeleteView(generics.DestroyAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [IsCanteenAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return FoodItem.objects.all()
        elif user.role == 'canteen_admin':
            return FoodItem.objects.filter(canteen=user.canteen_admin_profile.canteen)
        return FoodItem.objects.none()


class AdminFoodItemListView(generics.ListAPIView):
    """List all items for canteen admin (including unavailable)"""
    serializer_class = FoodItemSerializer
    permission_classes = [IsCanteenAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'canteen_admin':
            return FoodItem.objects.filter(canteen=user.canteen_admin_profile.canteen)
        elif user.role == 'super_admin':
            canteen_id = self.request.query_params.get('canteen')
            if canteen_id:
                return FoodItem.objects.filter(canteen_id=canteen_id)
            return FoodItem.objects.all()
        return FoodItem.objects.none()


class AdminCategoryListView(generics.ListAPIView):
    """List all categories for canteen admin"""
    serializer_class = FoodCategorySerializer
    permission_classes = [IsCanteenAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'canteen_admin':
            return FoodCategory.objects.filter(canteen=user.canteen_admin_profile.canteen)
        elif user.role == 'super_admin':
            return FoodCategory.objects.all()
        return FoodCategory.objects.none()
