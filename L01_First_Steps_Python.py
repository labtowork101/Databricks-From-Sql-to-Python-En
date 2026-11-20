# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 1 – First Steps with Python
# MAGIC
# MAGIC Notebook for Chapter 1 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Create and update variables with assignment; give correct names to variables and constants
# MAGIC - Recognize the basic types `int`, `float`, `str`, `bool`, `None` with `type()`
# MAGIC - Display values with `print()` and with f-strings, choosing the decimal places
# MAGIC - Convert values with `int()`, `float()`, `str()` and round with `round()`
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapter 0; notebook attached to **Serverless** compute
# MAGIC - No tables to prepare: the values of the guide properties are written by hand
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: sections 1.9 and 1.10 contain intentional errors.
# MAGIC Each section creates the variables it uses: after a session interruption, start again from the first cell of the section.
# MAGIC
# MAGIC | property_id | title | destination | property_type | base_price | 2024 Bookings | Canceled | 2024 Revenue |
# MAGIC |---|---|---|---|---|---|---|---|
# MAGIC | 11670 | Historic Inn in Rome | Rome | Historical Place | 284.97 | 6 | 0 | 3966.21 |
# MAGIC | 16317 | Bungalow in Sardinia | Sardinia | Summer Getaway | 213.91 | 7 | 1 | 5139.59 |
# MAGIC | 16225 | Beach House in Amalfi | Amalfi | Summer Getaway | 236.95 | 4 | 2 | 2896.92 |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.1 Variables and Assignment
# MAGIC `name = value` puts a value into a variable; the `=` symbol is read from right to left ("put"). The next cell shows nothing.

# COMMAND ----------

revenue_2024 = 3966.21

# COMMAND ----------

revenue_2024 = 3966.21
bookings_2024 = 6
revenue_2024 / bookings_2024

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `661.035` (average revenue per booking of the property in Rome).
# MAGIC
# MAGIC **SQL Bridge**: an `AS` alias gives a name to a value, but it's valid only inside the query.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 3966.21 AS revenue_2024, 6 AS bookings_2024

# COMMAND ----------

# MAGIC %md
# MAGIC **Reassigning a variable**: the new assignment replaces the previous value.

# COMMAND ----------

property_title = "Historic Inn in Rome"
property_title = "Bungalow in Sardinia"
property_title

# COMMAND ----------

# MAGIC %md
# MAGIC **Using the current value**: each line takes the current total, adds a revenue amount, and puts the result back into `total_revenue`. Expected result: `12002.72`.

# COMMAND ----------

total_revenue = 3966.21
total_revenue = total_revenue + 5139.59
total_revenue = total_revenue + 2896.92
total_revenue

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.2 Naming Variables
# MAGIC Rules: letters, digits, and `_`; no digit at the start; no spaces or hyphens; uppercase and lowercase are different.
# MAGIC The book's conventions: English snake_case for variables, UPPERCASE for **constants**.

# COMMAND ----------

ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0
WORK_SCHEMA = "workspace.python_book"
CANCELLATION_RATE_THRESHOLD

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.3 Basic Types
# MAGIC `int`, `float`, `str`, `bool`, `None` (type `NoneType`). `type()` shows the type of a value.

# COMMAND ----------

type(11670)

# COMMAND ----------

property_id = 11670
base_price = 284.97
property_type = "Historical Place"
is_deleted = False
rating = None
type(base_price)

# COMMAND ----------

# MAGIC %md
# MAGIC Try changing the last line of the previous cell to `type(property_type)`, `type(is_deleted)`, `type(rating)`: expected results `str`, `bool`, `NoneType`.
# MAGIC
# MAGIC **SQL Bridge**: column types with `DESCRIBE TABLE` (`data_type` column: `date` for `check_in`, `float` for `total_amount`, `string` for `status`) and the type of an expression with `typeof()`.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT typeof(6), typeof(3966.21), typeof('Rome'), typeof(true)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `int`, `decimal(6,2)`, `string`, `boolean`. In SQL, 3966.21 is a fixed-precision decimal; in Python, a `float`.
# MAGIC
# MAGIC ## 1.4 Text and Numbers
# MAGIC Quotation marks decide the type: `"11670"` is text, `11670` is a number.

