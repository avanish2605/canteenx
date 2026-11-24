from django.urls import path
from .views import (
    AdminDashboardView, AdminAnalyticsView,
    AdminReportsView, SuperAdminStatsView
)

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('analytics/', AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('reports/', AdminReportsView.as_view(), name='admin_reports'),
    path('superadmin/stats/', SuperAdminStatsView.as_view(), name='superadmin_stats'),
]
