from datetime import date, timedelta
import pytest
import csv
import io

from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from leaves.models import LeaveRequest
from leaves.utils import count_workdays

pytestmark = pytest.mark.django_db

Employee = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def employee():
    return Employee.objects.create_user(
        username="employee1",
        password="testpass123",
        employee_id="EMP-001",
        role="EMPLOYEE",
        first_name="John",
        last_name="Doe",
        cp_balance=25,
        rtt_balance=10,
    )


@pytest.fixture
def manager():
    return Employee.objects.create_user(
        username="manager1",
        password="testpass123",
        employee_id="EMP-002",
        role="MANAGER",
        first_name="Jane",
        last_name="Smith",
        cp_balance=25,
        rtt_balance=10,
    )


@pytest.fixture
def admin_user():
    return Employee.objects.create_user(
        username="admin1",
        password="testpass123",
        employee_id="EMP-003",
        role="ADMIN",
        first_name="Admin",
        last_name="User",
        cp_balance=25,
        rtt_balance=10,
    )


@pytest.fixture
def authenticated_client(employee):
    client = APIClient()
    client.force_authenticate(user=employee)
    return client


@pytest.fixture
def manager_client(manager):
    client = APIClient()
    client.force_authenticate(user=manager)
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def leave_data():
    tomorrow = date.today() + timedelta(days=1)
    day_after = tomorrow + timedelta(days=4)
    return {
        "start_date": tomorrow.isoformat(),
        "end_date": day_after.isoformat(),
        "leave_type": "CP",
        "reason": "Annual vacation",
    }


class TestCreateLeaveRequest:

    def test_create_leave_as_employee(self, authenticated_client, leave_data):
        response = authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        assert response.status_code == 201
        assert LeaveRequest.objects.count() == 1
        leave = LeaveRequest.objects.first()
        assert leave.employee == authenticated_client.handler._force_user

    def test_create_leave_requires_authentication(self, api_client, leave_data):
        response = api_client.post("/api/leaves/leaves/", leave_data, format="json")
        assert response.status_code in (401, 403)

    def test_create_leave_returns_serialized_data(self, authenticated_client, leave_data, employee):
        response = authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        assert response.status_code == 201
        assert response.data["employee"]["id"] == employee.id
        assert response.data["status"] == "PENDING"
        assert response.data["leave_type"] == "CP"


class TestListLeaves:

    def test_employee_sees_only_own_leaves(self, authenticated_client, employee, manager, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        manager_client = APIClient()
        manager_client.force_authenticate(user=manager)
        another_data = dict(leave_data)
        another_data["leave_type"] = "RTT"
        manager_client.post("/api/leaves/leaves/", another_data, format="json")
        response = authenticated_client.get("/api/leaves/leaves/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_manager_sees_own_and_team_leaves(self, authenticated_client, employee, manager, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        manager_client = APIClient()
        manager_client.force_authenticate(user=manager)
        another_data = dict(leave_data)
        another_data["leave_type"] = "RTT"
        manager_client.post("/api/leaves/leaves/", another_data, format="json")
        response = manager_client.get("/api/leaves/leaves/")
        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_admin_sees_all_leaves(self, admin_client, employee, manager, leave_data):
        emp_client = APIClient()
        emp_client.force_authenticate(user=employee)
        emp_client.post("/api/leaves/leaves/", leave_data, format="json")
        mgr_client = APIClient()
        mgr_client.force_authenticate(user=manager)
        another_data = dict(leave_data)
        another_data["leave_type"] = "SICK"
        mgr_client.post("/api/leaves/leaves/", another_data, format="json")
        response = admin_client.get("/api/leaves/leaves/")
        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_filter_by_status(self, authenticated_client, employee, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        another_data = dict(leave_data)
        another_data["leave_type"] = "RTT"
        authenticated_client.post("/api/leaves/leaves/", another_data, format="json")
        leave = LeaveRequest.objects.last()
        leave.status = "APPROVED"
        leave.save()
        response = authenticated_client.get("/api/leaves/leaves/pending/")
        assert response.status_code == 200
        for item in response.data:
            assert item["status"] == "PENDING"


class TestApproveLeave:

    def test_manager_can_approve_pending_leave(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "Approved"},
            format="json",
        )
        assert response.status_code == 200
        leave.refresh_from_db()
        assert leave.status == "APPROVED"
        assert leave.manager_comment == "Approved"

    def test_approve_deducts_cp_balance(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        days = leave.duration_days
        old_balance = employee.cp_balance
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "Approved"},
            format="json",
        )
        employee.refresh_from_db()
        assert employee.cp_balance == old_balance - days

    def test_approve_requires_comment(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_employee_cannot_approve(self, authenticated_client, employee, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "Approved"},
            format="json",
        )
        assert response.status_code in (403, 404)

    def test_approve_rejected_leave_returns_error(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        leave.status = "REJECTED"
        leave.save()
        response = manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "Approved"},
            format="json",
        )
        assert response.status_code == 400

    def test_approve_insufficient_cp_balance(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.cp_balance = 1
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "Approved"},
            format="json",
        )
        assert response.status_code == 400
        assert "balance" in response.data["error"].lower()


