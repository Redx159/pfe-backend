import pytest
from rest_framework.test import APIClient
from rest_framework import status
from employees.models import Employee

pytestmark = pytest.mark.django_db


@pytest.fixture
def employee_user():
    user = Employee.objects.create_user(
        username="johndoe",
        email="john@example.com",
        password="testpass123",
        employee_id="EMP001",
        first_name="John",
        last_name="Doe",
        cp_balance=25,
        rtt_balance=10,
        role="EMPLOYEE",
        is_active=True,
    )
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, employee_user):
    api_client.force_authenticate(user=employee_user)
    return api_client


def test_profile_returns_balances(auth_client):
    response = auth_client.get("/api/auth/profile/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["cp_balance"] == 25
    assert response.data["rtt_balance"] == 10
    assert response.data["employee_id"] == "EMP001"


def test_login_returns_jwt_tokens(api_client, employee_user):
    response = api_client.post(
        "/api/token/",
        {"username": "johndoe", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


def test_token_refresh_works(api_client, employee_user):
    login_resp = api_client.post(
        "/api/token/",
        {"username": "johndoe", "password": "testpass123"},
        format="json",
    )
    refresh_token = login_resp.data["refresh"]

    response = api_client.post(
        "/api/token/refresh/",
        {"refresh": refresh_token},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


def test_dashboard_summary_authenticated(auth_client):
    response = auth_client.get("/api/auth/dashboard/summary/")
    assert response.status_code == status.HTTP_200_OK
    assert "totals" in response.data
    assert "scope" in response.data
    assert response.data["scope"] == "team"
