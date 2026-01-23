import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import sys

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

STATE_FILE = "stock_states.json"
CONFIG_FILE = "config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"ERROR: {CONFIG_FILE} not found! Please create the file.")
        return {"tickers": [], "target_prices": {}}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: An error occurred while reading the config file: {e}")
        return {"tickers": [], "target_prices": {}}


config_data = load_config()
tickers = config_data.get("tickers", [])
TARGET_PRICES = config_data.get("target_prices", {})


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_state(states):
    with open(STATE_FILE, "w") as f:
        json.dump(states, f)


def send_email(subject, alert_message):
    if not EMAIL_USER or not EMAIL_PASS or not RECEIVER_EMAIL:
        print("Email credentials not set. Skipping email.")
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(alert_message, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")


def check_stocks():
    if not tickers:
        print("Stock watchlist is empty. Verify the config.json file.")
        return

    avg_alerts = []
    max_alerts = []
    custom_alerts = []

    current_states = load_state()
    new_states = {}

    print(f"Checking {len(tickers)} stocks from config...")

    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")

            if hist.empty:
                continue

            current_price = hist["Close"].iloc[-1]
            yearly_avg = hist["Close"].mean()
            yearly_max = hist["Close"].max()

            avg_threshold = yearly_avg * 0.80
            max_threshold = yearly_max * 0.70

            prev_state = current_states.get(symbol, {})
            if isinstance(prev_state, bool):
                prev_state = {"avg_below": prev_state, "max_below": False}

            was_below_avg = prev_state.get("avg_below", False)
            was_below_max = prev_state.get("max_below", False)

            is_below_avg = bool(current_price < avg_threshold)
            is_below_max = bool(current_price < max_threshold)

            new_states[symbol] = {
                "avg_below": is_below_avg,
                "max_below": is_below_max,
                "custom_low_below": prev_state.get("custom_low_below", False),
                "custom_high_above": prev_state.get("custom_high_above", False),
            }

            if is_below_avg and not was_below_avg:
                diff = ((yearly_avg - current_price) / yearly_avg) * 100
                avg_alerts.append(
                    f"🔻 DROP (AVG): {symbol} is {diff:.2f}% below yearly avg. Price: {current_price:.2f}"
                )

            elif not is_below_avg and was_below_avg:
                avg_alerts.append(
                    f"🚀 RECOVERY (AVG): {symbol} recovered above yearly avg threshold. Price: {current_price:.2f}"
                )

            if is_below_max and not was_below_max:
                diff = ((yearly_max - current_price) / yearly_max) * 100
                max_alerts.append(
                    f"🔻 DROP (MAX): {symbol} is {diff:.2f}% below yearly max. Price: {current_price:.2f}"
                )

            elif not is_below_max and was_below_max:
                max_alerts.append(
                    f"🚀 RECOVERY (MAX): {symbol} recovered above yearly max threshold. Price: {current_price:.2f}"
                )

            if symbol in TARGET_PRICES:
                targets = TARGET_PRICES[symbol]
                low_limit = targets.get("low")
                high_limit = targets.get("high")

                was_below_custom_low = prev_state.get("custom_low_below", False)
                was_above_custom_high = prev_state.get("custom_high_above", False)

                if low_limit:
                    is_below_custom_low = bool(current_price < low_limit)
                    new_states[symbol]["custom_low_below"] = is_below_custom_low

                    if is_below_custom_low and not was_below_custom_low:
                        custom_alerts.append(
                            f"🔻 CUSTOM LOW ALERT: {symbol} dropped below {low_limit} TL. Current: {current_price:.2f}"
                        )
                    elif not is_below_custom_low and was_below_custom_low:
                        custom_alerts.append(
                            f"🚀 CUSTOM RECOVERY: {symbol} rose back above {low_limit} TL. Current: {current_price:.2f}"
                        )

                if high_limit:
                    is_above_custom_high = bool(current_price > high_limit)
                    new_states[symbol]["custom_high_above"] = is_above_custom_high

                    if is_above_custom_high and not was_above_custom_high:
                        custom_alerts.append(
                            f"🚀 CUSTOM HIGH ALERT: {symbol} rose above {high_limit} TL. Current: {current_price:.2f}"
                        )
                    elif not is_above_custom_high and was_above_custom_high:
                        custom_alerts.append(
                            f"🔻 CUSTOM PULLBACK: {symbol} dropped back below {high_limit} TL. Current: {current_price:.2f}"
                        )

        except Exception as e:
            print(f"Error checking {symbol}: {e}")
            continue

    if avg_alerts:
        send_email("🚨 BIST Average Alert", "\n".join(avg_alerts))
    if max_alerts:
        send_email("📉 BIST Max Drop Alert", "\n".join(max_alerts))
    if custom_alerts:
        send_email("🎯 BIST Custom Price Alert", "\n\n".join(custom_alerts))

    save_state(new_states)


if __name__ == "__main__":
    check_stocks()
