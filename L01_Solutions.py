# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 1 – Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in `L01_Exercises` (the same as in Appendix A).
# MAGIC Run one cell at a time: exercise 8 contains intentional errors.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Variables of the Second Property

# COMMAND ----------

# Values of the Bungalow in Sardinia: the identifier is a whole number, like the property_id column
property_id = 16317
property_title = "Bungalow in Sardinia"
destination = "Sardinia"
base_price = 213.91

# print() with two values: the value and its type, separated by a space
print(property_id, type(property_id))
print(property_title, type(property_title))
print(destination, type(destination))
print(base_price, type(base_price))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Guess the Type
# MAGIC Quotation marks turn even `"2024"` and `"True"` into text; division always returns a `float`.

# COMMAND ----------

# 2024 – expected type: int
type(2024)

# COMMAND ----------

# "2024" – expected type: str (the quotation marks make it text)
type("2024")

# COMMAND ----------

# 30.0 – expected type: float (it has a decimal point)
type(30.0)

# COMMAND ----------

# True – expected type: bool
type(True)

# COMMAND ----------

# "True" – expected type: str (between quotation marks it isn't a true/false value)
type("True")

# COMMAND ----------

# None – expected type: NoneType
type(None)

# COMMAND ----------

# 4 / 2 – expected type: float (it equals 2.0: division always returns a float)
type(4 / 2)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – A Report Line

# COMMAND ----------

property_title = "Beach House in Amalfi"
destination = "Amalfi"
bookings_2024 = 4
revenue_2024 = 2896.92

# A single f-string: the parentheses around {destination} are text
print(f"{property_title} ({destination}): {bookings_2024} bookings, revenue {revenue_2024}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Three Cancellation Rates

# COMMAND ----------

CANCELLATION_RATE_THRESHOLD = 30.0

# Rome: 0 canceled out of 6 (a real zero, not a missing value)
rome_rate = 0 / 6 * 100
# Sardinia: 1 out of 7
sardinia_rate = 1 / 7 * 100
# Amalfi: 2 out of 4
amalfi_rate = 2 / 4 * 100

# :.1f shows one decimal place; the threshold is a float and appears as 30.0
print(f"Historic Inn in Rome: {rome_rate:.1f}% (threshold {CANCELLATION_RATE_THRESHOLD}%)")
print(f"Bungalow in Sardinia: {sardinia_rate:.1f}% (threshold {CANCELLATION_RATE_THRESHOLD}%)")
print(f"Beach House in Amalfi: {amalfi_rate:.1f}% (threshold {CANCELLATION_RATE_THRESHOLD}%)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Data Sheet That Arrived as Text

# COMMAND ----------

base_price_text = "236.95"
bookings_text = "4"
revenue_text = "2896.92"

# 1. Conversions: price and revenue have decimals (float), bookings are a whole number (int)
base_price = float(base_price_text)
bookings_2024 = int(bookings_text)
revenue_2024 = float(revenue_text)

# 2. Calculations
revenue_per_booking = revenue_2024 / bookings_2024
nights_at_base_price = revenue_per_booking / base_price
print(f"Average revenue per booking: {revenue_per_booking:.2f}")
print(f"Nights at the base price: {nights_at_base_price:.1f}")

# 3. int() truncates (236), round() rounds (237)
print(f"int: {int(base_price)} - round: {round(base_price)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Totals Step by Step

# COMMAND ----------

total_bookings = 0
total_cancelled = 0

# Rome
total_bookings = total_bookings + 6
total_cancelled = total_cancelled + 0
# Sardinia
total_bookings = total_bookings + 7
total_cancelled = total_cancelled + 1
# Amalfi
total_bookings = total_bookings + 4
total_cancelled = total_cancelled + 2

# The overall rate is calculated on the totals, not as the average of the three rates
total_rate = total_cancelled / total_bookings * 100
print(f"Bookings: {total_bookings} - canceled: {total_cancelled} - overall rate: {total_rate:.1f}%")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – The Average Base Price

# COMMAND ----------

total_base_price = 284.97 + 213.91 + 236.95
print(total_base_price)  # 735.8299999999999: approximate decimals of floats, not an error

average_base_price = total_base_price / 3
print(average_base_price)                # full value
print(f"{average_base_price:.2f}")       # format: changes only the displayed text
print(round(average_base_price, 2))      # new rounded value, usable in calculations
print(int(average_base_price))           # int() truncates: discards the decimals

# Explanation: floats are stored in binary form, and 284.97, 213.91, 236.95 have no
# exact representation; the sum shows the small difference. The value to use in later
# calculations with two decimal places is the one from round(..., 2); the :.2f format only displays it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC Each `INTENTIONAL ERROR` cell must fail; the fix below it must work.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
property title = "Historic Inn in Rome"

# COMMAND ----------

# Fix 8a (SyntaxError: invalid syntax – a name can't contain spaces)
property_title = "Historic Inn in Rome"
print(property_title)

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
rating = 3.2
print(f"Average rating: {Rating}")

# COMMAND ----------

# Fix 8b (NameError: name 'Rating' is not defined – uppercase and lowercase matter)
rating = 3.2
print(f"Average rating: {rating}")

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
print("Bookings: " + 6)

# COMMAND ----------

# Fix 8c (TypeError: can only concatenate str (not "int") to str – use an f-string)
print(f"Bookings: {6}")

# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
base_price = int("213,91")

# COMMAND ----------

# Fix 8d (ValueError: invalid literal for int() with base 10: '213,91')
# Two problems: the decimal comma and int() instead of float()
base_price = float("213.91")
print(base_price)

# COMMAND ----------

# SILENT ERROR – cell 8e
revenue_2024 = 5139.59
print("2024 revenue: {revenue_2024}")

# COMMAND ----------

# Fix 8e (no message, but the braces appear exactly as written: the f is missing)
revenue_2024 = 5139.59
print(f"2024 revenue: {revenue_2024}")
