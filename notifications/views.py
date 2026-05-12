from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification, Device, NotificationPreference
from .serializers import NotificationSerializer, DeviceSerializer, NotificationPreferenceSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"success": True})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({"success": True})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})


class DeviceViewSet(viewsets.GenericViewSet):

    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Device.objects.update_or_create(
            employee=request.user,
            defaults={
                "fcm_token": serializer.validated_data["fcm_token"],
                "platform": serializer.validated_data["platform"],
            },
        )
        return Response({"success": True}, status=status.HTTP_201_CREATED)


class NotificationPreferenceViewSet(viewsets.GenericViewSet):

    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(
            employee=request.user
        )
        serializer = self.get_serializer(prefs)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        prefs, _ = NotificationPreference.objects.get_or_create(
            employee=request.user
        )
        serializer = self.get_serializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
