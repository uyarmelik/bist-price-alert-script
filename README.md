# 📈 BIST Stock Tracker & Alert Bot

A lightweight Python automation tool that monitors **BIST 100** (Borsa Istanbul) stocks. It checks stock prices hourly and sends an email alert if a stock's current price drops **20% below its yearly average**.

The system runs automatically on **GitHub Actions**, requiring zero server costs or maintenance.

## 🚀 Features

- **Automated Scheduling:** Runs every hour between 09:15 - 17:15 (TRT) on weekdays.
- **Smart Analysis:** Compares real-time prices against the 52-week moving average.
- **Email Notifications:** Sends an instant alert via Gmail when an opportunity is detected.
- **Cloud Native:** Hosted 100% free on GitHub Actions.

## 🛠️ Installation & Setup

You don't need to install anything on your local machine to run this bot. It runs in the cloud. However, you need to configure your own repository.

### 1. Fork or Clone
Clone this repository to your own GitHub account.

### 2. Get a Google App Password
To send emails securely, you need a Google App Password (not your regular password).
1. Go to **Google Account** > **Security**.
2. Enable **2-Step Verification**.
3. Search for **"App Passwords"** and create a new one named "StockBot".
4. Copy the 16-character password.

### 3. Set GitHub Secrets
Go to your repository **Settings** > **Secrets and variables** > **Actions** and add the following secrets:

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `EMAIL_USER` | `your-email@gmail.com` | The sender's email address. |
| `EMAIL_PASS` | `abcd efgh ijkl mnop` | The 16-digit App Password from Google. |
| `RECEIVER_EMAIL` | `target@gmail.com` | The email address to receive alerts. |

## 📂 Project Structure

- `main.py`: The core script that fetches data using `yfinance` and handles email logic.
- `.github/workflows/bist-tracker.yml`: The scheduler configuration (Cron job).
- `requirements.txt`: List of Python dependencies.

## ⚠️ Disclaimer
This tool is for **informational purposes only** and does not constitute financial advice. Stock market data is fetched via `yfinance` and may have delays.

---
*Built with Python 🐍 and GitHub Actions ⚙️*# bist-price-alert-script