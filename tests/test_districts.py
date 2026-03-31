"""
Tests for the Tamil Nadu districts data module.
"""

import pytest
from src.districts import (
    TAMIL_NADU_DISTRICTS,
    DISTRICTS_BY_ID,
    DISTRICTS_BY_NAME,
    TOTAL_DISTRICTS,
    get_district,
    get_district_by_name,
    list_districts,
)


def test_total_district_count():
    assert TOTAL_DISTRICTS == 38, f"Expected 38 districts, got {TOTAL_DISTRICTS}"


def test_all_districts_have_unique_ids():
    ids = [d.id for d in TAMIL_NADU_DISTRICTS]
    assert len(ids) == len(set(ids)), "Duplicate district IDs found"


def test_all_districts_have_unique_names():
    names = [d.name for d in TAMIL_NADU_DISTRICTS]
    assert len(names) == len(set(names)), "Duplicate district names found"


def test_districts_by_id_index_size():
    assert len(DISTRICTS_BY_ID) == 38


def test_districts_by_name_index_size():
    assert len(DISTRICTS_BY_NAME) == 38


def test_get_district_valid():
    d = get_district("TN-CHE")
    assert d.name == "Chennai"
    assert d.id == "TN-CHE"


def test_get_district_invalid():
    with pytest.raises(KeyError):
        get_district("TN-INVALID")


def test_get_district_by_name_case_insensitive():
    d = get_district_by_name("chennai")
    assert d.id == "TN-CHE"
    d2 = get_district_by_name("CHENNAI")
    assert d2.id == "TN-CHE"


def test_get_district_by_name_invalid():
    with pytest.raises(KeyError):
        get_district_by_name("nonexistent")


def test_all_districts_have_coordinates():
    for d in TAMIL_NADU_DISTRICTS:
        assert d.latitude is not None, f"{d.name} missing latitude"
        assert d.longitude is not None, f"{d.name} missing longitude"
        assert 7.0 <= d.latitude <= 14.0, f"{d.name} latitude out of TN range"
        assert 75.0 <= d.longitude <= 81.0, f"{d.name} longitude out of TN range"


def test_all_districts_have_resources():
    required_resources = {
        "ambulances", "fire_trucks", "police_units",
        "rescue_teams", "medical_kits",
    }
    for d in TAMIL_NADU_DISTRICTS:
        for rtype in required_resources:
            assert rtype in d.resources, f"{d.name} missing resource '{rtype}'"
            assert d.resources[rtype] > 0, f"{d.name} has 0 {rtype}"


def test_all_districts_have_positive_population():
    for d in TAMIL_NADU_DISTRICTS:
        assert d.population > 0, f"{d.name} has non-positive population"


def test_list_districts_returns_dicts():
    districts = list_districts()
    assert len(districts) == 38
    for d in districts:
        assert isinstance(d, dict)
        assert "id" in d
        assert "name" in d
        assert "resources" in d


def test_district_to_dict():
    d = get_district("TN-MDU")
    data = d.to_dict()
    assert data["name"] == "Madurai"
    assert "resources" in data
    assert isinstance(data["resources"], dict)


def test_well_known_districts_present():
    """Verify key Tamil Nadu districts are in the dataset."""
    expected = [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli",
        "Salem", "Tirunelveli", "Kanyakumari", "Nilgiris",
        "Mayiladuthurai",  # 38th district
    ]
    names_in_data = {d.name for d in TAMIL_NADU_DISTRICTS}
    for name in expected:
        assert name in names_in_data, f"Expected district '{name}' not found"
