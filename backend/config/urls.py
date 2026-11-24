from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    db_status = "connected"
    try:
        connection.ensure_connection()
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        "status": "online",
        "service": "CanteenX Backend API",
        "database": db_status,
        "endpoints": {
            "auth": "/api/auth/",
            "food": "/api/food/",
            "orders": "/api/orders/",
            "admin": "/admin/",
        }
    })

urlpatterns = [
    path('', health_check, name='root_health'),
    path('api/health/', health_check, name='api_health'),
    path('admin/', admin.site.urls),

    # Core modules
    path('api/auth/', include('accounts.urls')),
    path('api/canteens/', include('canteens.urls')),
    path('api/food/', include('menu.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/admin/', include('analytics.urls')),

    # Additional convenience alias routes matching the specification
    path('api/student/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
