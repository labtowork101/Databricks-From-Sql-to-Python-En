# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 6 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**. Exercise 5 has a `%sql` check on `samples.wanderbricks.bookings`; exercise 6 a `%sql` check with `try_cast`.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L06_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L06_Exercises_done`). Run the setup cell first, then **one cell at a time**: almost all the exercises contain cells that must fail (**INTENTIONAL ERROR**) or that produce a wrong result (**SILENT ERROR**). Don't use Run all.
# MAGIC Each exercise has a **check** cell that prints the expected result, to compare with your own output. For each error, note the **type**, the **message**, and the **line** (`---->` arrow) before fixing it.

# COMMAND ----------

# Setup cell: constants and collections used in the exercises
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]
bookings_2024 = [6, 7, 4]
ratings_with_gap = [3.2, None, 3.0]   # Sardinia rating not available (example)

# The guide properties as a small table (Chapter 3)
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]

# The example amounts from Chapter 4, arriving as text
raw_amounts = ["879.15", "n/a", "412.5", "-42.76", "", "655.0"]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – Reading Three Messages
# MAGIC 1. Run the three cells 1a, 1b, 1c. For each one, note in the answer cell the **type** of the error and the **number of the line** indicated by the arrow.
# MAGIC 2. In the fix cell, write the corrected version of the three cells: 1a prints the total bookings for Rome and Sardinia, 1b the line `Beach House in Amalfi: 4 bookings`, 1c the revenue as a number (the comma in the text is fixed by writing the text with a decimal point).

# COMMAND ----------

# INTENTIONAL ERROR – cell 1a
rome_bookings = 6
sardinia_bookings = 7
total_bookings = rome_bookings + sardinia_booking
print(total_bookings)

# COMMAND ----------

# INTENTIONAL ERROR – cell 1b
amalfi_title = "Beach House in Amalfi"
amalfi_bookings = 4
print(amalfi_title + ": " + amalfi_bookings + " bookings")

# COMMAND ----------

# INTENTIONAL ERROR – cell 1c
raw_revenue = "2896,92"
amalfi_revenue = float(raw_revenue)
print(amalfi_revenue)

# COMMAND ----------

# Answers (error type and line indicated by the arrow)
# 1a: type ..., line ...
# 1b: type ..., line ...
# 1c: type ..., line ...

# Write your three fixes here


# COMMAND ----------

# Check: expected result
print("1a: NameError, line 4 - 1b: TypeError, line 4 - 1c: ValueError, line 3")
print(13)
print("Beach House in Amalfi: 4 bookings")
print(2896.92)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Syntax or Runtime?
# MAGIC The two cells below start with the same `print`. **Before running them**, write in the answer cell whether the line `Price check` will appear in the output, and why. Then run them and fix them: 2a must print the three prices, 2b the three prices and then the last price in the list.

# COMMAND ----------

# INTENTIONAL ERROR – cell 2a
print("Price check")
for price in base_prices
    print(price)

# COMMAND ----------

# INTENTIONAL ERROR – cell 2b
print("Price check")
for price in base_prices:
    print(price)
print(base_prices[3])

# COMMAND ----------

# Answers (is the initial print run? why?)
# 2a: ...
# 2b: ...

# Write your two fixes here


# COMMAND ----------

# Check: expected result
print("2a: no, syntax error (SyntaxError): no line is run")
print("2b: yes, runtime error (IndexError) on line 5: the previous lines are run")
print("Fix 2a: Price check, 284.97, 213.91, 236.95")
print("Fix 2b: Price check, 284.97, 213.91, 236.95, 236.95")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Collection Errors
# MAGIC Run the three cells, note the type of the error, and fix them:
# MAGIC - 3a must print Amalfi's 2024 revenue;
# MAGIC - 3b must print the title of the last property;
# MAGIC - 3c must add the example price 250.0 to the end of `extra_prices` and print the list.

# COMMAND ----------

# INTENTIONAL ERROR – cell 3a
amalfi_row = guide_properties[2]
print(amalfi_row["revenue"])

# COMMAND ----------

# INTENTIONAL ERROR – cell 3b
print(property_titles[3])

