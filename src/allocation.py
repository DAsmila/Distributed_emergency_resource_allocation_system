"""
Smart Resource Allocation Engine.

Implements a priority-aware, distance-optimised allocation algorithm that:
  1. Scores each candidate district by available resources, proximity, and
     spare capacity.
  2. Allocates resources greedily from the highest-scoring districts first.
  3. Respects minimum reserve thresholds so every district keeps a buffer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .districts import DISTRICTS_BY_ID, DistrictInfo
from .models import (
    Incident,
    IncidentSeverity,
    IncidentType,
    ResourceAllocation,
    AllocationStatus,
    store,
)


# ---------------------------------------------------------------------- #
# Constants                                                               #
# ---------------------------------------------------------------------- #

# Minimum fraction of a resource type that a district must retain
RESERVE_FRACTION: float = 0.20

# Severity → numeric priority (higher = more urgent)
SEVERITY_PRIORITY: Dict[IncidentSeverity, int] = {
    IncidentSeverity.LOW: 1,
    IncidentSeverity.MEDIUM: 2,
    IncidentSeverity.HIGH: 3,
    IncidentSeverity.CRITICAL: 4,
}

# Incident type → required resource types (ordered by importance)
INCIDENT_RESOURCE_REQUIREMENTS: Dict[IncidentType, List[str]] = {
    IncidentType.FLOOD: [
        "rescue_teams", "water_tankers", "food_packets",
        "medical_kits", "ambulances",
    ],
    IncidentType.FIRE: [
        "fire_trucks", "ambulances", "rescue_teams",
        "medical_kits", "water_tankers",
    ],
    IncidentType.EARTHQUAKE: [
        "rescue_teams", "ambulances", "medical_kits",
        "food_packets", "water_tankers",
    ],
    IncidentType.CYCLONE: [
        "rescue_teams", "food_packets", "water_tankers",
        "ambulances", "medical_kits",
    ],
    IncidentType.ACCIDENT: [
        "ambulances", "medical_kits", "rescue_teams",
        "fire_trucks", "police_units",
    ],
    IncidentType.MEDICAL: [
        "ambulances", "medical_kits", "rescue_teams",
    ],
    IncidentType.CHEMICAL: [
        "fire_trucks", "rescue_teams", "ambulances",
        "medical_kits", "police_units",
    ],
    IncidentType.OTHER: [
        "ambulances", "rescue_teams", "medical_kits",
        "food_packets", "water_tankers",
    ],
}

# Maximum distance (km) to search for resources
MAX_SEARCH_RADIUS_KM: float = 600.0


# ---------------------------------------------------------------------- #
# Haversine distance                                                      #
# ---------------------------------------------------------------------- #

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in kilometres between two points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------- #
# District candidate scoring                                              #
# ---------------------------------------------------------------------- #

@dataclass
class CandidateDistrict:
    district: DistrictInfo
    distance_km: float
    available: Dict[str, int]

    def score(self, resource_type: str) -> float:
        """
        Higher score → preferred source.
        Composed of:
          - Proximity score  (1 / (1 + distance))
          - Availability ratio (available / total inventory)
        """
        if self.available.get(resource_type, 0) <= 0:
            return 0.0
        total = self.district.resources.get(resource_type, 1)
        availability_ratio = self.available[resource_type] / max(total, 1)
        proximity_score = 1.0 / (1.0 + self.distance_km / 100.0)
        return availability_ratio * 0.6 + proximity_score * 0.4


def _compute_available(district: DistrictInfo) -> Dict[str, int]:
    """Return per-resource available count after respecting reserves."""
    live = store.get_district_resources(district.id)
    available: Dict[str, int] = {}
    for rtype, total in live.items():
        reserve = math.ceil(district.resources.get(rtype, 0) * RESERVE_FRACTION)
        surplus = total - reserve
        available[rtype] = max(0, surplus)
    return available


def _candidates_for_incident(
    incident: Incident,
) -> List[CandidateDistrict]:
    """Return a list of candidate districts sorted by proximity."""
    origin = DISTRICTS_BY_ID.get(incident.district_id)
    candidates: List[CandidateDistrict] = []
    for district in DISTRICTS_BY_ID.values():
        if origin is not None:
            dist = haversine_km(
                origin.latitude, origin.longitude,
                district.latitude, district.longitude,
            )
        else:
            # Fallback when incident lat/lon are set but district_id unknown
            if incident.latitude is not None and incident.longitude is not None:
                dist = haversine_km(
                    incident.latitude, incident.longitude,
                    district.latitude, district.longitude,
                )
            else:
                dist = 0.0

        if dist > MAX_SEARCH_RADIUS_KM and district.id != incident.district_id:
            continue
        available = _compute_available(district)
        candidates.append(CandidateDistrict(district, dist, available))

    return sorted(candidates, key=lambda c: c.distance_km)


# ---------------------------------------------------------------------- #
# Public allocation API                                                   #
# ---------------------------------------------------------------------- #

@dataclass
class AllocationResult:
    """Summary of a single auto-allocation run."""
    incident_id: str
    fulfilled: Dict[str, int]  # resource_type → total quantity allocated
    shortfall: Dict[str, int]  # resource_type → unmet quantity
    allocations: List[ResourceAllocation]
    priority: int


def auto_allocate(incident: Incident, allocated_by: str = "system") -> AllocationResult:
    """
    Automatically allocate resources for the given incident.

    Algorithm
    ---------
    1. Determine required resources from incident type and `resources_needed`.
    2. For each resource type, rank candidate districts by score.
    3. Greedily pull from the top-ranked districts until the need is met or
       all candidates are exhausted.
    4. Deduct allocated quantities from the live district resource counts.
    5. Return a summary of what was fulfilled and what remains as shortfall.
    """
    priority = SEVERITY_PRIORITY[incident.severity]
    needed = dict(incident.resources_needed)

    # If no explicit resource list, build a default based on incident type
    if not needed:
        rtype_list = INCIDENT_RESOURCE_REQUIREMENTS.get(
            incident.incident_type,
            INCIDENT_RESOURCE_REQUIREMENTS[IncidentType.OTHER],
        )
        base_qty = max(1, incident.affected_people // 50)
        needed = {rt: base_qty for rt in rtype_list}

    candidates = _candidates_for_incident(incident)
    fulfilled: Dict[str, int] = {}
    shortfall: Dict[str, int] = {}
    allocations: List[ResourceAllocation] = []

    for resource_type, quantity_needed in needed.items():
        remaining = quantity_needed
        for candidate in sorted(
            candidates,
            key=lambda c, rt=resource_type: c.score(rt),
            reverse=True,
        ):
            if remaining <= 0:
                break
            avail = candidate.available.get(resource_type, 0)
            if avail <= 0:
                continue
            take = min(avail, remaining)
            # Deduct from live store
            ok = store.update_district_resources(
                candidate.district.id, resource_type, -take
            )
            if not ok:
                continue
            # Record the allocation
            alloc = ResourceAllocation(
                incident_id=incident.id,
                source_district_id=candidate.district.id,
                resource_type=resource_type,
                quantity=take,
                status=AllocationStatus.DISPATCHED,
                allocated_by=allocated_by,
            )
            store.create_allocation(alloc)
            allocations.append(alloc)
            # Update candidate's available count for subsequent passes
            candidate.available[resource_type] = avail - take
            remaining -= take

        fulfilled[resource_type] = quantity_needed - remaining
        if remaining > 0:
            shortfall[resource_type] = remaining

    return AllocationResult(
        incident_id=incident.id,
        fulfilled=fulfilled,
        shortfall=shortfall,
        allocations=allocations,
        priority=priority,
    )


def release_allocation(allocation_id: str) -> bool:
    """
    Mark an allocation as completed and return resources to the source district.
    """
    allocation = store.get_allocation(allocation_id)
    if allocation is None:
        return False
    store.update_district_resources(
        allocation.source_district_id,
        allocation.resource_type,
        allocation.quantity,
    )
    store.update_allocation(allocation_id, status=AllocationStatus.COMPLETED)
    return True


def get_allocation_summary(incident_id: str) -> dict:
    """Return a summary of all allocations for the given incident."""
    allocations = store.list_allocations(incident_id=incident_id)
    by_type: Dict[str, int] = {}
    for alloc in allocations:
        by_type[alloc.resource_type] = (
            by_type.get(alloc.resource_type, 0) + alloc.quantity
        )
    return {
        "incident_id": incident_id,
        "total_allocations": len(allocations),
        "resources_allocated": by_type,
        "allocations": [a.to_dict() for a in allocations],
    }
