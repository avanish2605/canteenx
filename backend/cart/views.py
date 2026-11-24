from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import FoodItem
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(student=user)
    return cart


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        cart = get_or_create_cart(request.user)
        cart.items.all().delete()
        cart.canteen = None
        cart.save()
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        food_item = FoodItem.objects.get(id=serializer.validated_data['food_item_id'])
        quantity = serializer.validated_data['quantity']
        cart = get_or_create_cart(request.user)

        # Enforce single-canteen cart
        if cart.canteen and cart.canteen != food_item.canteen:
            return Response(
                {'error': 'Cart can only contain items from one canteen. Clear cart first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.canteen = food_item.canteen
        cart.save()

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            food_item=food_item,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = get_or_create_cart(request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

        quantity = serializer.validated_data['quantity']
        if quantity == 0:
            cart_item.delete()
            # Clear canteen if cart is now empty
            if not cart.items.exists():
                cart.canteen = None
                cart.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id):
        try:
            cart = get_or_create_cart(request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            if not cart.items.exists():
                cart.canteen = None
                cart.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CartSerializer(cart).data)
