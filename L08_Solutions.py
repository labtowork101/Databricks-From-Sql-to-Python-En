# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 8 – Exercise Solutions
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run (exercises 6, 7, and 8 read `workspace.python_book.b_bookings`). No cell writes tables.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Text of the exercises: the `L08_Exercises` notebook and the end of Chapter 8.
# MAGIC
# MAGIC Run the setup cell first, then **one cell at a time**: exercise 8 contains cells that must fail (**INTENTIONAL ERROR**) or that produce a wrong result (**SILENT ERROR**). Don't use Run all.
# MAGIC Each exercise has a **check** cell that prints the expected result and, when possible, a `%sql` check that calculates the same result with a query: the PySpark result must match both.

# COMMAND ----------

# Setup cell: imports, constants, and values used in the exercises
from datetime import date, timedelta, datetime

SOURCE_SCHEMA = "samples.wanderbricks"
WORK_SCHEMA = "workspace.python_book"
SOURCE_BOOKINGS_TABLE = f"{SOURCE_SCHEMA}.bookings"   # original bookings
PROPERTIES_TABLE = f"{SOURCE_SCHEMA}.properties"
DESTINATIONS_TABLE = f"{SOURCE_SCHEMA}.destinations"
REVIEWS_TABLE = f"{SOURCE_SCHEMA}.reviews"
BOOKINGS_TABLE = f"{WORK_SCHEMA}.b_bookings"           # teaching copy with anomalies (Chapter 0)

ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
GUIDE_PROPERTY_IDS = [11670, 16317, 16225]
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]


def classify_cancellation_rate(rate, threshold=CANCELLATION_RATE_THRESHOLD):
    """Classifies a cancellation rate (in %) into four states, as in Chapter 5."""
    if rate is None:
        return "missing data"
    if rate < 0 or rate > 100:
        return "impossible value"
    if rate > threshold:
        return "critical"
    return "ok"


print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – Counting with spark.sql
# MAGIC 1. With `spark.sql()` and an f-string that uses the constants `PROPERTIES_TABLE`, `DESTINATIONS_TABLE`, and `REVIEWS_TABLE`, prepare the DataFrames `properties_df`, `destinations_df`, and `reviews_df` with all the rows of the three tables.
# MAGIC 2. Count the rows of the three DataFrames with `count()` and print the three numbers on the same line.
# MAGIC 3. Print `Properties per destination: ...`, the average number of properties per destination, with one decimal place.

# COMMAND ----------

# Solution 1: three DataFrames, three counts, a division between ints
properties_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
destinations_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE}")
reviews_df = spark.sql(f"SELECT * FROM {REVIEWS_TABLE}")

properties_count = properties_df.count()
destinations_count = destinations_df.count()
reviews_count = reviews_df.count()
print(properties_count, destinations_count, reviews_count)
print(f"Properties per destination: {properties_count / destinations_count:.1f}")

# COMMAND ----------

# Check: expected result
print(18163, 42, 99793)
print("Properties per destination: 432.5")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 18163, 42, 99793
# MAGIC SELECT (SELECT COUNT(*) FROM samples.wanderbricks.properties)    AS properties_count,
# MAGIC        (SELECT COUNT(*) FROM samples.wanderbricks.destinations)  AS destinations_count,
# MAGIC        (SELECT COUNT(*) FROM samples.wanderbricks.reviews)       AS reviews_count

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – The Structure of a Table
# MAGIC 1. Print the schema of `properties_df` with `printSchema()`.
# MAGIC 2. Print the number of columns, calculated with `columns`.
# MAGIC 3. Print on the same line whether `"base_price"` and `"price"` are among the columns (`in` operator).

# COMMAND ----------

# Solution 2: schema, number of columns, check with in
properties_df.printSchema()
print(len(properties_df.columns))
print("base_price" in properties_df.columns, "price" in properties_df.columns)

# COMMAND ----------

# Check: expected result
print("Schema: 13 lines, including |-- property_id: long (nullable = false) and |-- base_price: float (nullable = true)")
print(13)
print(True, False)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 13 rows, one per column
# MAGIC DESCRIBE TABLE samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – select and distinct
# MAGIC 1. Count the distinct countries of `destinations_df` (`country` column).
# MAGIC 2. Show with `show(truncate=False)` the `destination_id` and `destination` columns of the Italian destinations (`country` equal to `"Italy"`), sorted by name.
# MAGIC 3. Show with `show()` the distinct property types of `properties_df`, in alphabetical order.

