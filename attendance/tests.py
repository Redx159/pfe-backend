import io
import csv
import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def employee():
    from employees.models import Employee
    user = Employee.objects.create_user(
        username="testuser",
        password="testpass123",
        employee_id="EMP001",
        first_name="Test",
        last_name="User",
        role="EMPLOYEE",
        cp_balance=15,
        rtt_balance=5,
    )
    return user


@pytest.fixture
def hr_user():
    from employees.models import Employee
    user = Employee.objects.create_user(
        username="hruser",
        password="hrpass123",
        employee_id="EMP002",
        first_name="HR",
        last_name="User",
        role="HR",
        cp_balance=20,
        rtt_balance=10,
    )
    return user


@pytest.fixture
def other_employee():
    from employees.models import Employee
    user = Employee.objects.create_user(
        username="otheruser",
        password="otherpass123",
        employee_id="EMP003",
        first_name="Other",
        last_name="User",
        role="EMPLOYEE",
        cp_balance=10,
        rtt_balance=3,
    )
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, employee):
    api_client.force_authenticate(user=employee)
    return api_client


@pytest.fixture
def hr_client(api_client, hr_user):
    api_client.force_authenticate(user=hr_user)
    return api_client


class TestGenerateCheckInQR:
    def test_generates_checkin_qr(self, auth_client):
        resp = auth_client.post("/api/attendance/qr/checkin/generate/")
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["purpose"] == "CHECK_IN"
        assert "expires_at" in data

    def test_requires_auth(self, api_client):
        resp = api_client.post("/api/attendance/qr/checkin/generate/")
        assert resp.status_code in (401, 403)


class TestGenerateCheckOutQR:
    def test_generates_checkout_qr(self, auth_client):
        resp = auth_client.post("/api/attendance/qr/checkout/generate/")
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["purpose"] == "CHECK_OUT"
        assert "expires_at" in data

    def test_requires_auth(self, api_client):
        resp = api_client.post("/api/attendance/qr/checkout/generate/")
        assert resp.status_code in (401, 403)


class TestScanQR:
    def test_successful_checkin(self, auth_client, employee):
        qr, token = self._create_qr(employee, "CHECK_IN")
        resp = auth_client.post("/api/attendance/scan/", {"token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["purpose"] == "CHECK_IN"
        assert data["check_in"] is not None

        attendance = employee.attendances.first()
        assert attendance is not None
        assert attendance.check_in is not None
        assert attendance.status in ("ON_TIME", "LATE")

    def test_successful_checkout(self, auth_client, employee):
        today = timezone.localdate()
        from attendance.models import Attendance
        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=8, minutes=30),
        )
        qr, token = self._create_qr(employee, "CHECK_OUT")
        resp = auth_client.post("/api/attendance/scan/", {"token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["purpose"] == "CHECK_OUT"
        assert data["check_out"] is not None
        assert data["duration"] is not None

    def test_invalid_token(self, auth_client):
        resp = auth_client.post("/api/attendance/scan/", {"token": "00000000-0000-0000-0000-000000000000"})
        assert resp.status_code == 400
        assert resp.json()["error"] == "Invalid QR"

    def test_expired_qr(self, auth_client, employee):
        from attendance.models import DailyQR
        token = "11111111-1111-1111-1111-111111111111"
        DailyQR.objects.create(
            token=token,
            employee=employee,
            date=timezone.localdate(),
            expires_at=timezone.now() - timedelta(minutes=1),
            purpose="CHECK_IN",
        )
        resp = auth_client.post("/api/attendance/scan/", {"token": token})
        assert resp.status_code == 400
        assert resp.json()["error"] == "Expired or used QR"

    def test_used_qr(self, auth_client, employee):
        from attendance.models import DailyQR
        token = "22222222-2222-2222-2222-222222222222"
        DailyQR.objects.create(
            token=token,
            employee=employee,
            date=timezone.localdate(),
            expires_at=timezone.now() + timedelta(minutes=10),
            purpose="CHECK_IN",
            is_used=True,
        )
        resp = auth_client.post("/api/attendance/scan/", {"token": token})
        assert resp.status_code == 400
        assert resp.json()["error"] == "Expired or used QR"

    def test_already_checked_in(self, auth_client, employee):
        today = timezone.localdate()
        from attendance.models import Attendance
        Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=2),
        )
        qr, token = self._create_qr(employee, "CHECK_IN")
        resp = auth_client.post("/api/attendance/scan/", {"token": token})
        assert resp.status_code == 400
        assert resp.json()["error"] == "Already checked in"

    def test_checkout_without_checkin(self, auth_client, employee):
        qr, token = self._create_qr(employee, "CHECK_OUT")
        resp = auth_client.post("/api/attendance/scan/", {"token": token})
        assert resp.status_code == 400
        assert resp.json()["error"] == "Must check in first"

    def test_requires_auth(self, api_client):
        resp = api_client.post("/api/attendance/scan/", {"token": "some-token"})
        assert resp.status_code in (401, 403)

    def _create_qr(self, employee, purpose):
        from attendance.models import DailyQR
        import uuid
        token = str(uuid.uuid4())
        DailyQR.objects.create(
            token=token,
            employee=employee,
            date=timezone.localdate(),
            expires_at=timezone.now() + timedelta(minutes=10),
            purpose=purpose,
        )
        return None, token


