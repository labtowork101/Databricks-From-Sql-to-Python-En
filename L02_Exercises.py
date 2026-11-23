# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 2 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**. The values are those of the guide properties, in the setup cell; exercise 5 has a `%sql` check on `samples.wanderbricks.properties`.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L02_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L02_Exercises_done`). Run the setup cell first, then one cell at a time (exercise 8 contains intentional errors).
# MAGIC Each exercise has a **check** cell that prints the expected result, to compare with your own output.
# MAGIC
# MAGIC | property_id | title | destination | property_type | base_price | 2024 Bookings | Canceled | 2024 Revenue |
# MAGIC |---|---|---|---|---|---|---|---|
# MAGIC | 11670 | Historic Inn in Rome | Rome | Historical Place | 284.97 | 6 | 0 | 3966.21 |
# MAGIC | 16317 | Bungalow in Sardinia | Sardinia | Summer Getaway | 213.91 | 7 | 1 | 5139.59 |
# MAGIC | 16225 | Beach House in Amalfi | Amalfi | Summer Getaway | 236.95 | 4 | 2 | 2896.92 |

# COMMAND ----------

# Setup cell: constants and values of the guide properties
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

rome_bookings = 6
rome_cancelled = 0
rome_revenue = 3966.21
sardinia_bookings = 7
sardinia_cancelled = 1
sardinia_revenue = 5139.59
amalfi_bookings = 4
amalfi_cancelled = 2
amalfi_revenue = 2896.92

property_id = 16225
property_title = "Beach House in Amalfi"
destination = "Amalfi"
property_type = "Summer Getaway"
base_price = 236.95
average_rating = 3.0

print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – Calculations on the Guide Properties
# MAGIC Using the variables of the setup cell, calculate: total bookings and cancellations of the three properties, total revenue (two decimal places), average revenue per booking of the three properties together (two decimal places), and average base price (284.97, 213.91, 236.95; two decimal places). Watch out for parentheses.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Bookings: 17 - canceled: 3")
print("Total revenue: 12002.72")
print("Average revenue per booking: 706.04")
print("Average base price: 245.28")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Weeks, Hours, and Minutes
# MAGIC 1. With `//` and `%`, calculate full weeks and extra nights for stays of 9 and 23 nights.
# MAGIC 2. The response time to a customer service message is 3725 seconds: write it in hours, minutes, and seconds. Hint: the minutes are calculated from the remainder of the division by 3600.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("9 nights: full weeks 1, extra nights 2")
print("23 nights: full weeks 3, extra nights 2")
print("3725 seconds = 1 h 2 min 5 s")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – True or False
# MAGIC For each expression, first write the expected result (`True` or `False`) in a comment; then check it with `print()`:
# MAGIC
# MAGIC a) `destination == "Amalfi"` · b) `destination == "AMALFI"` · c) `property_id == "16225"` · d) `base_price > 200 and base_price < 250` · e) `284.97 * 3 == 854.91` · f) `0 <= 50.0 <= 100` · g) `ANALYSIS_YEAR % 4 == 0` · h) `not (amalfi_bookings > 5)`

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("a) True  b) False  c) False  d) True  e) False  f) True  g) True  h) True")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Compound Conditions
# MAGIC For a booking with `booking_status = "confirmed"`, `total_amount = 1250.0`, `guests_count = 5`, calculate three `bool` variables:
# MAGIC - `is_active`: the status is `"confirmed"` or `"completed"`;
# MAGIC - `is_large`: amount of at least 1000 **and** at least 4 guests;
# MAGIC - `needs_check`: the status is `"cancelled"` or the amount is less than 100.
# MAGIC
# MAGIC Print them on one line; repeat with `booking_status = "cancelled"`, `total_amount = 80.0`, `guests_count = 2`.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("active: True - large: True - needs check: False")
print("active: False - large: False - needs check: True")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – Price Bands
# MAGIC Write in a cell the classification of the base price: at least 250 → `"high"`, at least 200 → `"medium"`, otherwise `"low"`, printing the title and the band.
# MAGIC Run the cell four times, changing the first two lines: Rome (284.97), Sardinia (213.91), Amalfi (236.95), and a test property (180.0). Then compare with the `%sql` check.

