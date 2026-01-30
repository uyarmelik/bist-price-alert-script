# Stock Market Watcher — BIST Stock Tracker & Alert Bot

A lightweight, cloud-native Python bot that monitors selected Borsa Istanbul (BIST) tickers and emails you when prices cross key levels. It runs automatically on GitHub Actions, compares the latest price against 52-week average, 52-week maximum, and your per-ticker custom targets, and persists state to prevent duplicate alerts.

- Core logic in [`check_stocks`](main.py) with email dispatch via [`send_email`](main.py).
- Configuration-driven watchlist and targets in [config.json](config.json).
- Persistent state across runs in [stock_states.json](stock_states.json).
- Automated scheduling and committing via [.github/workflows/bist-tracker.yml](.github/workflows/bist-tracker.yml).

## Highlights

- Automatic hourly checks on weekdays during BIST trading hours.
- Alerts on:
  - Price falling ≥20% below yearly average ($avg\_threshold = 0.8 \times yearly\_avg$).
  - Price falling ≥30% below yearly max ($max\_threshold = 0.7 \times yearly\_max$).
  - Crossing below/above your custom low/high targets with recovery/pullback notices.
- Clean, consolidated email notifications and stateful toggling to avoid spam.
- Zero server maintenance via GitHub Actions.

## Tech Stack

- Python 3.10
- Libraries:
  - yfinance — market data
  - pandas — series aggregation
  - smtplib — Gmail SMTP
- CI/CD:
  - GitHub Actions — scheduling, execution, auto-commit

Key modules and symbols:

- [`main.py`](main.py)
  - [`load_config`](main.py), [`load_state`](main.py), [`save_state`](main.py), [`send_email`](main.py), [`check_stocks`](main.py)
- [config.json](config.json), [stock_states.json](stock_states.json), [requirements.txt](requirements.txt), [.github/workflows/bist-tracker.yml](.github/workflows/bist-tracker.yml)

## Project Structure

- [main.py](main.py) — Fetch, compute thresholds, alerting, and state management.
- [config.json](config.json) — Watchlist and per-ticker custom targets.
- [stock_states.json](stock_states.json) — Persistent flags to avoid repeated alerts.
- [requirements.txt](requirements.txt) — Dependencies.
- [.github/workflows/bist-tracker.yml](.github/workflows/bist-tracker.yml) — Schedule and automation.
- [README.md](README.md) — Documentation.

## Configuration

Edit [config.json](config.json):

```json
{
  "tickers": ["AEFES.IS", "KONTR.IS", "SASA.IS", "ALTNY.IS", "..."],
  "target_prices": {
    "KONTR.IS": { "low": 9.1, "high": 10.26 },
    "SASA.IS": { "low": 2.26, "high": 2.86 },
    "ALTNY.IS": { "low": 15.75, "high": 17.75 },
    "PATEK.IS": { "low": 19.53, "high": 22.03 },
    "TKFEN.IS": { "low": 73.4, "high": 84.1 }
  }
}
```

Notes:

- Omit `low` or `high` if you don’t need that alert side.
- Use Yahoo Finance-compatible symbols (e.g., `*.IS` for BIST).

## Environment & Secrets

Set these environment variables (locally and in GitHub Actions repository secrets):

- `EMAIL_USER` — Sender Gmail address.
- `EMAIL_PASS` — Gmail App Password (16-digit, not your normal password).
- `RECEIVER_EMAIL` — Target inbox.

## Installation

Local:

1. Install Python 3.10+.
2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Export environment variables:

   macOS/Linux:

   ```sh
   export EMAIL_USER="your-email@gmail.com"
   export EMAIL_PASS="your-app-password"
   export RECEIVER_EMAIL="target@gmail.com"
   ```

   Windows (PowerShell):

   ```powershell
   $env:EMAIL_USER="your-email@gmail.com"
   $env:EMAIL_PASS="your-app-password"
   $env:RECEIVER_EMAIL="target@gmail.com"
   ```

Cloud (GitHub Actions):

1. Push the repo and set `EMAIL_USER`, `EMAIL_PASS`, `RECEIVER_EMAIL` in repository Secrets.
2. Actions will run by schedule.

## Usage

Run locally (VS Code integrated terminal or any shell):

```sh
python main.py
```

Run on GitHub Actions:

- Scheduled by [.github/workflows/bist-tracker.yml](.github/workflows/bist-tracker.yml):
  ```yml
  schedule:
    - cron: "15 6-14 * * 1-5" # 06:15–14:15 UTC ≈ 09:15–17:15 TRT, hourly on weekdays
  ```
- Manually via “Run workflow” in the Actions tab.

Outputs:

- Emails titled:
  - “🚨 BIST Average Alert” (below $avg\_threshold$)
  - “📉 BIST Max Drop Alert” (below $max\_threshold$)
  - “🎯 BIST Custom Price Alert” (custom low/high and reversals)
- Updated flags in [stock_states.json](stock_states.json) for each ticker:
  - `avg_below`, `max_below`, `custom_low_below`, `custom_high_above`

State transitions:

- Crossing above `high` flips `custom_high_above` to true; falling back below sets it to false and emits “🔻 CUSTOM PULLBACK”.
- Crossing below `low` sets `custom_low_below` to true; rising back above sets it to false and emits “🚀 CUSTOM RECOVERY”.

## Troubleshooting

- “Email credentials not set. Skipping email.” — Ensure all three env vars are present.
- Empty history — Validate ticker and market hours; Yahoo Finance may rate-limit or delay.
- No state updates — Confirm write permissions locally; on Actions, see commits updating [stock_states.json](stock_states.json).