# COMMAND ----------

# Solution 3: distinct, filter with sorting, sorted distinct values
print(destinations_df.select("country").distinct().count())

(
    destinations_df
    .filter(destinations_df["country"] == "Italy")
    .select("destination_id", "destination")
    .orderBy("destination")
    .show(truncate=False)
)

properties_df.select("property_type").distinct().orderBy("property_type").show()

# COMMAND ----------

# Check: expected result
print(18)
print("1100 Amalfi, 2300 Florence, 3900 Rome, 4200 Sardinia")
print("Historical Place, Ski Resort, Summer Getaway, Urban Year-Round")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: distinct countries (18) and property types in alphabetical order
# MAGIC SELECT COUNT(DISTINCT country) AS countries FROM samples.wanderbricks.destinations

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT DISTINCT property_type
# MAGIC FROM samples.wanderbricks.properties
# MAGIC ORDER BY property_type

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Two Forms of filter
# MAGIC 1. Count the `Summer Getaway` properties with the text form and with the column form; print the two counts on the same line.
# MAGIC 2. With the variable `chosen_type = "Urban Year-Round"`, count the properties of that type in the two forms (in the text form, with an f-string).
# MAGIC 3. On `reviews_df`, count in the column form the reviews with a missing `rating`, those with `is_deleted` equal to `True`, and those with both conditions; print the three counts on the same line.

# COMMAND ----------

# Solution 4: text form and column form, conditions with &
print(
    properties_df.filter("property_type = 'Summer Getaway'").count(),
    properties_df.filter(properties_df["property_type"] == "Summer Getaway").count(),
)

chosen_type = "Urban Year-Round"
print(
    properties_df.filter(f"property_type = '{chosen_type}'").count(),
    properties_df.filter(properties_df["property_type"] == chosen_type).count(),
)

missing_rating_count = reviews_df.filter(reviews_df["rating"].isNull()).count()
deleted_count = reviews_df.filter(reviews_df["is_deleted"] == True).count()
both_count = reviews_df.filter(
    (reviews_df["rating"].isNull())
    & (reviews_df["is_deleted"] == True)
).count()
print(missing_rating_count, deleted_count, both_count)

# COMMAND ----------

# Check: expected result
print(7068, 7068)
print(9264, 9264)
print(476, 476, 476)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 7068, 9264, 476, 476, 476
# MAGIC SELECT (SELECT COUNT(*) FROM samples.wanderbricks.properties WHERE property_type = 'Summer Getaway')   AS summer_count,
# MAGIC        (SELECT COUNT(*) FROM samples.wanderbricks.properties WHERE property_type = 'Urban Year-Round') AS urban_count,
# MAGIC        (SELECT COUNT(*) FROM samples.wanderbricks.reviews WHERE rating IS NULL)                         AS missing_rating,
# MAGIC        (SELECT COUNT(*) FROM samples.wanderbricks.reviews WHERE is_deleted = true)                      AS deleted_reviews,
# MAGIC        (SELECT COUNT(*) FROM samples.wanderbricks.reviews WHERE rating IS NULL AND is_deleted = true)   AS both_conditions

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – The Other Guide Properties
# MAGIC 1. Prepare `bookings_df` with all the rows of `SOURCE_BOOKINGS_TABLE`.
# MAGIC 2. Define the function `print_guide_rate(property_id)`, with a docstring, that filters the bookings of the property with check-in in `ANALYSIS_YEAR` (column form, `&`, and Python dates), counts the bookings and the canceled ones, calculates the rate and the status with `classify_cancellation_rate`, and prints `property_id: N bookings, N canceled, rate X.X% (status)`.
# MAGIC 3. Call the function for Rome (11670) and for Sardinia (16317).

# COMMAND ----------

# Solution 5: a function with the filter and the two counts
bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")


