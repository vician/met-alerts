"""Tests for warning parsing and normalization."""

from datetime import datetime, timezone
import json
from pathlib import Path
from src.parser import (
    html_to_plain_text,
    normalize_level,
    normalize_warning_type,
    parse_datetime,
    parse_warning,
    parse_warnings_feed,
)


def test_html_to_plain_text() -> None:
    """Ensure HTML formatting is cleaned into readable plain text."""
    html_content = (
        "<p>Heavy rain expected.</p>"
        "<p>&nbsp;</p>"
        "<ul>"
        "<li>Flooding possible</li>"
        "<li>Difficult travelling conditions</li>"
        "</ul>"
    )
    cleaned = html_to_plain_text(html_content)
    assert "Heavy rain expected." in cleaned
    assert "• Flooding possible" in cleaned
    assert "• Difficult travelling conditions" in cleaned
    assert "&nbsp;" not in cleaned
    assert "<p>" not in cleaned


def test_parse_datetime_utc() -> None:
    """Ensure timestamps are correctly converted to UTC timezone."""
    dt = parse_datetime("2026-10-22T19:00:00+01:00")
    assert dt is not None
    assert dt.tzinfo == timezone.utc
    assert dt.hour == 18  # 19:00 +01:00 is 18:00 UTC
    assert dt.day == 22

    dt_z = parse_datetime("2026-10-22T18:00:00Z")
    assert dt_z is not None
    assert dt_z.tzinfo == timezone.utc
    assert dt_z.hour == 18


def test_normalize_level() -> None:
    """Verify warning levels are properly normalized."""
    assert normalize_level("yellow") == "Yellow"
    assert normalize_level("orange") == "Orange"
    assert normalize_level("red") == "Red"
    assert normalize_level("advisory") == "Advisory"
    assert normalize_level(None, headline="Status Orange - Wind warning") == "Orange"
    assert normalize_level(None, headline="Status Red - Severe weather") == "Red"
    assert normalize_level(None, headline="Status Yellow - Rain warning") == "Yellow"


def test_normalize_warning_type() -> None:
    """Verify warning types are properly normalized."""
    assert normalize_warning_type("Rain") == "Rain"
    assert normalize_warning_type("small-craft") == "Small Craft"
    assert normalize_warning_type("gale") == "Gale"
    assert normalize_warning_type("wind") == "Wind"
    assert normalize_warning_type("snow/ice") == "Snow/Ice"
    assert normalize_warning_type(None, headline="Marine Gale warning") == "Gale"


def test_parse_warning_fixture() -> None:
    """Test parsing the complete sample warnings fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_warnings.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    warnings = parse_warnings_feed(data)
    assert len(warnings) == 4

    # Warning 1: Rain for Leinster, Munster
    w1 = warnings[0]
    assert w1.id == "1"
    assert w1.level == "Yellow"
    assert w1.warning_type == "Rain"
    assert "dublin" in w1.affected_counties
    assert "cork" in w1.affected_counties
    assert "kerry" in w1.affected_counties

    # Warning 2: Marine Small Craft warning for all coasts
    w2 = warnings[1]
    assert w2.id == "2"
    assert w2.warning_type == "Small Craft"
    assert w2.is_nationwide is False
    assert w2.is_marine is True

    # Warning 3 (id=5): Rain for Cork, Kerry, Waterford
    w3 = warnings[2]
    assert w3.id == "5"
    assert w3.level == "Orange"
    assert w3.affected_counties == {"cork", "kerry", "waterford"}

    # Warning 4 (id=6): Rain for Dublin, Wexford, Wicklow
    w4 = warnings[3]
    assert w4.id == "6"
    assert w4.level == "Orange"
    assert w4.affected_counties == {"dublin", "wexford", "wicklow"}


def test_parse_invalid_warning() -> None:
    """Test missing or invalid alert dictionaries are handled cleanly."""
    assert parse_warning({}) is None
    assert parse_warning({"id": 1}) is None  # Missing onset
