# Met Éireann Weather Warning Calendar Feeds 🌦️🇮🇪

An open-source, zero-cost weather warning calendar feed generator for **Met Éireann** (Ireland's National Meteorological Service).

This project continuously fetches live Irish weather warnings, produces standard `.ics` (iCalendar/webcal) feeds per county and nationwide, and publishes them as an interactive static site directly to **GitHub Pages** via GitHub Actions.

---

## ⚡ Key Highlights

- **100% Free & Serverless**: Runs completely on GitHub Actions' free cron schedule and GitHub Pages static hosting. Zero monthly fees, zero VPS or cloud servers required.
- **Clean Git History**: Feeds are deployed as ephemeral build artifacts directly to GitHub Pages (`actions/deploy-pages`) — no Git commit noise or repository bloat.
- **RFC 5545 Compliant**: Validated iCalendar format (`.ics`) with deterministic, persistent `UID`s to ensure warning updates, extensions, and cancellations update smoothly without duplicates.
- **Granular Feeds**:
  - `all.ics`: All active warnings nationwide (including marine and coastal warnings).
  - `<county>.ics`: Individual feeds for each of the 26 counties in the Republic of Ireland (e.g., `dublin.ics`, `cork.ics`, `galway.ics`).
- **Interactive Directory Page**: Responsive, mobile-friendly landing page with live search, warning status badges (Yellow, Orange, Red), one-click `webcal://` subscription buttons, and URL copy shortcuts.

---

## 🌐 Public Feed URL Structure

Live on GitHub Pages at **`https://vician.github.io/met-alerts/`**:

### 📍 Per-County Feeds (Recommended for Personal Use)

To prevent your calendar from being overwhelmed by alerts from distant parts of the country, **subscribing to your specific county is strongly recommended**. Each feed only contains warnings that directly impact that county:

| County | Province | HTTPS Feed URL | Webcal Subscribe Link |
| :--- | :--- | :--- | :--- |
| **Carlow** | Leinster | `https://vician.github.io/met-alerts/carlow.ics` | `webcal://vician.github.io/met-alerts/carlow.ics` |
| **Cavan** | Ulster | `https://vician.github.io/met-alerts/cavan.ics` | `webcal://vician.github.io/met-alerts/cavan.ics` |
| **Clare** | Munster | `https://vician.github.io/met-alerts/clare.ics` | `webcal://vician.github.io/met-alerts/clare.ics` |
| **Cork** | Munster | `https://vician.github.io/met-alerts/cork.ics` | `webcal://vician.github.io/met-alerts/cork.ics` |
| **Donegal** | Ulster | `https://vician.github.io/met-alerts/donegal.ics` | `webcal://vician.github.io/met-alerts/donegal.ics` |
| **Dublin** | Leinster | `https://vician.github.io/met-alerts/dublin.ics` | `webcal://vician.github.io/met-alerts/dublin.ics` |
| **Galway** | Connacht | `https://vician.github.io/met-alerts/galway.ics` | `webcal://vician.github.io/met-alerts/galway.ics` |
| **Kerry** | Munster | `https://vician.github.io/met-alerts/kerry.ics` | `webcal://vician.github.io/met-alerts/kerry.ics` |
| **Kildare** | Leinster | `https://vician.github.io/met-alerts/kildare.ics` | `webcal://vician.github.io/met-alerts/kildare.ics` |
| **Kilkenny** | Leinster | `https://vician.github.io/met-alerts/kilkenny.ics` | `webcal://vician.github.io/met-alerts/kilkenny.ics` |
| **Laois** | Leinster | `https://vician.github.io/met-alerts/laois.ics` | `webcal://vician.github.io/met-alerts/laois.ics` |
| **Leitrim** | Connacht | `https://vician.github.io/met-alerts/leitrim.ics` | `webcal://vician.github.io/met-alerts/leitrim.ics` |
| **Limerick** | Munster | `https://vician.github.io/met-alerts/limerick.ics` | `webcal://vician.github.io/met-alerts/limerick.ics` |
| **Longford** | Leinster | `https://vician.github.io/met-alerts/longford.ics` | `webcal://vician.github.io/met-alerts/longford.ics` |
| **Louth** | Leinster | `https://vician.github.io/met-alerts/louth.ics` | `webcal://vician.github.io/met-alerts/louth.ics` |
| **Mayo** | Connacht | `https://vician.github.io/met-alerts/mayo.ics` | `webcal://vician.github.io/met-alerts/mayo.ics` |
| **Meath** | Leinster | `https://vician.github.io/met-alerts/meath.ics` | `webcal://vician.github.io/met-alerts/meath.ics` |
| **Monaghan** | Ulster | `https://vician.github.io/met-alerts/monaghan.ics` | `webcal://vician.github.io/met-alerts/monaghan.ics` |
| **Offaly** | Leinster | `https://vician.github.io/met-alerts/offaly.ics` | `webcal://vician.github.io/met-alerts/offaly.ics` |
| **Roscommon** | Connacht | `https://vician.github.io/met-alerts/roscommon.ics` | `webcal://vician.github.io/met-alerts/roscommon.ics` |
| **Sligo** | Connacht | `https://vician.github.io/met-alerts/sligo.ics` | `webcal://vician.github.io/met-alerts/sligo.ics` |
| **Tipperary** | Munster | `https://vician.github.io/met-alerts/tipperary.ics` | `webcal://vician.github.io/met-alerts/tipperary.ics` |
| **Waterford** | Munster | `https://vician.github.io/met-alerts/waterford.ics` | `webcal://vician.github.io/met-alerts/waterford.ics` |
| **Westmeath** | Leinster | `https://vician.github.io/met-alerts/westmeath.ics` | `webcal://vician.github.io/met-alerts/westmeath.ics` |
| **Wexford** | Leinster | `https://vician.github.io/met-alerts/wexford.ics` | `webcal://vician.github.io/met-alerts/wexford.ics` |
| **Wicklow** | Leinster | `https://vician.github.io/met-alerts/wicklow.ics` | `webcal://vician.github.io/met-alerts/wicklow.ics` |

*(Note: Weather warnings for the 6 counties of Northern Ireland are officially issued by the UK Met Office, not Met Éireann).*

### 🌐 Broader & Specialized Feeds

These feeds cover broader geographic zones or specialized marine sectors.

| Feed | URL | Protocol | Description & Notes |
| :--- | :--- | :--- | :--- |
| **Nationwide (All Warnings)** | `https://vician.github.io/met-alerts/all.ics` | `webcal://vician.github.io/met-alerts/all.ics` | **⚠️ High Volume:** Aggregates all warnings across all 26 counties and coastal waters. Can result in numerous overlapping events during stormy periods. Recommended for emergency services, transport operators, or weather enthusiasts. |
| **Coastal & Marine Waters** | `https://vician.github.io/met-alerts/marine.ics` | `webcal://vician.github.io/met-alerts/marine.ics` | **🌊 For Mariners:** Covers gale warnings, storm warnings, and small craft advisories for Irish coastal waters (up to 30nm offshore) and the Irish Sea. |

---

## 🚀 Setup & Deployment Guide

You can easily host your own instance in under 2 minutes:

### 1. Fork or Clone This Repository
Click **Fork** in the top right of this repository to create your own copy.

### 2. Enable GitHub Pages via GitHub Actions
1. In your GitHub repository, navigate to **Settings** &rarr; **Pages** (under *Code and automation*).
2. Under **Build and deployment** &rarr; **Source**, select:
   ```text
   GitHub Actions
   ```
   *(Do NOT select "Deploy from a branch").*

### 3. Trigger Initial Workflow Run
1. Go to the **Actions** tab in your repository.
2. Under Workflows in the left sidebar, click **Update Met Éireann Weather Warnings**.
3. Click the **Run workflow** dropdown on the right and click **Run workflow**.
4. Once completed (approx. 30 seconds), your site will be live at:
   `https://vician.github.io/met-alerts/`

### 4. Automatic Scheduled Updates
The workflow runs automatically every 30 minutes (at 17 and 47 minutes past the hour via cron `17,47 * * * *`). The minutes are offset from the top of the hour to avoid runner queues and rate limiting.

---

## 📱 How to Subscribe to a Calendar Feed

### 🍏 Apple Calendar (iPhone, iPad, Mac)
1. On your device, open your GitHub Pages landing page.
2. Tap **📅 Subscribe** next to your county (or nationwide).
3. In the prompt, tap **Subscribe**.
4. In the settings modal, set **Auto-refresh** to **Every 15 minutes** or **Every hour**.

### 📬 Microsoft Outlook (Desktop / Web / Mobile)
1. Copy the feed URL (click **📋 Copy URL**).
2. In Outlook, go to the Calendar view.
3. Select **Add Calendar** &rarr; **Subscribe from web**.
4. Paste the feed URL, give it a name (e.g. *Met Éireann Alerts*), and click **Import**.

### 🌐 Google Calendar (Web / Android)
1. Copy the feed URL (click **📋 Copy URL**).
2. Open Google Calendar on the web.
3. In the left panel, find **Other calendars**, click the **`+`** icon, and select **From URL**.
4. Paste the URL and click **Add calendar**.

---

## ⚠️ Important Calendar Client Caveats

> [!WARNING]
> **Google Calendar Refresh Delay:**
> While **Apple Calendar** and **Microsoft Outlook** allow configurable refresh intervals (down to every 15–30 minutes), **Google Calendar** polls external `.ics` feeds on its own backend schedule. In practice, Google Calendar often refreshes only every **8 to 24 hours**. This limitation is enforced by Google's infrastructure and cannot be overridden by feed publishers or subscribers.
>
> **Recommendation:** If you rely on time-sensitive, fast-updating weather alerts, use **Apple Calendar**, **Microsoft Outlook**, or a dedicated calendar application that respects client-side refresh intervals.

---

## 🛠️ Architecture & Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── update_warnings.yml  # GitHub Actions workflow: cron & Pages deploy
├── src/
│   ├── __init__.py
│   ├── config.py                # County lists, FIPS mappings, URLs, constants
│   ├── fetcher.py               # HTTP fetcher with timeout & fallback handling
│   ├── parser.py                # Alert normalization, UTC timestamps, HTML stripper
│   ├── ical_builder.py          # RFC 5545 VCALENDAR and VEVENT builder
│   └── main.py                  # CLI & pipeline orchestrator
├── web/
│   └── index_template.html      # Responsive landing page template
├── tests/
│   ├── fixtures/
│   │   └── sample_warnings.json # Sample payload fixture
│   ├── test_config.py
│   ├── test_fetcher.py
│   ├── test_ical_builder.py
│   ├── test_main.py
│   └── test_parser.py
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧪 Local Development & Testing

### Prerequisites
- Python 3.11+
- Virtual environment

### Setup
```bash
# Clone the repository
git clone https://github.com/vician/met-alerts.git
cd met-alerts

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt pytest
```

### Running Locally
```bash
# Fetch live data and generate feeds into dist/
python -m src.main --output-dir dist

# Or run with local sample data
python -m src.main --output-dir dist --source tests/fixtures/sample_warnings.json
```

### Running the Test Suite
```bash
pytest -v
```

---

## 📜 Data Source & Attribution

- Weather warning data is sourced directly from **[Met Éireann Open Data](https://www.met.ie/Open_Data/json/warning_ALL.json)**.
- Met Éireann is Ireland's National Meteorological Service.
- Data is provided under Met Éireann's open data terms.
- **Disclaimer:** This project is an independent open-source tool and is not officially affiliated with or endorsed by Met Éireann. Always consult **[met.ie](https://www.met.ie)** for official emergency warnings and life-safety instructions.

---

## 📄 Licence

MIT Licence. Feel free to use, modify, and distribute.
