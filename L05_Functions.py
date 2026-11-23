# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 5 – Functions
# MAGIC
# MAGIC Notebook for Chapter 5 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Define a function with `def` and call it: defining isn't running
# MAGIC - Pass values with parameters and arguments; return a result with `return`
# MAGIC - Write functions with conditions and loops, and functions that call other functions
# MAGIC - Use default values and keyword arguments; understand local variables
# MAGIC - Document a function with a docstring and choose a good name for it
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–4; notebook attached to **Serverless** compute
# MAGIC - The `%sql` cells read `samples.wanderbricks`; no cell writes tables
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: section 5.10 contains intentional errors and silent errors.
# MAGIC Run the **setup cell** first. The cells with a `def` must be run before the cells that call the function; some functions are redefined in later versions: the last cell run is the one that counts.

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

# Sample of example amounts, with one negative value and two missing ones (Chapter 4)
sample_amounts = [879.15, None, 412.5, -42.76, 655.0, None]

# The guide properties as a small table (Chapter 3)
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.1 Defining and Calling a Function
# MAGIC **SQL Bridge**: two functions we already know, with a name, parentheses, values, and a result. Expected result: `Amalfi`, `AMALFI`, `248.80`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT destination,
# MAGIC        UPPER(destination)       AS destination_upper,
# MAGIC        ROUND(236.95 * 1.05, 2)  AS new_price
# MAGIC FROM samples.wanderbricks.destinations
# MAGIC WHERE destination_id = 1100

# COMMAND ----------

# MAGIC %md
# MAGIC Python's ready-made functions have the same form. Expected results: `248.8`, `3`, `284.97`.

# COMMAND ----------

print(round(236.95 * 1.05, 2))
print(len(property_titles))
print(max(base_prices))

# COMMAND ----------

# MAGIC %md
# MAGIC The first function: the cell **defines** the function and produces no output.

# COMMAND ----------

def print_report_header():
    print("Guide properties report")
    print(f"Analysis year: {ANALYSIS_YEAR}")
    print("-" * 30)

# COMMAND ----------

# MAGIC %md
# MAGIC The **call** runs the body. Expected result: `Guide properties report`, `Analysis year: 2024`, and thirty hyphens.

# COMMAND ----------

print_report_header()

# COMMAND ----------

# MAGIC %md
# MAGIC A function can be called as many times as you like. Expected result: two headers, each followed by a line with the number of properties (`3` and `18163`), separated by a blank line.

# COMMAND ----------

print_report_header()
print("Properties analyzed: 3")
print()
print_report_header()
print("Properties analyzed: 18163")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.2 Parameters and Arguments
# MAGIC Two parameters in the definition. The cell produces no output.

# COMMAND ----------

def print_bookings(title, bookings):
    print(f"{title}: {bookings} bookings")

# COMMAND ----------

# MAGIC %md
# MAGIC Arguments are matched to parameters by position. Expected results: `Historic Inn in Rome: 6 bookings` and `Bungalow in Sardinia: 7 bookings`.

# COMMAND ----------

print_bookings("Historic Inn in Rome", 6)
print_bookings("Bungalow in Sardinia", 7)

# COMMAND ----------

# MAGIC %md
# MAGIC Arguments can be variables with names different from the parameters. Expected result: `Beach House in Amalfi: 4 bookings`.

# COMMAND ----------

amalfi_title = "Beach House in Amalfi"
amalfi_bookings = 4
print_bookings(amalfi_title, amalfi_bookings)

# COMMAND ----------

# MAGIC %md
# MAGIC The call inside a loop, with different arguments on each pass. Expected result: the three lines of the guide properties.

# COMMAND ----------

for position in range(len(property_titles)):
    print_bookings(property_titles[position], bookings_2024[position])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.3 Returning a Result: return
# MAGIC `return` hands the value over to whoever calls the function. The cell produces no output.

# COMMAND ----------

def increase_price(price):
    new_price = round(price * 1.05, 2)
    return new_price

