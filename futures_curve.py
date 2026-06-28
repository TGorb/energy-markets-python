import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

url = "https://api.eia.gov/v2/natural-gas/pri/fut/data/"

CONTRACTS = {
    "RNGC1": "Prompt Month (M1)",
    "RNGC2": "2nd Month (M2)",
    "RNGC3": "3rd Month (M3)",
    "RNGC4": "4th Month (M4)",
}
# scraping last 30 days of all 4 futures contracts
params = [
    ("api_key", API_KEY),
    ("frequency", "daily"),
    ("data[0]", "value"),
    ("facets[series][]", "RNGC1"),
    ("facets[series][]", "RNGC2"),
    ("facets[series][]", "RNGC3"),
    ("facets[series][]", "RNGC4"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "desc"),
    ("length", 120),
]

response = requests.get(url, params=params)
raw = response.json()["response"]["data"]

# building DataFrame
df = pd.DataFrame(raw)
df["period"] = pd.to_datetime(df["period"])
df["value"] = df["value"].astype(float)
df["label"] = df["series"].map(CONTRACTS)

df_pivot = df.pivot_table(
    index="period",
    columns="label",
    values="value"
).sort_index()

print(df_pivot.tail(10))

# Latest curve snapshot
latest_date = df_pivot.index[-1]
latest = df_pivot.iloc[-1]

m1 = latest["Prompt Month (M1)"]
m2 = latest["2nd Month (M2)"]
m3 = latest["3rd Month (M3)"]
m4 = latest["4th Month (M4)"]

prompt_spread = m2 - m1
m1_m4_spread = m4 - m1

if prompt_spread > 0.10:
    structure = "CONTANGO"
    tone = "bearish near-term — deferred months pricing higher"
elif prompt_spread < -0.10:
    structure = "BACKWARDATION"
    tone = "bullish near-term — prompt month pricing at premium"
else:
    structure = "FLAT"
    tone = "neutral — curve relatively flat"

print("\n" + "=" * 55)
print(f"  NAT GAS FUTURES CURVE — {latest_date.strftime('%Y-%m-%d')}")
print("=" * 55)
print(f"  M1 Prompt:   ${m1:.3f}/MMBtu")
print(f"  M2:          ${m2:.3f}/MMBtu")
print(f"  M3:          ${m3:.3f}/MMBtu")
print(f"  M4:          ${m4:.3f}/MMBtu")
print("-" * 55)
print(f"  Prompt spread (M2-M1):  {prompt_spread:+.3f}")
print(f"  M1-M4 spread:           {m1_m4_spread:+.3f}")
print("-" * 55)
print(f"  Curve structure: {structure}")
print(f"  Signal: {tone}")
print("=" * 55)

# Drawing the Curve
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Top chart: futures curve shape on latest date
contracts = ["Prompt Month (M1)", "2nd Month (M2)", 
             "3rd Month (M3)", "4th Month (M4)"]
prices = [m1, m2, m3, m4]
months = ["M1", "M2", "M3", "M4"]

ax1.plot(months, prices, color="steelblue", linewidth=2.5, 
         marker="o", markersize=8)
ax1.set_title(f"Nat Gas Futures Curve — {latest_date.strftime('%Y-%m-%d')}", 
              fontsize=14, fontweight="bold")
ax1.set_ylabel("$/MMBtu")
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.2f}"))
ax1.grid(True, alpha=0.3)

for i, (month, price) in enumerate(zip(months, prices)):
    ax1.annotate(f"${price:.3f}", (month, price), 
                textcoords="offset points", xytext=(0, 10), 
                ha="center", fontsize=10)

# Bottom chart: prompt spread over time
df_pivot["prompt_spread"] = df_pivot["2nd Month (M2)"] - \
                             df_pivot["Prompt Month (M1)"]

ax2.plot(df_pivot.index, df_pivot["prompt_spread"], 
         color="coral", linewidth=1.5)
ax2.axhline(y=0, color="black", linewidth=0.8, linestyle="--")
ax2.fill_between(df_pivot.index, df_pivot["prompt_spread"], 0,
                 where=df_pivot["prompt_spread"] > 0,
                 alpha=0.2, color="red", label="Contango")
ax2.fill_between(df_pivot.index, df_pivot["prompt_spread"], 0,
                 where=df_pivot["prompt_spread"] < 0,
                 alpha=0.2, color="green", label="Backwardation")
ax2.set_title("Prompt Spread (M2 - M1) Over Time", 
              fontsize=14, fontweight="bold")
ax2.set_ylabel("$/MMBtu")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:+.2f}"))
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig("futures_curve.png", dpi=150, bbox_inches="tight")
plt.show()
print("Chart saved as futures_curve.png")