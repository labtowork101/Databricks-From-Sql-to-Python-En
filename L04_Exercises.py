# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 4 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**. Exercises 2, 3, 5, and 7 have a `%sql` check on `samples.wanderbricks`; exercise 4 on `workspace.python_book.b_bookings` (created by `L00_Prepare_Data`).
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L04_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L04_Exercises_done`). Run the setup cell first, then one cell at a time (exercise 8 contains intentional errors).
# MAGIC Each exercise has a **check** cell that prints the expected result, to compare with your own output.
# MAGIC The exercises ask you to use loops even where a ready-made function (`sum()`, `len()`) would give the same result: the goal is to practice with accumulators.
# MAGIC
# MAGIC | property_id | title | base_price | 2024 Bookings | Canceled | 2024 Revenue |
# MAGIC |---|---|---|---|---|---|
# MAGIC | 11670 | Historic Inn in Rome | 284.97 | 6 | 0 | 3966.21 |
# MAGIC | 16317 | Bungalow in Sardinia | 213.91 | 7 | 1 | 5139.59 |
# MAGIC | 16225 | Beach House in Amalfi | 236.95 | 4 | 2 | 2896.92 |

# COMMAND ----------

# Setup cell: constants and collections used in the exercises
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]
bookings_2024 = [6, 7, 4]

# The guide properties as a small table (Chapter 3)
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – A Loop over the Bookings
# MAGIC With the lists in the cell below:
# MAGIC 1. with a loop, print one line for each bookings value (`Bookings: 6`);
# MAGIC 2. with a second loop and three accumulators, calculate the number of properties (with a counter), the total bookings, and the total revenue;
# MAGIC 3. calculate the average revenue per booking; print the results with two decimal places where needed.

# COMMAND ----------

bookings_2024 = [6, 7, 4]
revenues_2024 = [3966.21, 5139.59, 2896.92]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Bookings: 6")
print("Bookings: 7")
print("Bookings: 4")
print("Properties: 3 - bookings: 17")
print("Total revenue: 12002.72")
print("Average revenue per booking: 706.04")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Nights and Positions with range()
# MAGIC 1. Print with `list()` and `range()` the possible nights of a booking, from 1 to 9, and how many there are (`Possible nights: 9`).
# MAGIC 2. With a loop over `range()` with step 2, print the cost of 1, 3, 5, 7, and 9 nights at the base price of the Amalfi property, 236.95, with two decimal places (`nights: 1 - cost: 236.95`).
# MAGIC 3. With `range(len(property_titles))`, print the titles of the guide properties numbered from 1 (`1 - Historic Inn in Rome`).

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print([1, 2, 3, 4, 5, 6, 7, 8, 9])
print("Possible nights: 9")
print("nights: 1 - cost: 236.95")
print("nights: 3 - cost: 710.85")
print("nights: 5 - cost: 1184.75")
print("nights: 7 - cost: 1658.65")
print("nights: 9 - cost: 2132.55")
print("1 - Historic Inn in Rome")
print("2 - Bungalow in Sardinia")
print("3 - Beach House in Amalfi")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: cost of 1, 3, 5, 7, 9 nights at the base price of the Amalfi property
# MAGIC SELECT id AS nights, ROUND(id * 236.95, 2) AS cost
# MAGIC FROM range(1, 10, 2)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Property Types in a Dictionary
# MAGIC With the `type_counts_by_name` dictionary (cell below):
# MAGIC 1. calculate the total number of properties with `values()` and an accumulator;
# MAGIC 2. with `items()`, print the count and the share with one decimal place for each type (`Urban Year-Round: 9264 (51.0%)`);
# MAGIC 3. build with a loop the list of the types with more than 5000 properties.

# COMMAND ----------

type_counts_by_name = {
    "Urban Year-Round": 9264,
    "Summer Getaway": 7068,
    "Historical Place": 1646,
    "Ski Resort": 185,
}

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Total properties: 18163")
print("Urban Year-Round: 9264 (51.0%)")
print("Summer Getaway: 7068 (38.9%)")
print("Historical Place: 1646 (9.1%)")
print("Ski Resort: 185 (1.0%)")
print(['Urban Year-Round', 'Summer Getaway'])

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: properties and shares by type (51.0, 38.9, 9.1, 1.0)
# MAGIC SELECT property_type,
# MAGIC        COUNT(*)                           AS property_count,
# MAGIC        ROUND(COUNT(*) * 100.0 / 18163, 1) AS share
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY property_type
# MAGIC ORDER BY property_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – A Sample of Amounts with Anomalies
# MAGIC With the `amounts_sample` list (cell below) and **a single loop**:
# MAGIC 1. count the missing amounts, the negative amounts, and the valid amounts;
# MAGIC 2. collect the negative amounts in a list;
# MAGIC 3. add up the valid amounts only.
# MAGIC
# MAGIC After the loop, calculate the average of the valid amounts. Hint: the check on `None` comes first.

# COMMAND ----------

amounts_sample = [512.4, -80.0, None, 1250.75, 333.3, None, -15.5, 968.1]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Missing: 2 - negative: 2 - valid: 4")
print("Negative amounts: [-80.0, -15.5]")
print("Valid total: 3064.55")
print("Valid average: 766.14")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same classification on the whole b_bookings teaching copy (30 nulls, 13 negatives)
# MAGIC SELECT COUNT(*) - COUNT(total_amount)                    AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – Price Bands for Each Row
# MAGIC With the `guide_rows` list of dictionaries (cell below), with a loop:
# MAGIC 1. add to each row the `price_band` key (`"high"` from 250 up, `"medium"` from 200 up, `"low"` below 200);
# MAGIC 2. add to each row the `revenue_per_booking` key (revenue divided by bookings);
# MAGIC 3. print one line per property in the format `Historic Inn in Rome: high - 661.03 per booking`.
# MAGIC
# MAGIC Finally, with a second loop, build the list of the titles in the `"medium"` band.

# COMMAND ----------

guide_rows = [
    {"title": "Historic Inn in Rome", "base_price": 284.97, "bookings_2024": 6, "revenue_2024": 3966.21},
    {"title": "Bungalow in Sardinia", "base_price": 213.91, "bookings_2024": 7, "revenue_2024": 5139.59},
    {"title": "Beach House in Amalfi", "base_price": 236.95, "bookings_2024": 4, "revenue_2024": 2896.92},
]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Historic Inn in Rome: high - 661.03 per booking")
print("Bungalow in Sardinia: medium - 734.23 per booking")
print("Beach House in Amalfi: medium - 724.23 per booking")
print(['Bungalow in Sardinia', 'Beach House in Amalfi'])

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: price bands of the guide properties (high, medium, medium)
# MAGIC SELECT property_id, title, base_price,
# MAGIC        CASE WHEN base_price >= 250 THEN 'high'
# MAGIC             WHEN base_price >= 200 THEN 'medium'
# MAGIC             ELSE 'low'
# MAGIC        END AS price_band
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – How Many Years Does It Take?
# MAGIC The base price of the property in Sardinia, 213.91, grows by 8% a year.
# MAGIC 1. With a `while` loop, calculate after how many years it exceeds the base price of the property in Rome, 284.97, and what price it reaches.
# MAGIC 2. Repeat the calculation with a growth of 3%.
# MAGIC 3. Rewrite the first calculation with a `for` over `range(1, 21)` and `break`.
# MAGIC
# MAGIC Watch out: if the cell doesn't end, stop it with **Interrupt** and check that the block updates the price.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("8%: 4 years - price 291.02")
print("3%: 10 years - price 287.48")
print("With for and break: 4 years - price 291.02")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Counting by Category
# MAGIC With the `sample_statuses` list of ten statuses (cell below):
# MAGIC 1. build with a loop the `status_counts` dictionary with the number of bookings per status: start from an empty dictionary and, for each status, use `in` to find out whether it's already among the keys (if so, increase the count; otherwise, add the key with value 1); print the dictionary;
# MAGIC 2. with `items()`, calculate the total and the cancellation rate of the sample, and classify it with `CANCELLATION_RATE_THRESHOLD` (`"critical"` if it exceeds it, otherwise `"ok"`);
# MAGIC 3. with `range(len(sample_statuses))` and `break`, find the position of the first `"completed"` booking.

# COMMAND ----------

sample_statuses = ["confirmed", "cancelled", "pending", "pending", "completed", "cancelled", "pending", "confirmed", "cancelled", "pending"]

# Write your solution here


# COMMAND ----------

# Check: expected result
print({'confirmed': 2, 'cancelled': 3, 'pending': 4, 'completed': 1})
print("Total: 10")
print("Sample cancellation rate: 30.0% (ok)")
print("First completed booking at position: 4")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same count by status, done by GROUP BY on the whole table
# MAGIC SELECT status, COUNT(*) AS bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC GROUP BY status
# MAGIC ORDER BY bookings DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one by one, note the name of the error (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: the three titles; `17`; the three titles; `17`; `Canceled: 2`; the years from 2022 to 2025.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
for title in property_titles
    print(title)

# COMMAND ----------

# Fix 8a (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
        print(total_bookings)

# COMMAND ----------

# Fix 8b (error name: ...; print the total only once, after the loop)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
for position in len(property_titles):
    print(property_titles[position])

# COMMAND ----------

# Fix 8c (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
total_bookings = 0
for row in guide_properties:
    total_bookings = total_bookings + row["Bookings_2024"]
print(total_bookings)

# COMMAND ----------

# Fix 8d (error name: ...)


# COMMAND ----------

# SILENT ERROR – cell 8e (canceled bookings in the sample)
sample_statuses = ["confirmed", "cancelled", "pending", "completed", "cancelled", "pending"]
for status in sample_statuses:
    cancelled_count = 0
    if status == "cancelled":
        cancelled_count = cancelled_count + 1
print(f"Canceled: {cancelled_count}")

# COMMAND ----------

# Fix 8e (what's wrong: ...)


# COMMAND ----------

# SILENT ERROR – cell 8f (years from 2022 to 2025)
for year in range(2022, 2025):
    print(year)

# COMMAND ----------

# Fix 8f (what's wrong: ...)

