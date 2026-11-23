# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 5 – Exercise Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in Chapter 5 (the same as in Appendix A).
# MAGIC Prerequisites: notebook attached to **Serverless**; exercise 7 has a check on `workspace.python_book.b_bookings` (created by `L00_Prepare_Data`).
# MAGIC Run the setup cell first, then one cell at a time.

# COMMAND ----------

# Setup cell: constants and collections used in the exercises
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]
bookings_2024 = [6, 7, 4]

# The guide properties as a small table (Chapter 3)
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – A Card for Each Property
# MAGIC The function prints and has no `return`: the result of the call is `None`.

# COMMAND ----------

def print_property_card(title, destination, base_price):
    print(title)
    print(f"  Destination: {destination}")
    print(f"  Base price: {base_price}")

print_property_card("Historic Inn in Rome", "Rome", 284.97)
print_property_card("Beach House in Amalfi", "Amalfi", 236.95)

# The call prints the card; the returned value is None, because the function has no return
card_result = print_property_card("Bungalow in Sardinia", "Sardinia", 213.91)
print(card_result)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – The Cost of a Stay
# MAGIC The function returns the cost: it can be used in a list comprehension and in a calculation.

# COMMAND ----------

def stay_cost(price, nights):
    return round(price * nights, 2)

# Cost of 3 nights for each base price
three_night_costs = [stay_cost(price, 3) for price in base_prices]
print(three_night_costs)

# Total of the three stays: an accumulator, displayed with two decimal places
total_cost = 0
for cost in three_night_costs:
    total_cost = total_cost + cost
print(f"Total: {total_cost:.2f}")

