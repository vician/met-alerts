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

When deployed to GitHub Pages at `https://<username>.github.io/<repo-name>/`:

| Feed | URL | Protocol |
| :--- | :--- | :--- |
| **Nationwide (All Warnings)** | `https://<username>.github.io/<repo-name>/all.ics` | `webcal://<username>.github.io/<repo-name>/all.ics` |
| **County Dublin** | `https://<username>.github.io/<repo-name>/dublin.ics` | `webcal://<username>.github.io/<repo-name>/dublin.ics` |
| **County Cork** | `https://<username>.github.io/<repo-name>/cork.ics` | `webcal://<username>.github.io/<repo-name>/cork.ics` |
| **County Galway** | `https://<username>.github.io/<repo-name>/galway.ics` | `webcal://<username>.github.io/<repo-name>/galway.ics` |
| *Any other county* | `https://<username>.github.io/<repo-name>/<slug>.ics` | `webcal://<username>.github.io/<repo-name>/<slug>.ics` |

*(County slugs are standard lowercase names: `carlow`, `cavan`, `clare`, `cork`, `donegal`, `dublin`, `galway`, `kerry`, `kildare`, `kilkenny`, `laois`, `leitrim`, `limerick`, `longford`, `louth`, `mayo`, `meath`, `monaghan`, `offaly`, `roscommon`, `sligo`, `tipperary`, `waterford`, `westmeath`, `wexford`, `wicklow`)*

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
   `https://<your-username>.github.io/<your-repo>/`

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
git clone https://github.com/your-username/met-alerts.git
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