# COMMAND ----------

# MAGIC %md
# MAGIC The call "is worth" the returned value. Expected results: `248.8`, `Increase: 11.85`, `[299.22, 224.61, 248.8]`.

# COMMAND ----------

amalfi_new_price = increase_price(236.95)
print(amalfi_new_price)
print(f"Increase: {amalfi_new_price - 236.95:.2f}")
new_prices = [increase_price(price) for price in base_prices]
print(new_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC Printing or returning: a function without `return` returns `None`. Expected results: `248.8`, then `None`.

# COMMAND ----------

def print_increased_price(price):
    print(round(price * 1.05, 2))

result = print_increased_price(236.95)
print(result)

# COMMAND ----------

# MAGIC %md
# MAGIC Early return for the special case (`None`, like `NULL * 1.05` in SQL). The cell redefines `increase_price`. Expected results: `248.8` and `None`.

# COMMAND ----------

def increase_price(price):
    if price is None:
        return None
    return round(price * 1.05, 2)

print(increase_price(236.95))
print(increase_price(None))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: a temporary function defined in SQL. The cell returns no rows.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMPORARY FUNCTION increase_price(price DOUBLE)
# MAGIC RETURNS DOUBLE
# MAGIC RETURN ROUND(price * 1.05, 2)

# COMMAND ----------

# MAGIC %md
# MAGIC The SQL function is used like `ROUND`. Expected result: 11670 284.97 299.22; 16225 236.95 248.8; 16317 213.91 224.61.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, base_price, increase_price(base_price) AS new_price
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC With `NULL`, the SQL function returns `NULL`. Expected result: `248.8` and `null`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT increase_price(236.95) AS amalfi, increase_price(NULL) AS missing

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.4 Functions with Conditions
# MAGIC The classification from Chapter 2 with a name: a `return` in every branch. The cell produces no output.

# COMMAND ----------

def classify_cancellation_rate(rate):
    if rate is None:
        return "missing data"
    if rate < 0 or rate > 100:
        return "impossible value"
    if rate > CANCELLATION_RATE_THRESHOLD:
        return "critical"
    return "ok"

# COMMAND ----------

# MAGIC %md
# MAGIC The function inside a loop. Expected results: `0.0: ok`, `14.3: ok`, `50.0: critical`, `None: missing data`, `120.0: impossible value`.

# COMMAND ----------

sample_rates = [0.0, 14.3, 50.0, None, 120.0]
for rate in sample_rates:
    print(f"{rate}: {classify_cancellation_rate(rate)}")

# COMMAND ----------

# MAGIC %md
# MAGIC The cancellation rate, with `None` if there are zero bookings. Expected results: `50.0`, `14.285714285714285`, `None`.

# COMMAND ----------

def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

print(cancellation_rate(2, 4))
print(cancellation_rate(1, 7))
print(cancellation_rate(0, 0))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.5 Functions with a Loop
# MAGIC `SUM` and `COUNT(column)` written by hand: the accumulator is prepared in the body, and the `return` goes after the loop. The two cells produce no output.

# COMMAND ----------

def calculate_total(values):
    total = 0
    for value in values:
        if value is not None:
            total = total + value
    return total

# COMMAND ----------

def count_present(values):
    count = 0
    for value in values:
        if value is not None:
            count = count + 1
    return count

# COMMAND ----------

# MAGIC %md
# MAGIC The same two functions on three different lists. Expected results: `6.2` of `2`; `1903.89` of `4`; `17` of `3`.

# COMMAND ----------

print(f"Ratings: sum {calculate_total(ratings_with_gap):.1f} of {count_present(ratings_with_gap)} values present")
print(f"Amounts: sum {calculate_total(sample_amounts):.2f} of {count_present(sample_amounts)} values present")
print(f"Bookings: sum {calculate_total(bookings_2024)} of {count_present(bookings_2024)} values present")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `SUM`, `COUNT`, and `AVG` on the same six amounts. Expected result: `1903.89`, `4`, `475.972500`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT SUM(amount)   AS amount_sum,
# MAGIC        COUNT(amount) AS amount_count,
# MAGIC        AVG(amount)   AS amount_avg
# MAGIC FROM VALUES (879.15), (NULL), (412.5), (-42.76), (655.0), (NULL) AS t(amount)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.6 Functions That Call Other Functions
# MAGIC The average of the values present uses the two functions from section 5.5 (run them first). Expected results: `Average rating: 3.1`, `Average amount: 475.97`, `None`.

# COMMAND ----------

def calculate_average(values):
    count = count_present(values)
    if count == 0:
        return None
    return calculate_total(values) / count

print(f"Average rating: {calculate_average(ratings_with_gap):.1f}")
print(f"Average amount: {calculate_average(sample_amounts):.2f}")
print(calculate_average([None, None]))

# COMMAND ----------

# MAGIC %md
# MAGIC The loop from Chapter 4 in two lines (you need `cancellation_rate` and `classify_cancellation_rate` from section 5.4). Expected results: `Historic Inn in Rome: 0.0% (ok)`, `Bungalow in Sardinia: 14.3% (ok)`, `Beach House in Amalfi: 50.0% (critical)`.

# COMMAND ----------

def describe_property(row):
    rate = cancellation_rate(row["cancelled_2024"], row["bookings_2024"])
    status = classify_cancellation_rate(rate)
    return f"{row['title']}: {rate:.1f}% ({status})"

for row in guide_properties:
    print(describe_property(row))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.7 Default Values and Keyword Arguments
# MAGIC **SQL Bridge**: the second value of `ROUND` is optional. Expected result: `214` and `213.9`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(213.91) AS no_digits, ROUND(213.91, 1) AS one_digit

# COMMAND ----------

# MAGIC %md
# MAGIC Parameters with a default value. Expected results: `248.8`, `302.41`, `348.16`.

# COMMAND ----------

def project_price(price, years=1, growth_rate=0.05):
    projected_price = price
    for year in range(years):
        projected_price = projected_price * (1 + growth_rate)
    return round(projected_price, 2)

print(project_price(236.95))
print(project_price(236.95, 5))
print(project_price(236.95, 5, 0.08))

# COMMAND ----------

# MAGIC %md
# MAGIC Keyword arguments: you change just one default. Expected results: `255.91`, `274.69`, `302.41`.

# COMMAND ----------

print(project_price(236.95, growth_rate=0.08))
print(project_price(236.95, years=5, growth_rate=0.03))
print(project_price(price=236.95, years=5))

# COMMAND ----------

# MAGIC %md
# MAGIC The threshold as a parameter with a default (the cell redefines `classify_cancellation_rate`). Expected results: `ok`, `critical`, `critical`.

# COMMAND ----------

def classify_cancellation_rate(rate, threshold=CANCELLATION_RATE_THRESHOLD):
    if rate is None:
        return "missing data"
    if rate < 0 or rate > 100:
        return "impossible value"
    if rate > threshold:
        return "critical"
    return "ok"

print(classify_cancellation_rate(14.3))
print(classify_cancellation_rate(14.3, 10.0))
print(classify_cancellation_rate(14.3, threshold=10.0))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.8 Variables Inside and Outside Functions
# MAGIC An assignment inside the function creates a local variable and doesn't touch the outside one. Expected results: `Inside the function: to be checked` and `Outside the function: ok`.

# COMMAND ----------

status = "ok"

def reset_status():
    status = "to be checked"
    print(f"Inside the function: {status}")

reset_status()
print(f"Outside the function: {status}")

# COMMAND ----------

# MAGIC %md
# MAGIC In through the parameters, out with `return`: the outside variable doesn't change. Expected results: `256.47` and `284.97`.

# COMMAND ----------

def apply_discount(price, discount=0.10):
    discounted_price = price * (1 - discount)
    return round(discounted_price, 2)

rome_price = 284.97
print(apply_discount(rome_price))
print(rome_price)

# COMMAND ----------

# MAGIC %md
# MAGIC A dictionary received as an argument: changes to its contents are visible outside. Expected result: the Amalfi row with `'cancellation_rate': 50.0` and `'cancellation_status': 'critical'`.

# COMMAND ----------

def add_cancellation_status(row):
    rate = cancellation_rate(row["cancelled_2024"], row["bookings_2024"])
    row["cancellation_rate"] = rate
    row["cancellation_status"] = classify_cancellation_rate(rate)

for row in guide_properties:
    add_cancellation_status(row)
print(guide_properties[2])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.9 Docstrings and Good Names
# MAGIC A one-line docstring, displayed by `help()`. Expected result: `Help on function cancellation_rate in module __main__:`, the line `cancellation_rate(cancelled, bookings)`, and the docstring.

# COMMAND ----------

def cancellation_rate(cancelled, bookings):
    """Returns the cancellation rate as a percentage, or None if there are no bookings."""
    if bookings == 0:
        return None
    return cancelled / bookings * 100

help(cancellation_rate)

# COMMAND ----------

# MAGIC %md
# MAGIC A multi-line docstring (you need the functions from section 5.5). Expected result: the help for `calculate_average` with the three lines of description.

# COMMAND ----------

def calculate_average(values):
    """Calculates the average of the values present in a list.

    None values are ignored, as AVG does in SQL.
    Returns None if the list contains no values present.
    """
    count = count_present(values)
    if count == 0:
        return None
    return calculate_total(values) / count

help(calculate_average)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5.10 Reading the Chapter's Errors
# MAGIC The following cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the name of the error and the description;
# MAGIC - the cell marked **SILENT ERROR** gives no error but produces a wrong result;
# MAGIC - the **Fix** cell right below must work **without errors**.
# MAGIC
# MAGIC Each cell contains the definition of the function it uses; the fixes bring the functions back to the correct form.
# MAGIC
# MAGIC Expected results of the fixes, in order: `248.8`; `248.8`; `302.41`; `50.0`; `248.8`; `256.47`; `497.6`; the report header; `248.8`; `17`; `50.0`.

# COMMAND ----------

# INTENTIONAL ERROR – the colon after the definition line is missing
def increase_price(price)
    return round(price * 1.05, 2)

# COMMAND ----------

# Fix: the definition line ends with a colon
def increase_price(price):
    return round(price * 1.05, 2)

print(increase_price(236.95))

# COMMAND ----------

# INTENTIONAL ERROR – the body of the function isn't indented
def increase_price(price):
return round(price * 1.05, 2)

# COMMAND ----------

# Fix: the body is indented by 4 spaces
def increase_price(price):
    return round(price * 1.05, 2)

print(increase_price(236.95))

# COMMAND ----------

# INTENTIONAL ERROR – growth_rate has no default but follows years, which has one
def project_price(price, years=1, growth_rate):
    return round(price * (1 + growth_rate) ** years, 2)

# COMMAND ----------

# Fix: growth_rate has a default too
def project_price(price, years=1, growth_rate=0.05):
    return round(price * (1 + growth_rate) ** years, 2)

print(project_price(236.95, 5))

# COMMAND ----------

# INTENTIONAL ERROR – the call passes only one argument, the function requires two
def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

print(cancellation_rate(2))

# COMMAND ----------

# Fix: pass both arguments
def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

print(cancellation_rate(2, 4))

# COMMAND ----------

# INTENTIONAL ERROR – the call passes two arguments, the function accepts one
def increase_price(price):
    return round(price * 1.05, 2)

print(increase_price(236.95, 0.10))

# COMMAND ----------

# Fix: the call passes only the price
def increase_price(price):
    return round(price * 1.05, 2)

print(increase_price(236.95))

# COMMAND ----------

# INTENTIONAL ERROR – discounted_price exists only inside the function
def apply_discount(price, discount=0.10):
    discounted_price = price * (1 - discount)
    return round(discounted_price, 2)

apply_discount(284.97)
print(discounted_price)

# COMMAND ----------

# Fix: the result is obtained from the returned value
def apply_discount(price, discount=0.10):
    discounted_price = price * (1 - discount)
    return round(discounted_price, 2)

rome_discounted = apply_discount(284.97)
print(rome_discounted)

# COMMAND ----------

# INTENTIONAL ERROR – the function prints but doesn't return: the result is None
def print_increased_price(price):
    print(round(price * 1.05, 2))

new_price = print_increased_price(236.95)
print(new_price * 2)

# COMMAND ----------

# Fix: the function that calculates returns the result, and the printing is done outside
def increase_price(price):
    return round(price * 1.05, 2)

new_price = increase_price(236.95)
print(new_price * 2)

# COMMAND ----------

# SILENT ERROR – without parentheses the function isn't called
def print_report_header():
    print("Guide properties report")
    print("-" * 30)

print_report_header

# COMMAND ----------

# Fix: the call has parentheses
def print_report_header():
    print("Guide properties report")
    print("-" * 30)

print_report_header()

# COMMAND ----------

# SILENT ERROR – the function calculates but doesn't return the result
def increase_price(price):
    new_price = round(price * 1.05, 2)

print(increase_price(236.95))

# COMMAND ----------

# Fix: the body ends with return
def increase_price(price):
    new_price = round(price * 1.05, 2)
    return new_price

print(increase_price(236.95))

# COMMAND ----------

# SILENT ERROR – the return is inside the loop: the function ends on the first pass
def calculate_total(values):
    total = 0
    for value in values:
        if value is not None:
            total = total + value
        return total

print(calculate_total(bookings_2024))

# COMMAND ----------

# Fix: the return is at the same level as the for, after the loop
def calculate_total(values):
    total = 0
    for value in values:
        if value is not None:
            total = total + value
    return total

print(calculate_total(bookings_2024))

# COMMAND ----------

# SILENT ERROR – arguments in the wrong order: bookings and cancellations swapped
def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

print(cancellation_rate(4, 2))

# COMMAND ----------

# Fix: keyword arguments, so the order no longer matters
def cancellation_rate(cancelled, bookings):
    if bookings == 0:
        return None
    return cancelled / bookings * 100

print(cancellation_rate(cancelled=2, bookings=4))

# COMMAND ----------

# MAGIC %md
# MAGIC **Silent error: def changed but not run again** (can't be reproduced in a single cell). You fix the body of a function in the `def` cell, but run again only the cell with the call: Python keeps using the version in memory and the result doesn't change. **Fix**: after every change, run the `def` cell again, then the cells that call the function.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - `def name(parameters):` and the indented body **define** the function without running it; `name(arguments)` **calls** it. Run the `def` cell before the calls and run it again after every change; a new `def` with the same name replaces the function.
# MAGIC - Parameters (in the definition) and arguments (in the call) are matched by position; their number must match.
# MAGIC - `return` hands over the value and ends the function; without `return` the result is `None`. A function that calculates returns; printing is done outside. Early return for special cases.
# MAGIC - Function with conditions = `CASE WHEN` with a name; function with a loop: accumulator in the body, `return` after the loop (`calculate_total`, `count_present`, `calculate_average` like `SUM`, `COUNT`, `AVG`).
# MAGIC - Functions can call other functions: each one does just one thing.
# MAGIC - Defaults (`parameter=value`) after the parameters without defaults; keyword arguments (`name=value`) after the positional ones. The default is read when the `def` runs.
# MAGIC - Local variables: they exist only during the call. Changes to the contents of lists and dictionaries received as arguments are visible outside.
# MAGIC - Docstring between `"""` on the first line of the body, displayed by `help()`; names with a verb, in English, `is_` for true/false, `print_` for functions that print, never the names of Python's ready-made functions.
