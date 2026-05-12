from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from meetings.models import Meeting, MeetingParticipant
from leaves.models import LeaveRequest
from .models import Notification, Device, NotificationPreference
from .fcm_service import send_push_notification


def _notify_and_push(notification, employee):
    devices = Device.objects.filter(employee=employee)
    for device in devices:
        send_push_notification(
            device.fcm_token,
            notification.title,
            notification.body,
            data={"type": notification.type, "id": str(notification.id)},
        )


def _can_notify(employee, notification_type):
    try:
        prefs = employee.notification_prefs
    except NotificationPreference.DoesNotExist:
        prefs = NotificationPreference.objects.create(employee=employee)

    if prefs.vacation_mode:
        return False

    if notification_type == Notification.TypeChoices.MEETING_INVITE:
        return prefs.meeting_invites
    if notification_type == Notification.TypeChoices.MEETING_CANCELLED:
        return prefs.meeting_invites
    if notification_type in (
        Notification.TypeChoices.LEAVE_APPROVED,
        Notification.TypeChoices.LEAVE_REJECTED,
    ):
        return prefs.leave_status
    return True


@receiver(post_save, sender=MeetingParticipant)
def notify_meeting_invite(sender, instance, created, **kwargs):
    if not created:
        return

    if not _can_notify(instance.employee, Notification.TypeChoices.MEETING_INVITE):
        return

    meeting = instance.meeting
    notification = Notification.objects.create(
        recipient=instance.employee,
        title=f"Meeting Invitation: {meeting.title}",
        body=f"You have been invited to '{meeting.title}' on {meeting.start_time.strftime('%d %b %Y at %H:%M')}.",
        type=Notification.TypeChoices.MEETING_INVITE,
        related_link=f"/meetings/{meeting.id}",
    )
    _notify_and_push(notification, instance.employee)


@receiver(pre_save, sender=Meeting)
def track_meeting_cancelled(sender, instance, **kwargs):
    if instance.pk is None:
        instance._was_cancelled = False
        return
    try:
        original = Meeting.objects.get(pk=instance.pk)
        instance._was_cancelled = not original.is_cancelled and instance.is_cancelled
    except Meeting.DoesNotExist:
        instance._was_cancelled = False


@receiver(post_save, sender=Meeting)
def notify_meeting_cancelled(sender, instance, created, **kwargs):
    if created or not getattr(instance, "_was_cancelled", False):
        return

    participants = instance.participants.select_related("employee")
    for participant in participants:
        if not _can_notify(participant.employee, Notification.TypeChoices.MEETING_CANCELLED):
            continue

        notification = Notification.objects.create(
            recipient=participant.employee,
            title=f"Meeting Cancelled: {instance.title}",
            body=f"'{instance.title}' scheduled on {instance.start_time.strftime('%d %b %Y at %H:%M')} has been cancelled.",
            type=Notification.TypeChoices.MEETING_CANCELLED,
            related_link=f"/meetings/{instance.id}",
        )
        _notify_and_push(notification, participant.employee)


@receiver(pre_save, sender=LeaveRequest)
def track_leave_status_change(sender, instance, **kwargs):
    if instance.pk is None:
        instance._old_status = None
        return
    try:
        original = LeaveRequest.objects.get(pk=instance.pk)
        instance._old_status = original.status
    except LeaveRequest.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=LeaveRequest)
def notify_leave_status_change(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)
    if old_status == instance.status:
        return

    if instance.status not in ("APPROVED", "REJECTED"):
        return

    type_choice = (
        Notification.TypeChoices.LEAVE_APPROVED
        if instance.status == "APPROVED"
        else Notification.TypeChoices.LEAVE_REJECTED
    )

    if not _can_notify(instance.employee, type_choice):
        return

    status_label = "approved" if instance.status == "APPROVED" else "rejected"
    notification = Notification.objects.create(
        recipient=instance.employee,
        title=f"Leave {status_label.capitalize()}",
        body=f"Your {instance.leave_type} leave request ({instance.start_date} -> {instance.end_date}) has been {status_label}.",
        type=type_choice,
        related_link=f"/leaves/{instance.id}",
    )
    _notify_and_push(notification, instance.employee)
