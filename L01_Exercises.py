# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 1 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**. No tables to prepare: the values are those of the guide properties, written by hand.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L01_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L01_Exercises_done`). Run one cell at a time (exercise 8 contains intentional errors).
# MAGIC Each exercise has a **check** cell that prints the expected result, to compare with your own output.
# MAGIC
# MAGIC | property_id | title | destination | base_price | 2024 Bookings | Canceled | 2024 Revenue |
# MAGIC |---|---|---|---|---|---|---|
# MAGIC | 11670 | Historic Inn in Rome | Rome | 284.97 | 6 | 0 | 3966.21 |
# MAGIC | 16317 | Bungalow in Sardinia | Sardinia | 213.91 | 7 | 1 | 5139.59 |
# MAGIC | 16225 | Beach House in Amalfi | Amalfi | 236.95 | 4 | 2 | 2896.92 |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Variables of the Second Property
# MAGIC Create the variables `property_id`, `property_title`, `destination`, and `base_price` with the values of the Bungalow in Sardinia and print each one together with its type, with one `print()` per variable.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("16317 <class 'int'>")
print("Bungalow in Sardinia <class 'str'>")
print("Sardinia <class 'str'>")
print("213.91 <class 'float'>")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Guess the Type
# MAGIC For each value, first write the expected type in a comment; then check it with `type()`, one value per cell:
# MAGIC `2024`, `"2024"`, `30.0`, `True`, `"True"`, `None`, `4 / 2`.

# COMMAND ----------

# 2024 – expected type: ...


# COMMAND ----------

# "2024" – expected type: ...


# COMMAND ----------

# 30.0 – expected type: ...


# COMMAND ----------

# True – expected type: ...


# COMMAND ----------

# "True" – expected type: ...


# COMMAND ----------

# None – expected type: ...


# COMMAND ----------

# 4 / 2 – expected type: ...


# COMMAND ----------

# Check: expected result
print("int, str, float, bool, str, NoneType, float")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – A Report Line
# MAGIC Using the variables of the Beach House in Amalfi (`property_title`, `destination`, `bookings_2024`, `revenue_2024`), print the report line with **a single f-string**.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Beach House in Amalfi (Amalfi): 4 bookings, revenue 2896.92")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Three Cancellation Rates
# MAGIC Define the constant `CANCELLATION_RATE_THRESHOLD = 30.0`. For each guide property, calculate the cancellation rate (canceled / bookings × 100) and print it with one decimal place, together with the threshold.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Historic Inn in Rome: 0.0% (threshold 30.0%)")
print("Bungalow in Sardinia: 14.3% (threshold 30.0%)")
print("Beach House in Amalfi: 50.0% (threshold 30.0%)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Data Sheet That Arrived as Text
# MAGIC The data sheet of the Beach House in Amalfi arrives with all values as text (cell below).
# MAGIC 1. Convert the three values to the appropriate type.
# MAGIC 2. Calculate the average revenue per booking (two decimal places) and how many nights at the base price it corresponds to (average revenue / base price, one decimal place).
# MAGIC 3. Print `int()` and `round()` of the base price.

# COMMAND ----------

base_price_text = "236.95"
bookings_text = "4"
revenue_text = "2896.92"

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Average revenue per booking: 724.23")
print("Nights at the base price: 3.1")
print("int: 236 - round: 237")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Totals Step by Step
# MAGIC Starting from `total_bookings = 0` and `total_cancelled = 0`, add the bookings (6, 7, 4) and the cancellations (0, 1, 2) one property at a time, with reassignments. Then calculate the overall cancellation rate with one decimal place.

# COMMAND ----------

total_bookings = 0
total_cancelled = 0

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Bookings: 17 - canceled: 3 - overall rate: 17.6%")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – The Average Base Price
# MAGIC Calculate the average base price of the three guide properties (284.97, 213.91, 236.95) and display it in four ways: full value, `:.2f` format, `round(..., 2)`, `int()`.
# MAGIC Explain in a comment why the sum of the three prices appears as `735.8299999999999` and which of the four results is a value you can use in later calculations with two decimal places.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("245.27666666666664")
print("245.28")
print("245.28")
print("245")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the fifth a **silent error**. Run them one at a time, note the name of the error (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `Historic Inn in Rome`, `Average rating: 3.2`, `Bookings: 6`, `213.91`, `2024 revenue: 5139.59`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
property title = "Historic Inn in Rome"

# COMMAND ----------

# Fix 8a (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
rating = 3.2
print(f"Average rating: {Rating}")

# COMMAND ----------

# Fix 8b (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
print("Bookings: " + 6)

# COMMAND ----------

# Fix 8c (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
base_price = int("213,91")

# COMMAND ----------

# Fix 8d (error name: ...)


# COMMAND ----------

# SILENT ERROR – cell 8e
revenue_2024 = 5139.59
print("2024 revenue: {revenue_2024}")

# COMMAND ----------

# Fix 8e (what's wrong: ...)

