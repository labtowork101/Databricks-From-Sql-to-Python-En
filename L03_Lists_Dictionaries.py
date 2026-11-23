# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 3 – Collections: Lists and Dictionaries
# MAGIC
# MAGIC Notebook for Chapter 3 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Create lists, read their values with indexes, and take a part of them with slicing
# MAGIC - Change a list and add values with `append()` (the first method)
# MAGIC - Use `len()`, `sum()`, `min()`, `max()`, and the `in` operator
# MAGIC - Represent a row with a dictionary and use a dictionary as a lookup table
# MAGIC - Recognize tuples and sets; copy a list with `copy()`
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–2; notebook attached to **Serverless** compute
# MAGIC - The `%sql` cells read only `samples.wanderbricks`
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: section 3.12 contains intentional and silent errors.
# MAGIC Run the **setup cell** first. Lists and dictionaries are created in the sections: each section creates the collections it uses.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Setup cell: the book's constants
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.1 Lists
# MAGIC A list is an ordered sequence of values between square brackets. Expected results: `[284.97, 213.91, 236.95]` and `<class 'list'>`.

# COMMAND ----------

base_prices = [284.97, 213.91, 236.95]
print(base_prices)
print(type(base_prices))

# COMMAND ----------

# MAGIC %md
# MAGIC Lists of text: the order stays as written, and repetitions are allowed (`"Summer Getaway"` twice).

# COMMAND ----------

property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
property_types = ["Historical Place", "Summer Getaway", "Summer Getaway"]
print(property_titles)
print(property_types)

# COMMAND ----------

# MAGIC %md
# MAGIC An empty list and a list with a missing value (`None`). Expected results: `[]` and `[3.2, None, 3.0]`.

# COMMAND ----------

flagged_properties = []
print(flagged_properties)

# COMMAND ----------

ratings_with_gap = [3.2, None, 3.0]
print(ratings_with_gap)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: a column of the result is a list. Expected result: pending 31575, confirmed 17948, cancelled 15285, completed 7439.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status, COUNT(*) AS bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC GROUP BY status
# MAGIC ORDER BY bookings DESC

# COMMAND ----------

status_names = ["pending", "confirmed", "cancelled", "completed"]
status_counts = [31575, 17948, 15285, 7439]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.2 Indexes
# MAGIC The first value has index 0. Expected results: `pending`, `confirmed`, `completed`.

# COMMAND ----------

status_names = ["pending", "confirmed", "cancelled", "completed"]
print(status_names[0])
print(status_names[1])
print(status_names[3])

# COMMAND ----------

# MAGIC %md
# MAGIC Negative indexes: `-1` is the last value. Expected results: `completed`, `cancelled`.

# COMMAND ----------

print(status_names[-1])
print(status_names[-2])

# COMMAND ----------

# MAGIC %md
# MAGIC Two aligned lists, read at the same position. Expected result: `cancelled: 15285 bookings`.

# COMMAND ----------

status_counts = [31575, 17948, 15285, 7439]
print(f"{status_names[2]}: {status_counts[2]} bookings")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.3 Slicing
# MAGIC `[start:end]`: the start is included, the end is excluded. Expected results: `['confirmed', 'cancelled']` and `[31575, 17948, 15285]`.

# COMMAND ----------

print(status_names[1:3])
print(status_counts[0:3])

# COMMAND ----------

# MAGIC %md
# MAGIC Start or end omitted: `[:3]` like `LIMIT 3`, `[2:]` up to the end, `[-2:]` the last two.

# COMMAND ----------

print(status_counts[:3])
print(status_names[2:])
print(status_names[-2:])

# COMMAND ----------

# MAGIC %md
# MAGIC Slicing beyond the limits gives no errors. Expected results: the whole list and `[]`.

# COMMAND ----------

print(status_names[:10])
print(status_names[5:])

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `LIMIT 3` returns the same statuses as `status_names[:3]`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status, COUNT(*) AS bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC GROUP BY status
# MAGIC ORDER BY bookings DESC
# MAGIC LIMIT 3

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.4 Changing a List: The First Method
# MAGIC Replacing a value by position. Expected result: `[284.97, 213.91, 249.0]`.

