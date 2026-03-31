"""
Data models for the Distributed Emergency Resource Allocation System.
Uses in-memory storage backed by Python dicts for portability.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
import uuid


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    ACTIVE = "active"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentType(str, Enum):
    FLOOD = "flood"
    FIRE = "fire"
    EARTHQUAKE = "earthquake"
    CYCLONE = "cyclone"
    ACCIDENT = "accident"
    MEDICAL = "medical"
    CHEMICAL = "chemical"
    OTHER = "other"


class AllocationStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    ON_SCENE = "on_scene"
    RETURNING = "returning"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Incident:
    """An emergency incident requiring resource allocation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    district_id: str = ""
    incident_type: IncidentType = IncidentType.OTHER
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.OPEN
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: str = ""
    affected_people: int = 0
    resources_needed: Dict[str, int] = field(default_factory=dict)
    created_by: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "district_id": self.district_id,
            "incident_type": self.incident_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
            "affected_people": self.affected_people,
            "resources_needed": dict(self.resources_needed),
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ResourceAllocation:
    """Tracks a resource allocation from a source district to an incident."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = ""
    source_district_id: str = ""
    resource_type: str = ""
    quantity: int = 0
    status: AllocationStatus = AllocationStatus.PENDING
    allocated_by: str = ""
    allocated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "source_district_id": self.source_district_id,
            "resource_type": self.resource_type,
            "quantity": self.quantity,
            "status": self.status.value,
            "allocated_by": self.allocated_by,
            "allocated_at": self.allocated_at,
            "updated_at": self.updated_at,
        }


class InMemoryStore:
    """
    Thread-safe in-memory data store for incidents and allocations.
    Serves as the persistence layer; can be swapped for a real database.
    """

    def __init__(self) -> None:
        self._incidents: Dict[str, Incident] = {}
        self._allocations: Dict[str, ResourceAllocation] = {}
        # Mutable resource snapshot per district (district_id -> resource dict)
        self._district_resources: Dict[str, Dict[str, int]] = {}

    # ------------------------------------------------------------------ #
    # Incident CRUD                                                        #
    # ------------------------------------------------------------------ #

    def create_incident(self, incident: Incident) -> Incident:
        self._incidents[incident.id] = incident
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self._incidents.get(incident_id)

    def list_incidents(
        self,
        district_id: Optional[str] = None,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
    ) -> List[Incident]:
        results = list(self._incidents.values())
        if district_id:
            results = [i for i in results if i.district_id == district_id]
        if status:
            results = [i for i in results if i.status == status]
        if severity:
            results = [i for i in results if i.severity == severity]
        return results

    def update_incident(self, incident_id: str, **kwargs) -> Optional[Incident]:
        incident = self._incidents.get(incident_id)
        if incident is None:
            return None
        for key, value in kwargs.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
        incident.updated_at = datetime.now(timezone.utc).isoformat()
        return incident

    def delete_incident(self, incident_id: str) -> bool:
        if incident_id in self._incidents:
            del self._incidents[incident_id]
            return True
        return False

    # ------------------------------------------------------------------ #
    # Allocation CRUD                                                      #
    # ------------------------------------------------------------------ #

    def create_allocation(self, allocation: ResourceAllocation) -> ResourceAllocation:
        self._allocations[allocation.id] = allocation
        return allocation

    def get_allocation(self, allocation_id: str) -> Optional[ResourceAllocation]:
        return self._allocations.get(allocation_id)

    def list_allocations(
        self,
        incident_id: Optional[str] = None,
        source_district_id: Optional[str] = None,
        status: Optional[AllocationStatus] = None,
    ) -> List[ResourceAllocation]:
        results = list(self._allocations.values())
        if incident_id:
            results = [a for a in results if a.incident_id == incident_id]
        if source_district_id:
            results = [a for a in results if a.source_district_id == source_district_id]
        if status:
            results = [a for a in results if a.status == status]
        return results

    def update_allocation(self, allocation_id: str, **kwargs) -> Optional[ResourceAllocation]:
        allocation = self._allocations.get(allocation_id)
        if allocation is None:
            return None
        for key, value in kwargs.items():
            if hasattr(allocation, key):
                setattr(allocation, key, value)
        allocation.updated_at = datetime.now(timezone.utc).isoformat()
        return allocation

    # ------------------------------------------------------------------ #
    # District resource management                                        #
    # ------------------------------------------------------------------ #

    def init_district_resources(self, district_id: str, resources: Dict[str, int]) -> None:
        """Seed the mutable resource snapshot from static district data."""
        self._district_resources[district_id] = dict(resources)

    def get_district_resources(self, district_id: str) -> Dict[str, int]:
        return dict(self._district_resources.get(district_id, {}))

    def update_district_resources(
        self, district_id: str, resource_type: str, delta: int
    ) -> bool:
        """
        Adjust a district's resource count by *delta* (can be negative).
        Returns False if the adjustment would make the count negative.
        """
        resources = self._district_resources.get(district_id)
        if resources is None:
            return False
        current = resources.get(resource_type, 0)
        if current + delta < 0:
            return False
        resources[resource_type] = current + delta
        return True


# Module-level singleton store
store = InMemoryStore()
