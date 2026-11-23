# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 6 – Errors and Debugging
# MAGIC
# MAGIC Notebook for Chapter 6 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Read a complete error message: type, message, line, traceback
# MAGIC - Tell syntax errors apart from runtime errors
# MAGIC - Recognize the typical causes of NameError, TypeError, ValueError, ZeroDivisionError, IndexError, KeyError, and AttributeError
# MAGIC - Find a silent error with a method: expected result, debug prints, `type()`
# MAGIC - Handle values that can't be converted with `try` / `except`, like `try_cast` in SQL
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–5; notebook attached to **Serverless** compute
# MAGIC - The `%sql` cells don't read tables; no cell writes tables
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: almost every section contains intentional errors.
# MAGIC Run the **setup cell** first. The cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the type, the message, and the line;
# MAGIC - the cell marked **SILENT ERROR** gives no errors but produces a wrong result;
# MAGIC - the **Fix** cell right below must work **without errors**, with the result indicated.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Setup cell: constants and collections used in the sections
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

# The example amounts from Chapter 4, arriving as text (for example, from a file)
raw_amounts = ["879.15", "n/a", "412.5", "-42.76", "", "655.0"]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.1 Anatomy of an Error Message
# MAGIC A runtime error: read the **type** (`TypeError`), the **message**, and the **line** indicated by the `---->` arrow (here, line 4).

# COMMAND ----------

# INTENTIONAL ERROR – a number added to a piece of text
amalfi_revenue = 2896.92
sardinia_revenue = "5139.59"   # value that arrived as text
total_revenue = amalfi_revenue + sardinia_revenue
print(total_revenue)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the text is converted with `float()` before the addition. Expected result: `Amalfi and Sardinia revenue: 8036.51`.

# COMMAND ----------

