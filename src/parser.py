"""Parser for Met Éireann weather warnings data."""

from dataclasses import dataclass
from datetime import datetime, timezone
import html
from html.parser import HTMLParser
import logging
import re
from typing import Any, Dict, List, Optional, Set
from dateutil import parser as date_parser

from src.config import (
    ALL_COUNTY_SLUGS,
    COUNTY_BY_SLUG,
    EI_REGION_TO_COUNTY,
    MARINE_REGIONS,
    PROVINCES,
)

logger = logging.getLogger(__name__)


class _HTMLToPlainTextParser(HTMLParser):
    """Converts HTML markup into clean, readable plain text for calendar descriptions."""

    def __init__(self) -> None:
        super().__init__()
        self.pieces: List[str] = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        tag = tag.lower()
        if tag in ("p", "div", "tr"):
            self.pieces.append("\n")
        elif tag == "br":
            self.pieces.append("\n")
        elif tag == "li":
            self.pieces.append("\n• ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in ("p", "div", "ul", "ol", "table"):
            self.pieces.append("\n")

    def handle_data(self, data: str) -> None:
        self.pieces.append(data)

    def get_text(self) -> str:
        raw = "".join(self.pieces)
        raw = html.unescape(raw)
        # Collapse excessive blank lines
        lines = [line.strip() for line in raw.split("\n")]
        cleaned: List[str] = []
        for line in lines:
            if line:
                cleaned.append(line)
            elif cleaned and cleaned[-1] != "":
                cleaned.append("")
        return "\n".join(cleaned).strip()


def html_to_plain_text(html_content: Optional[str]) -> str:
    """Strip HTML tags and convert formatting to clean plaintext."""
    if not html_content:
        return ""
    parser = _HTMLToPlainTextParser()
    try:
        parser.feed(html_content)
        parser.close()
        text = parser.get_text()
        return text if text else html.unescape(html_content).strip()
    except Exception:
        # Fallback to regex tag stripping
        clean = re.sub(r"<[^>]+>", " ", html_content)
        return html.unescape(re.sub(r"\s+", " ", clean)).strip()


@dataclass
class WeatherWarning:
    """Represents a standardized Met Éireann weather warning."""

    id: str
    cap_id: str
    level: str  # Yellow, Orange, Red, Advisory
    warning_type: str  # Rain, Wind, Gale, Snow/Ice, etc.
    severity: str
    certainty: str
    headline: str
    description: str  # Clean plain-text
    raw_description: str
    onset: datetime  # UTC
    expiry: datetime  # UTC
    issued: Optional[datetime]
    updated: Optional[datetime]
    status: str
    affected_counties: Set[str]  # Set of county slugs
    is_nationwide: bool
    is_marine: bool
    raw_regions: List[str]


def parse_datetime(dt_val: Any) -> Optional[datetime]:
    """Parse date string into UTC datetime object."""
    if not dt_val:
        return None
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is None:
            return dt_val.replace(tzinfo=timezone.utc)
        return dt_val.astimezone(timezone.utc)
    try:
        dt = date_parser.parse(str(dt_val))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception as exc:
        logger.warning("Could not parse datetime string '%s': %s", dt_val, exc)
        return None


def normalize_level(raw_level: Optional[str], headline: str = "") -> str:
    """Normalize warning level to Yellow, Orange, Red, or Advisory."""
    if raw_level:
        lvl = str(raw_level).strip().lower()
        if "red" in lvl:
            return "Red"
        if "orange" in lvl:
            return "Orange"
        if "yellow" in lvl:
            return "Yellow"
        if "advisory" in lvl:
            return "Advisory"

    # Fallback to searching the headline
    headline_lower = headline.lower()
    if "status red" in headline_lower or "red warning" in headline_lower:
        return "Red"
    if "status orange" in headline_lower or "orange warning" in headline_lower:
        return "Orange"
    if "status yellow" in headline_lower or "yellow warning" in headline_lower:
        return "Yellow"
    if "advisory" in headline_lower:
        return "Advisory"

    return "Yellow"  # Default fallback


def normalize_warning_type(raw_type: Optional[str], headline: str = "") -> str:
    """Normalize warning type (e.g., Rain, Wind, Gale, Snow/Ice, Small Craft)."""
    if raw_type:
        t = str(raw_type).strip()
        t_lower = t.lower()
        if "small-craft" in t_lower or "small craft" in t_lower:
            return "Small Craft"
        if "snow" in t_lower or "ice" in t_lower:
            return "Snow/Ice"
        if "rain" in t_lower:
            return "Rain"
        if "wind" in t_lower:
            return "Wind"
        if "gale" in t_lower:
            return "Gale"
        if "storm" in t_lower:
            return "Storm"
        if "temp" in t_lower or "heat" in t_lower:
            return "High Temperature"
        if "cold" in t_lower or "frost" in t_lower:
            return "Low Temperature"
        if "thunder" in t_lower:
            return "Thunderstorm"
        if "fog" in t_lower:
            return "Fog"
        return t.title()

    # Fallback from headline
    headline_lower = headline.lower()
    for candidate in [
        ("small craft", "Small Craft"),
        ("snow", "Snow/Ice"),
        ("ice", "Snow/Ice"),
        ("rain", "Rain"),
        ("wind", "Wind"),
        ("gale", "Gale"),
        ("storm", "Storm"),
        ("fog", "Fog"),
        ("thunderstorm", "Thunderstorm"),
        ("temperature", "Temperature"),
    ]:
        if candidate[0] in headline_lower:
            return candidate[1]

    return "Weather"


def extract_counties(
    regions: List[str],
    headline: str = "",
    description: str = "",
    warning_type: str = "",
) -> tuple[Set[str], bool, bool]:
    """Extract affected county slugs from region codes and text content.

    Returns:
        (affected_counties, is_nationwide, is_marine)
    """
    affected: Set[str] = set()
    marine_count = 0
    total_regions = len(regions)

    for reg in regions:
        reg_clean = str(reg).strip().upper()
        if reg_clean in EI_REGION_TO_COUNTY:
            affected.add(EI_REGION_TO_COUNTY[reg_clean])
        elif reg_clean in MARINE_REGIONS or reg_clean.startswith("EI8"):
            marine_count += 1

    # Check for province mentions in headline if regions didn't resolve all
    combined_text = f"{headline} {description}".lower()

    for prov_name, prov_counties in PROVINCES.items():
        if re.search(r"\b" + re.escape(prov_name) + r"\b", combined_text):
            affected.update(prov_counties)

    # Check for direct county name mentions in headline if no region codes matched
    if not affected:
        for slug, meta in COUNTY_BY_SLUG.items():
            name_lower = meta["name"].lower()
            pattern = r"\b" + re.escape(name_lower) + r"\b"
            if re.search(pattern, combined_text):
                affected.add(slug)

    # Check if this alert is marine
    hl_lower = headline.lower()
    is_marine = False
    if (marine_count > 0 and not affected) or (
        any(k in hl_lower for k in ("marine", "small craft", "all coasts", "irish sea"))
        and not affected
    ):
        is_marine = True

    # Check for nationwide terrestrial land indicators (only if not a marine-only warning)
    is_nationwide = False
    if not is_marine:
        nationwide_patterns = [
            r"\bnationwide\b",
            r"\ball counties\b",
            r"\bentire country\b",
            r"\ball of ireland\b",
        ]
        for pat in nationwide_patterns:
            if re.search(pat, hl_lower):
                is_nationwide = True
                break

        # If all 26 counties are present in affected, it is nationwide
        if len(affected.intersection(ALL_COUNTY_SLUGS)) == len(ALL_COUNTY_SLUGS):
            is_nationwide = True

    return affected, is_nationwide, is_marine

    return affected, is_nationwide, is_marine


def parse_warning(raw_alert: Dict[str, Any]) -> Optional[WeatherWarning]:
    """Parse a single raw warning item into a standardized WeatherWarning object."""
    if not isinstance(raw_alert, dict):
        return None

    # Alert Identifier
    alert_id = str(
        raw_alert.get("id")
        or raw_alert.get("capId")
        or raw_alert.get("identifier")
        or ""
    ).strip()
    cap_id = str(raw_alert.get("capId") or alert_id).strip()
    if not alert_id:
        return None

    # Headline & Text
    headline = str(raw_alert.get("headline") or raw_alert.get("header") or "Weather Warning").strip()
    raw_desc = str(raw_alert.get("description") or raw_alert.get("warnText") or "").strip()
    clean_desc = html_to_plain_text(raw_desc)

    # Dates
    onset = parse_datetime(
        raw_alert.get("onset")
        or raw_alert.get("validFrom")
        or raw_alert.get("validFromTime")
        or raw_alert.get("startTime")
    )
    expiry = parse_datetime(
        raw_alert.get("expiry")
        or raw_alert.get("validTo")
        or raw_alert.get("validToTime")
        or raw_alert.get("endTime")
    )
    issued = parse_datetime(raw_alert.get("issued") or raw_alert.get("sent"))
    updated = parse_datetime(raw_alert.get("updated") or raw_alert.get("modified") or raw_alert.get("issued"))

    if onset is None:
        logger.warning("Warning %s missing onset timestamp; skipping.", alert_id)
        return None

    if expiry is None:
        # Default to onset + 24 hours if missing
        expiry = onset.replace() + date_parser.relativedelta(hours=24)

    # Levels and types
    raw_level = raw_alert.get("level") or raw_alert.get("globalAwarenessLevel") or raw_alert.get("severity")
    level = normalize_level(raw_level, headline)

    raw_type = raw_alert.get("type") or raw_alert.get("warningType") or raw_alert.get("category")
    warning_type = normalize_warning_type(raw_type, headline)

    severity = str(raw_alert.get("severity") or level).strip()
    certainty = str(raw_alert.get("certainty") or "Observed").strip()
    status = str(raw_alert.get("status") or "Warning").strip()

    # Regions / Counties
    regions_field = raw_alert.get("regions") or raw_alert.get("counties") or []
    if isinstance(regions_field, str):
        regions_list = [r.strip() for r in regions_field.split(",") if r.strip()]
    elif isinstance(regions_field, list):
        regions_list = [str(r).strip() for r in regions_field if r]
    else:
        regions_list = []

    affected_counties, is_nationwide, is_marine = extract_counties(
        regions_list, headline, clean_desc, warning_type
    )

    return WeatherWarning(
        id=alert_id,
        cap_id=cap_id,
        level=level,
        warning_type=warning_type,
        severity=severity,
        certainty=certainty,
        headline=headline,
        description=clean_desc,
        raw_description=raw_desc,
        onset=onset,
        expiry=expiry,
        issued=issued,
        updated=updated,
        status=status,
        affected_counties=affected_counties,
        is_nationwide=is_nationwide,
        is_marine=is_marine,
        raw_regions=regions_list,
    )


def parse_warnings_feed(raw_feed: List[Dict[str, Any]]) -> List[WeatherWarning]:
    """Parse list of raw alert dictionaries into validated WeatherWarning objects."""
    parsed: List[WeatherWarning] = []
    for item in raw_feed:
        try:
            warning = parse_warning(item)
            if warning:
                parsed.append(warning)
        except Exception as exc:
            logger.warning("Error parsing warning item: %s; error: %s", item, exc)
    return parsed
