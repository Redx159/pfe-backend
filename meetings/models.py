from django.db import models
from employees.models import Employee


class Meeting(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    created_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="created_meetings",
    )

    is_online = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    is_cancelled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MeetingParticipant(models.Model):

    STATUS_CHOICES = [
        ("INVITED", "Invited"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="meeting_participations",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="INVITED",
    )

    responded_at = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)

    class Meta:
        unique_together = ("meeting", "employee")

    def __str__(self):
        return f"{self.employee} → {self.meeting}"
