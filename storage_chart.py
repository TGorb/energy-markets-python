import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

url = "https://api.eia.gov/v2/natural-gas/stor/wkly/data/"

# --- Current year data ---
params = [
    ("api_key", API_KEY),
    ("frequency", "weekly"),
    ("data[0]", "value"),
    ("facets[series][]", "NW2_EPG0_SWO_R48_BCF"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "asc"),
    ("start", "2025-06-01"),
    ("length", 52),
]

response = requests.get(url, params=params)
raw = response.json()["response"]["data"]

df = pd.DataFrame(raw)
df["period"] = pd.to_datetime(df["period"])
df["value"] = df["value"].astype(int)

# --- Historical data (5-year average) ---
params_hist = [
    ("api_key", API_KEY),
    ("frequency", "weekly"),
    ("data[0]", "value"),
    ("facets[series][]", "NW2_EPG0_SWO_R48_BCF"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "asc"),
    ("start", "2020-01-01"),
    ("end", "2024-12-31"),
    ("length", 300),
]

response_hist = requests.get(url, params=params_hist)
raw_hist = response_hist.json()["response"]["data"]

df_hist = pd.DataFrame(raw_hist)
df_hist["period"] = pd.to_datetime(df_hist["period"])
df_hist["value"] = df_hist["value"].astype(int)

# --- Seasonal calculations ---
df_hist["week"] = df_hist["period"].dt.isocalendar().week
df["week"] = df["period"].dt.isocalendar().week

seasonal_avg = df_hist.groupby("week")["value"].mean()
seasonal_min = df_hist.groupby("week")["value"].min()
seasonal_max = df_hist.groupby("week")["value"].max()

df["avg"] = df["week"].map(seasonal_avg)
df["min"] = df["week"].map(seasonal_min)
df["max"] = df["week"].map(seasonal_max)

# --- Chart ---
fig, ax = plt.subplots(figsize=(12, 6))

ax.fill_between(df["period"], df["min"], df["max"],
                alpha=0.15, color="grey",
                label="5-year min/max range")

ax.plot(df["period"], df["avg"],
        color="grey", linewidth=1.5,
        linestyle="--", label="5-year average")

ax.plot(df["period"], df["value"],
        color="steelblue", linewidth=2.5,
        label="2025-2026 Storage")

ax.set_title("US Natural Gas Storage — Lower 48 States",
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Billion Cubic Feet (Bcf)", fontsize=12)

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))

ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig("storage_chart.png", dpi=150, bbox_inches="tight")
plt.show()

print("Chart saved as storage_chart.png")