# COMMAND ----------

# INTENTIONAL ERROR – cell 3c
extra_prices = base_prices.copy()
extra_prices.add(250.0)
print(extra_prices)

# COMMAND ----------

# Answers (error type)
# 3a: ...
# 3b: ...
# 3c: ...

# Write your three fixes here


# COMMAND ----------

# Check: expected result
print("3a: KeyError - 3b: IndexError - 3c: AttributeError")
print(2896.92)
print("Beach House in Amalfi")
print([284.97, 213.91, 236.95, 250.0])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – A Two-Level Traceback
# MAGIC 1. Run cell 4 and read the traceback **from the bottom**: in which function and on which line does the error occur? From which line of the other function was it called? Which row of `report_rows` causes it (look at the output printed before the message)?
# MAGIC 2. Fix it: `revenue_per_booking` returns `None` if there are zero bookings; `print_revenue_report` prints `n/a` when the value is `None`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 4
def revenue_per_booking(revenue, bookings):
    return round(revenue / bookings, 2)

def print_revenue_report(rows):
    for row in rows:
        value = revenue_per_booking(row["revenue_2024"], row["bookings_2024"])
        print(f"{row['title']}: {value:.2f}")

report_rows = guide_properties.copy()
report_rows.append({"property_id": 99999, "title": "Sample property", "bookings_2024": 0, "cancelled_2024": 0, "revenue_2024": 0.0})
print_revenue_report(report_rows)

# COMMAND ----------

# Answers
# Function and line of the error: ...
# Line of the calling function: ...
# Row of report_rows that causes it: ...

# Write your fix here


# COMMAND ----------

# Check: expected result
print("Error: ZeroDivisionError in revenue_per_booking, line 3, called from line 7 of print_revenue_report; row: Sample property")
print("Historic Inn in Rome: 661.03")
print("Bungalow in Sardinia: 734.23")
print("Beach House in Amalfi: 724.23")
print("Sample property: n/a")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Silent Error, with a Method
# MAGIC The function in cell 5 should calculate the overall cancellation rate of the three guide properties.
# MAGIC 1. **Step zero**: calculate the expected result by hand (total canceled divided by total bookings, times one hundred) and write it in the answer cell.
# MAGIC 2. Run cell 5 and compare.
# MAGIC 3. Repeat the calculation outside the function with **debug prints** of `total_cancelled`, `total_bookings`, and the denominator used.
# MAGIC 4. Fix the function and check it against the expected result and the `%sql` cell.

# COMMAND ----------

# SILENT ERROR – cell 5
def overall_cancellation_rate(rows):
    total_cancelled = 0
    total_bookings = 0
    for row in rows:
        total_cancelled = total_cancelled + row["cancelled_2024"]
        total_bookings = total_bookings + row["bookings_2024"]
    return total_cancelled / len(rows) * 100

print(f"Overall rate: {overall_cancellation_rate(guide_properties):.1f}%")

# COMMAND ----------

# Answer (step zero): ...

# Write your debug prints and the fix here


# COMMAND ----------

# Check: expected result
print("Wrong result: 100.0% (3 canceled divided by 3 rows)")
print("total_cancelled: 3 - total_bookings: 17 - len(rows): 3")
print("Overall rate: 17.6%")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: overall rate of the three guide properties in 2024 (17.6)
# MAGIC SELECT SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS total_cancelled,
# MAGIC        COUNT(*)                                             AS total_bookings,
# MAGIC        ROUND(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS overall_rate
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Nights Arriving as Text
# MAGIC The `raw_nights` list (cell below) contains the nights of six example stays, arriving as text.
# MAGIC 1. With a loop, convert each value with `int()` inside a `try` / `except ValueError as error`, collecting the valid values in a list and counting the discarded ones.
# MAGIC 2. For each discarded value, print `Discarded: ` followed by the message of the error.
# MAGIC 3. Print the list of valid values and the line `Valid: ... - discarded: ... - total nights: ... - average: ...` (average with one decimal place).

# COMMAND ----------