# Fix: the text is converted to a number before the addition
amalfi_revenue = 2896.92
sardinia_revenue = "5139.59"   # value that arrived as text
total_revenue = amalfi_revenue + float(sardinia_revenue)
print(f"Amalfi and Sardinia revenue: {total_revenue:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: Databricks SQL errors have a name too. The next cell must fail with `CAST_INVALID_INPUT`.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- INTENTIONAL ERROR – a piece of text that doesn't represent a number
# MAGIC SELECT CAST('n/a' AS DOUBLE) AS price

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: a piece of text that represents a number. Expected result: `236.95`.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix: the text represents a number
# MAGIC SELECT CAST('236.95' AS DOUBLE) AS price

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.2 Syntax Errors and Runtime Errors
# MAGIC Two cells with the same first line. The first one contains a syntax error: **no line is run**, not even the initial `print`.

# COMMAND ----------

# INTENTIONAL ERROR – syntax error: the cell isn't run
print("Start of the cell")
if 50.0 > CANCELLATION_RATE_THRESHOLD
    print("critical")

# COMMAND ----------

# MAGIC %md
# MAGIC In the second one, the error occurs while the code is running: the lines before the error are run. Expected output before the message: `Start of the cell` and `Amalfi rate: 50.0`.

# COMMAND ----------

# INTENTIONAL ERROR – runtime error: the previous lines are run
print("Start of the cell")
amalfi_rate = 2 / 4 * 100
print(f"Amalfi rate: {amalfi_rate}")
print(amalfi_rate > "30")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the comparison is made with a number, the threshold constant. Expected result: `Start of the cell`, `Amalfi rate: 50.0`, `True`.

# COMMAND ----------

# Fix: the threshold is a number, not a piece of text
print("Start of the cell")
amalfi_rate = 2 / 4 * 100
print(f"Amalfi rate: {amalfi_rate}")
print(amalfi_rate > CANCELLATION_RATE_THRESHOLD)

# COMMAND ----------

# MAGIC %md
# MAGIC Another frequent syntax error: a parenthesis opened and never closed.

# COMMAND ----------

# INTENTIONAL ERROR – a parenthesis opened and never closed
total_bookings = sum(bookings_2024
print(total_bookings)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: every open parenthesis is closed. Expected result: `17`.

# COMMAND ----------

# Fix: the parenthesis of sum() is closed
total_bookings = sum(bookings_2024)
print(total_bookings)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.3 Reading a Traceback
# MAGIC An error inside a function called by another function. Expected output before the message: `Guide properties: average rating 3.1`; then a `ZeroDivisionError` with **three** `File <command-…>` blocks: the traceback is read **from the bottom**.

# COMMAND ----------

# INTENTIONAL ERROR – the division by zero happens inside a function called by another one
def average_of_present(values):
    total = 0
    count = 0
    for value in values:
        if value is not None:
            total = total + value
            count = count + 1
    return total / count

def describe_ratings(title, ratings):
    average = average_of_present(ratings)
    return f"{title}: average rating {average:.1f}"

print(describe_ratings("Guide properties", ratings_with_gap))
print(describe_ratings("Property without reviews", [None, None]))

# COMMAND ----------

# MAGIC %md
# MAGIC A halfway fix: `average_of_present` returns `None` if there are no values, but `describe_ratings` doesn't expect it. The error **moves** into the calling function: now it's a `TypeError` on the line with the `:.1f` format.

# COMMAND ----------

# INTENTIONAL ERROR – halfway fix: the None reaches the :.1f format
def average_of_present(values):
    total = 0
    count = 0
    for value in values:
        if value is not None:
            total = total + value
            count = count + 1
    if count == 0:
        return None
    return total / count

def describe_ratings(title, ratings):
    average = average_of_present(ratings)
    return f"{title}: average rating {average:.1f}"

print(describe_ratings("Guide properties", ratings_with_gap))
print(describe_ratings("Property without reviews", [None, None]))

# COMMAND ----------

# MAGIC %md
# MAGIC Complete fix: `describe_ratings` also handles the case without ratings. Expected result: `Guide properties: average rating 3.1` and `Property without reviews: average rating n/a`.

# COMMAND ----------

# Fix: both functions handle the case without values present
def average_of_present(values):
    total = 0
    count = 0
    for value in values:
        if value is not None:
            total = total + value
            count = count + 1
    if count == 0:
        return None
    return total / count

def describe_ratings(title, ratings):
    average = average_of_present(ratings)
    if average is None:
        return f"{title}: average rating n/a"
    return f"{title}: average rating {average:.1f}"

print(describe_ratings("Guide properties", ratings_with_gap))
print(describe_ratings("Property without reviews", [None, None]))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.4 NameError: A Name Python Doesn't Know
# MAGIC Three frequent causes, one per cell: a misspelled name, a piece of text without quotes, a function defined in another notebook.

# COMMAND ----------

# INTENTIONAL ERROR – the name of the list is written in the singular
print(max(base_price))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the right name is `base_prices`. Expected result: `284.97`.

# COMMAND ----------

# Fix: the name is the one from the setup cell
print(max(base_prices))

# COMMAND ----------

# INTENTIONAL ERROR – a piece of text without quotes is read as a name
destination = Rome
print(destination)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: text goes between quotes. Expected result: `Rome`.

# COMMAND ----------

# Fix: the text is between quotes
destination = "Rome"
print(destination)

# COMMAND ----------

# INTENTIONAL ERROR – calculate_average was defined in the Chapter 5 notebook, not in this one
print(calculate_average(ratings_with_gap))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: in this notebook, use the function defined in section 6.3 (run its fix cell first). Expected result: `3.1`.

# COMMAND ----------

# Fix: use a function defined in this notebook (section 6.3)
print(average_of_present(ratings_with_gap))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.5 TypeError and ValueError: Wrong Type, Wrong Value
# MAGIC `TypeError`: an operation receives a value of the wrong **type**. The name `NoneType` in the message points to a `None`.

# COMMAND ----------

# INTENTIONAL ERROR – the Sardinia rating is None
sardinia_rating = ratings_with_gap[1]
print(sardinia_rating * 2)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: check for `None` before the calculation. Expected result: `Rating not available`.

# COMMAND ----------

# Fix: the None case is checked before the calculation
sardinia_rating = ratings_with_gap[1]
if sardinia_rating is None:
    print("Rating not available")
else:
    print(sardinia_rating * 2)

# COMMAND ----------

# MAGIC %md
# MAGIC `ValueError`: the type is right (a piece of text), but the **value** can't be converted. Three cells, three different pieces of text.

# COMMAND ----------

# INTENTIONAL ERROR – a piece of text that doesn't represent a number
print(float("n/a"))

# COMMAND ----------

# INTENTIONAL ERROR – the decimal comma isn't recognized by float()
print(float("284,97"))

# COMMAND ----------

# INTENTIONAL ERROR – an empty piece of text
print(float(""))

# COMMAND ----------

# MAGIC %md
# MAGIC A fix is possible only for the value with the comma, at the source: the number is written with a decimal point. Expected result: `284.97`. For `"n/a"` and `""` there's no right number: we decide what to do in section 6.8.

# COMMAND ----------

# Fix: the number with the decimal point is converted
print(float("284.97"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.6 ZeroDivisionError and Collection Errors
# MAGIC A property with no bookings: the division by zero stops the cell.

# COMMAND ----------

# INTENTIONAL ERROR – a property with no bookings in 2024
cancelled = 0
bookings = 0
print(cancelled / bookings * 100)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the Chapter 5 function, with the special case handled by an `if`. Expected results: `None` and `50.0`.

# COMMAND ----------

# Fix: the zero denominator is checked before the division
def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

print(cancellation_rate(0, 0))
print(cancellation_rate(2, 4))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same division in SQL. The cell must fail with `DIVIDE_BY_ZERO`.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- INTENTIONAL ERROR – division by zero
# MAGIC SELECT 0 / 0 * 100 AS cancellation_rate

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `NULLIF` turns the zero denominator into `NULL`, and the division returns `NULL`. Expected result: `null` and `50` (the grid shows the value without decimals).

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix: NULLIF turns the zero into NULL
# MAGIC SELECT 0 / NULLIF(0, 0) * 100 AS no_bookings,
# MAGIC        2 / NULLIF(4, 0) * 100 AS amalfi

# COMMAND ----------

# MAGIC %md
# MAGIC `IndexError`: a position the list doesn't have.

# COMMAND ----------

# INTENTIONAL ERROR – the list has three rows: the positions are 0, 1, and 2
print(guide_properties[3])

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the last row is at position 2, or -1. Expected result: `Beach House in Amalfi`.

# COMMAND ----------

# Fix: the last row is read with index -1
print(guide_properties[-1]["title"])

# COMMAND ----------

# MAGIC %md
# MAGIC `KeyError`: a key the dictionary doesn't have. The message contains **only the key**.

# COMMAND ----------

# INTENTIONAL ERROR – the keys are lowercase
amalfi_row = guide_properties[2]
print(amalfi_row["Title"])

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the key written as in the dictionary. Expected results: `Beach House in Amalfi` and `None` (with `get()`, for a key that isn't there).

# COMMAND ----------

# Fix: the key is "title"; get() returns None for a missing key
amalfi_row = guide_properties[2]
print(amalfi_row["title"])
print(amalfi_row.get("base_price"))

# COMMAND ----------

# MAGIC %md
# MAGIC `AttributeError`: a method called on a value that doesn't have it. The error is on line 4, but the wrong line is line 3.

# COMMAND ----------

# INTENTIONAL ERROR – append() returns None: after line 3 the list is gone
critical_titles = []
critical_titles = critical_titles.append("Beach House in Amalfi")
critical_titles = critical_titles.append("Bungalow in Sardinia")
print(critical_titles)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `append()` changes the list and isn't assigned. Expected result: `['Beach House in Amalfi', 'Bungalow in Sardinia']`.

# COMMAND ----------

# Fix: append() is called without assigning the result
critical_titles = []
critical_titles.append("Beach House in Amalfi")
critical_titles.append("Bungalow in Sardinia")
print(critical_titles)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.7 Silent Errors and a Debugging Method
# MAGIC Step zero: know the expected result. The average of the ratings present for the guide properties is (3.2 + 3.0) / 2 = **3.1**.

# COMMAND ----------

# SILENT ERROR – the average divides by all the values, including the missing ones
def average_rating(ratings):
    total = 0
    for rating in ratings:
        if rating is not None:
            total = total + rating
    return total / len(ratings)

print(f"Average rating: {average_rating(ratings_with_gap):.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Debug: repeat the calculation outside the function with **debug prints** of the intermediate values. Expected results: `total: 6.2` (right) and `len: 3` (wrong: it also counts the `None`).

# COMMAND ----------

# Debug: debug prints of the intermediate values
total = 0
for rating in ratings_with_gap:
    if rating is not None:
        total = total + rating
print("total:", total)
print("len:", len(ratings_with_gap))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the denominator counts only the values present. Expected result: `Average rating: 3.10`.

# COMMAND ----------

# Fix: a counter of the values present only
def average_rating(ratings):
    total = 0
    count = 0
    for rating in ratings:
        if rating is not None:
            total = total + rating
            count = count + 1
    return total / count

print(f"Average rating: {average_rating(ratings_with_gap):.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `AVG` versus `SUM / COUNT(*)` on the same three ratings. Expected result: `3.10` and `2.07`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(AVG(rating), 2)              AS avg_rating,
# MAGIC        ROUND(SUM(rating) / COUNT(*), 2)   AS sum_over_all_rows
# MAGIC FROM VALUES (3.2), (NULL), (3.0) AS t(rating)

# COMMAND ----------

# MAGIC %md
# MAGIC A second silent error: the prices are pieces of text, and the maximum is calculated in alphabetical order. Result (wrong): `99.5`.

# COMMAND ----------

# SILENT ERROR – the prices are text: the maximum is the alphabetical one
raw_prices = ["284.97", "1250.0", "213.91", "99.5"]   # example values
print(max(raw_prices))

# COMMAND ----------

# MAGIC %md
# MAGIC Debug: `type()` shows the type of the values. Expected results: `<class 'str'>` and `<class 'str'>`.

# COMMAND ----------

# Debug: the type of the values and of the result
print(type(raw_prices[0]))
print(type(max(raw_prices)))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the pieces of text are converted to numbers before the comparison. Expected result: `1250.0`.

# COMMAND ----------

# Fix: convert the pieces of text to numbers, then calculate the maximum
prices = [float(raw_price) for raw_price in raw_prices]
print(max(prices))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.8 try / except
# MAGIC **SQL Bridge**: `try_cast` and `try_divide` return `NULL` instead of stopping. Expected result: `null`, `236.95`, `null`, `50`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT try_cast('n/a' AS DOUBLE)    AS price_nd,
# MAGIC        try_cast('236.95' AS DOUBLE) AS price_ok,
# MAGIC        try_divide(0, 0) * 100       AS rate_no_bookings,
# MAGIC        try_divide(2, 4) * 100       AS rate_amalfi

# COMMAND ----------

# MAGIC %md
# MAGIC The value can't be converted: the rest of the `try` block is skipped and the `except` block is run. Expected results: `Value cannot be converted` and `Price: None`.

# COMMAND ----------

raw_price = "n/a"
try:
    price = float(raw_price)
    print("Conversion succeeded")
except ValueError:
    price = None
    print("Value cannot be converted")
print(f"Price: {price}")

# COMMAND ----------

# MAGIC %md
# MAGIC The value can be converted: the `try` block reaches the end and the `except` block is skipped. Expected results: `Conversion succeeded` and `Price: 236.95`.

# COMMAND ----------

raw_price = "236.95"
try:
    price = float(raw_price)
    print("Conversion succeeded")
except ValueError:
    price = None
    print("Value cannot be converted")
print(f"Price: {price}")

# COMMAND ----------

# MAGIC %md
# MAGIC `except ValueError` catches only `ValueError` errors: an error of another type stops the cell as always.

# COMMAND ----------

# INTENTIONAL ERROR – except ValueError doesn't catch a TypeError
raw_price = None
try:
    price = float(raw_price)
except ValueError:
    price = None
print(f"Price: {price}")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: a second `except` block for the `TypeError`. Expected results: `Missing value` and `Price: None`.

# COMMAND ----------

# Fix: one except block for each expected type of error
raw_price = None
try:
    price = float(raw_price)
except ValueError:
    price = None
    print("Text cannot be converted")
except TypeError:
    price = None
    print("Missing value")
print(f"Price: {price}")

# COMMAND ----------

# MAGIC %md
# MAGIC `except ... as error`: the message of the caught error in a variable. Expected result: `Discarded: could not convert string to float: '284,97'` and `Price: None`.

# COMMAND ----------

raw_price = "284,97"
try:
    price = float(raw_price)
except ValueError as error:
    price = None
    print(f"Discarded: {error}")
print(f"Price: {price}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.9 A Conversion Function: to_float
# MAGIC The book's `try_cast`, written in Python. The cell produces no output.

# COMMAND ----------

def to_float(text):
    """Converts a piece of text to float, like try_cast in SQL.

    Returns None if the text is missing (None) or doesn't represent a number.
    """
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None

# COMMAND ----------

# MAGIC %md
# MAGIC Five tests with a known result. Expected results: `236.95`, `None`, `None`, `None`, `None`.

# COMMAND ----------

print(to_float("236.95"))
print(to_float("n/a"))
print(to_float(""))
print(to_float("284,97"))
print(to_float(None))

# COMMAND ----------

# MAGIC %md
# MAGIC The function in a loop, with a count of the discarded values. Expected results: `Discarded: 'n/a'`, `Discarded: ''`, `[879.15, 412.5, -42.76, 655.0]`, `Valid: 4 - discarded: 2 - total: 1903.89`.

# COMMAND ----------

valid_amounts = []
rejected_count = 0
for raw_amount in raw_amounts:
    amount = to_float(raw_amount)
    if amount is None:
        rejected_count = rejected_count + 1
        print(f"Discarded: '{raw_amount}'")
    else:
        valid_amounts.append(amount)

print(valid_amounts)
print(f"Valid: {len(valid_amounts)} - discarded: {rejected_count} - total: {sum(valid_amounts):.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same calculation with `try_cast`. Expected result: `1903.89`, `4`, `2`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(SUM(try_cast(raw_amount AS DOUBLE)), 2)  AS total_valid,
# MAGIC        COUNT(try_cast(raw_amount AS DOUBLE))            AS valid_count,
# MAGIC        COUNT(*) - COUNT(try_cast(raw_amount AS DOUBLE)) AS rejected_count
# MAGIC FROM VALUES ('879.15'), ('n/a'), ('412.5'), ('-42.76'), (''), ('655.0') AS t(raw_amount)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6.10 Common Mistakes with try / except
# MAGIC `except` without a type catches **all** errors, including typos. Result (wrong): `[None, None, None, None, None, None]`.

# COMMAND ----------

# SILENT ERROR – except without a type hides a NameError (flaot instead of float)
converted = []
for raw_amount in raw_amounts:
    try:
        converted.append(flaot(raw_amount))
    except:
        converted.append(None)
print(converted)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `except ValueError` and the name of the function spelled correctly. Expected result: `[879.15, None, 412.5, -42.76, None, 655.0]`.

# COMMAND ----------

# Fix: catch only the expected ValueError
converted = []
for raw_amount in raw_amounts:
    try:
        converted.append(float(raw_amount))
    except ValueError:
        converted.append(None)
print(converted)

# COMMAND ----------

# MAGIC %md
# MAGIC A `try` block that's too big: the first error skips the whole rest of the loop. Result (wrong): `Value cannot be converted` and `[879.15]`.

# COMMAND ----------

# SILENT ERROR – the try contains the whole loop: the first error stops the conversions
converted = []
try:
    for raw_amount in raw_amounts:
        converted.append(float(raw_amount))
except ValueError:
    print("Value cannot be converted")
print(converted)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the `try` contains only the conversion, inside `to_float` (section 6.9, to be run first). Expected result: `[879.15, None, 412.5, -42.76, None, 655.0]`.

# COMMAND ----------

# Fix: the try wraps a single conversion, on every iteration
converted = []
for raw_amount in raw_amounts:
    converted.append(to_float(raw_amount))
print(converted)

# COMMAND ----------

# MAGIC %md
# MAGIC A syntax error can't be caught: the cell isn't run, and the `try` block doesn't even start.

# COMMAND ----------

# INTENTIONAL ERROR – a syntax error can't be caught with try
try:
    price = float("236.95"
except SyntaxError:
    price = None

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: syntax errors are fixed in the code. Expected result: `236.95`.

# COMMAND ----------

# Fix: the parenthesis is closed
try:
    price = float("236.95")
except ValueError:
    price = None
print(price)

# COMMAND ----------

# MAGIC %md
# MAGIC When the special case can be recognized beforehand, an `if` is clearer than `try` / `except`. The two functions give the same result. Expected results: `None None` and `50.0 50.0`.

# COMMAND ----------

def rate_with_if(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

def rate_with_try(cancelled, bookings):
    try:
        return cancelled / bookings * 100
    except ZeroDivisionError:
        return None

print(rate_with_if(0, 0), rate_with_try(0, 0))
print(rate_with_if(2, 4), rate_with_try(2, 4))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - An error has a **type**, a **message**, and a **line** (`---->` arrow); read it in this order. Databricks shows the summary line at the top and the complete **traceback** below, which ends with the same line.
# MAGIC - Syntax error: the cell isn't run, and the message is one line long. Runtime error: the previous lines have been run.
# MAGIC - The traceback is read **from the bottom**: the last block shows where it happened, the blocks above show who called. The line of the error isn't always the wrong line.
# MAGIC - NameError: misspelled name, text without quotes, cell not run, function from another notebook. TypeError: wrong type (often `NoneType`). ValueError: value that can't be converted. ZeroDivisionError, IndexError, KeyError (only the key), AttributeError (often an unexpected `None`).
# MAGIC - Silent errors: step zero, the expected result; then debug prints of the intermediate values, `type()`, one fix at a time, a check with a known case or with SQL.
# MAGIC - `try` / `except Type:` tries a block and, if that error occurs, runs the alternative block; the rest of the `try` is skipped; errors of other types aren't caught. Several `except` blocks, `except ... as error`.
# MAGIC - `to_float` is the book's `try_cast`: a small `try`, a precise type, the discarded values counted. Never `except` without a type; an `if` when it's enough.
