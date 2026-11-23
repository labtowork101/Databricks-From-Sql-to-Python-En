# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 5 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**. Exercises 2, 4, and 5 have a `%sql` check on `samples.wanderbricks`; exercise 7 on `workspace.python_book.b_bookings` (created by `L00_Prepare_Data`).
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L05_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L05_Exercises_done`). Run the setup cell first, then one cell at a time (exercise 8 contains intentional errors).
# MAGIC Each exercise has a **check** cell that prints the expected result, to compare with your own output. Test every function with the calls indicated; after every change to a function, run the `def` cell again.
# MAGIC
# MAGIC | property_id | title | base_price | 2024 Bookings | Canceled | 2024 Revenue |
# MAGIC |---|---|---|---|---|---|
# MAGIC | 11670 | Historic Inn in Rome | 284.97 | 6 | 0 | 3966.21 |
# MAGIC | 16317 | Bungalow in Sardinia | 213.91 | 7 | 1 | 5139.59 |
# MAGIC | 16225 | Beach House in Amalfi | 236.95 | 4 | 2 | 2896.92 |

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
# MAGIC 1. Define the function `print_property_card(title, destination, base_price)` that prints three lines: the title, then `  Destination: ...` and `  Base price: ...` (with two leading spaces).
# MAGIC 2. Call it for Rome (`"Historic Inn in Rome"`, `"Rome"`, 284.97) and for Amalfi (`"Beach House in Amalfi"`, `"Amalfi"`, 236.95).
# MAGIC 3. Put the result of a third call, for Sardinia (`"Bungalow in Sardinia"`, `"Sardinia"`, 213.91), into a variable `card_result` and print it. What does it contain, and why?

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Historic Inn in Rome")
print("  Destination: Rome")
print("  Base price: 284.97")
print("Beach House in Amalfi")
print("  Destination: Amalfi")
print("  Base price: 236.95")
print("Bungalow in Sardinia")
print("  Destination: Sardinia")
print("  Base price: 213.91")
print(None)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – The Cost of a Stay
# MAGIC 1. Define the function `stay_cost(price, nights)` that **returns** the cost of the stay rounded to two decimal places.
# MAGIC 2. With a list comprehension, calculate the cost of 3 nights for each price in `base_prices` and print the list.
# MAGIC 3. With an accumulator, calculate the total cost of the three stays and print it with two decimal places (`Total: ...`).
# MAGIC 4. Print the cost of 7 nights in Amalfi (`Amalfi, 7 nights: ...`).

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print([854.91, 641.73, 710.85])
print("Total: 2207.49")
print("Amalfi, 7 nights: 1658.65")

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
# MAGIC The function `show_average` (cell below) prints the average of a list, but doesn't return it.
# MAGIC 1. Rewrite it as `calculate_mean(values)`, which **returns** the average.
# MAGIC 2. Use it to calculate the average base price and print it with two decimal places (`Average base price: ...`).
# MAGIC 3. With a loop and a counter, count the base prices above the average (`Prices above the average: ...`).
# MAGIC 4. Calculate the average of the 2024 bookings (`Average bookings: ...`, two decimal places).
# MAGIC
# MAGIC Hint: try `result = show_average(base_prices)` and `print(result)` to see why `show_average` isn't enough.

# COMMAND ----------

def show_average(values):
    print(sum(values) / len(values))

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Average base price: 245.28")
print("Prices above the average: 1")
print("Average bookings: 5.67")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Price Bands with a Function
# MAGIC 1. Define `classify_price(price)` that returns `"missing data"` for `None`, `"high"` from 250 up, `"medium"` from 200 up, and `"low"` below 200, with a `return` in every branch and **without `elif`**.
# MAGIC 2. Apply it with a loop to the example list `sample_prices` (cell below), printing one line per price (`284.97: high`).
# MAGIC 3. In the same loop, use a dictionary to count how many prices fall into each band (as in exercise 7 of Chapter 4) and print the dictionary.

# COMMAND ----------

sample_prices = [284.97, 213.91, 236.95, 189.0, None, 312.5]   # the last three are example values

# Write your solution here


# COMMAND ----------

# Check: expected result
print("284.97: high")
print("213.91: medium")
print("236.95: medium")
print("189.0: low")
print("None: missing data")
print("312.5: high")
print({'high': 2, 'medium': 2, 'low': 1, 'missing data': 1})

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
# MAGIC 1. Define `cancellation_rate(cancelled, bookings)`, which returns `None` if there are zero bookings.
# MAGIC 2. Define `classify_cancellation_rate(rate, threshold=CANCELLATION_RATE_THRESHOLD)` with the chapter's four states (`"missing data"`, `"impossible value"`, `"critical"`, `"ok"`).
# MAGIC 3. For each row of `guide_properties`, print the rate with one decimal place and the status with the default threshold and with a threshold of 10, passed **by keyword** (`Historic Inn in Rome: 0.0% - threshold 30: ok - threshold 10: ok`).
# MAGIC 4. Count the critical properties in the two cases.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Historic Inn in Rome: 0.0% - threshold 30: ok - threshold 10: ok")
print("Bungalow in Sardinia: 14.3% - threshold 30: ok - threshold 10: critical")
print("Beach House in Amalfi: 50.0% - threshold 30: critical - threshold 10: critical")
print("Critical with threshold 30: 1 - with threshold 10: 2")

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
# MAGIC Define `years_to_reach(price, target, growth_rate=0.05)` that returns the number of years after which the price, with a constant annual growth, **exceeds** the target:
# MAGIC - if the price already exceeds the target, it returns 0;
# MAGIC - use a `for` loop over `range(1, 51)` with a `return` inside the loop, in the branch where the target is exceeded;
# MAGIC - if the target isn't exceeded within 50 years, it returns `None`.
# MAGIC
# MAGIC Test it with: Amalfi 236.95 toward 300 (default); Sardinia 213.91 toward 284.97 at 8% and at 3% (`growth_rate` by keyword); Rome 284.97 toward 250; Amalfi toward 300 with growth 0.0.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Amalfi, 300 at 5%: 5 years")
print("Sardinia, 284.97 at 8%: 4 years")
print("Sardinia, 284.97 at 3%: 10 years")
print("Rome, 250: 0 years")
print("Amalfi, 300 at 0%: None")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – A Summary of the Amounts
# MAGIC 1. Define `is_valid_amount(amount)`, which returns `True` if the amount is present and not negative, and `False` otherwise.
# MAGIC 2. Define `summarize_amounts(amounts)`, which with a single loop counts missing, negative, and valid amounts (using `is_valid_amount`), adds up the valid ones, and returns a dictionary with the keys `missing`, `negative`, `valid`, `total`, `average` (average of the valid amounts, `None` if there are none).
# MAGIC 3. Apply it to `amounts_sample` (cell below) and to a second list with only invalid values, `[None, -10.0]`; print the results as in the check.
# MAGIC
# MAGIC Write a docstring for both functions.

# COMMAND ----------

amounts_sample = [512.4, -80.0, None, 1250.75, 333.3, None, -15.5, 968.1]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Missing: 2 - negative: 2 - valid: 4")
print("Valid total: 3064.55 - average: 766.14")
print("Second sample: valid 0 - total 0 - average None")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: nulls and negatives of the whole b_bookings teaching copy (30 and 13)
# MAGIC SELECT COUNT(*) - COUNT(total_amount)                    AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one at a time, note the name of the error (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `1658.65` in the first three (testing the function with 236.95 and 7 nights); `12002.72` in the fourth and fifth; `724.23` in the sixth.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
def stay_cost(price, nights)
    return round(price * nights, 2)

# COMMAND ----------

# Fix 8a (error name: ...; test the function with 236.95 and 7 nights)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
def stay_cost(price, nights):
    return round(price * nights, 2)

print(stay_cost(236.95))

# COMMAND ----------

# Fix 8b (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
def stay_cost(price=236.95, nights):
    return round(price * nights, 2)

# COMMAND ----------

# Fix 8c (error name: ...; keep 236.95 as the default price)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
def total_revenue(revenues):
    revenue_sum = 0
    for revenue in revenues:
        revenue_sum = revenue_sum + revenue
    return revenue_sum

total_revenue([3966.21, 5139.59, 2896.92])
print(f"{revenue_sum:.2f}")

# COMMAND ----------

# Fix 8d (error name: ...)


# COMMAND ----------

# SILENT ERROR – cell 8e (total revenue of the guide properties)
def total_revenue(revenues):
    revenue_sum = 0
    for revenue in revenues:
        revenue_sum = revenue_sum + revenue
        return revenue_sum

print(f"{total_revenue([3966.21, 5139.59, 2896.92]):.2f}")

# COMMAND ----------

# Fix 8e (what's wrong: ...)


# COMMAND ----------

# SILENT ERROR – cell 8f (revenue per booking in Amalfi)
def revenue_per_booking(revenue, bookings):
    result = round(revenue / bookings, 2)

print(revenue_per_booking(2896.92, 4))

# COMMAND ----------

# Fix 8f (what's wrong: ...)

