"""
Integration tests for the Flask REST API.
"""

import pytest
import json

from src.app import create_app
from src.districts import DISTRICTS_BY_ID
from src.models import store


@pytest.fixture(autouse=True)
def reset_resources():
    """Re-seed district resources before each test."""
    for district in DISTRICTS_BY_ID.values():
        store.init_district_resources(district.id, district.resources)
    yield


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _login(client, username: str, password: str):
    resp = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    return resp.get_json()["token"]


# ---------------------------------------------------------------------- #
# Auth                                                                    #
# ---------------------------------------------------------------------- #

def test_login_success(client):
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={"username": "admin"})
    assert resp.status_code == 400


def test_me_endpoint(client):
    token = _login(client, "admin", "Admin@123")
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "admin"


def test_unauthenticated_access_denied(client):
    resp = client.get("/api/districts")
    assert resp.status_code == 401


# ---------------------------------------------------------------------- #
# Districts                                                               #
# ---------------------------------------------------------------------- #

def test_get_districts(client):
    token = _login(client, "viewer", "Viewer@123")
    resp = client.get("/api/districts", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 38
    assert data["state"] == "Tamil Nadu"
    assert len(data["districts"]) == 38


def test_get_district_detail(client):
    token = _login(client, "viewer", "Viewer@123")
    resp = client.get(
        "/api/districts/TN-CHE",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Chennai"


def test_get_invalid_district(client):
    token = _login(client, "viewer", "Viewer@123")
    resp = client.get(
        "/api/districts/TN-INVALID",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------- #
# Incidents                                                               #
# ---------------------------------------------------------------------- #

def test_create_incident(client):
    token = _login(client, "admin", "Admin@123")
    resp = client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "district_id": "TN-CHE",
            "incident_type": "flood",
            "severity": "high",
            "description": "Flooding in North Chennai",
            "affected_people": 200,
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "incident" in data
    assert data["incident"]["district_id"] == "TN-CHE"


def test_create_incident_with_auto_allocate(client):
    token = _login(client, "admin", "Admin@123")
    resp = client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "district_id": "TN-MDU",
            "incident_type": "fire",
            "severity": "critical",
            "affected_people": 50,
            "auto_allocate": True,
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "allocation_result" in data
    assert "fulfilled" in data["allocation_result"]


def test_viewer_cannot_create_incident(client):
    token = _login(client, "viewer", "Viewer@123")
    resp = client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "district_id": "TN-CHE",
            "incident_type": "flood",
            "severity": "medium",
        },
    )
    assert resp.status_code == 403


def test_list_incidents(client):
    token = _login(client, "admin", "Admin@123")
    # Create an incident first
    client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={"district_id": "TN-SLM", "incident_type": "flood", "severity": "low"},
    )
    resp = client.get("/api/incidents", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_district_manager_sees_only_own_district(client):
    admin_token = _login(client, "admin", "Admin@123")
    # Create incidents in two districts
    client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"district_id": "TN-CHE", "incident_type": "flood", "severity": "low"},
    )
    client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"district_id": "TN-MDU", "incident_type": "fire", "severity": "low"},
    )

    dm_token = _login(client, "dm_chennai", "District@123")
    resp = client.get(
        "/api/incidents",
        headers={"Authorization": f"Bearer {dm_token}"},
    )
    assert resp.status_code == 200
    incidents = resp.get_json()
    for inc in incidents:
        assert inc["district_id"] == "TN-CHE"


# ---------------------------------------------------------------------- #
# Allocations                                                             #
# ---------------------------------------------------------------------- #

def test_allocate_resources_endpoint(client):
    token = _login(client, "admin", "Admin@123")
    # Create incident
    create_resp = client.post(
        "/api/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "district_id": "TN-CBE",
            "incident_type": "earthquake",
            "severity": "critical",
            "affected_people": 100,
            "resources_needed": {"ambulances": 5, "rescue_teams": 2},
        },
    )
    incident_id = create_resp.get_json()["incident"]["id"]

    alloc_resp = client.post(
        f"/api/incidents/{incident_id}/allocate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert alloc_resp.status_code == 201
    data = alloc_resp.get_json()
    assert "fulfilled" in data
    assert data["fulfilled"].get("ambulances", 0) > 0


def test_viewer_cannot_allocate(client):
    token = _login(client, "viewer", "Viewer@123")
    resp = client.post(
        "/api/incidents/fake-id/allocate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------- #
# System health                                                           #
# ---------------------------------------------------------------------- #

def test_system_health_admin_only(client):
    admin_token = _login(client, "admin", "Admin@123")
    resp = client.get(
        "/api/system/health",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_nodes" in data
    assert "healthy" in data


def test_system_health_viewer_forbidden(client):
    token = _login(client, "viewer", "Viewer@123")
    resp = client.get(
        "/api/system/health",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------- #
# Root endpoint                                                           #
# ---------------------------------------------------------------------- #

def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["state"] == "Tamil Nadu"
    assert data["districts"] == 38
