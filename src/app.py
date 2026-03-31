"""
Distributed Emergency Resource Allocation System — Tamil Nadu
Flask REST API
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request, g

from .auth import (
    Permission,
    Role,
    User,
    generate_token,
    hash_password,
    login_required,
    require_permission,
    user_store,
    verify_password,
)
from .allocation import auto_allocate, get_allocation_summary, release_allocation
from .districts import (
    DISTRICTS_BY_ID,
    list_districts,
    get_district,
    TOTAL_DISTRICTS,
)
from .fault_tolerance import (
    health_monitor,
    node_registry,
    replication_manager,
    NodeStatus,
)
from .models import (
    AllocationStatus,
    Incident,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    ResourceAllocation,
    store,
)


def create_app() -> Flask:
    app = Flask(__name__)

    # Seed district resources into the live store on startup
    for district in DISTRICTS_BY_ID.values():
        store.init_district_resources(district.id, district.resources)

    # ---------------------------------------------------------------------- #
    # Auth endpoints                                                           #
    # ---------------------------------------------------------------------- #

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.get_json(force=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")
        if not username or not password:
            return jsonify({"error": "username and password required"}), 400

        user = user_store.get_by_username(username)
        if user is None or not user.active or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401

        token = generate_token(user)
        return jsonify({"token": token, "user": user.to_dict()})

    @app.route("/api/auth/me", methods=["GET"])
    @login_required
    def me():
        return jsonify(g.current_user.to_dict())

    # ---------------------------------------------------------------------- #
    # User management                                                          #
    # ---------------------------------------------------------------------- #

    @app.route("/api/users", methods=["GET"])
    @login_required
    @require_permission(Permission.USER_MANAGE)
    def list_users():
        return jsonify([u.to_dict() for u in user_store.list_users()])

    @app.route("/api/users", methods=["POST"])
    @login_required
    @require_permission(Permission.USER_MANAGE)
    def create_user():
        data = request.get_json(force=True) or {}
        required = {"username", "password", "role"}
        if not required.issubset(data):
            return jsonify({"error": f"Required fields: {required}"}), 400

        try:
            role = Role(data["role"])
        except ValueError:
            return jsonify({"error": f"Invalid role: {data['role']}"}), 400

        try:
            user = User(
                id=str(uuid.uuid4()),
                username=data["username"],
                password_hash=hash_password(data["password"]),
                role=role,
                district_id=data.get("district_id"),
                full_name=data.get("full_name", ""),
            )
            user_store.create(user)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 409

        return jsonify(user.to_dict()), 201

    # ---------------------------------------------------------------------- #
    # Districts                                                                #
    # ---------------------------------------------------------------------- #

    @app.route("/api/districts", methods=["GET"])
    @login_required
    @require_permission(Permission.DISTRICT_READ)
    def get_districts():
        districts = list_districts()
        # Attach live resource counts
        for d in districts:
            d["live_resources"] = store.get_district_resources(d["id"])
        return jsonify({
            "total": TOTAL_DISTRICTS,
            "state": "Tamil Nadu",
            "districts": districts,
        })

    @app.route("/api/districts/<district_id>", methods=["GET"])
    @login_required
    @require_permission(Permission.DISTRICT_READ)
    def get_district_detail(district_id: str):
        try:
            district = get_district(district_id.upper())
        except KeyError:
            return jsonify({"error": "District not found"}), 404
        d = district.to_dict()
        d["live_resources"] = store.get_district_resources(district.id)
        return jsonify(d)

    # ---------------------------------------------------------------------- #
    # Incidents                                                                #
    # ---------------------------------------------------------------------- #

    @app.route("/api/incidents", methods=["GET"])
    @login_required
    @require_permission(Permission.INCIDENT_READ)
    def list_incidents():
        user: User = g.current_user
        district_filter = request.args.get("district_id")
        status_filter = request.args.get("status")
        severity_filter = request.args.get("severity")

        # District managers and field officers see only their district
        if user.role in (Role.DISTRICT_MANAGER, Role.FIELD_OFFICER):
            district_filter = user.district_id

        status = IncidentStatus(status_filter) if status_filter else None
        severity = IncidentSeverity(severity_filter) if severity_filter else None

        incidents = store.list_incidents(
            district_id=district_filter,
            status=status,
            severity=severity,
        )
        return jsonify([i.to_dict() for i in incidents])

    @app.route("/api/incidents", methods=["POST"])
    @login_required
    @require_permission(Permission.INCIDENT_CREATE)
    def create_incident():
        data = request.get_json(force=True) or {}
        required = {"district_id", "incident_type", "severity"}
        if not required.issubset(data):
            return jsonify({"error": f"Required fields: {required}"}), 400

        if data["district_id"].upper() not in DISTRICTS_BY_ID:
            return jsonify({"error": "Invalid district_id"}), 400

        try:
            incident = Incident(
                district_id=data["district_id"].upper(),
                incident_type=IncidentType(data["incident_type"]),
                severity=IncidentSeverity(data["severity"]),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                description=data.get("description", ""),
                affected_people=int(data.get("affected_people", 0)),
                resources_needed=data.get("resources_needed", {}),
                created_by=g.current_user.id,
            )
        except (ValueError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400

        store.create_incident(incident)

        # Auto-allocate if requested
        result = None
        if data.get("auto_allocate", False):
            alloc_result = auto_allocate(incident, allocated_by=g.current_user.id)
            result = {
                "fulfilled": alloc_result.fulfilled,
                "shortfall": alloc_result.shortfall,
                "total_allocations": len(alloc_result.allocations),
            }

        response = {"incident": incident.to_dict()}
        if result:
            response["allocation_result"] = result
        return jsonify(response), 201

    @app.route("/api/incidents/<incident_id>", methods=["GET"])
    @login_required
    @require_permission(Permission.INCIDENT_READ)
    def get_incident(incident_id: str):
        incident = store.get_incident(incident_id)
        if incident is None:
            return jsonify({"error": "Incident not found"}), 404
        _enforce_district_scope(incident)
        return jsonify(incident.to_dict())

    @app.route("/api/incidents/<incident_id>", methods=["PUT"])
    @login_required
    @require_permission(Permission.INCIDENT_UPDATE)
    def update_incident(incident_id: str):
        incident = store.get_incident(incident_id)
        if incident is None:
            return jsonify({"error": "Incident not found"}), 404

        data = request.get_json(force=True) or {}
        allowed = {
            "severity", "status", "description",
            "affected_people", "resources_needed",
        }
        updates = {k: v for k, v in data.items() if k in allowed}

        if "severity" in updates:
            updates["severity"] = IncidentSeverity(updates["severity"])
        if "status" in updates:
            updates["status"] = IncidentStatus(updates["status"])

        updated = store.update_incident(incident_id, **updates)
        return jsonify(updated.to_dict())

    @app.route("/api/incidents/<incident_id>", methods=["DELETE"])
    @login_required
    @require_permission(Permission.INCIDENT_DELETE)
    def delete_incident(incident_id: str):
        if not store.delete_incident(incident_id):
            return jsonify({"error": "Incident not found"}), 404
        return jsonify({"message": "Incident deleted"}), 200

    # ---------------------------------------------------------------------- #
    # Allocations                                                              #
    # ---------------------------------------------------------------------- #

    @app.route("/api/incidents/<incident_id>/allocate", methods=["POST"])
    @login_required
    @require_permission(Permission.ALLOCATION_CREATE)
    def allocate_resources(incident_id: str):
        incident = store.get_incident(incident_id)
        if incident is None:
            return jsonify({"error": "Incident not found"}), 404

        result = auto_allocate(incident, allocated_by=g.current_user.id)
        return jsonify({
            "incident_id": incident_id,
            "priority": result.priority,
            "fulfilled": result.fulfilled,
            "shortfall": result.shortfall,
            "allocations": [a.to_dict() for a in result.allocations],
        }), 201

    @app.route("/api/incidents/<incident_id>/allocations", methods=["GET"])
    @login_required
    @require_permission(Permission.ALLOCATION_READ)
    def get_incident_allocations(incident_id: str):
        return jsonify(get_allocation_summary(incident_id))

    @app.route("/api/allocations", methods=["GET"])
    @login_required
    @require_permission(Permission.ALLOCATION_READ)
    def list_allocations():
        incident_id = request.args.get("incident_id")
        source_district = request.args.get("source_district_id")
        status_str = request.args.get("status")
        status = AllocationStatus(status_str) if status_str else None

        allocations = store.list_allocations(
            incident_id=incident_id,
            source_district_id=source_district,
            status=status,
        )
        return jsonify([a.to_dict() for a in allocations])

    @app.route("/api/allocations/<allocation_id>/release", methods=["POST"])
    @login_required
    @require_permission(Permission.ALLOCATION_UPDATE)
    def release_alloc(allocation_id: str):
        if not release_allocation(allocation_id):
            return jsonify({"error": "Allocation not found"}), 404
        return jsonify({"message": "Resources returned to source district"})

    # ---------------------------------------------------------------------- #
    # Fault tolerance / system health                                          #
    # ---------------------------------------------------------------------- #

    @app.route("/api/system/health", methods=["GET"])
    @login_required
    @require_permission(Permission.SYSTEM_ADMIN)
    def system_health():
        return jsonify(health_monitor.status_report())

    @app.route("/api/system/nodes", methods=["GET"])
    @login_required
    @require_permission(Permission.SYSTEM_ADMIN)
    def list_nodes():
        return jsonify(node_registry.to_dict())

    @app.route("/api/system/nodes/<node_id>/heartbeat", methods=["POST"])
    @login_required
    @require_permission(Permission.SYSTEM_ADMIN)
    def node_heartbeat(node_id: str):
        if not node_registry.record_heartbeat(node_id):
            return jsonify({"error": "Node not found"}), 404
        return jsonify({"message": f"Heartbeat recorded for {node_id}"})

    @app.route("/api/system/nodes/<node_id>/failover", methods=["POST"])
    @login_required
    @require_permission(Permission.SYSTEM_ADMIN)
    def trigger_failover(node_id: str):
        replacement = node_registry.failover_for(node_id)
        if replacement is None:
            return jsonify({"error": "No healthy node available for failover"}), 503
        return jsonify({
            "failed_node": node_id,
            "replacement_node": replacement.to_dict(),
        })

    # ---------------------------------------------------------------------- #
    # Root                                                                     #
    # ---------------------------------------------------------------------- #

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "system": "Distributed Emergency Resource Allocation System",
            "state": "Tamil Nadu",
            "districts": TOTAL_DISTRICTS,
            "version": "1.0.0",
            "endpoints": [
                "/api/auth/login",
                "/api/auth/me",
                "/api/users",
                "/api/districts",
                "/api/incidents",
                "/api/allocations",
                "/api/system/health",
                "/api/system/nodes",
            ],
        })

    # ---------------------------------------------------------------------- #
    # Helper: district-scope enforcement                                       #
    # ---------------------------------------------------------------------- #

    def _enforce_district_scope(incident: Incident) -> None:
        """Return 403 if a district-scoped user accesses another district's data."""
        user: User = g.current_user
        if (
            user.district_id
            and user.role in (Role.DISTRICT_MANAGER, Role.FIELD_OFFICER)
            and incident.district_id != user.district_id
        ):
            from flask import abort
            abort(403)

    return app


# Allow running directly: python -m src.app
if __name__ == "__main__":
    import os
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=5000)
