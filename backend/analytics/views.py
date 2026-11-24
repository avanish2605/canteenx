from datetime import timedelta
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsCanteenAdmin, IsSuperAdmin
from accounts.models import User
from canteens.models import Canteen
from menu.models import FoodItem
from orders.models import Order, OrderItem, Payment


def get_admin_canteen(user):
    if user.role == 'canteen_admin':
        return getattr(user, 'canteen_admin_profile', None).canteen
    return None


class AdminDashboardView(APIView):
    permission_classes = [IsCanteenAdmin]

    def get(self, request):
        user = request.user
        canteen = get_admin_canteen(user)
        today = timezone.now().date()
        month_start = today.replace(day=1)

        orders_qs = Order.objects.all()
        items_qs = FoodItem.objects.all()

        if canteen:
            orders_qs = orders_qs.filter(canteen=canteen)
            items_qs = items_qs.filter(canteen=canteen)
        elif user.role == 'super_admin':
            canteen_id = request.query_params.get('canteen')
            if canteen_id:
                orders_qs = orders_qs.filter(canteen_id=canteen_id)
                items_qs = items_qs.filter(canteen_id=canteen_id)

        orders_today = orders_qs.filter(created_at__date=today)
        orders_month = orders_qs.filter(created_at__date__gte=month_start)

        revenue_today = orders_today.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        revenue_month = orders_month.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        pending_orders = orders_qs.filter(status='placed').count()
        preparing_orders = orders_qs.filter(status__in=['accepted', 'preparing']).count()
        ready_orders = orders_qs.filter(status='ready').count()
        completed_today = orders_today.filter(status='completed').count()

        popular_items = (
            items_qs.order_by('-total_orders')[:5]
            .values('id', 'name', 'price', 'total_orders', 'is_available')
        )

        return Response({
            'today_orders_count': orders_today.count(),
            'pending_orders': pending_orders,
            'preparing_orders': preparing_orders,
            'ready_orders': ready_orders,
            'completed_today': completed_today,
            'revenue_today': float(revenue_today),
            'revenue_month': float(revenue_month),
            'active_items_count': items_qs.filter(is_available=True).count(),
            'total_items_count': items_qs.count(),
            'popular_items': list(popular_items),
        })


class AdminAnalyticsView(APIView):
    permission_classes = [IsCanteenAdmin]

    def get(self, request):
        user = request.user
        canteen = get_admin_canteen(user)
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now().date() - timedelta(days=days - 1)

        orders_qs = Order.objects.filter(created_at__date__gte=start_date)
        if canteen:
            orders_qs = orders_qs.filter(canteen=canteen)
        elif user.role == 'super_admin':
            canteen_id = request.query_params.get('canteen')
            if canteen_id:
                orders_qs = orders_qs.filter(canteen_id=canteen_id)

        # Daily sales trend
        daily_sales = (
            orders_qs.filter(status='completed')
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(revenue=Sum('total_amount'), count=Count('id'))
            .order_by('date')
        )

        # Status distribution
        status_dist = (
            orders_qs.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Payment methods breakdown
        payment_dist = (
            orders_qs.values('payment_method')
            .annotate(count=Count('id'), total=Sum('total_amount'))
        )

        # Top 5 selling items
        top_items = (
            OrderItem.objects.filter(order__in=orders_qs, order__status='completed')
            .values('item_name')
            .annotate(total_qty=Sum('quantity'), total_rev=Sum('subtotal'))
            .order_by('-total_qty')[:5]
        )

        # Format daily sales to guarantee continuous dates
        daily_dict = {d['date'].strftime('%Y-%m-%d'): (float(d['revenue'] or 0), d['count']) for d in daily_sales}
        timeline = []
        for i in range(days):
            d = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            rev, cnt = daily_dict.get(d, (0.0, 0))
            timeline.append({
                'date': d,
                'revenue': rev,
                'orders': cnt
            })

        return Response({
            'timeline': timeline,
            'status_distribution': list(status_dist),
            'payment_distribution': list(payment_dist),
            'top_items': list(top_items),
        })


class AdminReportsView(APIView):
    permission_classes = [IsCanteenAdmin]

    def get(self, request):
        user = request.user
        canteen = get_admin_canteen(user)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        orders_qs = Order.objects.all()
        if canteen:
            orders_qs = orders_qs.filter(canteen=canteen)
        elif user.role == 'super_admin':
            canteen_id = request.query_params.get('canteen')
            if canteen_id:
                orders_qs = orders_qs.filter(canteen_id=canteen_id)

        if start_date:
            orders_qs = orders_qs.filter(created_at__date__gte=start_date)
        if end_date:
            orders_qs = orders_qs.filter(created_at__date__lte=end_date)

        completed_orders = orders_qs.filter(status='completed')
        total_revenue = completed_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = orders_qs.count()
        completed_count = completed_orders.count()
        cancelled_count = orders_qs.filter(status='cancelled').count()

        payment_breakdown = (
            orders_qs.values('payment_method')
            .annotate(count=Count('id'), total=Sum('total_amount'))
        )

        return Response({
            'total_orders': total_orders,
            'completed_orders': completed_count,
            'cancelled_orders': cancelled_count,
            'total_revenue': float(total_revenue),
            'payment_breakdown': list(payment_breakdown),
        })


class SuperAdminStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total_students = User.objects.filter(role='student').count()
        total_admins = User.objects.filter(role='canteen_admin').count()
        total_canteens = Canteen.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0

        canteen_summary = []
        for c in Canteen.objects.all():
            c_orders = Order.objects.filter(canteen=c)
            c_rev = c_orders.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
            canteen_summary.append({
                'id': c.id,
                'name': c.name,
                'location': c.location,
                'is_active': c.is_active,
                'total_orders': c_orders.count(),
                'revenue': float(c_rev),
            })

        return Response({
            'total_students': total_students,
            'total_canteen_admins': total_admins,
            'total_canteens': total_canteens,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'canteens': canteen_summary,
        })