class TestRejectLeave:

    def test_manager_can_reject_pending_leave(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = manager_client.post(
            f"/api/leaves/leaves/{leave.id}/reject/",
            {"manager_comment": "Not approved"},
            format="json",
        )
        assert response.status_code == 200
        leave.refresh_from_db()
        assert leave.status == "REJECTED"

    def test_reject_requires_comment(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = manager_client.post(
            f"/api/leaves/leaves/{leave.id}/reject/",
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_employee_cannot_reject(self, authenticated_client, employee, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/reject/",
            {"manager_comment": "Rejected"},
            format="json",
        )
        assert response.status_code in (403, 404)


class TestCancelLeave:

    def test_owner_can_cancel_pending_leave(self, authenticated_client, employee, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        response = authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/cancel/",
            format="json",
        )
        assert response.status_code == 200
        leave.refresh_from_db()
        assert leave.status == "CANCELLED"

    def test_owner_can_cancel_approved_leave(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        response = authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/cancel/",
            format="json",
        )
        assert response.status_code == 200
        leave.refresh_from_db()
        assert leave.status == "CANCELLED"

    def test_other_user_cannot_cancel(self, api_client, employee, manager, authenticated_client, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        api_client.force_authenticate(user=manager)
        response = api_client.post(
            f"/api/leaves/leaves/{leave.id}/cancel/",
            format="json",
        )
        assert response.status_code in (403, 404)

    def test_cannot_cancel_rejected_leave(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/reject/",
            {"manager_comment": "No"},
            format="json",
        )
        response = authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/cancel/",
            format="json",
        )
        assert response.status_code == 400


class TestLeaveHistory:

    def test_history_returns_aggregated_data(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        response = authenticated_client.get("/api/leaves/leaves/history/")
        assert response.status_code == 200
        assert response.data["year"] == date.today().year
        assert response.data["total_days_used"] > 0
        assert "CP" in response.data["by_type"]

    def test_history_with_year_param(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        response = authenticated_client.get(f"/api/leaves/leaves/history/?year={date.today().year}")
        assert response.status_code == 200
        assert response.data["year"] == date.today().year


class TestLeaveProjections:

    def test_projections_returns_expected_structure(self, authenticated_client, employee):
        response = authenticated_client.get("/api/leaves/leaves/projections/")
        assert response.status_code == 200
        assert "cp" in response.data
        assert "rtt" in response.data
        assert "projected_end_of_year" in response.data
        assert response.data["cp"]["initial"] == 25
        assert response.data["rtt"]["initial"] == 10
        assert response.data["cp"]["remaining"] == employee.cp_balance

    def test_projections_accounts_for_pending_leaves(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        response = authenticated_client.get("/api/leaves/leaves/projections/")
        assert response.status_code == 200
        pending_cp = response.data["cp"]["pending"]
        assert pending_cp > 0


class TestExportLeavesCSV:

    def test_export_returns_csv(self, authenticated_client, leave_data, employee):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        response = authenticated_client.get("/api/leaves/leaves/export/")
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"

    def test_export_csv_content(self, authenticated_client, leave_data, employee):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        response = authenticated_client.get("/api/leaves/leaves/export/")
        content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Leave Type"] == "CP"
        assert rows[0]["Employee"] == "John Doe"

    def test_export_filter_by_status(self, authenticated_client, employee, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        response = authenticated_client.get("/api/leaves/leaves/export/?status=APPROVED")
        content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 0

    def test_export_content_disposition(self, authenticated_client, leave_data):
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        response = authenticated_client.get("/api/leaves/leaves/export/")
        assert "attachment" in response["Content-Disposition"]
        assert "leave-report" in response["Content-Disposition"]


class TestBalanceRestoredOnCancel:

    def test_cp_balance_restored_when_cancelling_approved_leave(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        days = leave.duration_days
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        employee.refresh_from_db()
        balance_after_approval = employee.cp_balance
        authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/cancel/",
            format="json",
        )
        employee.refresh_from_db()
        assert employee.cp_balance == balance_after_approval + days

    def test_rtt_balance_restored_when_cancelling_approved_leave(self, employee, manager, authenticated_client, manager_client):
        employee.manager = manager
        employee.save()
        tomorrow = date.today() + timedelta(days=1)
        data = {
            "start_date": tomorrow.isoformat(),
            "end_date": (tomorrow + timedelta(days=2)).isoformat(),
            "leave_type": "RTT",
            "reason": "RTT",
        }
        authenticated_client.post("/api/leaves/leaves/", data, format="json")
        leave = LeaveRequest.objects.first()
        days = leave.duration_days
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        employee.refresh_from_db()
        balance_after_approval = employee.rtt_balance
        authenticated_client.post(
            f"/api/leaves/leaves/{leave.id}/cancel/",
            format="json",
        )
        employee.refresh_from_db()
        assert employee.rtt_balance == balance_after_approval + days


class TestPendingApprovedActions:

    def test_pending_action_returns_only_pending(self, authenticated_client, employee, manager, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        another = dict(leave_data)
        another["leave_type"] = "SICK"
        authenticated_client.post("/api/leaves/leaves/", another, format="json")
        leave = LeaveRequest.objects.first()
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        response = authenticated_client.get("/api/leaves/leaves/pending/")
        assert response.status_code == 200
        for item in response.data:
            assert item["status"] == "PENDING"

    def test_approved_action_returns_only_approved(self, employee, manager, authenticated_client, manager_client, leave_data):
        employee.manager = manager
        employee.save()
        authenticated_client.post("/api/leaves/leaves/", leave_data, format="json")
        leave = LeaveRequest.objects.first()
        manager_client.post(
            f"/api/leaves/leaves/{leave.id}/approve/",
            {"manager_comment": "OK"},
            format="json",
        )
        response = authenticated_client.get("/api/leaves/leaves/approved/")
        assert response.status_code == 200
        for item in response.data:
            assert item["status"] == "APPROVED"
