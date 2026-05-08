from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import Attendance
from notifications.models import Notification, Device
from notifications.fcm_service import send_push_notification


class Command(BaseCommand):
    help = "Send push notification to employees who checked in but forgot to check out"

    def handle(self, *args, **options):
        now = timezone.now()
        cutoff = now.replace(hour=19, minute=0, second=0, microsecond=0)

        if now < cutoff:
            self.stdout.write(f"Before 19:00 ({now.hour}:{now.minute}), skipping")
            return

        today = now.date()
        yesterday = today - timedelta(days=1)

        forgotten = Attendance.objects.filter(
            check_in__isnull=False,
            check_out__isnull=True,
            date__gte=yesterday,
        ).select_related("employee")

        sent = 0
        for att in forgotten:
            employee = att.employee
            notification = Notification.objects.create(
                recipient=employee,
                title="Check-out Reminder",
                body=f"You checked in today but haven't checked out yet. Please scan the QR to check out.",
                type="CHECKOUT_REMINDER",
            )

            devices = Device.objects.filter(employee=employee)
            for device in devices:
                send_push_notification(
                    device.fcm_token,
                    notification.title,
                    notification.body,
                    data={"type": "CHECKOUT_REMINDER", "id": str(notification.id)},
                )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} check-out reminders"))