def print_guide_rate(property_id):
    """Prints bookings, cancellations, rate, and status of a property in the analysis year."""
    property_df = bookings_df.filter(
        (bookings_df["property_id"] == property_id)
        & (bookings_df["check_in"] >= date(ANALYSIS_YEAR, 1, 1))
        & (bookings_df["check_in"] <= date(ANALYSIS_YEAR, 12, 31))
    )
    booking_total = property_df.count()
    cancelled_total = property_df.filter(property_df["status"] == "cancelled").count()
    rate = cancelled_total / booking_total * 100
    status = classify_cancellation_rate(rate)
    print(f"{property_id}: {booking_total} bookings, {cancelled_total} canceled, rate {rate:.1f}% ({status})")


print_guide_rate(11670)
print_guide_rate(16317)

# COMMAND ----------

# Check: expected result
print("11670: 6 bookings, 0 canceled, rate 0.0% (ok)")
print("16317: 7 bookings, 1 canceled, rate 14.3% (ok)")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 11670 6 0; 16317 7 1
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                              AS bookings_2024,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – The Profile of the Teaching Copy
# MAGIC 1. Prepare `teaching_bookings_df` with all the rows of `BOOKINGS_TABLE`.
# MAGIC 2. Collect six counts in a dictionary `profile`, with these keys: `"rows"`, `"distinct rows"`, `"missing amounts"`, `"negative amounts"`, `"swapped dates"` (check-out before check-in), `"missing or negative amounts"`.
# MAGIC 3. With a loop over `profile.items()`, print one `key value` line per check.

# COMMAND ----------

# Solution 6: a dictionary of counts and a loop over items()
teaching_bookings_df = spark.sql(f"SELECT * FROM {BOOKINGS_TABLE}")
amount = teaching_bookings_df["total_amount"]

profile = {
    "rows": teaching_bookings_df.count(),
    "distinct rows": teaching_bookings_df.distinct().count(),
    "missing amounts": teaching_bookings_df.filter(amount.isNull()).count(),
    "negative amounts": teaching_bookings_df.filter(amount < 0).count(),
    "swapped dates": teaching_bookings_df.filter(
        teaching_bookings_df["check_out"] < teaching_bookings_df["check_in"]
    ).count(),
    "missing or negative amounts": teaching_bookings_df.filter((amount.isNull()) | (amount < 0)).count(),
}
for check_name, value in profile.items():
    print(check_name, value)

# COMMAND ----------

# Check: expected result
print("rows 72287")
print("distinct rows 72247")
print("missing amounts 30")
print("negative amounts 13")
print("swapped dates 8")
print("missing or negative amounts 43")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 72287, 72247, 30, 13, 8, 43
# MAGIC SELECT COUNT(*)                                                         AS row_count,
# MAGIC        (SELECT COUNT(*) FROM (SELECT DISTINCT * FROM workspace.python_book.b_bookings)) AS distinct_rows,
# MAGIC        SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END)            AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END)                AS negative_amounts,
# MAGIC        SUM(CASE WHEN check_out < check_in THEN 1 ELSE 0 END)            AS inverted_dates,
# MAGIC        SUM(CASE WHEN total_amount IS NULL OR total_amount < 0 THEN 1 ELSE 0 END) AS amount_problems
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Revenue from the Teaching Copy
# MAGIC The bookings of the guide properties aren't among those modified in `b_bookings` (Chapter 0), but the amounts in the copy are rounded row by row: let's check that the 2024 revenue stays the same as the values written by hand.
# MAGIC 1. For each row of `guide_properties`, filter `teaching_bookings_df` (property and check-in in 2024), bring only the `total_amount` column into Python with `collect()`, and add it up with an accumulator.
# MAGIC 2. Append to a list `revenue_checks` a dictionary with `property_id`, `title`, `revenue_from_table` (rounded to 2 decimal places), `revenue_written` (the value from `guide_properties`), and `same_value` (`True` if the two values match).
# MAGIC 3. Turn the list into a DataFrame with `spark.createDataFrame()`, arrange the columns in the order of step 2 with `select()`, and show it with `display()` in descending order of `revenue_from_table`.

# COMMAND ----------

