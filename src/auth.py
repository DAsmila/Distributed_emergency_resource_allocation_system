"""
Role-Based Access Control (RBAC) for the Distributed Emergency Resource
Allocation System.  Uses JWT tokens for stateless authentication.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from typing import Dict, List, Optional, Set

import jwt
from flask import request, jsonify, g

# ---------------------------------------------------------------------- #
# Configuration                                                           #
# ---------------------------------------------------------------------- #

JWT_SECRET = os.environ.get("JWT_SECRET", "tn-emergency-secret-key-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8


# ---------------------------------------------------------------------- #
# Roles and Permissions                                                   #
# ---------------------------------------------------------------------- #

class Role(str, Enum):
    ADMIN = "admin"
    STATE_COORDINATOR = "state_coordinator"
    DISTRICT_MANAGER = "district_manager"
    FIELD_OFFICER = "field_officer"
    VIEWER = "viewer"


class Permission(str, Enum):
    # Incident permissions
    INCIDENT_CREATE = "incident:create"
    INCIDENT_READ = "incident:read"
    INCIDENT_UPDATE = "incident:update"
    INCIDENT_DELETE = "incident:delete"
    # Allocation permissions
    ALLOCATION_CREATE = "allocation:create"
    ALLOCATION_READ = "allocation:read"
    ALLOCATION_UPDATE = "allocation:update"
    ALLOCATION_DELETE = "allocation:delete"
    # District permissions
    DISTRICT_READ = "district:read"
    DISTRICT_UPDATE = "district:update"
    # User management
    USER_MANAGE = "user:manage"
    # System
    SYSTEM_ADMIN = "system:admin"


# Role → granted permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: set(Permission),  # all permissions

    Role.STATE_COORDINATOR: {
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.INCIDENT_DELETE,
        Permission.ALLOCATION_CREATE,
        Permission.ALLOCATION_READ,
        Permission.ALLOCATION_UPDATE,
        Permission.ALLOCATION_DELETE,
        Permission.DISTRICT_READ,
        Permission.DISTRICT_UPDATE,
    },

    Role.DISTRICT_MANAGER: {
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.ALLOCATION_CREATE,
        Permission.ALLOCATION_READ,
        Permission.ALLOCATION_UPDATE,
        Permission.DISTRICT_READ,
    },

    Role.FIELD_OFFICER: {
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.ALLOCATION_READ,
        Permission.DISTRICT_READ,
    },

    Role.VIEWER: {
        Permission.INCIDENT_READ,
        Permission.ALLOCATION_READ,
        Permission.DISTRICT_READ,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    """Return True if the given role has the specified permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


# ---------------------------------------------------------------------- #
# Password helpers (defined early so UserStore can use them)              #
# ---------------------------------------------------------------------- #

def hash_password(password: str) -> str:
    """Return a hex-encoded PBKDF2-HMAC-SHA256 hash of the password."""
    salt = b"tn_emergency_salt"  # static salt for demo; use per-user salt in prod
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return dk.hex()


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time comparison of the supplied password against a hash."""
    candidate = hash_password(password)
    return hmac.compare_digest(candidate, password_hash)


# ---------------------------------------------------------------------- #
# User model                                                              #
# ---------------------------------------------------------------------- #

@dataclass
class User:
    id: str
    username: str
    password_hash: str
    role: Role
    district_id: Optional[str] = None  # None means state-level access
    full_name: str = ""
    active: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.value,
            "district_id": self.district_id,
            "full_name": self.full_name,
            "active": self.active,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------- #
# In-memory user store                                                    #
# ---------------------------------------------------------------------- #

class UserStore:
    def __init__(self) -> None:
        self._users: Dict[str, User] = {}
        self._username_index: Dict[str, str] = {}  # username → user_id
        self._seed_default_users()

    def _seed_default_users(self) -> None:
        defaults: List[dict] = [
            {
                "id": "admin-001",
                "username": "admin",
                "password": "Admin@123",
                "role": Role.ADMIN,
                "full_name": "System Administrator",
            },
            {
                "id": "sc-001",
                "username": "state_coordinator",
                "password": "State@123",
                "role": Role.STATE_COORDINATOR,
                "full_name": "Tamil Nadu State Coordinator",
            },
            {
                "id": "dm-chen-001",
                "username": "dm_chennai",
                "password": "District@123",
                "role": Role.DISTRICT_MANAGER,
                "district_id": "TN-CHE",
                "full_name": "Chennai District Manager",
            },
            {
                "id": "fo-chen-001",
                "username": "fo_chennai",
                "password": "Field@123",
                "role": Role.FIELD_OFFICER,
                "district_id": "TN-CHE",
                "full_name": "Chennai Field Officer",
            },
            {
                "id": "viewer-001",
                "username": "viewer",
                "password": "Viewer@123",
                "role": Role.VIEWER,
                "full_name": "Read-only Viewer",
            },
        ]
        for u in defaults:
            user = User(
                id=u["id"],
                username=u["username"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                district_id=u.get("district_id"),
                full_name=u.get("full_name", ""),
            )
            self._users[user.id] = user
            self._username_index[user.username] = user.id

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        uid = self._username_index.get(username)
        return self._users.get(uid) if uid else None

    def create(self, user: User) -> User:
        if user.username in self._username_index:
            raise ValueError(f"Username '{user.username}' already exists")
        self._users[user.id] = user
        self._username_index[user.username] = user.id
        return user

    def list_users(self) -> List[User]:
        return list(self._users.values())

    def update(self, user_id: str, **kwargs) -> Optional[User]:
        user = self._users.get(user_id)
        if user is None:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user

    def delete(self, user_id: str) -> bool:
        user = self._users.pop(user_id, None)
        if user:
            self._username_index.pop(user.username, None)
            return True
        return False


# Module-level singleton
user_store = UserStore()


# ---------------------------------------------------------------------- #
# JWT helpers                                                             #
# ---------------------------------------------------------------------- #

def generate_token(user: User) -> str:
    """Generate a signed JWT for *user*."""
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role.value,
        "district_id": user.district_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT, returning the payload dict."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# ---------------------------------------------------------------------- #
# Flask decorators                                                        #
# ---------------------------------------------------------------------- #

def login_required(f):
    """Decorator: requires a valid Bearer token in the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = user_store.get_by_id(payload["sub"])
        if user is None or not user.active:
            return jsonify({"error": "User not found or inactive"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_permission(permission: Permission):
    """Decorator: requires the current user to hold *permission*."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user: User = getattr(g, "current_user", None)
            if user is None:
                return jsonify({"error": "Authentication required"}), 401
            if not has_permission(user.role, permission):
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_role(*roles: Role):
    """Decorator: requires the current user to have one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user: User = getattr(g, "current_user", None)
            if user is None:
                return jsonify({"error": "Authentication required"}), 401
            if user.role not in roles:
                return jsonify({"error": "Insufficient role"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
