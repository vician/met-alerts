"""Orchestrator for Met Éireann weather warning calendar feeds generation."""

import argparse
from datetime import datetime, timezone
import logging
from pathlib import Path
import sys
from typing import Dict, List, Optional, Set

from src.config import COUNTIES, COUNTY_BY_SLUG
from src.fetcher import fetch_warnings
from src.ical_builder import build_calendar_feed, export_calendar_ics
from src.parser import WeatherWarning, parse_warnings_feed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("met_alerts")


def get_severity_badge_html(warnings: List[WeatherWarning]) -> str:
    """Generate HTML badge representing active warnings status."""
    if not warnings:
        return '<span class="badge badge-none">✓ No Warnings</span>'

    # Check highest severity level among active warnings
    levels = {w.level.lower() for w in warnings}
    count = len(warnings)
    label = f"{count} Active Warning" if count == 1 else f"{count} Active Warnings"

    if "red" in levels:
        types = ", ".join(sorted({w.warning_type for w in warnings if w.level.lower() == "red"}))
        return f'<span class="badge badge-red">⚠️ {label} (Red: {types})</span>'
    if "orange" in levels:
        types = ", ".join(sorted({w.warning_type for w in warnings if w.level.lower() == "orange"}))
        return f'<span class="badge badge-orange">⚠️ {label} (Orange: {types})</span>'
    if "yellow" in levels:
        types = ", ".join(sorted({w.warning_type for w in warnings if w.level.lower() == "yellow"}))
        return f'<span class="badge badge-yellow">⚠️ {label} (Yellow: {types})</span>'

    return f'<span class="badge badge-yellow">⚠️ {label}</span>'


def generate_county_card_html(
    county: Dict[str, str],
    county_warnings: List[WeatherWarning],
) -> str:
    """Render HTML for an individual county feed card."""
    slug = county["slug"]
    name = county["name"]
    province = county.get("province", "Ireland")
    feed_file = f"{slug}.ics"
    badge_html = get_severity_badge_html(county_warnings)

    return f"""
    <div class="county-card" data-county="{name.lower()}" data-province="{province.lower()}">
      <div>
        <div class="county-header">
          <div>
            <div class="county-title">Co. {name}</div>
            <div class="county-meta">{province} • {county.get('code', '')}</div>
          </div>
          <div>{badge_html}</div>
        </div>
      </div>
      <div class="button-group">
        <a href="webcal://{feed_file}" class="btn btn-primary" onclick="handleSubscribe(event, '{feed_file}')">
          <span>📅 Subscribe</span>
        </a>
        <button class="btn btn-secondary" onclick="copyFeedUrl('{feed_file}')">
          <span>📋 Copy URL</span>
        </button>
      </div>
    </div>"""


def generate_index_html(
    template_path: Path,
    output_path: Path,
    all_active_warnings: List[WeatherWarning],
    county_warnings_map: Dict[str, List[WeatherWarning]],
    now_utc: datetime,
) -> None:
    """Populate index_template.html with active feeds and county data."""
    if not template_path.exists():
        logger.error("Template file not found at %s", template_path)
        raise FileNotFoundError(f"Template not found: {template_path}")

    template_content = template_path.read_text(encoding="utf-8")

    # Render county cards
    county_cards_html = []
    for county in sorted(COUNTIES, key=lambda c: c["name"]):
        c_warnings = county_warnings_map.get(county["slug"], [])
        county_cards_html.append(generate_county_card_html(county, c_warnings))

    cards_joined = "\n".join(county_cards_html)
    nationwide_badge = get_severity_badge_html(all_active_warnings)
    last_updated_str = now_utc.strftime("%Y-%m-%d %H:%M")

    # String replacements
    rendered = template_content.replace("{{ TOTAL_ACTIVE_WARNINGS }}", str(len(all_active_warnings)))
    rendered = rendered.replace("{{ LAST_UPDATED_UTC }}", last_updated_str)
    rendered = rendered.replace("{{ NATIONWIDE_BADGE }}", nationwide_badge)
    rendered = rendered.replace("{{ COUNTY_TOTAL_COUNT }}", str(len(COUNTIES)))
    rendered = rendered.replace("{{ COUNTY_CARDS }}", cards_joined)
    rendered = rendered.replace("{{ SITE_HOST }}", "")

    output_path.write_text(rendered, encoding="utf-8")
    logger.info("Generated landing page at %s", output_path)


def run_pipeline(
    output_dir: Path,
    source: Optional[str] = None,
    template_path: Optional[Path] = None,
    now_utc: Optional[datetime] = None,
    filter_expired: bool = True,
) -> None:
    """Execute the end-to-end feed generation pipeline."""
    now = now_utc or datetime.now(timezone.utc)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch raw warnings
    raw_warnings = fetch_warnings(source=source)
    logger.info("Raw items retrieved: %d", len(raw_warnings))

    # 2. Parse into domain objects
    parsed_warnings = parse_warnings_feed(raw_warnings)
    logger.info("Parsed %d warnings successfully.", len(parsed_warnings))

    # 3. Filter active warnings (not yet expired)
    if filter_expired:
        active_warnings = [w for w in parsed_warnings if w.expiry >= now]
    else:
        active_warnings = parsed_warnings

    logger.info("Active warnings (expiry >= %s): %d", now.isoformat(), len(active_warnings))

    # 4. Generate nationwide feed (all.ics)
    all_cal = build_calendar_feed(
        feed_slug="all",
        warnings=active_warnings,
        now_utc=now,
    )
    all_ics_path = output_dir / "all.ics"
    all_ics_path.write_text(export_calendar_ics(all_cal), encoding="utf-8")
    logger.info("Wrote nationwide feed: %s (%d events)", all_ics_path, len(active_warnings))

    # 5. Generate per-county feeds (<county>.ics)
    county_warnings_map: Dict[str, List[WeatherWarning]] = {}

    for county in COUNTIES:
        slug = county["slug"]
        c_name = county["name"]

        # An alert applies to this county if:
        # - it is nationwide, OR
        # - this county slug is in the alert's affected counties
        c_warnings = [
            w for w in active_warnings
            if w.is_nationwide or (slug in w.affected_counties)
        ]
        county_warnings_map[slug] = c_warnings

        cal = build_calendar_feed(
            feed_slug=slug,
            warnings=c_warnings,
            county_name=c_name,
            now_utc=now,
        )
        c_path = output_dir / f"{slug}.ics"
        c_path.write_text(export_calendar_ics(cal), encoding="utf-8")

    logger.info("Generated %d per-county .ics feeds.", len(COUNTIES))

    # 6. Generate dist/index.html
    tpl_path = template_path or (Path(__file__).parent.parent / "web" / "index_template.html")
    index_out_path = output_dir / "index.html"
    generate_index_html(
        template_path=tpl_path,
        output_path=index_out_path,
        all_active_warnings=active_warnings,
        county_warnings_map=county_warnings_map,
        now_utc=now,
    )

    print("\n" + "=" * 60)
    print(" Met Éireann Weather Warning Calendar Feeds Generated")
    print("=" * 60)
    print(f" Output directory : {output_dir.resolve()}")
    print(f" Active warnings  : {len(active_warnings)} nationwide")
    print(f" County feeds     : {len(COUNTIES)} counties")
    print(f" Landing page     : {index_out_path.name}")
    print("=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Met Éireann weather warning calendar feeds (.ics) and web directory."
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Directory to write .ics feeds and index.html into (default: dist)",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Optional local JSON file or custom URL to fetch warnings from.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute pipeline and output summary without making network changes.",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    try:
        run_pipeline(output_dir=output_dir, source=args.source)
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
