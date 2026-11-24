from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')


class IsCanteenAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['canteen_admin', 'super_admin'])


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'super_admin')


class IsCanteenOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == 'super_admin':
            return True
        if request.user.role == 'canteen_admin':
            admin_profile = getattr(request.user, 'canteen_admin_profile', None)
            if not admin_profile:
                return False
            # If obj is Canteen
            if hasattr(obj, 'id') and obj.__class__.__name__ == 'Canteen':
                return obj.id == admin_profile.canteen.id
            # If obj has canteen attribute (FoodItem, Order, Category)
            if hasattr(obj, 'canteen'):
                return obj.canteen.id == admin_profile.canteen.id
        return False