# COMMAND ----------

property_title = "Historic Inn in Rome"
base_price = 284.97

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Historic Inn in Rome: high")
print("Bungalow in Sardinia: medium")
print("Beach House in Amalfi: medium")
print("Test property: low")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the three guide properties classified with CASE WHEN (high, medium, medium)
# MAGIC SELECT property_id,
# MAGIC        title,
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
# MAGIC ## Exercise 6 ★★ – The Rate in Four Statuses
# MAGIC Write the classification of `cancellation_rate` into four statuses: `"missing data"` (None), `"impossible value"` (below 0 or above 100), `"critical"` (above `CANCELLATION_RATE_THRESHOLD`), `"ok"`.
# MAGIC Run the cell six times with `0.0`, `14.3`, `50.0`, `None`, `120.0`, `-5.0`. Answer in a comment: what happens with `None` if the `None` check is moved to the end?

# COMMAND ----------

cancellation_rate = 0.0

# Write your solution here


# COMMAND ----------

# Check: expected result
print("0.0 ok")
print("14.3 ok")
print("50.0 critical")
print("None missing data")
print("120.0 impossible value")
print("-5.0 impossible value")
print("With the None check at the end: TypeError: '<' not supported between instances of 'NoneType' and 'int'")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – A Record to Validate
# MAGIC The data of a property arrives as text (cell below). Write a cell that:
# MAGIC 1. converts bookings and cancellations to integers;
# MAGIC 2. calculates the cancellation rate only if there are more than zero bookings, otherwise sets it to `None`;
# MAGIC 3. sets the rating to `None` if the text is empty, otherwise converts it to `float`;
# MAGIC 4. classifies the rate into the four statuses of exercise 6;
# MAGIC 5. prints a report line with `n/a` in place of the missing values (rate with one decimal place and `%`, rating with one decimal place).
# MAGIC
# MAGIC Run the cell four times with (`"4"`, `"2"`, `""`), (`"4"`, `"2"`, `"3.0"`), (`"0"`, `"0"`, `"3.0"`), (`"4"`, `"5"`, `""`).

# COMMAND ----------

property_title = "Beach House in Amalfi"
bookings_text = "4"
cancelled_text = "2"
rating_text = ""

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Beach House in Amalfi: rate 50.0% (critical), average rating n/a")
print("Beach House in Amalfi: rate 50.0% (critical), average rating 3.0")
print("Beach House in Amalfi: rate n/a (missing data), average rating 3.0")
print("Beach House in Amalfi: rate 125.0% (impossible value), average rating n/a")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four of the following cells produce an error, the last two a **silent error**. Run them one by one (after the setup cell), note the name of the error (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `high`, `Summer property`, `critical`, `Rating not available`, `critical`, `No check needed`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
rome_price = 284.97
if rome_price >= 250
    print("high")

# COMMAND ----------

# Fix 8a (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
if property_type = "Summer Getaway":
    print("Summer property")

# COMMAND ----------

# Fix 8b (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
amalfi_rate = 50.0
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
print("critical")

# COMMAND ----------

# Fix 8c (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
average_rating = None
if average_rating >= 3.0:
    print("Satisfactory rating")

# COMMAND ----------

# Fix 8d (error name: ...; with the rating missing, print "Rating not available")


# COMMAND ----------

# SILENT ERROR – cell 8e
amalfi_rate = 50.0
if amalfi_rate > 15:
    print("warning")
elif amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print("critical")
else:
    print("ok")

# COMMAND ----------

# Fix 8e (what's wrong: ...)


# COMMAND ----------

# SILENT ERROR – cell 8f
status = "completed"
if status == "cancelled" or "pending":
    print("To be checked")
else:
    print("No check needed")

# COMMAND ----------

# Fix 8f (what's wrong: ...)
