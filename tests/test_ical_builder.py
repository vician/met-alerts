"""Tests for RFC 5545 iCalendar generation."""

from datetime import datetime, timezone
import json
from pathlib import Path
from icalendar import Calendar
from src.ical_builder import build_calendar_feed, export_calendar_ics
from src.parser import parse_warnings_feed


def test_empty_calendar() -> None:
    """Ensure empty feeds still generate a valid VCALENDAR object."""
    cal = build_calendar_feed(feed_slug="dublin", warnings=[], county_name="Dublin")
    ics_str = export_calendar_ics(cal)

    assert "BEGIN:VCALENDAR" in ics_str
    assert "VERSION:2.0" in ics_str
    assert "PRODID:-//Met Éireann Calendar Feeds//met-alerts//EN" in ics_str
    assert "X-WR-CALNAME:Met Éireann Weather Warnings - Co. Dublin" in ics_str
    assert "BEGIN:VEVENT" not in ics_str
    assert "END:VCALENDAR" in ics_str


def test_calendar_with_events() -> None:
    """Verify generated VEVENT objects meet all RFC 5545 and project specs."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_warnings.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    warnings = parse_warnings_feed(data)

    cal = build_calendar_feed(
        feed_slug="dublin",
        warnings=warnings,
        county_name="Dublin",
        now_utc=datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc),
    )
    ics_str = export_calendar_ics(cal)

    # Validate parsing with icalendar parser
    parsed_cal = Calendar.from_ical(ics_str)
    assert parsed_cal.get("version") == "2.0"
    events = [c for c in parsed_cal.walk() if c.name == "VEVENT"]
    assert len(events) == 4

    for event in events:
        # UID deterministic format
        uid = str(event.get("uid"))
        assert uid.startswith("met-eireann-")
        assert uid.endswith("-dublin@met-eireann-calendar")

        # Status & Transparency
        assert str(event.get("status")) == "CONFIRMED"
        assert str(event.get("transp")) == "TRANSPARENT"

        # Summary format
        summary = str(event.get("summary"))
        assert summary.startswith("[")
        assert "] Met Éireann Warning:" in summary

        # Description requirements
        desc = str(event.get("description"))
        assert "Warning Level:" in desc
        assert "Weather Type:" in desc
        assert "Valid Period:" in desc
        assert "Impacted Areas:" in desc
        assert "Source: Met Éireann Open Data. Please consult met.ie for updates." in desc

        # Categories
        cats = event.get("categories")
        assert cats is not None

        # DTSTART and DTEND UTC formatting
        dtstart = event.get("dtstart").dt
        dtend = event.get("dtend").dt
        assert dtstart.tzinfo is not None
        assert dtend.tzinfo is not None
        assert dtend >= dtstart


def test_uid_determinism() -> None:
    """Ensure repeated runs produce identical UIDs."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_warnings.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    warnings = parse_warnings_feed(data)

    cal1 = build_calendar_feed(feed_slug="cork", warnings=warnings, county_name="Cork")
    cal2 = build_calendar_feed(feed_slug="cork", warnings=warnings, county_name="Cork")

    uids1 = [str(c.get("uid")) for c in cal1.walk() if c.name == "VEVENT"]
    uids2 = [str(c.get("uid")) for c in cal2.walk() if c.name == "VEVENT"]

    assert uids1 == uids2
