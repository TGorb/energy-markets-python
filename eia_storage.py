import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

url = "https://api.eia.gov/v2/natural-gas/stor/wkly/data/"

params = [
    ("api_key", API_KEY),
    ("frequency", "weekly"),
    ("data[0]", "value"),
    ("facets[series][]", "NW2_EPG0_SWO_R48_BCF"),
    ("sort[0][column]", "period"),
    ("sort[0][direction]", "desc"),
    ("length", 5),
]



response = requests.get(url, params=params)
data = response.json()
records = data["response"]["data"]

print("EIA Natural Gas Storage — Lower 48 States")
print("=" * 45)

for record in records:
    period = record["period"]
    value = int(record["value"])
    print(f"{period}:  {value:,} Bcf")

print("=" * 45)

latest = int(records[0]["value"])
previous = int(records[1]["value"])
weekly_change = latest - previous

if weekly_change > 0:
    direction = "injection"
else:
    direction = "withdrawal"

print(f"Week-on-week change: {weekly_change:+,} Bcf ({direction})")