raw_nights = ["3", "7", "n/a", "2", "", "4"]   # example values

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Discarded: invalid literal for int() with base 10: 'n/a'")
print("Discarded: invalid literal for int() with base 10: ''")
print([3, 7, 2, 4])
print("Valid: 4 - discarded: 2 - total nights: 16 - average: 4.0")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same calculation with try_cast (16, 4, 2, 4.0)
# MAGIC SELECT SUM(try_cast(raw_nights AS INT))            AS total_nights,
# MAGIC        COUNT(try_cast(raw_nights AS INT))          AS valid_count,
# MAGIC        COUNT(*) - COUNT(try_cast(raw_nights AS INT)) AS rejected_count,
# MAGIC        ROUND(AVG(try_cast(raw_nights AS INT)), 1)   AS average_nights
# MAGIC FROM VALUES ('3'), ('7'), ('n/a'), ('2'), (''), ('4') AS t(raw_nights)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Rows Arriving as Text
# MAGIC The `raw_booking_rows` list (cell below) contains six example bookings arriving as text; one of them is missing the `total_amount` key.
# MAGIC 1. Define `to_float(text)` as in section 6.9 and `to_int(text)`, its twin for whole numbers. Both return `None` for a piece of text that's missing or can't be converted; write a docstring for each one.
# MAGIC 2. Define `clean_booking_row(row)`, which returns a **new** dictionary with `booking_id` (integer), `nights` (integer or `None`), and `total_amount` (float or `None`). For the key that may be missing, use `get()`.
# MAGIC 3. With a loop, clean all the rows and count: missing nights, missing amounts, complete rows (nights and amount present). Add up the amounts present.
# MAGIC 4. For the complete rows only, calculate the average amount per night (sum of the amounts divided by the sum of the nights, two decimal places).

# COMMAND ----------

raw_booking_rows = [   # example values
    {"booking_id": "1001", "nights": "3", "total_amount": "854.91"},
    {"booking_id": "1002", "nights": "7", "total_amount": "n/a"},
    {"booking_id": "1003", "nights": "", "total_amount": "641.73"},
    {"booking_id": "1004", "nights": "2"},
    {"booking_id": "1005", "nights": "4", "total_amount": "947.80"},
    {"booking_id": "1006", "nights": "3,5", "total_amount": "710,85"},
]

# Write your solution here


# COMMAND ----------

# Check: expected result
print({'booking_id': 1004, 'nights': 2, 'total_amount': None})
print("Missing nights: 2 - missing amounts: 3 - complete rows: 2")
print("Total of the amounts present: 2444.44")
print("Average amount per night (complete rows): 257.53")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one by one, note the type, message, and line (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `Average price: 245.28`; `3.2`; `236.95` and `None`; `[3.2, 3.0]`; `[284.97, 213.91, None]`; `Total: 1903.89`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
average_price = sum(base_prices) / len(base_prices
print(f"Average price: {average_price:.2f}")

# COMMAND ----------

# Fix 8a (error type: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b (the highest of the ratings present)
best_rating = max(ratings_with_gap)
print(best_rating)

# COMMAND ----------

# Fix 8b (error type: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
def to_number(text):
    try:
        return float(text)
    except ValueError:
        return None

print(to_number("236.95"))
print(to_number(None))

# COMMAND ----------

# Fix 8c (error type: ...; in which function and on which line?)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8d (the ratings present in a new list)
present_ratings = []
for rating in ratings_with_gap:
    if rating is not None:
        present_ratings = present_ratings.append(rating)
print(present_ratings)

# COMMAND ----------

# Fix 8d (error type: ...; which line is wrong?)


# COMMAND ----------

# SILENT ERROR – cell 8e
def to_number(text):
    try:
        return flaot(text)
    except:
        return None

print([to_number(value) for value in ["284.97", "213.91", "n/a"]])

# COMMAND ----------

# Fix 8e (what's wrong: ...)


# COMMAND ----------

# SILENT ERROR – cell 8f (total of the valid amounts)
total = 0
try:
    for raw_amount in raw_amounts:
        total = total + float(raw_amount)
except ValueError:
    print("Invalid amount")
print(f"Total: {total:.2f}")

# COMMAND ----------

# Fix 8f (what's wrong: ...)