# COMMAND ----------

base_prices = [284.97, 213.91, 236.95]
base_prices[2] = 249.0
print(base_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC **`append()`**: the first method (value, period, name, parentheses). It adds a value at the end and is written on a line of its own. Expected results: `['Beach House in Amalfi']` and `1`.

# COMMAND ----------

flagged_properties = []
amalfi_rate = 2 / 4 * 100
if amalfi_rate > CANCELLATION_RATE_THRESHOLD:
    flagged_properties.append("Beach House in Amalfi")
print(flagged_properties)
print(len(flagged_properties))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.5 Counting, Adding Up, Finding the Minimum and Maximum
# MAGIC `len()`, `sum()`, `min()`, `max()`. Expected results: `3`, `17`, `4`, `7`.

# COMMAND ----------

bookings_2024 = [6, 7, 4]
print(len(bookings_2024))
print(sum(bookings_2024))
print(min(bookings_2024))
print(max(bookings_2024))

# COMMAND ----------

# MAGIC %md
# MAGIC The average is `sum() / len()`. Expected results: `5.666666666666667` and `5.7`.

# COMMAND ----------

average_bookings = sum(bookings_2024) / len(bookings_2024)
print(average_bookings)
print(f"Average bookings per property: {average_bookings:.1f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Lists of `float` values: the results are shown with two decimal places. Expected results: `735.83`, `245.28`, `213.91`, `284.97`.

# COMMAND ----------

base_prices = [284.97, 213.91, 236.95]
total_price = sum(base_prices)
average_price = sum(base_prices) / len(base_prices)
print(f"Sum: {total_price:.2f}")
print(f"Average: {average_price:.2f}")
print(f"Minimum: {min(base_prices)} - maximum: {max(base_prices)}")

# COMMAND ----------

# MAGIC %md
# MAGIC Total bookings and the share of canceled ones. Expected results: `72247` and `21.2%`.

# COMMAND ----------

status_counts = [31575, 17948, 15285, 7439]
total_bookings = sum(status_counts)
cancelled_share = status_counts[2] / total_bookings * 100
print(total_bookings)
print(f"Share of canceled bookings: {cancelled_share:.1f}%")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same aggregations on the three guide properties. Expected result: `3`, `735.83`, `213.91`, `284.97`, `245.28`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)                 AS property_count,
# MAGIC        ROUND(SUM(base_price), 2) AS total_price,
# MAGIC        MIN(base_price)           AS min_price,
# MAGIC        MAX(base_price)           AS max_price,
# MAGIC        ROUND(AVG(base_price), 2) AS average_price
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)

# COMMAND ----------

# MAGIC %md
# MAGIC **Lists with `None`**: `sum()` stops with `TypeError` (cell in section 3.12). In SQL, aggregations ignore `NULL`s. Expected result: `99793` and `99317`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)      AS review_count,
# MAGIC        COUNT(rating) AS rating_count
# MAGIC FROM samples.wanderbricks.reviews

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.6 The in Operator
# MAGIC `in` / `not in` check whether a value is in a list, like `IN` / `NOT IN`. Expected results: `True`, `False`, `True`.

# COMMAND ----------

active_statuses = ["confirmed", "completed"]
status = "completed"
print(status in active_statuses)
print("pending" in active_statuses)
print("pending" not in active_statuses)

# COMMAND ----------

# MAGIC %md
# MAGIC `in` after an `if`. Expected result: `16225 is a guide property`.

# COMMAND ----------

guide_property_ids = [11670, 16317, 16225]
property_id = 16225
if property_id in guide_property_ids:
    print(f"{property_id} is a guide property")

# COMMAND ----------

# MAGIC %md
# MAGIC Between two pieces of text, `in` looks for the first inside the second, like `LIKE '%Amalfi%'`. Expected results: `True`, `False`.

# COMMAND ----------

property_title = "Beach House in Amalfi"
print("Amalfi" in property_title)
print("Rome" in property_title)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: active bookings with `IN`. Expected result: `25387`, the same as the next Python cell.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS active_bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE status IN ('confirmed', 'completed')

