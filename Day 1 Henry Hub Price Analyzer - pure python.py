# Henry Hub natural gas spot prices, $/MMBtu, last 6 trading days.
henry_hub_prices = [2.85, 2.91, 2.78, 2.95, 3.02, 2.88]

print("Henry hub price analysis")
print("-----------------")
print(f"Number of days: {len(henry_hub_prices)}")
print(f"most recent price: ${henry_hub_prices[-1]}")

total = sum(henry_hub_prices)
average_price = total / len(henry_hub_prices)
highest_price = max(henry_hub_prices)
lowest_price = min(henry_hub_prices)

print(f"Average price: ${average_price:.2f}")
print(f"Highest price: ${highest_price}")
print(f"Lowest price: ${lowest_price}")

first_price = henry_hub_prices[0]
last_price = henry_hub_prices[-1]
change = last_price - first_price
percent_change = (change / first_price) * 100

print(f"Change over period: ${change:.2f} ({percent_change:.2f}%)")

price_range = highest_price - lowest_price

daily_changes = []
for i in range(1, len(henry_hub_prices)):
    daily_change = henry_hub_prices[i] - henry_hub_prices[i-1]
    daily_changes.append(daily_change)

print(f"Price range (high-low): ${price_range:.2f}")
daily_changes_rounded = [round(change, 2) for change in daily_changes]
print(f"Daily changes: {daily_changes_rounded}")

print("\n--- Market Summary ---")
up_days = len([change for change in daily_changes if change > 0])
down_days = len([change for change in daily_changes if change < 0])
print(f"up days: {up_days} | down days: {down_days}")

if change > 0:
    market_tone = "bullish"
elif change < 0:
    market_tone = "bearish"
else:
    market_tone = "flat"

print(f"Market tone: {market_tone}")
print(f"Henry Hub moved {percent_change:.2f}% over the period, ranging ${lowest_price} to ${highest_price}")
