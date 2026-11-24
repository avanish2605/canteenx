from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, CanteenAdminProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'mobile', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'mobile')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'mobile')}),
        ('Permissions & Roles', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password', 'role', 'is_staff', 'is_active'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_number', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'enrollment_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CanteenAdminProfile)
class CanteenAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'canteen', 'created_at')
    list_filter = ('canteen',)
    search_fields = ('user__email', 'user__full_name', 'canteen__name')
    readonly_fields = ('created_at',)