# COMMAND ----------

status_counts = [31575, 17948, 15285, 7439]
print(status_counts[1] + status_counts[3])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.7 Dictionaries
# MAGIC A dictionary associates keys and values: a row of the `properties` table, with the column names as keys.

# COMMAND ----------

amalfi_property = {
    "property_id": 16225,
    "title": "Beach House in Amalfi",
    "destination_id": 1100,
    "property_type": "Summer Getaway",
    "base_price": 236.95,
}
print(amalfi_property)
print(type(amalfi_property))

# COMMAND ----------

# MAGIC %md
# MAGIC Reading by key; in f-strings, keys go between single quotes. A key that doesn't exist produces `KeyError` (section 3.12).

# COMMAND ----------

print(amalfi_property["title"])
print(amalfi_property["base_price"])
print(f"{amalfi_property['title']}: base price {amalfi_property['base_price']}")

# COMMAND ----------

# MAGIC %md
# MAGIC `get()` returns `None` if the key is missing. Expected results: `236.95` and `None`.

# COMMAND ----------

print(amalfi_property.get("base_price"))
print(amalfi_property.get("max_guests"))

# COMMAND ----------

# MAGIC %md
# MAGIC The same notation updates an existing key and adds a new one. Expected results: `249.0` and the dictionary with `bookings_2024`.

# COMMAND ----------

amalfi_property["base_price"] = 249.0
amalfi_property["bookings_2024"] = 4
print(amalfi_property["base_price"])
print(amalfi_property)

# COMMAND ----------

# MAGIC %md
# MAGIC `in` checks the keys; `len()` counts the pairs. Expected results: `True`, `False`, `6`, then `Rating not available`.

# COMMAND ----------

print("base_price" in amalfi_property)
print("rating" in amalfi_property)
print(len(amalfi_property))

# COMMAND ----------

if "rating" in amalfi_property:
    print(amalfi_property["rating"])
else:
    print("Rating not available")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the row that corresponds to the dictionary (with the original base price, 236.95).

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, title, destination_id, property_type, base_price
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id = 16225

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.8 The Dictionary as a Lookup Table
# MAGIC Code → name, like a `JOIN` with `destinations`. Run the cell with the `amalfi_property` dictionary (section 3.7) first. Expected results: `Amalfi` twice.

# COMMAND ----------

destination_names = {
    1100: "Amalfi",
    2300: "Florence",
    3900: "Rome",
    4200: "Sardinia",
}
print(destination_names[1100])
print(destination_names[amalfi_property["destination_id"]])

# COMMAND ----------

# MAGIC %md
# MAGIC The type of the key matters: `"1100"` isn't `1100`. Expected results: `None` and `Amalfi`.

# COMMAND ----------

print(destination_names.get("1100"))
print(destination_names.get(int("1100")))

# COMMAND ----------

# MAGIC %md
# MAGIC A missing code with `get()`. Expected result: `Destination not found`.

# COMMAND ----------

unknown_destination = destination_names.get(9999)
if unknown_destination is None:
    print("Destination not found")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the Italian destinations. Expected result: 1100 Amalfi, 2300 Florence, 3900 Rome, 4200 Sardinia.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT destination_id, destination
# MAGIC FROM samples.wanderbricks.destinations
# MAGIC WHERE country = 'Italy'
# MAGIC ORDER BY destination_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.9 Lists of Dictionaries
# MAGIC A list of dictionaries is a small table: each dictionary is a row. Expected results: `3` and the row for Rome.

# COMMAND ----------

guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]
print(len(guide_properties))
print(guide_properties[0])

# COMMAND ----------

# MAGIC %md
# MAGIC Double access: first the row, then the key. Expected results: `Beach House in Amalfi` and `2`.

# COMMAND ----------

print(guide_properties[2]["title"])
print(guide_properties[-1]["cancelled_2024"])

# COMMAND ----------

# MAGIC %md
# MAGIC A new key in a row, like a new column. `amalfi_row` and `guide_properties[2]` are the same dictionary (section 3.11). Expected results: `Beach House in Amalfi: 50.0%` and `50.0`.

