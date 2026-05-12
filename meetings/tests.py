import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from employees.models import Employee
from meetings.models import Meeting, MeetingParticipant

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def employee_user():
    return Employee.objects.create_user(
        username="employee1",
        password="pass123",
        employee_id="EMP-001",
        role="EMPLOYEE",
    )


@pytest.fixture
def other_employee():
    return Employee.objects.create_user(
        username="employee2",
        password="pass123",
        employee_id="EMP-002",
        role="EMPLOYEE",
    )


@pytest.fixture
def third_employee():
    return Employee.objects.create_user(
        username="employee3",
        password="pass123",
        employee_id="EMP-003",
        role="EMPLOYEE",
    )


@pytest.fixture
def manager_user():
    return Employee.objects.create_user(
        username="manager1",
        password="pass123",
        employee_id="EMP-004",
        role="MANAGER",
    )


@pytest.fixture
def admin_user():
    return Employee.objects.create_user(
        username="admin1",
        password="pass123",
        employee_id="EMP-005",
        role="ADMIN",
    )


@pytest.fixture
def meeting(employee_user):
    return Meeting.objects.create(
        title="Sprint Review",
        description="Monthly review",
        start_time=timezone.now() + timezone.timedelta(hours=2),
        end_time=timezone.now() + timezone.timedelta(hours=3),
        created_by=employee_user,
    )


@pytest.fixture
def authenticated_client(api_client, employee_user):
    api_client.force_authenticate(user=employee_user)
    return api_client


