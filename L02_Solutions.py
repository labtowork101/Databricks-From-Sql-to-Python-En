# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 2 – Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in `L02_Exercises` (the same as in Appendix A).
# MAGIC Run the setup cell first, then one cell at a time: exercise 8 contains intentional errors.

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

# COMMAND ----------

total_bookings = rome_bookings + sardinia_bookings + amalfi_bookings
total_cancelled = rome_cancelled + sardinia_cancelled + amalfi_cancelled
total_revenue = rome_revenue + sardinia_revenue + amalfi_revenue

# The average revenue is calculated on the totals
revenue_per_booking = total_revenue / total_bookings

# The parentheses are essential: without them, only the last price would be divided by 3
average_base_price = (284.97 + 213.91 + 236.95) / 3

print(f"Bookings: {total_bookings} - canceled: {total_cancelled}")
print(f"Total revenue: {total_revenue:.2f}")
print(f"Average revenue per booking: {revenue_per_booking:.2f}")
print(f"Average base price: {average_base_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Weeks, Hours, and Minutes

# COMMAND ----------

nights = 9
# // gives the full weeks, % the nights left over
print(f"{nights} nights: full weeks {nights // 7}, extra nights {nights % 7}")

nights = 23
print(f"{nights} nights: full weeks {nights // 7}, extra nights {nights % 7}")

# COMMAND ----------

seconds = 3725
hours = seconds // 3600
# First the remainder of the hours (the parentheses aren't needed: % and // have the same
# precedence and run from left to right, but we write them for clarity)
minutes = (seconds % 3600) // 60
remaining_seconds = seconds % 60
print(f"{seconds} seconds = {hours} h {minutes} min {remaining_seconds} s")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – True or False

# COMMAND ----------

print(destination == "Amalfi")              # a) True
print(destination == "AMALFI")              # b) False: different capitalization
print(property_id == "16225")               # c) False: a number and a piece of text are never equal
print(base_price > 200 and base_price < 250) # d) True
print(284.97 * 3 == 854.91)                 # e) False: approximate decimals
print(0 <= 50.0 <= 100)                     # f) True: chained comparison
print(ANALYSIS_YEAR % 4 == 0)               # g) True: remainder zero, leap year
print(not (amalfi_bookings > 5))            # h) True: 4 > 5 is false, not reverses it

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Compound Conditions

# COMMAND ----------

booking_status = "confirmed"
total_amount = 1250.0
guests_count = 5

# With or, each comparison is written in full
is_active = booking_status == "confirmed" or booking_status == "completed"
is_large = total_amount >= 1000 and guests_count >= 4
needs_check = booking_status == "cancelled" or total_amount < 100
print(f"active: {is_active} - large: {is_large} - needs check: {needs_check}")

# COMMAND ----------

booking_status = "cancelled"
total_amount = 80.0
guests_count = 2

is_active = booking_status == "confirmed" or booking_status == "completed"
is_large = total_amount >= 1000 and guests_count >= 4
needs_check = booking_status == "cancelled" or total_amount < 100
print(f"active: {is_active} - large: {is_large} - needs check: {needs_check}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – Price Bands
# MAGIC The cell is run four times, changing the first two lines: Rome (284.97), Sardinia (213.91), Amalfi (236.95), test property (180.0).

# COMMAND ----------

property_title = "Historic Inn in Rome"
base_price = 284.97

# From the highest band to the lowest: the first true condition wins
if base_price >= 250:
    price_band = "high"
elif base_price >= 200:
    price_band = "medium"
else:
    price_band = "low"
print(f"{property_title}: {price_band}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same classification with CASE WHEN
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
# MAGIC The cell is run six times, changing the first line: `0.0`, `14.3`, `50.0`, `None`, `120.0`, `-5.0`.

# COMMAND ----------

cancellation_rate = 0.0

# The None check goes first: the other comparisons with None would give TypeError
if cancellation_rate is None:
    cancellation_status = "missing data"
elif cancellation_rate < 0 or cancellation_rate > 100:
    cancellation_status = "impossible value"
elif cancellation_rate > CANCELLATION_RATE_THRESHOLD:
    cancellation_status = "critical"
else:
    cancellation_status = "ok"
print(cancellation_rate, cancellation_status)

# Answer to the question: if the None check is moved to the end, with None the
# first condition (cancellation_rate < 0) produces
# TypeError: '<' not supported between instances of 'NoneType' and 'int'.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – A Record to Validate
# MAGIC The cell is run four times, changing the three text lines: (`"4"`, `"2"`, `""`), (`"4"`, `"2"`, `"3.0"`), (`"0"`, `"0"`, `"3.0"`), (`"4"`, `"5"`, `""`).

# COMMAND ----------

property_title = "Beach House in Amalfi"
bookings_text = "4"
cancelled_text = "2"
rating_text = ""

# 1. Conversions
bookings = int(bookings_text)
cancelled = int(cancelled_text)

# 2. Rate: calculated only if there are bookings, otherwise it's missing data
if bookings > 0:
    cancellation_rate = cancelled / bookings * 100
else:
    cancellation_rate = None

# 3. Rating: empty text means a missing rating
if rating_text == "":
    rating = None
else:
    rating = float(rating_text)

# 4. Status of the rate (same classification as in exercise 6)
if cancellation_rate is None:
    cancellation_status = "missing data"
elif cancellation_rate < 0 or cancellation_rate > 100:
    cancellation_status = "impossible value"
elif cancellation_rate > CANCELLATION_RATE_THRESHOLD:
    cancellation_status = "critical"
else:
    cancellation_status = "ok"

# 5. Text for the report: "n/a" in place of the missing values
if cancellation_rate is None:
    rate_label = "n/a"
else:
    rate_label = f"{cancellation_rate:.1f}%"

if rating is None:
    rating_label = "n/a"
else:
    rating_label = f"{rating:.1f}"

print(f"{property_title}: rate {rate_label} ({cancellation_status}), average rating {rating_label}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC Every `INTENTIONAL ERROR` cell must fail, every `SILENT ERROR` cell produces a wrong result; the fix below must work.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
rome_price = 284.97
if rome_price >= 250
    print("high")

# COMMAND ----------

# Fix 8a (SyntaxError: expected ':' – the colon is missing)
rome_price = 284.97
if rome_price >= 250:
    print("high")

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
if property_type = "Summer Getaway":
    print("Summer property")

# COMMAND ----------

# Fix 8b (SyntaxError: invalid syntax. Maybe you meant '==' ... – the condition needs ==)
if property_type == "Summer Getaway":
    print("Summer property")

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
amalfi_rate = 50.0
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
print("critical")

# COMMAND ----------

# Fix 8c (IndentationError: expected an indented block – the line of the block must be indented)
amalfi_rate = 50.0
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print("critical")

# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
average_rating = None
if average_rating >= 3.0:
    print("Satisfactory rating")

# COMMAND ----------

# Fix 8d (TypeError: '>=' not supported between instances of 'NoneType' and 'float')
# First the None check; with the rating missing, a dedicated message is printed
average_rating = None
if average_rating is None:
    print("Rating not available")
elif average_rating >= 3.0:
    print("Satisfactory rating")

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

# Fix 8e (prints "warning" instead of "critical": the first true condition wins,
# so the higher threshold must be checked first)
amalfi_rate = 50.0
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    print("critical")
elif amalfi_rate > 15:
    print("warning")
else:
    print("ok")

# COMMAND ----------

# SILENT ERROR – cell 8f
status = "completed"
if status == "cancelled" or "pending":
    print("To be checked")
else:
    print("No check needed")

# COMMAND ----------

# Fix 8f (always prints "To be checked": "pending" on its own is non-empty text,
# so it counts as true; each comparison must be written in full)
status = "completed"
if status == "cancelled" or status == "pending":
    print("To be checked")
else:
    print("No check needed")