# COMMAND ----------

amalfi_row = guide_properties[2]
amalfi_row["cancellation_rate"] = amalfi_row["cancelled_2024"] / amalfi_row["bookings_2024"] * 100
print(f"{amalfi_row['title']}: {amalfi_row['cancellation_rate']:.1f}%")
print(guide_properties[2]["cancellation_rate"])

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same three rows recalculated from `bookings`. Expected result: 11670 6 0 3966.21; 16225 4 2 2896.92; 16317 7 1 5139.59.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                              AS bookings_2024,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_2024,
# MAGIC        ROUND(SUM(total_amount), 2)                           AS revenue_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.10 Tuples and Sets
# MAGIC **Tuple**: a sequence between parentheses that can't be changed (error in section 3.12). Expected results: `(213.91, 284.97)`, `213.91`, `<class 'tuple'>`.

# COMMAND ----------

price_range = (213.91, 284.97)
print(price_range)
print(price_range[0])
print(type(price_range))

# COMMAND ----------

# MAGIC %md
# MAGIC A decimal written with a comma creates a tuple. Expected results: `(284, 97)` and `<class 'tuple'>`.

# COMMAND ----------

price_with_comma = 284,97
print(price_with_comma)
print(type(price_with_comma))

# COMMAND ----------

# MAGIC %md
# MAGIC **Set**: values with no repetitions and no order, like `DISTINCT`. Expected results: the two types (in any order) and `2`.

# COMMAND ----------

property_types = ["Historical Place", "Summer Getaway", "Summer Getaway"]
distinct_types = set(property_types)
print(distinct_types)
print(len(distinct_types))

# COMMAND ----------

# MAGIC %md
# MAGIC `{}` is an empty dictionary; the empty set is `set()`. Expected results: `<class 'dict'>` and `<class 'set'>`.

# COMMAND ----------

print(type({}))
print(type(set()))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `DISTINCT` on the types of the guide properties (2 rows) and `COUNT(DISTINCT)` on the whole table (`4`).

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT DISTINCT property_type
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(DISTINCT property_type) AS type_count
# MAGIC FROM samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.11 Copying a List
# MAGIC `new_prices = base_prices` doesn't copy: the two names point to the same list. Expected result: two identical lines, with `249.0`.

# COMMAND ----------

