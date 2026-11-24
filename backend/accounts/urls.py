from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    ChangePasswordView, SuperAdminUserListView,
    SuperAdminToggleUserActiveView, SuperAdminCreateCanteenAdminView,
    ForgotPasswordView, ResetPasswordConfirmView,
    VerifyOTPView, ResendOTPView, DebugEmailView,
)

urlpatterns = [
    path('debug-email/', DebugEmailView.as_view(), name='debug_email'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('users/', SuperAdminUserListView.as_view(), name='user_list'),
    path('users/<int:pk>/toggle-active/', SuperAdminToggleUserActiveView.as_view(), name='toggle_user_active'),
    path('create-canteen-admin/', SuperAdminCreateCanteenAdminView.as_view(), name='create_canteen_admin'),
]