# COMMAND ----------

type("11670")

# COMMAND ----------

# MAGIC %md
# MAGIC **Zero, empty text, and None** are three different values: a count that equals zero, a piece of text with no characters, a missing value.

# COMMAND ----------

cancelled_bookings = 0
review_comment = ""
average_rating = None
print(cancelled_bookings, type(cancelled_bookings))
print(review_comment, type(review_comment))
print(average_rating, type(average_rating))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.5 Displaying Values: print() and f-strings
# MAGIC Each `print()` writes one line; text appears without quotes.

# COMMAND ----------

property_title = "Historic Inn in Rome"
revenue_2024 = 3966.21
bookings_2024 = 6
print(property_title)
print(revenue_2024)
print(bookings_2024)

# COMMAND ----------

print("2024 revenue:", revenue_2024, "- bookings:", bookings_2024)

# COMMAND ----------

# MAGIC %md
# MAGIC **f-strings**: `f` in front of the quotation marks; every name (or calculation) between braces is replaced by its value.

# COMMAND ----------

print(f"{property_title}: {bookings_2024} bookings, revenue {revenue_2024}")

# COMMAND ----------

print(f"Average revenue per booking: {revenue_2024 / bookings_2024}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same text with `||` and `CAST`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'Historic Inn in Rome: ' || CAST(6 AS STRING) || ' bookings' AS label

# COMMAND ----------

# MAGIC %md
# MAGIC **Choosing the decimal places**: `:.1f` = one decimal place, `:.2f` = two, `:.0f` = none. The value of the variable doesn't change.

# COMMAND ----------

cancellation_rate = 1 / 7 * 100
print(cancellation_rate)
print(f"Cancellation rate: {cancellation_rate:.1f}%")

# COMMAND ----------

print(f"Average revenue: {revenue_2024 / bookings_2024:.2f}")
print(f"Rate rounded to a whole number: {cancellation_rate:.0f}%")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `Average revenue: 661.03` (not 661.04: see section 1.6) and `Rate rounded to a whole number: 14%`.
# MAGIC
# MAGIC The next cell is a **silent error**: no message, but the output isn't the one we wanted. The fix is in the cell after it.

# COMMAND ----------

# SILENT ERROR – the f in front of the quotation marks is missing
print("2024 revenue: {revenue_2024}")

# COMMAND ----------

# Fix
print(f"2024 revenue: {revenue_2024}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.6 Approximate Decimals
# MAGIC Expected result: `854.9100000000001`. It's not an error: `float` values are stored in binary form, and some decimals aren't exact.

# COMMAND ----------

base_price = 284.97
base_price * 3

# COMMAND ----------

print(f"Three nights at the base price: {base_price * 3:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.7 Comments
# MAGIC Python ignores the text after `#`, like `--` in SQL. Ctrl+/ (Cmd+/ on a Mac) adds or removes the `#` on the selected lines.

# COMMAND ----------

# 2024 data for the guide property in Amalfi
cancelled_bookings = 2
bookings_2024 = 4

cancellation_rate = cancelled_bookings / bookings_2024 * 100  # as a percentage
print(f"Cancellation rate: {cancellation_rate:.1f}%")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.8 Type Conversions
# MAGIC `float()`, `int()`, `str()` convert a value to the indicated type, like `CAST` in SQL. The date stays text until Chapter 7.

# COMMAND ----------

base_price_text = "284.97"
bookings_text = "6"
check_in_text = "2024-03-15"

base_price = float(base_price_text)
bookings_2024 = int(bookings_text)
print(base_price * 2)
print(bookings_2024 + 1)
print(type(base_price), type(bookings_2024))

# COMMAND ----------

property_id = 11670
property_id_text = str(property_id)
print(property_id_text, type(property_id_text))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same conversions with `CAST`. In Databricks, `CAST(284.97 AS INT)` truncates to 284, like `int()`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT CAST('284.97' AS DOUBLE) AS base_price,
# MAGIC        CAST('6' AS INT)         AS bookings_2024,
# MAGIC        CAST(11670 AS STRING)    AS property_id_text,
# MAGIC        CAST(284.97 AS INT)      AS truncated_price

# COMMAND ----------

# MAGIC %md
# MAGIC **int() truncates, round() rounds**. `round(value, n)` rounds to n decimal places and produces a new value (the `:.1f` format changes only the displayed text).

# COMMAND ----------

print(int(284.97))
print(round(284.97))

# COMMAND ----------

cancellation_rate = 1 / 7 * 100
rounded_rate = round(cancellation_rate, 1)
print(rounded_rate)

# COMMAND ----------

# MAGIC %md
# MAGIC **A conversion that works by going through float()**: `int("284.97")` fails (we'll see it in section 1.10), `int(float("284.97"))` works. Expected result: `284`.

# COMMAND ----------

int(float("284.97"))

# COMMAND ----------

# MAGIC %md
# MAGIC **bool() in brief**: zero, empty text, and `None` become `False`; all other values become `True`.

# COMMAND ----------

print(bool(0), bool(6), bool(""), bool("Rome"), bool(None))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.9 Variables Live in Compute Memory
# MAGIC What counts is the order of execution, not the position in the notebook. Try this:
# MAGIC 1. run the cell marked `INTENTIONAL ERROR` **first**: it must fail with `NameError: name 'reviews_count' is not defined`, because the variable doesn't exist yet;
# MAGIC 2. run the cell with the assignment;
# MAGIC 3. run the `INTENTIONAL ERROR` cell again: now it works and prints `11`.
# MAGIC
# MAGIC The same `NameError` appears on any variable after the compute session closes: in that case, run the cells again from the beginning.

# COMMAND ----------

# INTENTIONAL ERROR (if run before the cell below) – variable not yet created
print(reviews_count)

# COMMAND ----------

# Assignment: reviews (not deleted) of the property in Rome
reviews_count = 11

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.10 Reading the Chapter's Errors
# MAGIC The following cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the name of the error and the description (last line of the message);
# MAGIC - the **Fix** cell right below must work **without errors**.
# MAGIC
# MAGIC Expected results of the fixes: no output (assignment); `12002.72`; no output (assignment); two lines `2024 revenue: 3966.21`; `6`.

# COMMAND ----------

# INTENTIONAL ERROR – variable name that starts with a digit
2024_revenue = 3966.21

# COMMAND ----------

# Fix: the year goes at the end of the name
revenue_2024 = 3966.21

# COMMAND ----------

# INTENTIONAL ERROR – capital letter in the variable name
total_revenue = 12002.72
print(Total_revenue)

# COMMAND ----------

# Fix
total_revenue = 12002.72
print(total_revenue)

# COMMAND ----------

# INTENTIONAL ERROR – text without quotation marks
destination = Rome

# COMMAND ----------

# Fix
destination = "Rome"

# COMMAND ----------

# INTENTIONAL ERROR – text and number joined with +
revenue_2024 = 3966.21
print("2024 revenue: " + revenue_2024)

# COMMAND ----------

# Fix: an f-string, or values separated by a comma
revenue_2024 = 3966.21
print(f"2024 revenue: {revenue_2024}")
print("2024 revenue:", revenue_2024)

# COMMAND ----------

# INTENTIONAL ERROR – int() on text with decimals
bookings_2024 = int("6.0")

# COMMAND ----------

# Fix: first float(), then int()
bookings_2024 = int(float("6.0"))
bookings_2024

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - `name = value` creates a variable (read as "put"); `total = total + x` updates it using its current value.
# MAGIC - Names in snake_case and in English; constants in UPPERCASE; uppercase and lowercase matter.
# MAGIC - Basic types: `int`, `float`, `str`, `bool`, `None`; `type()` shows the type. `"11670"` isn't `11670`; `0`, `""`, and `None` are different.
# MAGIC - `print()` displays several values; f-strings `f"... {name:.1f} ..."` build text and choose the decimal places.
# MAGIC - `float` values are approximate: format them with `:.2f`.
# MAGIC - Comments with `#`.
# MAGIC - `int()`, `float()`, `str()` like `CAST`; `int()` truncates, `round()` rounds; impossible conversion = `ValueError`.
# MAGIC - Variables live in compute memory: the order of execution counts; `NameError` after an interruption → run again from the top.