base_prices = [284.97, 213.91, 236.95]
new_prices = base_prices
new_prices[2] = 249.0
print(new_prices)
print(base_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC `copy()` creates an independent list. Expected results: `[284.97, 213.91, 249.0]` and `[284.97, 213.91, 236.95]`.

# COMMAND ----------

base_prices = [284.97, 213.91, 236.95]
new_prices = base_prices.copy()
new_prices[2] = 249.0
print(new_prices)
print(base_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3.12 Reading the Chapter's Errors
# MAGIC The following cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the name of the error and the description;
# MAGIC - the cell marked **SILENT ERROR** gives no errors but produces a wrong result;
# MAGIC - the **Fix** cell right below must work **without errors**.
# MAGIC
# MAGIC Expected results of the fixes, in order: `[284.97, 213.91, 236.95]`; `completed`; `236.95` and `None`; `6.2`; `(213.91, 300.0)` and `[213.91, 300.0]`; `Most frequent status: pending`; `[31575, 17948, 15285]`; `['Beach House in Amalfi']`; `[284.97, 213.91, 236.95]`.

# COMMAND ----------

# INTENTIONAL ERROR – a comma is missing between two values of the list
base_prices = [284.97 213.91, 236.95]

# COMMAND ----------

# Fix: a comma between each pair of values
base_prices = [284.97, 213.91, 236.95]
print(base_prices)

# COMMAND ----------

# INTENTIONAL ERROR – the list has four values: the last index is 3
status_names = ["pending", "confirmed", "cancelled", "completed"]
print(status_names[4])

# COMMAND ----------

# Fix: the last value has index -1 (or 3)
status_names = ["pending", "confirmed", "cancelled", "completed"]
print(status_names[-1])

# COMMAND ----------

# INTENTIONAL ERROR – the key is called base_price, not price
amalfi_property = {"property_id": 16225, "title": "Beach House in Amalfi", "base_price": 236.95}
print(amalfi_property["price"])

# COMMAND ----------

# Fix: the exact key; get() if the key may be missing
amalfi_property = {"property_id": 16225, "title": "Beach House in Amalfi", "base_price": 236.95}
print(amalfi_property["base_price"])
print(amalfi_property.get("price"))

# COMMAND ----------

# INTENTIONAL ERROR – sum() can't add a None value
ratings_with_gap = [3.2, None, 3.0]
print(sum(ratings_with_gap))

# COMMAND ----------

# Fix: add up only the values that are present (in Chapter 4, for lists of any length)
ratings_with_gap = [3.2, None, 3.0]
print(ratings_with_gap[0] + ratings_with_gap[2])

# COMMAND ----------

# INTENTIONAL ERROR – a tuple can't be changed
price_range = (213.91, 284.97)
price_range[1] = 300.0

# COMMAND ----------

# Fix: a new tuple, or a list, which can be changed
price_range = (213.91, 300.0)
print(price_range)
price_range = [213.91, 284.97]
price_range[1] = 300.0
print(price_range)

# COMMAND ----------

# SILENT ERROR – index 1 is the second value, not the first
status_names = ["pending", "confirmed", "cancelled", "completed"]
print(f"Most frequent status: {status_names[1]}")

# COMMAND ----------

# Fix: the first value has index 0
status_names = ["pending", "confirmed", "cancelled", "completed"]
print(f"Most frequent status: {status_names[0]}")

# COMMAND ----------

# SILENT ERROR – [0:2] takes two values, not three
status_counts = [31575, 17948, 15285, 7439]
top_three = status_counts[0:2]
print(top_three)

# COMMAND ----------

# Fix: the end is excluded; for the first three, write [:3]
status_counts = [31575, 17948, 15285, 7439]
top_three = status_counts[:3]
print(top_three)

# COMMAND ----------

# SILENT ERROR – append() changes the list and returns None
flagged_properties = []
flagged_properties = flagged_properties.append("Beach House in Amalfi")
print(flagged_properties)

# COMMAND ----------

# Fix: append() on a line of its own, without assignment
flagged_properties = []
flagged_properties.append("Beach House in Amalfi")
print(flagged_properties)

# COMMAND ----------

# SILENT ERROR – new_prices is a second name for the same list
base_prices = [284.97, 213.91, 236.95]
new_prices = base_prices
new_prices[0] = 299.0
print(base_prices)

# COMMAND ----------

# Fix: copy() creates an independent list
base_prices = [284.97, 213.91, 236.95]
new_prices = base_prices.copy()
new_prices[0] = 299.0
print(base_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - List: `[...]`, ordered, with repetitions; index from 0, `-1` for the last; `IndexError` outside the limits.
# MAGIC - Slicing `[start:end]`: end excluded; `[:3]` like `LIMIT 3`; no errors beyond the limits.
# MAGIC - `list[i] = value` replaces; `append()` (a method) adds at the end, on a line of its own.
# MAGIC - `len`, `sum`, `min`, `max` like `COUNT(*)`, `SUM`, `MIN`, `MAX`; average = `sum / len`; with `None` → `TypeError` (SQL ignores `NULL`s).
# MAGIC - `in` / `not in` like `IN` / `NOT IN`; between pieces of text like `LIKE '%...%'`.
# MAGIC - Dictionary `{key: value}` = a row; `d[key]` (`KeyError`) or `d.get(key)` (`None`); the same notation updates or adds; `in` checks the keys.
# MAGIC - Lookup dictionary like a `JOIN`; the type of the key matters.
# MAGIC - List of dictionaries = small table: `list[row][key]`.
# MAGIC - Tuple `(...)` can't be changed (watch out for `284,97`); set with no repetitions and no order, like `DISTINCT`; `{}` is a dictionary.
# MAGIC - `b = a` doesn't copy; `copy()` does.