class TestMyAttendance:
    def test_returns_own_attendance(self, auth_client, employee):
        from attendance.models import Attendance
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=8),
            check_out=timezone.now() - timedelta(hours=1),
        )
        Attendance.objects.create(
            employee=employee,
            date=yesterday,
            check_in=timezone.now() - timedelta(hours=8),
            check_out=timezone.now() - timedelta(hours=1),
        )
        resp = auth_client.get("/api/attendance/my/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["employee_name"] == "Test User"

    def test_empty_when_no_attendance(self, auth_client):
        resp = auth_client.get("/api/attendance/my/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_requires_auth(self, api_client):
        resp = api_client.get("/api/attendance/my/")
        assert resp.status_code in (401, 403)


class TestExportAttendanceCSV:
    def test_export_returns_csv(self, hr_client, employee):
        from attendance.models import Attendance
        today = timezone.localdate()
        Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=8),
            check_out=timezone.now() - timedelta(hours=1),
            status="ON_TIME",
            work_duration=timedelta(hours=7),
            overtime_minutes=0,
        )
        resp = hr_client.get("/api/attendance/export/")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "text/csv"
        content = resp.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["Employee", "Date", "Status", "Check In", "Check Out", "Work Duration", "Overtime Minutes"]
        assert rows[1][0] == "Test User"
        assert rows[1][2] == "ON_TIME"

    def test_export_filters_by_month(self, hr_client, employee):
        from attendance.models import Attendance
        today = timezone.localdate()
        last_month = today.replace(day=1) - timedelta(days=1)
        last_month = last_month.replace(day=1)
        Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=8),
            status="ON_TIME",
        )
        Attendance.objects.create(
            employee=employee,
            date=last_month,
            check_in=timezone.now() - timedelta(hours=8),
            status="LATE",
        )
        month_str = today.strftime("%Y-%m")
        resp = hr_client.get(f"/api/attendance/export/?month={month_str}")
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 2

    def test_export_filters_by_status(self, hr_client, employee):
        from attendance.models import Attendance
        today = timezone.localdate()
        Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=8),
            status="ON_TIME",
        )
        resp = hr_client.get("/api/attendance/export/?status=ON_TIME")
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 2

    def test_requires_hr_permission(self, auth_client):
        resp = auth_client.get("/api/attendance/export/")
        assert resp.status_code == 403


class TestMobileDashboardView:
    def test_returns_correct_structure(self, auth_client, employee):
        resp = auth_client.get("/api/dashboard/")
        assert resp.status_code == 200
        data = resp.json()
        assert "needs_checkin" in data
        assert "needs_checkout" in data
        assert "cp_balance" in data
        assert "rtt_balance" in data
        assert "upcoming_meeting" in data
        assert "unread_notifications" in data
        assert "attendance_today" in data

    def test_needs_checkin_when_no_attendance_today(self, auth_client):
        resp = auth_client.get("/api/dashboard/")
        data = resp.json()
        assert data["needs_checkin"] is True
        assert data["needs_checkout"] is False
        assert data["attendance_today"] is None

    def test_needs_checkout_when_checked_in_not_out(self, auth_client, employee):
        from attendance.models import Attendance
        today = timezone.localdate()
        Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now() - timedelta(hours=3),
        )
        resp = auth_client.get("/api/dashboard/")
        data = resp.json()
        assert data["needs_checkin"] is False
        assert data["needs_checkout"] is True

    def test_balances_returned(self, auth_client, employee):
        resp = auth_client.get("/api/dashboard/")
        data = resp.json()
        assert data["cp_balance"] == 15
        assert data["rtt_balance"] == 5

    def test_upcoming_meeting_included(self, auth_client, employee):
        from meetings.models import Meeting
        future = timezone.now() + timedelta(hours=2)
        Meeting.objects.create(
            title="Sprint Review",
            start_time=future,
            end_time=future + timedelta(hours=1),
            created_by=employee,
        )
        resp = auth_client.get("/api/dashboard/")
        data = resp.json()
        assert data["upcoming_meeting"] is not None
        assert data["upcoming_meeting"]["title"] == "Sprint Review"
        assert data["upcoming_meeting"]["countdown_seconds"] >= 0

    def test_unread_notifications_count(self, auth_client, employee):
        from notifications.models import Notification
        Notification.objects.create(
            recipient=employee,
            title="Test Notification",
            body="Test body",
            type="MEETING_INVITE",
        )
        resp = auth_client.get("/api/dashboard/")
        data = resp.json()
        assert data["unread_notifications"] == 1

    def test_requires_auth(self, api_client):
        resp = api_client.get("/api/dashboard/")
        assert resp.status_code in (401, 403)
