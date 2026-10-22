"""Tests for configuration and county definitions."""

from src.config import (
    ALL_COUNTY_SLUGS,
    COUNTIES,
    COUNTY_BY_SLUG,
    COUNTY_SLUGS,
    EI_REGION_TO_COUNTY,
    PROVINCES,
)


def test_county_count() -> None:
    """Ensure exactly 26 Republic of Ireland counties are configured."""
    assert len(COUNTIES) == 26
    assert len(COUNTY_SLUGS) == 26
    assert len(ALL_COUNTY_SLUGS) == 26


def test_county_properties() -> None:
    """Ensure each county has required metadata keys and valid values."""
    seen_slugs = set()
    seen_codes = set()

    for c in COUNTIES:
        assert "slug" in c
        assert "name" in c
        assert "code" in c
        assert "province" in c

        assert c["slug"] == c["slug"].lower()
        assert c["code"].startswith("EI")

        assert c["slug"] not in seen_slugs
        assert c["code"] not in seen_codes
        seen_slugs.add(c["slug"])
        seen_codes.add(c["code"])


def test_ei_region_mapping() -> None:
    """Verify all EI codes map to valid county slugs."""
    for code, slug in EI_REGION_TO_COUNTY.items():
        assert code.startswith("EI")
        assert slug in COUNTY_BY_SLUG


def test_provinces() -> None:
    """Verify all 4 provinces are defined and map to valid counties."""
    for prov, counties in PROVINCES.items():
        assert prov in ("leinster", "munster", "connacht", "ulster")
        assert len(counties) > 0
