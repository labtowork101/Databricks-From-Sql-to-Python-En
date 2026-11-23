# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 2 – Operators and Conditions
# MAGIC
# MAGIC Notebook for Chapter 2 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Calculate with the arithmetic operators, including `//`, `%`, and `**`, following the rules of precedence
# MAGIC - Join and repeat text with `+` and `*`
# MAGIC - Write conditions with the comparison operators and with `and`, `or`, `not`; check for `None` with `is None`
# MAGIC - Make the code take decisions with `if`, `elif`, `else`, following the indentation rules
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0 and 1; notebook attached to **Serverless** compute
# MAGIC - `L00_Prepare_Data` run once (Chapter 0, section 0.7): the `%sql` cells read only `samples.wanderbricks`, but the book assumes the preparation has already been done
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: sections 2.2 and 2.10 contain intentional and silent errors.
# MAGIC Run the **setup cell** below first; after a session interruption, running that cell again is enough.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC Constants and values of the guide properties used in the sections of the chapter.

# COMMAND ----------

# Setup cell: constants and values of the guide properties
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# 2024 bookings, cancellations, and revenue of the three guide properties
rome_bookings = 6
rome_cancelled = 0
rome_revenue = 3966.21
sardinia_bookings = 7
sardinia_cancelled = 1
sardinia_revenue = 5139.59
amalfi_bookings = 4
amalfi_cancelled = 2
amalfi_revenue = 2896.92

# Descriptive data of the property in Amalfi
property_id = 16225
property_title = "Beach House in Amalfi"
destination = "Amalfi"
property_type = "Summer Getaway"
base_price = 236.95
average_rating = 3.0

print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.1 Arithmetic Operators
# MAGIC `+` `-` `*` `/` as in SQL. Expected results: `17`, `2242.67`, `710.8499999999999` (approximate decimals, Chapter 1), `724.23`.

# COMMAND ----------

total_bookings = rome_bookings + sardinia_bookings + amalfi_bookings
revenue_gap = sardinia_revenue - amalfi_revenue
three_nights = base_price * 3
revenue_per_booking = amalfi_revenue / amalfi_bookings
print(total_bookings)
print(revenue_gap)
print(three_nights)
print(revenue_per_booking)

# COMMAND ----------

# MAGIC %md
# MAGIC **Division with `/` always returns a `float`**, even when the result is a whole number. Expected result: `2.0` and `<class 'float'>`.

# COMMAND ----------

half_bookings = amalfi_bookings / 2
print(half_bookings, type(half_bookings))

# COMMAND ----------

# MAGIC %md
# MAGIC **Integer division `//` and remainder `%`**: how many full weeks and how many extra nights there are in a 9-night stay.

# COMMAND ----------

nights = 9
full_weeks = nights // 7
extra_nights = nights % 7
print(f"{nights} nights: full weeks {full_weeks}, extra nights {extra_nights}")

# COMMAND ----------

# MAGIC %md
# MAGIC The remainder also tells us whether one number is divisible by another: remainder 0. The year 2024 is divisible by 4 (leap year). Expected result: `0`.

# COMMAND ----------

ANALYSIS_YEAR % 4

# COMMAND ----------

# MAGIC %md
# MAGIC **Power `**`**: the base price after two yearly increases of 5%. Expected results: `1.1025`, `261.237375`, `261.24`.

# COMMAND ----------

