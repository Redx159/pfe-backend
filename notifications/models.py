from django.db import models
from employees.models import Employee


class NotificationPreference(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="notification_prefs"
    )
    meeting_invites = models.BooleanField(default=True)
    leave_status = models.BooleanField(default=True)
    reminders = models.BooleanField(default=True)
    vacation_mode = models.BooleanField(default=False)
    vacation_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Prefs: {self.employee}"


class Notification(models.Model):

    class TypeChoices(models.TextChoices):
        MEETING_INVITE = "MEETING_INVITE", "Meeting Invitation"
        MEETING_CANCELLED = "MEETING_CANCELLED", "Meeting Cancelled"
        LEAVE_APPROVED = "LEAVE_APPROVED", "Leave Approved"
        LEAVE_REJECTED = "LEAVE_REJECTED", "Leave Rejected"

    recipient = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=50, choices=TypeChoices.choices)
    is_read = models.BooleanField(default=False)
    related_link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] {self.title} → {self.recipient}"


class Device(models.Model):

    PLATFORM_CHOICES = [
        ("android", "Android"),
        ("ios", "iOS"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="devices"
    )
    fcm_token = models.TextField(unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee} ({self.platform})"
