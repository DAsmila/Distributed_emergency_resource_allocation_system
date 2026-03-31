"""
Tests for Role-Based Access Control (RBAC) and authentication.
"""

import pytest
import jwt

from src.auth import (
    Role,
    Permission,
    User,
    UserStore,
    ROLE_PERMISSIONS,
    has_permission,
    hash_password,
    verify_password,
    generate_token,
    decode_token,
    JWT_SECRET,
    JWT_ALGORITHM,
)


# ---------------------------------------------------------------------- #
# Permission tests                                                        #
# ---------------------------------------------------------------------- #

def test_admin_has_all_permissions():
    for perm in Permission:
        assert has_permission(Role.ADMIN, perm), f"Admin missing permission {perm}"


def test_viewer_has_only_read_permissions():
    viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
    writable = {
        Permission.INCIDENT_CREATE, Permission.INCIDENT_UPDATE, Permission.INCIDENT_DELETE,
        Permission.ALLOCATION_CREATE, Permission.ALLOCATION_UPDATE, Permission.ALLOCATION_DELETE,
        Permission.DISTRICT_UPDATE, Permission.USER_MANAGE, Permission.SYSTEM_ADMIN,
    }
    for perm in writable:
        assert perm not in viewer_perms, f"Viewer should not have {perm}"

    assert Permission.INCIDENT_READ in viewer_perms
    assert Permission.ALLOCATION_READ in viewer_perms
    assert Permission.DISTRICT_READ in viewer_perms


def test_district_manager_can_create_incident():
    assert has_permission(Role.DISTRICT_MANAGER, Permission.INCIDENT_CREATE)


def test_district_manager_cannot_delete_incident():
    assert not has_permission(Role.DISTRICT_MANAGER, Permission.INCIDENT_DELETE)


def test_field_officer_cannot_create_allocation():
    assert not has_permission(Role.FIELD_OFFICER, Permission.ALLOCATION_CREATE)


def test_state_coordinator_can_delete_incident():
    assert has_permission(Role.STATE_COORDINATOR, Permission.INCIDENT_DELETE)


def test_state_coordinator_cannot_manage_users():
    assert not has_permission(Role.STATE_COORDINATOR, Permission.USER_MANAGE)


# ---------------------------------------------------------------------- #
# Password tests                                                          #
# ---------------------------------------------------------------------- #

def test_hash_password_is_deterministic():
    h1 = hash_password("TestPass123")
    h2 = hash_password("TestPass123")
    assert h1 == h2


def test_verify_password_correct():
    pw = "MyPassword@2024"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed)


def test_verify_password_wrong():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


# ---------------------------------------------------------------------- #
# JWT tests                                                               #
# ---------------------------------------------------------------------- #

def _make_user(role: Role = Role.VIEWER, district_id: str = None) -> User:
    return User(
        id="test-user-001",
        username="testuser",
        password_hash=hash_password("Test@123"),
        role=role,
        district_id=district_id,
        full_name="Test User",
    )


def test_generate_and_decode_token():
    user = _make_user(Role.DISTRICT_MANAGER, "TN-CHE")
    token = generate_token(user)
    payload = decode_token(token)
    assert payload["sub"] == "test-user-001"
    assert payload["username"] == "testuser"
    assert payload["role"] == Role.DISTRICT_MANAGER.value
    assert payload["district_id"] == "TN-CHE"


def test_invalid_token_raises():
    with pytest.raises(jwt.InvalidTokenError):
        decode_token("not.a.valid.token")


def test_tampered_token_raises():
    user = _make_user()
    token = generate_token(user)
    tampered = token[:-4] + "AAAA"
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(tampered)


# ---------------------------------------------------------------------- #
# UserStore tests                                                         #
# ---------------------------------------------------------------------- #

def test_default_users_seeded():
    us = UserStore()
    assert us.get_by_username("admin") is not None
    assert us.get_by_username("viewer") is not None
    assert us.get_by_username("dm_chennai") is not None


def test_create_and_retrieve_user():
    us = UserStore()
    user = User(
        id="new-001",
        username="new_officer",
        password_hash=hash_password("NewPass@1"),
        role=Role.FIELD_OFFICER,
        district_id="TN-MDU",
    )
    us.create(user)
    retrieved = us.get_by_username("new_officer")
    assert retrieved is not None
    assert retrieved.role == Role.FIELD_OFFICER


def test_duplicate_username_raises():
    us = UserStore()
    user = User(
        id="dup-001",
        username="admin",  # already exists
        password_hash=hash_password("SomePass"),
        role=Role.VIEWER,
    )
    with pytest.raises(ValueError, match="already exists"):
        us.create(user)


def test_delete_user():
    us = UserStore()
    user = User(
        id="del-001",
        username="to_delete",
        password_hash=hash_password("TempPass"),
        role=Role.VIEWER,
    )
    us.create(user)
    assert us.get_by_username("to_delete") is not None
    us.delete("del-001")
    assert us.get_by_username("to_delete") is None


def test_list_users_returns_all():
    us = UserStore()
    users = us.list_users()
    assert len(users) >= 5  # at least the default seed users


def test_user_to_dict_excludes_password():
    us = UserStore()
    user = us.get_by_username("admin")
    d = user.to_dict()
    assert "password_hash" not in d
    assert "id" in d
    assert "role" in d