growth_factor = 1.05 ** 2
new_price = base_price * growth_factor
print(growth_factor)
print(new_price)
print(f"{new_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `div`, `%` (or `mod`), `power`; in Databricks SQL, `7 / 2` also returns a number with decimals.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 9 div 7        AS full_weeks,
# MAGIC        9 % 7          AS extra_nights,
# MAGIC        mod(9, 7)      AS extra_nights_mod,
# MAGIC        power(1.05, 2) AS growth_factor,
# MAGIC        7 / 2          AS division

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `1`, `2`, `2`, `1.1025`, `3.5`.
# MAGIC
# MAGIC ## 2.2 Precedence and Parentheses
# MAGIC Order: `**`, then `*` `/` `//` `%`, then `+` `-`; at the same level, from left to right. Parentheses change the order.
# MAGIC
# MAGIC The next cell is a **silent error**: no message, but `577.8633333333333` isn't the average price. The fix is in the following cell (expected result `245.27666666666664`).

# COMMAND ----------

# SILENT ERROR – the parentheses around the sum are missing
average_price = 284.97 + 213.91 + 236.95 / 3
print(average_price)

# COMMAND ----------

# Fix: first the sum, then the division
average_price = (284.97 + 213.91 + 236.95) / 3
print(average_price)
print(f"{average_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC The cancellation rate is calculated from left to right: first the division, then the multiplication. The parentheses in the third line change the meaning. Expected results: `50.0`, `50.0`, `0.005`.

# COMMAND ----------

amalfi_rate = amalfi_cancelled / amalfi_bookings * 100
print(amalfi_rate)
print((amalfi_cancelled / amalfi_bookings) * 100)
print(amalfi_cancelled / (amalfi_bookings * 100))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.3 Operators with Strings
# MAGIC `+` joins two pieces of text, `*` repeats a piece of text. Expected results: `Amalfi - Summer Getaway` and a line of 30 hyphens.

# COMMAND ----------

label = destination + " - " + property_type
separator = "-" * 30
print(label)
print(separator)

# COMMAND ----------

# MAGIC %md
# MAGIC A number must be converted with `str()` before joining it to text (or you use an f-string). Two pieces of text that contain digits are joined, not added: expected results `Analysis 2024`, `305`, `35`.

# COMMAND ----------

print("Analysis " + str(ANALYSIS_YEAR))
print("30" + "5")
print(30 + 5)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `||` joins, `repeat` repeats.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'Amalfi' || ' - ' || 'Summer Getaway' AS label,
# MAGIC        repeat('-', 30)                       AS separator

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.4 Comparison Operators
# MAGIC `==` `!=` `<` `>` `<=` `>=` compare two values and return `True` or `False`. Expected results: `True`, `True`, `True`.

# COMMAND ----------

amalfi_rate = amalfi_cancelled / amalfi_bookings * 100
print(amalfi_rate > CANCELLATION_RATE_THRESHOLD)
print(amalfi_rate == 50.0)
print(amalfi_bookings != 0)

# COMMAND ----------

# MAGIC %md
# MAGIC The result of a comparison is a `bool` value and can be saved in a variable. `=` puts, `==` asks. Expected results: `True <class 'bool'>` and `False`.

# COMMAND ----------

is_critical = amalfi_rate > CANCELLATION_RATE_THRESHOLD
print(is_critical, type(is_critical))

sardinia_rate = sardinia_cancelled / sardinia_bookings * 100
print(sardinia_rate > CANCELLATION_RATE_THRESHOLD)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same comparison in SQL returns a `boolean` value.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 2 / 4 * 100 > 30 AS is_critical,
# MAGIC        1 / 7 * 100 > 30 AS is_critical_sardinia

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `true`, `false`.
# MAGIC
# MAGIC **Watch out for `float`s**: because of approximate decimals (Chapter 1), a comparison with `==` can give `False`. Compare rounded values. Expected results: `False`, `True`.

# COMMAND ----------

print(284.97 * 3 == 854.91)
print(round(284.97 * 3, 2) == 854.91)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.5 Comparing Text and Different Types
# MAGIC Text comparison distinguishes uppercase and lowercase. Expected results: `True`, `False`.

# COMMAND ----------

print(destination == "Amalfi")
print(destination == "amalfi")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: in Databricks SQL, too, text comparison distinguishes uppercase and lowercase. Expected results: `false` and `1`, `0`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'Amalfi' = 'amalfi' AS same_text

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   (SELECT COUNT(*) FROM samples.wanderbricks.destinations WHERE destination = 'Amalfi') AS with_capital,
# MAGIC   (SELECT COUNT(*) FROM samples.wanderbricks.destinations WHERE destination = 'amalfi') AS lowercase

# COMMAND ----------

# MAGIC %md
# MAGIC **Text and number**: `==` between a piece of text and a number returns `False` without errors; `<` and `>` between a piece of text and a number produce `TypeError` (section 2.10). Between two pieces of text, `<` follows alphabetical order. Expected results: `False`, `True`, `True`.

# COMMAND ----------

print(property_id == "16225")
print(property_id == int("16225"))
print("Amalfi" < "Rome")

# COMMAND ----------

# MAGIC %md
# MAGIC **Chained comparisons**: `0 <= x <= 100` is equivalent to `x BETWEEN 0 AND 100` (both ends included). Expected results: `True`, `False`.

# COMMAND ----------

print(0 <= amalfi_rate <= 100)
print(0 <= 120.0 <= 100)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 50.0 BETWEEN 0 AND 100  AS valid_rate,
# MAGIC        120.0 BETWEEN 0 AND 100 AS invalid_rate

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.6 Logical Operators
# MAGIC `and` (both true), `or` (at least one true), `not` (the opposite), like `AND`, `OR`, `NOT` in `WHERE`. Expected results: `True`, `True`, `False`.

# COMMAND ----------

is_summer = property_type == "Summer Getaway"
is_critical = amalfi_rate > CANCELLATION_RATE_THRESHOLD
print(is_summer and is_critical)
print(is_summer or is_critical)
print(not is_critical)

# COMMAND ----------

# MAGIC %md
# MAGIC With `or`, each comparison must be written in full. Expected result: `True`.

# COMMAND ----------

status = "completed"
is_active = status == "confirmed" or status == "completed"
print(is_active)

# COMMAND ----------

# MAGIC %md
# MAGIC **`and` before `or`**: without parentheses, `and` is evaluated first. Expected results: `True` (without parentheses) and `False` (with parentheses).

# COMMAND ----------

status = "confirmed"
total_amount = 450.0
print(status == "confirmed" or status == "completed" and total_amount > 1000)
print((status == "confirmed" or status == "completed") and total_amount > 1000)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the 2024 cancellations of the property in Amalfi with `AND` and `BETWEEN`. Expected result: `2`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS cancelled_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id = 16225
# MAGIC   AND status = 'cancelled'
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.7 The None Value in Conditions
# MAGIC `is None` / `is not None` like `IS NULL` / `IS NOT NULL`. Expected results: `True`, `False`.

# COMMAND ----------

missing_rating = None
print(missing_rating is None)
print(missing_rating is not None)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: in SQL, `= NULL` is never true. Expected results: `476` with `IS NULL`, `0` with `= NULL`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS null_ratings
# MAGIC FROM samples.wanderbricks.reviews
# MAGIC WHERE rating IS NULL

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS null_ratings
# MAGIC FROM samples.wanderbricks.reviews
# MAGIC WHERE rating = NULL

# COMMAND ----------

# MAGIC %md
# MAGIC **First the `None` check, then the comparison**: `and` stops as soon as the result is known, so the second comparison isn't run. Expected results: `False` and `True`.

# COMMAND ----------

missing_rating = None
print(missing_rating is not None and missing_rating >= 3.0)
print(average_rating is not None and average_rating >= 3.0)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.8 Making Decisions: if, else, elif
# MAGIC **`if`**: the indented block runs only if the condition is true; the line that isn't indented always runs. Expected result: two lines.

# COMMAND ----------

amalfi_rate = amalfi_cancelled / amalfi_bookings * 100
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print(f"Warning: cancellation rate {amalfi_rate:.1f}%, above the threshold")
print("Check complete")

# COMMAND ----------

# MAGIC %md
# MAGIC With the property in Sardinia (14.3%) the condition is false: expected result only `Check complete`.

# COMMAND ----------

sardinia_rate = sardinia_cancelled / sardinia_bookings * 100
if sardinia_rate > CANCELLATION_RATE_THRESHOLD:
    print(f"Warning: cancellation rate {sardinia_rate:.1f}%, above the threshold")
print("Check complete")

# COMMAND ----------

# MAGIC %md
# MAGIC **`if` / `else`**: one of the two blocks always runs. Expected result: `Bungalow in Sardinia: 14.3% - ok`.

# COMMAND ----------

if sardinia_rate > CANCELLATION_RATE_THRESHOLD:
    status_label = "critical"
else:
    status_label = "ok"
print(f"Bungalow in Sardinia: {sardinia_rate:.1f}% - {status_label}")

# COMMAND ----------

# MAGIC %md
# MAGIC **Watch Out**: a value used on its own as a condition follows the `bool()` rules (Chapter 1): `0`, `""`, and `None` count as false. It works, but it hides whether the value is zero or missing: an explicit comparison is better. Expected results: `No cancellations` twice.

# COMMAND ----------

if rome_cancelled:
    print("There are cancellations")
else:
    print("No cancellations")

if rome_cancelled > 0:
    print("There are cancellations")
else:
    print("No cancellations")

# COMMAND ----------

# MAGIC %md
# MAGIC **`if` / `elif` / `else`**: base price bands. The first true condition wins. Expected result: `Beach House in Amalfi: 236.95 - medium`.

# COMMAND ----------

if base_price >= 250:
    price_band = "high"
elif base_price >= 200:
    price_band = "medium"
else:
    price_band = "low"
print(f"{property_title}: {base_price} - {price_band}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same classification with `CASE WHEN` on the three guide properties. Expected result: 11670 `high`, 16225 `medium`, 16317 `medium`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id,
# MAGIC        base_price,
# MAGIC        CASE
# MAGIC          WHEN base_price >= 250 THEN 'high'
# MAGIC          WHEN base_price >= 200 THEN 'medium'
# MAGIC          ELSE 'low'
# MAGIC        END AS price_band
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC **Classifying the cancellation rate into four statuses.** The `None` check goes first.
# MAGIC Expected result: `50.0 critical`. Then try changing the first line to `cancellation_rate = None`, `cancellation_rate = 120.0`, `cancellation_rate = sardinia_rate`: expected results `None missing data`, `120.0 impossible value`, `14.285714285714285 ok`.

# COMMAND ----------

cancellation_rate = amalfi_rate
if cancellation_rate is None:
    cancellation_status = "missing data"
elif cancellation_rate < 0 or cancellation_rate > 100:
    cancellation_status = "impossible value"
elif cancellation_rate > CANCELLATION_RATE_THRESHOLD:
    cancellation_status = "critical"
else:
    cancellation_status = "ok"
print(cancellation_rate, cancellation_status)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: in SQL a `NULL` doesn't satisfy any `WHEN` and ends up in the `ELSE` without errors. Expected result: `ok`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT CASE WHEN NULL > 30 THEN 'critical' ELSE 'ok' END AS cancellation_status

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.9 Blocks and Indentation
# MAGIC The block is made up of the lines indented by 4 spaces after the colon; it ends at the first line that goes back to the margin. Expected result: only `End of check`.

# COMMAND ----------

if sardinia_rate > CANCELLATION_RATE_THRESHOLD:
    print("Critical property")
    print("Report to the manager")
print("End of check")

# COMMAND ----------

# MAGIC %md
# MAGIC **Nested if** (in brief): an `if` inside the block of another, indented by another 4 spaces. Expected results: `Critical Summer Getaway` twice (the second time with `and`).

# COMMAND ----------

if property_type == "Summer Getaway":
    if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
        print("Critical Summer Getaway")
    else:
        print("Summer Getaway within normal range")

if property_type == "Summer Getaway" and amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print("Critical Summer Getaway")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.10 Reading the Chapter's Errors
# MAGIC The following cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the name of the error and the description;
# MAGIC - the cell marked **SILENT ERROR** gives no errors but produces a wrong result;
# MAGIC - the **Fix** cell right below must work **without errors**.
# MAGIC
# MAGIC Before starting, run the setup cell again. Expected results of the fixes, in order: `critical`; `Amalfi property`; `critical`; `ok`; `False`; `True`; `high`; `Amalfi property`; `Inactive booking`.

# COMMAND ----------

# INTENTIONAL ERROR – the colon after the condition is missing
amalfi_rate = 50.0
if amalfi_rate > CANCELLATION_RATE_THRESHOLD
    print("critical")

# COMMAND ----------

# Fix: the colon closes the if line
amalfi_rate = 50.0
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print("critical")

# COMMAND ----------

# INTENTIONAL ERROR – = instead of == in the condition
if destination = "Amalfi":
    print("Amalfi property")

# COMMAND ----------

# Fix: == compares
if destination == "Amalfi":
    print("Amalfi property")

# COMMAND ----------

# INTENTIONAL ERROR – line of the block without indentation
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
print("critical")

# COMMAND ----------

# Fix: the line of the block is indented by 4 spaces
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print("critical")

# COMMAND ----------

# INTENTIONAL ERROR – indentation with no block to open
status_label = "ok"
    print(status_label)

# COMMAND ----------

# Fix: no indentation outside a block
status_label = "ok"
print(status_label)

# COMMAND ----------

# INTENTIONAL ERROR – the comparison comes before the None check
missing_rating = None
print(missing_rating >= 3.0 and missing_rating is not None)

# COMMAND ----------

# Fix: first the None check, then the comparison
missing_rating = None
print(missing_rating is not None and missing_rating >= 3.0)

# COMMAND ----------

# INTENTIONAL ERROR – comparison between a piece of text and a number
property_id_text = "16225"
print(property_id_text > 16000)

# COMMAND ----------

# Fix: convert the text to a number before comparing
property_id_text = "16225"
print(int(property_id_text) > 16000)

# COMMAND ----------

# SILENT ERROR – conditions in the wrong order
rome_price = 284.97
if rome_price >= 200:
    price_band = "medium"
elif rome_price >= 250:
    price_band = "high"
else:
    price_band = "low"
print(price_band)

# COMMAND ----------

# Fix: from the most restrictive condition to the least restrictive
rome_price = 284.97
if rome_price >= 250:
    price_band = "high"
elif rome_price >= 200:
    price_band = "medium"
else:
    price_band = "low"
print(price_band)

# COMMAND ----------

# SILENT ERROR – different capitalization in the compared text
if destination == "amalfi":
    print("Amalfi property")
else:
    print("Other destination")

# COMMAND ----------

# Fix: write the text exactly as it is in the data
if destination == "Amalfi":
    print("Amalfi property")
else:
    print("Other destination")

# COMMAND ----------

# SILENT ERROR – or between a comparison and a piece of text
status = "pending"
if status == "confirmed" or "completed":
    print("Active booking")
else:
    print("Inactive booking")

# COMMAND ----------

# Fix: each comparison must be written in full
status = "pending"
if status == "confirmed" or status == "completed":
    print("Active booking")
else:
    print("Inactive booking")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - Arithmetic operators: `+` `-` `*` `/` (always `float`), `//` integer division, `%` remainder, `**` power; precedence `**` → `*` `/` `//` `%` → `+` `-`; when in doubt, parentheses.
# MAGIC - With text: `+` joins, `*` repeats; a number must be converted with `str()` or placed in an f-string.
# MAGIC - Comparisons `==` `!=` `<` `>` `<=` `>=` → `True`/`False`; `=` puts, `==` asks; text is case-sensitive; `0 <= x <= 100` like `BETWEEN`; `float`s are compared after rounding.
# MAGIC - `and`, `or`, `not` as in `WHERE`; `and` before `or`; with `or`, each comparison in full.
# MAGIC - `is None` / `is not None` like `IS NULL`; first the `None` check, then the comparison (`and` stops as soon as the result is known).
# MAGIC - `if` / `elif` / `else` like `CASE WHEN`: the first true condition wins; in SQL a `NULL` ends up in the `ELSE`, in Python a `None` produces `TypeError`.
# MAGIC - Colon at the end of the line and block indented by 4 spaces: indentation is part of the syntax.
