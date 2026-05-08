from django.contrib import admin
from .models import Notification, Device


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "recipient", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["employee", "platform", "created_at"]