print(f"Amalfi, 7 nights: {stay_cost(236.95, 7)}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: cost of 3 nights for the guide properties (854.91, 710.85, 641.73)
# MAGIC SELECT property_id, base_price, ROUND(base_price * 3, 2) AS three_night_cost
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – From print to return
# MAGIC `show_average` prints and returns `None`; `calculate_mean` returns the average, which can be used in comparisons.

# COMMAND ----------

def show_average(values):
    print(sum(values) / len(values))

def calculate_mean(values):
    return sum(values) / len(values)

mean_price = calculate_mean(base_prices)
print(f"Average base price: {mean_price:.2f}")

# Counter with a condition: the returned value is compared with each price
above_mean_count = 0
for price in base_prices:
    if price > mean_price:
        above_mean_count = above_mean_count + 1
print(f"Prices above the average: {above_mean_count}")

print(f"Average bookings: {calculate_mean(bookings_2024):.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Price Bands with a Function
# MAGIC A `return` in every branch, with the check on `None` first; the count per band uses a dictionary as in exercise 7 of Chapter 4.

# COMMAND ----------

def classify_price(price):
    if price is None:
        return "missing data"
    if price >= 250:
        return "high"
    if price >= 200:
        return "medium"
    return "low"

sample_prices = [284.97, 213.91, 236.95, 189.0, None, 312.5]

band_counts = {}
for price in sample_prices:
    band = classify_price(price)
    print(f"{price}: {band}")
    if band in band_counts:
        band_counts[band] = band_counts[band] + 1
    else:
        band_counts[band] = 1
print(band_counts)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: price bands of the guide properties (high, medium, medium)
# MAGIC SELECT property_id, base_price,
# MAGIC        CASE WHEN base_price >= 250 THEN 'high'
# MAGIC             WHEN base_price >= 200 THEN 'medium'
# MAGIC             ELSE 'low'
# MAGIC        END AS price_band
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Different Threshold
# MAGIC The threshold is a parameter with a default: without an argument the book's threshold applies, and by keyword you choose another value.

# COMMAND ----------

def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

def classify_cancellation_rate(rate, threshold=CANCELLATION_RATE_THRESHOLD):
    if rate is None:
        return "missing data"
    if rate < 0 or rate > 100:
        return "impossible value"
    if rate > threshold:
        return "critical"
    return "ok"

critical_default = 0
critical_low = 0
for row in guide_properties:
    rate = cancellation_rate(row["cancelled_2024"], row["bookings_2024"])
    status_default = classify_cancellation_rate(rate)
    status_low = classify_cancellation_rate(rate, threshold=10.0)
    print(f"{row['title']}: {rate:.1f}% - threshold 30: {status_default} - threshold 10: {status_low}")
    if status_default == "critical":
        critical_default = critical_default + 1
    if status_low == "critical":
        critical_low = critical_low + 1
print(f"Critical with threshold 30: {critical_default} - with threshold 10: {critical_low}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: statuses with threshold 30 and threshold 10 (11670 ok/ok; 16225 critical/critical; 16317 ok/critical)
# MAGIC SELECT property_id,
# MAGIC        ROUND(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS cancellation_rate,
# MAGIC        CASE WHEN SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 30
# MAGIC             THEN 'critical' ELSE 'ok' END AS status_30,
# MAGIC        CASE WHEN SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 10
# MAGIC             THEN 'critical' ELSE 'ok' END AS status_10
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – How Many Years Does It Take?
# MAGIC Here the `return` inside the loop is intentional: it's in the `if` branch and ends the function in the first year in which the target is exceeded. The final `return None` is reached only if the loop ends without exceeding it.

# COMMAND ----------

def years_to_reach(price, target, growth_rate=0.05):
    if price > target:
        return 0
    projected_price = price
    for year in range(1, 51):
        projected_price = projected_price * (1 + growth_rate)
        if projected_price > target:
            return year
    return None

print(f"Amalfi, 300 at 5%: {years_to_reach(236.95, 300)} years")
print(f"Sardinia, 284.97 at 8%: {years_to_reach(213.91, 284.97, growth_rate=0.08)} years")
print(f"Sardinia, 284.97 at 3%: {years_to_reach(213.91, 284.97, growth_rate=0.03)} years")
print(f"Rome, 250: {years_to_reach(284.97, 250)} years")
print(f"Amalfi, 300 at 0%: {years_to_reach(236.95, 300, growth_rate=0.0)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – A Summary of the Amounts
# MAGIC Two functions: `is_valid_amount` decides whether an amount is valid, and `summarize_amounts` uses it in the loop and returns a dictionary.

# COMMAND ----------

def is_valid_amount(amount):
    """Returns True if the amount is present and not negative."""
    return amount is not None and amount >= 0

def summarize_amounts(amounts):
    """Counts missing, negative, and valid amounts; sum and average of the valid amounts only.

    Returns a dictionary; the average is None if there are no valid amounts.
    """
    missing = 0
    negative = 0
    valid = 0
    total = 0
    for amount in amounts:
        if amount is None:
            missing = missing + 1
        elif not is_valid_amount(amount):
            negative = negative + 1
        else:
            valid = valid + 1
            total = total + amount
    if valid == 0:
        average = None
    else:
        average = total / valid
    return {"missing": missing, "negative": negative, "valid": valid, "total": total, "average": average}

amounts_sample = [512.4, -80.0, None, 1250.75, 333.3, None, -15.5, 968.1]
summary = summarize_amounts(amounts_sample)
print(f"Missing: {summary['missing']} - negative: {summary['negative']} - valid: {summary['valid']}")
print(f"Valid total: {summary['total']:.2f} - average: {summary['average']:.2f}")

second_summary = summarize_amounts([None, -10.0])
print(f"Second sample: valid {second_summary['valid']} - total {second_summary['total']} - average {second_summary['average']}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: nulls and negatives of the whole b_bookings teaching copy (30 and 13)
# MAGIC SELECT COUNT(*) - COUNT(total_amount)                    AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC For each cell: the name of the error (or the wrong result) and the corrected version.

# COMMAND ----------

# Fix 8a – SyntaxError: expected ':' (the colon after the definition line is missing)
def stay_cost(price, nights):
    return round(price * nights, 2)

print(stay_cost(236.95, 7))

# COMMAND ----------

# Fix 8b – TypeError: stay_cost() missing 1 required positional argument: 'nights'
def stay_cost(price, nights):
    return round(price * nights, 2)

print(stay_cost(236.95, 7))

# COMMAND ----------

# Fix 8c – SyntaxError: parameter without a default follows parameter with a default
# The parameter with a default goes after the one without a default
def stay_cost(nights, price=236.95):
    return round(price * nights, 2)

print(stay_cost(7))

# COMMAND ----------

# Fix 8d – NameError: name 'revenue_sum' is not defined
# revenue_sum is a local variable: the result is obtained from the returned value
def total_revenue(revenues):
    revenue_sum = 0
    for revenue in revenues:
        revenue_sum = revenue_sum + revenue
    return revenue_sum

revenue_2024 = total_revenue([3966.21, 5139.59, 2896.92])
print(f"{revenue_2024:.2f}")

# COMMAND ----------

# Fix 8e – silent error: the return was inside the loop (3966.21 instead of 12002.72)
def total_revenue(revenues):
    revenue_sum = 0
    for revenue in revenues:
        revenue_sum = revenue_sum + revenue
    return revenue_sum

print(f"{total_revenue([3966.21, 5139.59, 2896.92]):.2f}")

# COMMAND ----------

# Fix 8f – silent error: the return was missing (None instead of 724.23)
def revenue_per_booking(revenue, bookings):
    result = round(revenue / bookings, 2)
    return result

print(revenue_per_booking(2896.92, 4))
