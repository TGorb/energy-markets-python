import requests
import pandas as pd
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

CSV_FILE = "henry_hub_prices.csv"

# --- Fetch latest Henry Hub spot price ---

params = [
    ("api_key", API_KEY),
    ("frequency", "daily"),
    ("data[0]", "value"),
    ("facets[series][]", "RNGWHHD"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "desc"),
    ("length", 7),
]

url = "https://api.eia.gov/v2/natural-gas/pri/fut/data/"
response = requests.get(url, params=params)
data = response.json()["response"]["data"]

latest = data[0]
latest_date = latest["period"]
latest_price = float(latest["value"])

print(f"Latest Henry Hub: ${latest_price:.2f} on {latest_date}")


# --- Load or create CSV ---
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
else:
    df = pd.DataFrame(columns=["date", "price"])
    print(f"Created new file: {CSV_FILE}")

# --- Append today's entry if not already recorded ---
today = pd.Timestamp(date.today())
already_recorded = (df["date"] == pd.Timestamp(today)).any()

if already_recorded:
    print(f"Price for {today} already recorded — skipping.")
else:
    new_row = pd.DataFrame([{"date": today, "price": latest_price}])
    df = pd.concat([df, new_row], ignore_index=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(CSV_FILE, index=False)
    print(f"Saved: ${latest_price:.2f} on {today}")



    # --- Print summary ---
df_sorted = df.sort_values("date")

latest_saved = df_sorted.iloc[-1]["price"]
oldest_saved = df_sorted.iloc[0]["price"]
total_change = latest_saved - oldest_saved
pct_change = (total_change / oldest_saved) * 100

print(f"\n--- HENRY HUB PRICE TRACKER ---")
print(f"Days tracked:     {len(df_sorted)}")
print(f"First entry:      ${oldest_saved:.2f} on {df_sorted.iloc[0]['date'].strftime('%Y-%m-%d')}")
print(f"Latest entry:     ${latest_saved:.2f} on {df_sorted.iloc[-1]['date'].strftime('%Y-%m-%d')}")
print(f"Total change:     ${total_change:+.2f} ({pct_change:+.2f}%)")

if len(df_sorted) >= 2:
    prev_price = df_sorted.iloc[-2]["price"]
    daily_move = latest_saved - prev_price
    print(f"vs previous day:  ${daily_move:+.2f}")