"""
Tests for the Smart Resource Allocation Engine.
"""

import pytest

from src.allocation import (
    auto_allocate,
    get_allocation_summary,
    haversine_km,
    release_allocation,
    SEVERITY_PRIORITY,
    INCIDENT_RESOURCE_REQUIREMENTS,
)
from src.districts import get_district
from src.models import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    InMemoryStore,
    store,
)


@pytest.fixture(autouse=True)
def reset_store():
    """Re-seed district resources before every test to ensure isolation."""
    from src.districts import DISTRICTS_BY_ID
    for district in DISTRICTS_BY_ID.values():
        store.init_district_resources(district.id, district.resources)
    yield


# ---------------------------------------------------------------------- #
# Haversine distance                                                      #
# ---------------------------------------------------------------------- #

def test_haversine_same_point():
    assert haversine_km(13.08, 80.27, 13.08, 80.27) == pytest.approx(0.0, abs=0.01)


def test_haversine_chennai_to_madurai():
    # Chennai → Madurai: ~460 km by road, ~400 km straight-line
    dist = haversine_km(13.0827, 80.2707, 9.9252, 78.1198)
    assert 380 < dist < 440, f"Unexpected distance: {dist}"


def test_haversine_symmetry():
    d1 = haversine_km(13.08, 80.27, 9.92, 78.12)
    d2 = haversine_km(9.92, 78.12, 13.08, 80.27)
    assert d1 == pytest.approx(d2, abs=0.001)


# ---------------------------------------------------------------------- #
# Auto-allocation                                                         #
# ---------------------------------------------------------------------- #

def _make_incident(
    district_id="TN-CHE",
    incident_type=IncidentType.FLOOD,
    severity=IncidentSeverity.HIGH,
    affected_people=100,
    resources_needed=None,
):
    inc = Incident(
        district_id=district_id,
        incident_type=incident_type,
        severity=severity,
        affected_people=affected_people,
        resources_needed=resources_needed or {},
        created_by="test",
    )
    store.create_incident(inc)
    return inc


def test_auto_allocate_returns_result():
    incident = _make_incident()
    result = auto_allocate(incident)
    assert result.incident_id == incident.id
    assert isinstance(result.fulfilled, dict)
    assert isinstance(result.shortfall, dict)
    assert isinstance(result.allocations, list)


def test_auto_allocate_deducts_from_district():
    incident = _make_incident(
        district_id="TN-CHE",
        resources_needed={"ambulances": 5},
    )
    before = store.get_district_resources("TN-CHE")["ambulances"]
    auto_allocate(incident)
    after = store.get_district_resources("TN-CHE")["ambulances"]
    assert after < before


def test_auto_allocate_critical_has_highest_priority():
    incident = _make_incident(severity=IncidentSeverity.CRITICAL)
    result = auto_allocate(incident)
    assert result.priority == SEVERITY_PRIORITY[IncidentSeverity.CRITICAL]


def test_auto_allocate_explicit_resources():
    incident = _make_incident(
        resources_needed={"ambulances": 3, "fire_trucks": 2},
    )
    result = auto_allocate(incident)
    assert result.fulfilled.get("ambulances", 0) > 0
    # All fulfilled resources were actually recorded as allocations
    total_in_allocs = sum(
        a.quantity for a in result.allocations if a.resource_type == "ambulances"
    )
    assert total_in_allocs == result.fulfilled.get("ambulances", 0)


def test_auto_allocate_no_double_allocation():
    """Each allocation references a unique combination of source+resource."""
    incident = _make_incident(
        resources_needed={"ambulances": 10},
    )
    result = auto_allocate(incident)
    keys = [(a.source_district_id, a.resource_type) for a in result.allocations]
    assert len(keys) == len(set(keys)), "Duplicate allocations detected"


def test_release_allocation_returns_resources():
    incident = _make_incident(resources_needed={"ambulances": 5})
    result = auto_allocate(incident)
    assert len(result.allocations) > 0

    alloc = result.allocations[0]
    before = store.get_district_resources(alloc.source_district_id)[alloc.resource_type]
    ok = release_allocation(alloc.id)
    after = store.get_district_resources(alloc.source_district_id)[alloc.resource_type]

    assert ok
    assert after == before + alloc.quantity


def test_release_nonexistent_allocation():
    assert not release_allocation("does-not-exist")


def test_get_allocation_summary():
    incident = _make_incident(resources_needed={"ambulances": 2})
    auto_allocate(incident)
    summary = get_allocation_summary(incident.id)
    assert summary["incident_id"] == incident.id
    assert summary["total_allocations"] > 0
    assert "ambulances" in summary["resources_allocated"]


def test_severity_priorities_are_ordered():
    assert (
        SEVERITY_PRIORITY[IncidentSeverity.LOW]
        < SEVERITY_PRIORITY[IncidentSeverity.MEDIUM]
        < SEVERITY_PRIORITY[IncidentSeverity.HIGH]
        < SEVERITY_PRIORITY[IncidentSeverity.CRITICAL]
    )


def test_incident_resource_requirements_defined():
    for itype in IncidentType:
        assert itype in INCIDENT_RESOURCE_REQUIREMENTS, \
            f"No resource requirements defined for {itype}"
