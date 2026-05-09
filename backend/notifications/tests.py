import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from employees.models import Employee
from notifications.models import Notification, Device, NotificationPreference

pytestmark = pytest.mark.django_db


@pytest.fixture
def employee():
    return Employee.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        employee_id="EMP001",
        position="Developer",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def auth_client(employee):
    client = APIClient()
    client.force_authenticate(user=employee)
    return client


class TestNotificationViewSet:
    def test_list_empty(self, auth_client):
        url = reverse("notification-list")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_create_and_list(self, auth_client, employee):
        Notification.objects.create(
            recipient=employee,
            title="Test Notification",
            body="This is a test body",
            type=Notification.TypeChoices.MEETING_INVITE,
        )
        url = reverse("notification-list")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Test Notification"
        assert response.data["results"][0]["is_read"] is False

    def test_mark_read(self, auth_client, employee):
        notification = Notification.objects.create(
            recipient=employee,
            title="Test",
            body="Body",
            type=Notification.TypeChoices.MEETING_INVITE,
        )
        url = reverse("notification-mark-read", kwargs={"pk": notification.pk})
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.data == {"success": True}
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_all_read(self, auth_client, employee):
        Notification.objects.create(
            recipient=employee,
            title="N1",
            body="B1",
            type=Notification.TypeChoices.MEETING_INVITE,
        )
        Notification.objects.create(
            recipient=employee,
            title="N2",
            body="B2",
            type=Notification.TypeChoices.LEAVE_APPROVED,
        )
        url = reverse("notification-mark-all-read")
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.data == {"success": True}
        assert Notification.objects.filter(recipient=employee, is_read=True).count() == 2

    def test_unread_count(self, auth_client, employee):
        Notification.objects.create(
            recipient=employee,
            title="Read",
            body="B",
            type=Notification.TypeChoices.MEETING_INVITE,
            is_read=True,
        )
        Notification.objects.create(
            recipient=employee,
            title="Unread",
            body="B",
            type=Notification.TypeChoices.LEAVE_APPROVED,
        )
        url = reverse("notification-unread-count")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data == {"count": 1}


class TestDeviceViewSet:
    def test_register_device(self, auth_client):
        url = reverse("device-list")
        data = {"fcm_token": "test-token", "platform": "android"}
        response = auth_client.post(url, data, format="json")
        assert response.status_code == 201
        assert response.data == {"success": True}
        assert Device.objects.count() == 1

    def test_register_device_updates_existing(self, auth_client, employee):
        Device.objects.create(employee=employee, fcm_token="old-token", platform="ios")
        url = reverse("device-list")
        data = {"fcm_token": "new-token", "platform": "android"}
        response = auth_client.post(url, data, format="json")
        assert response.status_code == 201
        assert Device.objects.count() == 1
        device = Device.objects.get(employee=employee)
        assert device.fcm_token == "new-token"
        assert device.platform == "android"


class TestNotificationPreferenceViewSet:
    def test_get_preferences_creates_defaults(self, auth_client):
        url = reverse("preference-list")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data["meeting_invites"] is True
        assert response.data["leave_status"] is True
        assert response.data["reminders"] is True
        assert response.data["vacation_mode"] is False
        assert response.data["vacation_until"] is None

    def test_update_preferences(self, auth_client, employee):
        prefs = NotificationPreference.objects.get_or_create(employee=employee)[0]
        url = reverse("preference-detail", kwargs={"pk": prefs.pk})
        data = {"meeting_invites": False, "reminders": False}
        response = auth_client.patch(url, data, format="json")
        assert response.status_code == 200
        assert response.data["meeting_invites"] is False
        assert response.data["reminders"] is False
        assert response.data["leave_status"] is True