class TestCreateMeeting:
    def test_create_meeting_authenticated(self, authenticated_client):
        data = {
            "title": "Team Sync",
            "description": "Weekly sync",
            "start_time": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "end_time": (timezone.now() + timezone.timedelta(days=1, hours=1)).isoformat(),
            "is_online": True,
            "meeting_url": "https://meet.example.com/sync",
        }
        response = authenticated_client.post("/api/meetings/meetings/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Team Sync"
        assert response.data["created_by"]["username"] == "employee1"

    def test_create_meeting_unauthenticated(self, api_client):
        data = {
            "title": "Team Sync",
            "start_time": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "end_time": (timezone.now() + timezone.timedelta(days=1, hours=1)).isoformat(),
        }
        response = api_client.post("/api/meetings/meetings/", data, format="json")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


class TestListMeetings:
    def test_employee_sees_own_meetings(self, authenticated_client, meeting, other_employee):
        Meeting.objects.create(
            title="Other Meeting",
            start_time=timezone.now() + timezone.timedelta(hours=5),
            end_time=timezone.now() + timezone.timedelta(hours=6),
            created_by=other_employee,
        )
        response = authenticated_client.get("/api/meetings/meetings/")
        assert response.status_code == status.HTTP_200_OK
        titles = [m["title"] for m in response.data["results"]]
        assert "Sprint Review" in titles
        assert "Other Meeting" not in titles

    def test_employee_sees_participated_meetings(self, authenticated_client, meeting, employee_user, other_employee):
        MeetingParticipant.objects.create(meeting=meeting, employee=employee_user)
        other_meeting = Meeting.objects.create(
            title="Team Standup",
            start_time=timezone.now() + timezone.timedelta(hours=4),
            end_time=timezone.now() + timezone.timedelta(hours=5),
            created_by=other_employee,
        )
        MeetingParticipant.objects.create(meeting=other_meeting, employee=employee_user)
        response = authenticated_client.get("/api/meetings/meetings/")
        assert response.status_code == status.HTTP_200_OK
        titles = [m["title"] for m in response.data["results"]]
        assert "Sprint Review" in titles
        assert "Team Standup" in titles

    def test_admin_sees_all_meetings(self, api_client, admin_user, meeting, other_employee):
        api_client.force_authenticate(user=admin_user)
        Meeting.objects.create(
            title="Admin Visible",
            start_time=timezone.now() + timezone.timedelta(hours=5),
            end_time=timezone.now() + timezone.timedelta(hours=6),
            created_by=other_employee,
        )
        response = api_client.get("/api/meetings/meetings/")
        assert response.status_code == status.HTTP_200_OK
        titles = [m["title"] for m in response.data["results"]]
        assert "Sprint Review" in titles
        assert "Admin Visible" in titles


class TestInviteParticipants:
    def test_invite_participants_by_creator(self, authenticated_client, meeting, other_employee):
        response = authenticated_client.post(
            f"/api/meetings/meetings/{meeting.id}/invite/",
            {"employee_ids": [other_employee.id]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert MeetingParticipant.objects.filter(meeting=meeting, employee=other_employee).exists()

    def test_invite_by_non_creator_fails(self, api_client, meeting, other_employee):
        api_client.force_authenticate(user=other_employee)
        response = api_client.post(
            f"/api/meetings/meetings/{meeting.id}/invite/",
            {"employee_ids": [other_employee.id]},
            format="json",
        )
        assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    def test_invite_without_employee_ids_fails(self, authenticated_client, meeting):
        response = authenticated_client.post(
            f"/api/meetings/meetings/{meeting.id}/invite/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_manager_can_only_invite_team_members(self, api_client, manager_user, other_employee, third_employee):
        other_employee.manager = manager_user
        other_employee.save()
        api_client.force_authenticate(user=manager_user)
        meeting = Meeting.objects.create(
            title="Manager Meeting",
            start_time=timezone.now() + timezone.timedelta(hours=2),
            end_time=timezone.now() + timezone.timedelta(hours=3),
            created_by=manager_user,
        )
        response = api_client.post(
            f"/api/meetings/meetings/{meeting.id}/invite/",
            {"employee_ids": [other_employee.id, third_employee.id]},
            format="json",
        )
        assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


class TestRespondToInvitation:
    def test_accept_invitation(self, authenticated_client, meeting, employee_user):
        MeetingParticipant.objects.create(meeting=meeting, employee=employee_user)
        response = authenticated_client.post(
            f"/api/meetings/meetings/{meeting.id}/respond/",
            {"status": "ACCEPTED"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        participant = MeetingParticipant.objects.get(meeting=meeting, employee=employee_user)
        assert participant.status == "ACCEPTED"

    def test_decline_with_reason(self, authenticated_client, meeting, employee_user):
        MeetingParticipant.objects.create(meeting=meeting, employee=employee_user)
        response = authenticated_client.post(
            f"/api/meetings/meetings/{meeting.id}/respond/",
            {"status": "DECLINED", "decline_reason": "Conflict"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        participant = MeetingParticipant.objects.get(meeting=meeting, employee=employee_user)
        assert participant.status == "DECLINED"
        assert participant.decline_reason == "Conflict"

    def test_respond_not_invited_fails(self, authenticated_client, meeting, other_employee):
        authenticated_client.force_authenticate(user=other_employee)
        response = authenticated_client.post(
            f"/api/meetings/meetings/{meeting.id}/respond/",
            {"status": "ACCEPTED"},
            format="json",
        )
        assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    def test_respond_invalid_status_fails(self, authenticated_client, meeting, employee_user):
        MeetingParticipant.objects.create(meeting=meeting, employee=employee_user)
        response = authenticated_client.post(
            f"/api/meetings/meetings/{meeting.id}/respond/",
            {"status": "INVALID"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCancelMeeting:
    def test_cancel_by_creator(self, authenticated_client, meeting):
        response = authenticated_client.post(f"/api/meetings/meetings/{meeting.id}/cancel/")
        assert response.status_code == status.HTTP_200_OK
        meeting.refresh_from_db()
        assert meeting.is_cancelled is True

    def test_cancel_by_non_creator_fails(self, api_client, meeting, other_employee):
        api_client.force_authenticate(user=other_employee)
        response = api_client.post(f"/api/meetings/meetings/{meeting.id}/cancel/")
        assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
        meeting.refresh_from_db()
        assert meeting.is_cancelled is False

    def test_cancel_already_cancelled_fails(self, authenticated_client, meeting):
        meeting.is_cancelled = True
        meeting.save()
        response = authenticated_client.post(f"/api/meetings/meetings/{meeting.id}/cancel/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestMeetingDetail:
    def test_meeting_detail_includes_participants_and_status(self, authenticated_client, meeting, other_employee):
        MeetingParticipant.objects.create(meeting=meeting, employee=other_employee)
        response = authenticated_client.get(f"/api/meetings/meetings/{meeting.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Sprint Review"
        assert len(response.data["participants"]) == 1
        assert response.data["participants"][0]["employee"]["username"] == "employee2"

    def test_meeting_detail_my_status(self, authenticated_client, meeting, employee_user):
        MeetingParticipant.objects.create(meeting=meeting, employee=employee_user, status="ACCEPTED")
        response = authenticated_client.get(f"/api/meetings/meetings/{meeting.id}/")
        assert response.data["my_status"] == "ACCEPTED"


class TestFilterEndpoints:
    def test_upcoming_filter(self, authenticated_client, employee_user):
        past = Meeting.objects.create(
            title="Past Meeting",
            start_time=timezone.now() - timezone.timedelta(days=2),
            end_time=timezone.now() - timezone.timedelta(days=2, hours=-1),
            created_by=employee_user,
        )
        future = Meeting.objects.create(
            title="Future Meeting",
            start_time=timezone.now() + timezone.timedelta(days=2),
            end_time=timezone.now() + timezone.timedelta(days=2, hours=1),
            created_by=employee_user,
        )
        response = authenticated_client.get("/api/meetings/meetings/upcoming/")
        titles = [m["title"] for m in response.data]
        assert "Future Meeting" in titles
        assert "Past Meeting" not in titles