# Solution 7: collect() and accumulator, then a DataFrame again
revenue_checks = []
for guide in guide_properties:
    amount_rows = (
        teaching_bookings_df
        .filter(
            (teaching_bookings_df["property_id"] == guide["property_id"])
            & (teaching_bookings_df["check_in"] >= date(ANALYSIS_YEAR, 1, 1))
            & (teaching_bookings_df["check_in"] <= date(ANALYSIS_YEAR, 12, 31))
        )
        .select("total_amount")
        .collect()
    )
    revenue_total = 0
    for row in amount_rows:
        revenue_total = revenue_total + row["total_amount"]
    revenue_from_table = round(revenue_total, 2)
    revenue_checks.append({
        "property_id": guide["property_id"],
        "title": guide["title"],
        "revenue_from_table": revenue_from_table,
        "revenue_written": guide["revenue_2024"],
        "same_value": revenue_from_table == guide["revenue_2024"],
    })

checks_df = (
    spark.createDataFrame(revenue_checks)
    .select("property_id", "title", "revenue_from_table", "revenue_written", "same_value")
    .orderBy("revenue_from_table", ascending=False)
)
display(checks_df)

# COMMAND ----------

# Check: expected result (grid)
print("property_id  title                  revenue_from_table  revenue_written  same_value")
print("16317        Bungalow in Sardinia   5139.59             5139.59          true")
print("11670        Historic Inn in Rome   3966.21             3966.21          true")
print("16225        Beach House in Amalfi  2896.92             2896.92          true")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 2024 revenue from the teaching copy (5139.59, 3966.21, 2896.92)
# MAGIC SELECT property_id,
# MAGIC        ROUND(SUM(total_amount), 2) AS revenue_2024
# MAGIC FROM workspace.python_book.b_bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY revenue_2024 DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one at a time, note the type of the error and the message (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `18163`; `4`; `4`; `42`; `30`; `7068`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (the properties)
properties_df = spark.sql("SELECT * FROM samples.wanderbricks.propertie")
print(properties_df.count())

# COMMAND ----------

# Fix 8a (error type: TABLE_OR_VIEW_NOT_FOUND, the table is called properties)
properties_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
print(properties_df.count())

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b (the destinations of one country)
country = "Italy"
italy_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE} WHERE country = {country}")
print(italy_df.count())

# COMMAND ----------

# Fix 8b (error type: UNRESOLVED_COLUMN, Italy without quotes becomes the name of a column)
country = "Italy"
italy_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE} WHERE country = '{country}'")
print(italy_df.count())

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c (the 2024 bookings of the Amalfi property)
bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
amalfi_df = bookings_df.filter(
    (bookings_df["property_id"] == 16225)
    and (bookings_df["check_in"] >= date(ANALYSIS_YEAR, 1, 1))
    and (bookings_df["check_in"] <= date(ANALYSIS_YEAR, 12, 31))
)
print(amalfi_df.count())

# COMMAND ----------

# Fix 8c (error type: CANNOT_CONVERT_COLUMN_INTO_BOOL, and instead of &)
bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
amalfi_df = bookings_df.filter(
    (bookings_df["property_id"] == 16225)
    & (bookings_df["check_in"] >= date(ANALYSIS_YEAR, 1, 1))
    & (bookings_df["check_in"] <= date(ANALYSIS_YEAR, 12, 31))
)
print(amalfi_df.count())

# COMMAND ----------

# INTENTIONAL ERROR – cell 8d (how many destinations)
destinations_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE}").show(3)
print(destinations_df.count())

# COMMAND ----------

# Fix 8d (error type: AttributeError, show() returns None)
destinations_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE}")
destinations_df.show(3)
print(destinations_df.count())

# COMMAND ----------

# SILENT ERROR – cell 8e (the missing amounts in the teaching copy)
teaching_bookings_df = spark.sql(f"SELECT * FROM {BOOKINGS_TABLE}")
print(teaching_bookings_df.filter(teaching_bookings_df["total_amount"] == None).count())

# COMMAND ----------

# Fix 8e (what's wrong: == None is never true; nulls are found with isNull())
teaching_bookings_df = spark.sql(f"SELECT * FROM {BOOKINGS_TABLE}")
print(teaching_bookings_df.filter(teaching_bookings_df["total_amount"].isNull()).count())

# COMMAND ----------

# SILENT ERROR – cell 8f (the Summer Getaway properties)
summer_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
summer_df.filter(summer_df["property_type"] == "Summer Getaway")
print(summer_df.count())

# COMMAND ----------

# Fix 8f (what's wrong: the result of filter() wasn't assigned)
summer_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
summer_df = summer_df.filter(summer_df["property_type"] == "Summer Getaway")
print(summer_df.count())
