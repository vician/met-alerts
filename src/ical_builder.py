"""iCalendar (RFC 5545) feed builder for Met Éireann weather warnings."""

from datetime import datetime, timezone
from typing import List, Optional
from icalendar import Calendar, Event

from src.config import COUNTY_BY_SLUG
from src.parser import WeatherWarning


def format_description(warning: WeatherWarning) -> str:
    """Format description string according to project requirements."""
    start_str = warning.onset.strftime("%Y-%m-%d %H:%M UTC")
    end_str = warning.expiry.strftime("%Y-%m-%d %H:%M UTC")

    if warning.is_nationwide:
        impacted = "All of Ireland / Nationwide"
    elif warning.affected_counties:
        names = sorted(
            [COUNTY_BY_SLUG[s]["name"] for s in warning.affected_counties if s in COUNTY_BY_SLUG]
        )
        impacted = ", ".join(names) if names else ", ".join(sorted(warning.affected_counties))
    elif warning.is_marine:
        impacted = "Coastal & Marine Areas"
    else:
        impacted = "Ireland (see met.ie)"

    lines = [
        f"Warning Level: Status {warning.level}",
        f"Weather Type: {warning.warning_type}",
        f"Valid Period: {start_str} to {end_str}",
        f"Impacted Areas: {impacted}",
        "",
        "--- Summary ---",
        warning.headline,
        "",
        "--- Warning Details & Advice ---",
        warning.description if warning.description else "No additional description provided.",
        "",
        "Source: Met Éireann Open Data. Please consult met.ie for updates.",
    ]
    return "\n".join(lines)


def build_calendar_feed(
    feed_slug: str,
    warnings: List[WeatherWarning],
    county_name: Optional[str] = None,
    now_utc: Optional[datetime] = None,
) -> Calendar:
    """Build an RFC 5545 compliant Calendar object for a given county or national feed.

    Args:
        feed_slug: Slug of the feed (e.g. 'all', 'dublin', 'cork').
        warnings: List of WeatherWarning objects applicable to this feed.
        county_name: Human-friendly name of the county (e.g. 'Dublin').
        now_utc: Timestamp for DTSTAMP and metadata (defaults to current UTC time).

    Returns:
        icalendar.Calendar object ready for serialization.
    """
    now = now_utc or datetime.now(timezone.utc)

    cal = Calendar()
    cal.add("prodid", "-//Met Éireann Calendar Feeds//met-alerts//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    if feed_slug == "all":
        cal_name = "Met Éireann Weather Warnings - Nationwide"
        cal_desc = "Live weather warning calendar feed for all of Ireland from Met Éireann Open Data."
    elif county_name:
        cal_name = f"Met Éireann Weather Warnings - Co. {county_name}"
        cal_desc = f"Live weather warning calendar feed for County {county_name} from Met Éireann Open Data."
    else:
        cal_name = f"Met Éireann Weather Warnings - {feed_slug.capitalize()}"
        cal_desc = f"Live weather warning calendar feed for {feed_slug.capitalize()} from Met Éireann Open Data."

    cal.add("x-wr-calname", cal_name)
    cal.add("x-wr-caldesc", cal_desc)
    cal.add("x-wr-timezone", "UTC")
    # Recommended client refresh interval: 30 minutes
    cal.add("refresh-interval;value=duration", "PT30M")
    cal.add("x-published-ttl", "PT30M")

    for warning in warnings:
        event = Event()

        # Deterministic and persistent UID per county feed
        uid = f"met-eireann-{warning.id}-{feed_slug}@met-eireann-calendar"
        event.add("uid", uid)
        event.add("dtstamp", now)
        event.add("dtstart", warning.onset)
        event.add("dtend", warning.expiry)

        # SUMMARY: [{LEVEL} {TYPE}] Met Éireann Warning: {HEADLINE}
        summary = f"[{warning.level} {warning.warning_type}] Met Éireann Warning: {warning.headline}"
        event.add("summary", summary)

        # DESCRIPTION
        event.add("description", format_description(warning))

        # STATUS & TRANSP
        event.add("status", "CONFIRMED")
        event.add("transp", "TRANSPARENT")  # Do not block calendar time

        # CATEGORIES
        event.add("categories", [warning.level, warning.warning_type])

        # Timestamps & revision
        if warning.updated:
            event.add("last-modified", warning.updated)
        elif warning.issued:
            event.add("last-modified", warning.issued)

        event.add("sequence", 0)
        event.add("url", "https://www.met.ie/warnings")

        cal.add_component(event)

    return cal


def export_calendar_ics(calendar: Calendar) -> str:
    """Serialize an iCalendar object into RFC 5545 string."""
    raw_bytes = calendar.to_ical()
    # Normalize line endings to standard CRLF as required by RFC 5545
    return raw_bytes.decode("utf-8")
