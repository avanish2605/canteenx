from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from notifications.models import Notification
from notifications.services import dispatch_order_notifications
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.prefetch_related('items__food_item').get(student=request.user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.canteen:
            return Response({'error': 'No canteen assigned to cart.'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = sum(item.subtotal for item in cart.items.all())
        tax = subtotal * Decimal('0.00')
        total = subtotal + tax

        order = Order.objects.create(
            student=request.user,
            canteen=cart.canteen,
            subtotal=subtotal,
            tax_amount=tax,
            total_amount=total,
            payment_method=serializer.validated_data.get('payment_method', 'cash'),
            special_instructions=serializer.validated_data.get('special_instructions', ''),
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                food_item=cart_item.food_item,
                item_name=cart_item.food_item.name,
                item_price=cart_item.food_item.price,
                quantity=cart_item.quantity,
            )
            cart_item.food_item.total_orders += cart_item.quantity
            cart_item.food_item.save(update_fields=['total_orders'])

        # Clear cart
        cart.items.all().delete()
        cart.canteen = None
        cart.save()

        # Create payment record
        Payment.objects.create(order=order, amount=total, method=order.payment_method)

        # Notify canteen admin
        try:
            from accounts.models import CanteenAdminProfile
            admin_profiles = CanteenAdminProfile.objects.filter(canteen=order.canteen)
            for ap in admin_profiles:
                Notification.objects.create(
                    recipient=ap.user,
                    title='New Order Pending Acceptance',
                    message=f'Order #{order.order_number} placed by {request.user.full_name}. Needs your acceptance.',
                    notification_type='new_order',
                    related_order=order,
                )
        except Exception as e:
            print(f"[Admin In-App Notification Error] {e}")

        # Dispatch multi-channel notifications via on_commit so external service issues NEVER rollback order
        order_id = order.id
        def send_order_notifs():
            try:
                fresh_order = Order.objects.get(id=order_id)
                dispatch_order_notifications(fresh_order, 'placed', async_delivery=True)
            except Exception as e:
                print(f"[Order Notification Dispatch Error] {e}")

        transaction.on_commit(send_order_notifs)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class StudentOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(student=self.request.user).prefetch_related('items', 'payment').order_by('-created_at')

    def post(self, request, *args, **kwargs):
        return OrderCreateView().post(request)


class StudentOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(student=self.request.user)


class CanteenOrderListView(generics.ListAPIView):
    """Canteen admin view - list orders for their canteen (newest first)"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'canteen_admin':
            profile = getattr(user, 'canteen_admin_profile', None)
            if not profile or not profile.canteen:
                return Order.objects.none()
            canteen = profile.canteen
        elif user.role == 'super_admin':
            canteen_id = self.request.query_params.get('canteen')
            if canteen_id:
                from canteens.models import Canteen
                try:
                    canteen = Canteen.objects.get(id=canteen_id)
                except Canteen.DoesNotExist:
                    return Order.objects.none()
            else:
                qs = Order.objects.all().prefetch_related('items', 'payment').order_by('-created_at')
                status_filter = self.request.query_params.get('status')
                date = self.request.query_params.get('date')
                if status_filter:
                    qs = qs.filter(status=status_filter.lower())
                if date:
                    qs = qs.filter(created_at__date=date)
                return qs
        else:
            return Order.objects.none()

        qs = Order.objects.filter(canteen=canteen).prefetch_related('items', 'payment').order_by('-created_at')
        status_filter = self.request.query_params.get('status')
        date = self.request.query_params.get('date')

        if status_filter:
            qs = qs.filter(status=status_filter.lower())
        if date:
            qs = qs.filter(created_at__date=date)
        return qs


class OrderStatusUpdateView(APIView):
    """Canteen admin updates order status"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        user = request.user
        if user.role not in ['canteen_admin', 'super_admin']:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            if user.role == 'canteen_admin':
                order = Order.objects.get(id=order_id, canteen=user.canteen_admin_profile.canteen)
            else:
                order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_status = order.status
        new_status = serializer.validated_data['status']
        order.status = new_status
        if new_status == 'cancelled':
            order.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')

        # Handle estimated completion / preparation time
        prep_minutes = serializer.validated_data.get('estimated_prep_minutes')
        if prep_minutes is not None:
            order.estimated_prep_minutes = prep_minutes
            order.estimated_ready_at = timezone.now() + timedelta(minutes=prep_minutes)

        order.save()

        # Multi-channel notification dispatch (non-blocking)
        try:
            dispatch_order_notifications(order, new_status, async_delivery=True)
        except Exception as e:
            print(f"[Status Notification Error] {e}")

        return Response(OrderSerializer(order).data)


class CancelOrderView(APIView):
    """Student cancels their own order"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, student=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in ['placed']:
            return Response(
                {'error': 'Only placed orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.cancellation_reason = request.data.get('reason', 'Cancelled by student')
        order.save()

        # Multi-channel notification for student cancellation (non-blocking)
        try:
            dispatch_order_notifications(order, 'cancelled', async_delivery=True)
        except Exception as e:
            print(f"[Cancel Notification Error] {e}")

        return Response(OrderSerializer(order).data)


class RateOrderView(APIView):
    """Student rates their completed order (1 to 5 stars + review)"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, student=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        rating = request.data.get('rating')
        if not rating or int(rating) < 1 or int(rating) > 5:
            return Response({'error': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        order.rating = int(rating)
        order.review = request.data.get('review', '')
        order.save()

        return Response(OrderSerializer(order).data)


class VerifyOrderPinView(APIView):
    """Canteen staff verifies student pickup PIN for fast counter handover"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role not in ['canteen_admin', 'super_admin']:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        pin = request.data.get('pickup_pin', '').strip()
        if not pin:
            return Response({'error': 'PIN is required.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Order.objects.filter(pickup_pin=pin)
        if user.role == 'canteen_admin':
            qs = qs.filter(canteen=user.canteen_admin_profile.canteen)

        order = qs.first()
        if not order:
            return Response({'error': f'No order found with PIN {pin}.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderSerializer(order).data)
