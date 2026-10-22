"""Tests for main pipeline orchestrator."""

from datetime import datetime, timezone
from pathlib import Path
from icalendar import Calendar
from src.config import COUNTIES
from src.main import run_pipeline


def test_run_pipeline_end_to_end(tmp_path: Path) -> None:
    """Test full pipeline execution with sample fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_warnings.json"
    template_path = Path(__file__).parent.parent / "web" / "index_template.html"

    # Use a fixed test timestamp: 2026-10-22 12:00 UTC (before all sample warning expiries)
    test_now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)

    run_pipeline(
        output_dir=tmp_path,
        source=str(fixture_path),
        template_path=template_path,
        now_utc=test_now,
    )

    # 1. Check all.ics
    all_ics = tmp_path / "all.ics"
    assert all_ics.exists()
    all_cal = Calendar.from_ical(all_ics.read_text(encoding="utf-8"))
    events = [c for c in all_cal.walk() if c.name == "VEVENT"]
    assert len(events) == 4

    # 2. Check all 26 counties exist
    for county in COUNTIES:
        slug = county["slug"]
        county_ics = tmp_path / f"{slug}.ics"
        assert county_ics.exists(), f"Missing feed for {slug}"

        c_cal = Calendar.from_ical(county_ics.read_text(encoding="utf-8"))
        c_events = [c for c in c_cal.walk() if c.name == "VEVENT"]

        if slug in ("dublin", "cork", "kerry", "waterford", "wexford", "wicklow"):
            assert len(c_events) >= 1

    # 3. Check index.html
    index_file = tmp_path / "index.html"
    assert index_file.exists()
    index_html = index_file.read_text(encoding="utf-8")
    assert "Met Éireann Weather Warning Calendars" in index_html
    assert "All Ireland (Nationwide Feed)" in index_html
    assert "Co. Dublin" in index_html
    assert "Co. Cork" in index_html
    assert "Co. Galway" in index_html
    assert "webcal://" in index_html


def test_run_pipeline_empty_warnings(tmp_path: Path) -> None:
    """Test pipeline execution when there are no active warnings."""
    empty_file = tmp_path / "empty_warnings.json"
    empty_file.write_text("[]", encoding="utf-8")
    template_path = Path(__file__).parent.parent / "web" / "index_template.html"

    run_pipeline(
        output_dir=tmp_path,
        source=str(empty_file),
        template_path=template_path,
    )

    all_ics = tmp_path / "all.ics"
    assert all_ics.exists()
    all_cal = Calendar.from_ical(all_ics.read_text(encoding="utf-8"))
    events = [c for c in all_cal.walk() if c.name == "VEVENT"]
    assert len(events) == 0

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Active Warnings Nationwide: <strong>0</strong>" in index_html
    assert "✓ No Warnings" in index_html
