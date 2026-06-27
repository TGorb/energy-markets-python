import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

url = "https://api.eia.gov/v2/natural-gas/stor/wkly/data/"

# Current: last 8 weekly storage reports
params_current = [
    ("api_key", API_KEY),
    ("frequency", "weekly"),
    ("data[0]", "value"),
    ("facets[series][]", "NW2_EPG0_SWO_R48_BCF"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "desc"),
    ("length", 9),
]
# Historical: 5 years seasonal average
params_hist = [
    ("api_key", API_KEY),
    ("frequency", "weekly"),
    ("data[0]", "value"),
    ("facets[series][]", "NW2_EPG0_SWO_R48_BCF"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "desc"),
    ("start", "2020-01-01"),
    ("end", "2024-12-31"),
    ("length", 300),
]

response_current = requests.get(url, params=params_current)
response_hist = requests.get(url, params=params_hist)

raw_current = response_current.json()["response"]["data"]
print(response_current.status_code)
print(raw_current[:2])
raw_hist = response_hist.json()["response"]["data"]

# building dataframes
df = pd.DataFrame(raw_current)
df["period"] = pd.to_datetime(df["period"])
df["value"] = df["value"].astype(int)
df = df.sort_values("period").reset_index(drop=True)

df_hist = pd.DataFrame(raw_hist)
df_hist["period"] = pd.to_datetime(df_hist["period"])
df_hist["value"] = df_hist["value"].astype(int)

# Seasonal average by/ week number
df_hist["week"] = df_hist["period"].dt.isocalendar().week
df["week"] = df["period"].dt.isocalendar().week
seasonal_avg = df_hist.groupby("week")["value"].mean()
df["seasonal_avg"] = df["week"].map(seasonal_avg)

#calculating w-o-w change + surplus/deficit
df["wow_change"] = df["value"].diff()
df["vs_seasonal"] = df["value"] - df["seasonal_avg"]

#determing market sentinment/ market tone
def get_tone(vs_seasonal, wow_change):
    if wow_change > 0 and vs_seasonal > 50:
        return "BEARISH"
    elif wow_change < 0 and vs_seasonal < -50:
        return "BULLISH"
    elif vs_seasonal > 25:
        return "Slightly Bearish"
    elif vs_seasonal < -25:
        return "Slightly Bullish"
    else:
        return "Neutral"

df["tone"] = df.apply(
    lambda row: get_tone(row["vs_seasonal"], row["wow_change"]), axis=1
) 

# Printing the report
print("=" * 60)
print("  NAT GAS STORAGE REPORT ANALYZER — LAST 8 WEEKS")
print("=" * 60)

df_report = df.dropna(subset=["wow_change"]).tail(8)

for _, row in df_report.iterrows():
    period = row["period"].strftime("%Y-%m-%d")
    value = int(row["value"])
    wow = int(row["wow_change"])
    vs_avg = int(row["vs_seasonal"])
    tone = row["tone"]

    print(f"\nWeek of {period}")
    print(f"  Storage:        {value:>6,} Bcf")
    print(f"  Week-on-week:   {wow:>+6,} Bcf")
    print(f"  vs 5-yr avg:    {vs_avg:>+6,} Bcf  →  {tone}")

print("\n" + "=" * 60)

latest = df_report.iloc[-1]
print(f"\nLATEST REPORT: Week of {latest['period'].strftime('%Y-%m-%d')}")
print(f"Storage at {int(latest['value']):,} Bcf — {int(latest['vs_seasonal']):+,} Bcf vs seasonal average")
print(f"Market tone: {latest['tone']}")
print("=" * 60)