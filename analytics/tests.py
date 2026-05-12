import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from employees.models import Employee, Department
from attendance.models import Attendance
from leaves.models import LeaveRequest

pytestmark = pytest.mark.django_db


@pytest.fixture
def employee():
    dept = Department.objects.create(name="Engineering")
    return Employee.objects.create_user(
        username="johndoe",
        password="testpass123",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        employee_id="EMP001",
        department=dept,
        position="Developer",
    )


@pytest.fixture
def auth_client(employee):
    client = APIClient()
    client.force_authenticate(user=employee)
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def attendance_today(employee):
    return Attendance.objects.create(
        employee=employee,
        date=timezone.localdate(),
        check_in=timezone.now(),
        status="ON_TIME",
    )


@pytest.fixture
def leave_pending(employee):
    today = timezone.localdate()
    return LeaveRequest.objects.create(
        employee=employee,
        start_date=today,
        end_date=today + timedelta(days=2),
        leave_type="CP",
        status="PENDING",
        reason="Vacation",
    )


class TestDashboard:
    def test_unauthenticated(self, api_client):
        response = api_client.get("/api/analytics/dashboard/")
        assert response.status_code in (401, 403)

    def test_dashboard_structure(self, auth_client, attendance_today, leave_pending):
        response = auth_client.get("/api/analytics/dashboard/")
        assert response.status_code == 200
        data = response.json()

        assert data["total_employees"] == 1
        assert data["present_today"] == 1
        assert data["on_leave_today"] == 0
        assert data["late_today"] == 0
        assert data["absent_today"] == 0
        assert data["pending_leaves"] == 1
        assert data["attendance_rate"] == 100.0

        assert isinstance(data["monthly_trend"], list)
        assert len(data["monthly_trend"]) >= 1
        entry = data["monthly_trend"][0]
        assert "month" in entry
        assert "rate" in entry
        assert "total" in entry
        assert "present" in entry
        assert "late" in entry
        assert "absent" in entry

        assert isinstance(data["leave_by_type"], list)
        assert isinstance(data["department_stats"], list)
        assert len(data["department_stats"]) == 1
        dept = data["department_stats"][0]
        assert dept["name"] == "Engineering"
        assert dept["total"] == 1
        assert dept["present"] == 1
        assert dept["late"] == 0


class TestReport:
    def test_report_pdf(self, auth_client):
        response = auth_client.get("/api/analytics/report/?export_format=pdf")
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert "Content-Disposition" in response
        assert response["Content-Disposition"].startswith("attachment;")
        assert len(response.content) > 0

    def test_report_unauthenticated(self):
        response = APIClient().get("/api/analytics/report/?export_format=pdf")
        assert response.status_code in (401, 403)
