from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Canteen
from .serializers import CanteenSerializer, CanteenListSerializer


class CanteenListView(generics.ListAPIView):
    serializer_class = CanteenListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Canteen.objects.filter(is_active=True)


class CanteenDetailView(generics.RetrieveAPIView):
    serializer_class = CanteenSerializer
    permission_classes = [AllowAny]
    queryset = Canteen.objects.filter(is_active=True)


class CanteenCreateView(generics.CreateAPIView):
    serializer_class = CanteenSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only super admins can create canteens.")
        serializer.save()


class CanteenUpdateView(generics.UpdateAPIView):
    serializer_class = CanteenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Canteen.objects.all()
        elif user.role == 'canteen_admin':
            return Canteen.objects.filter(id=user.canteen_admin_profile.canteen.id)
        return Canteen.objects.none()
