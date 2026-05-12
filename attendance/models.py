from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class Attendance(models.Model):

    STATUS_CHOICES = [
        ("ON_TIME", "On Time"),
        ("LATE", "Late"),
        ("ABSENT", "Absent"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendances",
    )

    date = models.DateField()

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    work_duration = models.DurationField(null=True, blank=True)
    overtime_minutes = models.IntegerField(default=0)


    location = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ON_TIME",
    )


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "date")

    def __str__(self):
        return f"{self.employee} - {self.date}"





class DailyQR(models.Model):

    PURPOSE_CHOICES = [
        ("CHECK_IN", "Check In"),
        ("CHECK_OUT", "Check Out"),
    ]

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    date = models.DateField()

    expires_at = models.DateTimeField()

    purpose = models.CharField(
        max_length=15,
        choices=PURPOSE_CHOICES,
    )

    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return (
            self.date == timezone.localdate()
            and timezone.now() < self.expires_at
            and not self.is_used
        )

