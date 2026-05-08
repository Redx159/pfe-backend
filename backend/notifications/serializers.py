from rest_framework import serializers
from .models import Notification, Device


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "body",
            "type",
            "is_read",
            "related_link",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "title",
            "body",
            "type",
            "related_link",
            "created_at",
        ]


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ["fcm_token", "platform"]
