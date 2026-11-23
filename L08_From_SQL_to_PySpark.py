# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 8 – From SQL to PySpark
# MAGIC
# MAGIC Notebook for Chapter 8 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Run SQL queries from Python with `spark.sql()`, including with f-strings
# MAGIC - Understand the DataFrame as a recipe: operations that prepare, and actions (`display`, `show`, `count`, `collect`)
# MAGIC - Look at a DataFrame with `display()`, `show()`, `printSchema()`, `columns`
# MAGIC - Use `select`, `distinct`, `filter`, `orderBy`, `limit` in place of the SQL clauses
# MAGIC - Bring small results into Python with `collect()` and go back to Spark with `spark.createDataFrame()`
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–7; notebook attached to **Serverless** compute
# MAGIC - `L00_Prepare_Data` already run (sections 8.7–8.8 read `workspace.python_book.b_bookings`); no cell writes tables
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter, **from top to bottom**. **Don't use Run all**: some cells contain intentional errors.
# MAGIC Run the **setup cell** first. The cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the type, the message, and the line;
# MAGIC - the cell marked **SILENT ERROR** gives no error but produces a wrong result;
# MAGIC - the **Fix** cell below must work **without errors**, with the result indicated.
# MAGIC
# MAGIC For Spark errors (name in square brackets and `SQLSTATE`), read the **summary line**; in the traceback, look for the line of the cell and skip the blocks of the PySpark library.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Setup cell: imports, constants, and values used in the sections
from datetime import date, timedelta, datetime

# Schemas and tables: samples is read-only, workspace.python_book is the working schema
SOURCE_SCHEMA = "samples.wanderbricks"
WORK_SCHEMA = "workspace.python_book"
SOURCE_BOOKINGS_TABLE = f"{SOURCE_SCHEMA}.bookings"   # original bookings
PROPERTIES_TABLE = f"{SOURCE_SCHEMA}.properties"
DESTINATIONS_TABLE = f"{SOURCE_SCHEMA}.destinations"
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
# MAGIC ## 8.1 Spark and the spark Variable

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `<class 'pyspark.sql.connect.session.SparkSession'>`.

# COMMAND ----------

print(type(spark))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `DataFrame[bookings_count: bigint]`.

# COMMAND ----------

spark.sql("SELECT COUNT(*) AS bookings_count FROM samples.wanderbricks.bookings")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC bookings_count
# MAGIC 72247
# MAGIC ```

# COMMAND ----------

display(spark.sql("SELECT COUNT(*) AS bookings_count FROM samples.wanderbricks.bookings"))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC bookings_count
# MAGIC 72247
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS bookings_count
# MAGIC FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.2 The Query as Text: Triple Quotes and f-Strings

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC cancelled_count
# MAGIC 15285
# MAGIC ```

# COMMAND ----------

query = """
SELECT COUNT(*) AS cancelled_count
FROM samples.wanderbricks.bookings
WHERE status = 'cancelled'
"""
display(spark.sql(query))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC
# MAGIC SELECT COUNT(*) AS bookings_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id = 16225
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC
# MAGIC
# MAGIC bookings_2024
# MAGIC 4
# MAGIC ```

# COMMAND ----------

property_id = 16225
query = f"""
SELECT COUNT(*) AS bookings_2024
FROM {SOURCE_BOOKINGS_TABLE}
WHERE property_id = {property_id}
  AND check_in BETWEEN '{ANALYSIS_YEAR}-01-01' AND '{ANALYSIS_YEAR}-12-31'
"""
print(query)
display(spark.sql(query))

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the text value is inserted without quotes).

# COMMAND ----------

# INTENTIONAL ERROR – the text value is inserted without quotes
city = "Amalfi"
query = f"SELECT destination_id, destination FROM {DESTINATIONS_TABLE} WHERE destination = {city}"
display(spark.sql(query))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the quotes around the braces. Expected result: one row, `1100 Amalfi`.

# COMMAND ----------

# Fix: text goes between quotes in the f-string too
city = "Amalfi"
query = f"SELECT destination_id, destination FROM {DESTINATIONS_TABLE} WHERE destination = '{city}'"
display(spark.sql(query))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.3 The DataFrame: Recipe and Dish

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC DataFrame[booking_id: bigint, user_id: bigint, property_id: bigint, check_in: date, check_out: date, guests_count: int, total_amount: float, status: string, created_at: timestamp, updated_at: timestamp]
# MAGIC ```

# COMMAND ----------

bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
bookings_df

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `<class 'pyspark.sql.connect.dataframe.DataFrame'>`.

# COMMAND ----------

print(type(bookings_df))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 72247
# MAGIC <class 'int'>
# MAGIC ```

# COMMAND ----------

bookings_count = bookings_df.count()
print(bookings_count)
print(type(bookings_count))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Canceled: 15285 of 72247 (21.2%)
# MAGIC ok
# MAGIC ```

# COMMAND ----------

cancelled_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE} WHERE status = 'cancelled'")
cancelled_count = cancelled_df.count()
cancellation_rate = cancelled_count / bookings_count * 100
print(f"Canceled: {cancelled_count} of {bookings_count} ({cancellation_rate:.1f}%)")
print(classify_cancellation_rate(cancellation_rate))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC ['booking_id', 'user_id', 'property_id', 'check_in', 'check_out', 'guests_count', 'total_amount', 'status', 'created_at', 'updated_at']
# MAGIC 10
# MAGIC ```

# COMMAND ----------

print(bookings_df.columns)
print(len(bookings_df.columns))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.4 Looking at the Data: display, show, and printSchema

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination_id  destination  country
# MAGIC 1100            Amalfi       Italy
# MAGIC 2300            Florence     Italy
# MAGIC 3900            Rome         Italy
# MAGIC 4200            Sardinia     Italy
# MAGIC ```

# COMMAND ----------

italy_df = spark.sql(f"""
SELECT destination_id, destination, country
FROM {DESTINATIONS_TABLE}
WHERE country = 'Italy'
ORDER BY destination_id
""")
display(italy_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC +--------------+-----------+-------+
# MAGIC |destination_id|destination|country|
# MAGIC +--------------+-----------+-------+
# MAGIC |          1100|     Amalfi|  Italy|
# MAGIC |          2300|   Florence|  Italy|
# MAGIC |          3900|       Rome|  Italy|
# MAGIC |          4200|   Sardinia|  Italy|
# MAGIC +--------------+-----------+-------+
# MAGIC ```

# COMMAND ----------

italy_df.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC +-----------+--------------------+----------+
# MAGIC |property_id|               title|base_price|
# MAGIC +-----------+--------------------+----------+
# MAGIC |      11670|Historic Inn in Rome|    284.97|
# MAGIC |      16225|Beach House in Am...|    236.95|
# MAGIC |      16317|Bungalow in Sardinia|    213.91|
# MAGIC +-----------+--------------------+----------+
# MAGIC
# MAGIC +-----------+---------------------+----------+
# MAGIC |property_id|title                |base_price|
# MAGIC +-----------+---------------------+----------+
# MAGIC |11670      |Historic Inn in Rome |284.97    |
# MAGIC |16225      |Beach House in Amalfi|236.95    |
# MAGIC |16317      |Bungalow in Sardinia |213.91    |
# MAGIC +-----------+---------------------+----------+
# MAGIC ```

# COMMAND ----------

guide_titles_df = spark.sql(f"""
SELECT property_id, title, base_price
FROM {PROPERTIES_TABLE}
WHERE property_id IN (11670, 16317, 16225)
ORDER BY property_id
""")
guide_titles_df.show()
guide_titles_df.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC +--------------+-----------+-------+
# MAGIC |destination_id|destination|country|
# MAGIC +--------------+-----------+-------+
# MAGIC |          1100|     Amalfi|  Italy|
# MAGIC +--------------+-----------+-------+
# MAGIC only showing top 1 row
# MAGIC None
# MAGIC ```

# COMMAND ----------

result = italy_df.show(1)
print(result)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC root
# MAGIC  |-- booking_id: long (nullable = false)
# MAGIC  |-- user_id: long (nullable = true)
# MAGIC  |-- property_id: long (nullable = true)
# MAGIC  |-- check_in: date (nullable = true)
# MAGIC  |-- check_out: date (nullable = true)
# MAGIC  |-- guests_count: integer (nullable = true)
# MAGIC  |-- total_amount: float (nullable = true)
# MAGIC  |-- status: string (nullable = true)
# MAGIC  |-- created_at: timestamp (nullable = true)
# MAGIC  |-- updated_at: timestamp (nullable = true)
# MAGIC ```

# COMMAND ----------

bookings_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.5 Choosing Columns: select and distinct

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `18163 42`.

# COMMAND ----------

bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
properties_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
destinations_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE}")
print(properties_df.count(), destinations_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, title, property_type, base_price
# MAGIC FROM samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `['property_id', 'title', 'property_type', 'base_price']`.

# COMMAND ----------

property_prices_df = properties_df.select("property_id", "title", "property_type", "base_price")
print(property_prices_df.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Column<'base_price'>
# MAGIC <class 'pyspark.sql.connect.column.Column'>
# MAGIC ```

# COMMAND ----------

print(properties_df["base_price"])
print(type(properties_df["base_price"]))

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the column is called base_price, not price).

# COMMAND ----------

# INTENTIONAL ERROR – the column is called base_price, not price
prices_df = properties_df.select("property_id", "price")
display(prices_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the correct column name. Expected result: `['property_id', 'base_price']`.

# COMMAND ----------

# Fix: the column is called base_price
prices_df = properties_df.select("property_id", "base_price")
print(prices_df.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_type
# MAGIC Historical Place
# MAGIC Urban Year-Round
# MAGIC Summer Getaway
# MAGIC Ski Resort
# MAGIC
# MAGIC 4
# MAGIC ```

# COMMAND ----------

property_types_df = properties_df.select("property_type").distinct()
display(property_types_df)
print(property_types_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC property_types  countries
# MAGIC 4               18
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(DISTINCT property_type) AS property_types,
# MAGIC        (SELECT COUNT(DISTINCT country) FROM samples.wanderbricks.destinations) AS countries
# MAGIC FROM samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.6 Filtering Rows: filter and where

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `185`.

# COMMAND ----------

ski_df = properties_df.filter("property_type = 'Ski Resort'")
print(ski_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `185`.

# COMMAND ----------

ski_df = properties_df.filter(properties_df["property_type"] == "Ski Resort")
print(ski_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `Column<'==(property_type, Ski Resort)'>`.

# COMMAND ----------

print(properties_df["property_type"] == "Ski Resort")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `1646 1646`.

# COMMAND ----------

chosen_type = "Historical Place"
text_df = properties_df.filter(f"property_type = '{chosen_type}'")
column_df = properties_df.filter(properties_df["property_type"] == chosen_type)
print(text_df.count(), column_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC historical_count
# MAGIC 1646
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS historical_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_type = 'Historical Place'

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 15285
# MAGIC 40672
# MAGIC 0
# MAGIC ```

# COMMAND ----------

print(bookings_df.filter(bookings_df["status"] == "cancelled").count())
print(bookings_df.filter(bookings_df["status"] != "pending").count())
print(bookings_df.filter(bookings_df["check_in"] > date(2025, 7, 30)).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.7 Multiple Conditions and Null Values

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 2024 bookings: 4 - canceled: 2 - rate: 50.0%
# MAGIC critical
# MAGIC ```

# COMMAND ----------

amalfi_2024_df = bookings_df.filter(
    (bookings_df["property_id"] == 16225)
    & (bookings_df["check_in"] >= date(ANALYSIS_YEAR, 1, 1))
    & (bookings_df["check_in"] <= date(ANALYSIS_YEAR, 12, 31))
)
amalfi_bookings = amalfi_2024_df.count()
amalfi_cancelled = amalfi_2024_df.filter(amalfi_2024_df["status"] == "cancelled").count()
amalfi_rate = amalfi_cancelled / amalfi_bookings * 100
print(f"2024 bookings: {amalfi_bookings} - canceled: {amalfi_cancelled} - rate: {amalfi_rate:.1f}%")
print(classify_cancellation_rate(amalfi_rate))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC bookings_2024  cancelled_2024
# MAGIC 4              2
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS bookings_2024,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id = 16225
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `1831 40672`.

# COMMAND ----------

historic_or_ski_df = properties_df.filter(
    (properties_df["property_type"] == "Historical Place")
    | (properties_df["property_type"] == "Ski Resort")
)
not_pending_df = bookings_df.filter(~(bookings_df["status"] == "pending"))
print(historic_or_ski_df.count(), not_pending_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (without parentheses, | is evaluated before ==).

# COMMAND ----------

# INTENTIONAL ERROR – without parentheses, | is evaluated before ==
historic_or_ski_df = properties_df.filter(properties_df["property_type"] == "Historical Place" | properties_df["property_type"] == "Ski Resort")
print(historic_or_ski_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: each comparison between parentheses. Expected result: `1831`.

# COMMAND ----------

# Fix: each condition between parentheses
historic_or_ski_df = properties_df.filter(
    (properties_df["property_type"] == "Historical Place")
    | (properties_df["property_type"] == "Ski Resort")
)
print(historic_or_ski_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `72287 30 72257`.

# COMMAND ----------

teaching_bookings_df = spark.sql(f"SELECT * FROM {BOOKINGS_TABLE}")
missing_amount_df = teaching_bookings_df.filter(teaching_bookings_df["total_amount"].isNull())
present_amount_df = teaching_bookings_df.filter(teaching_bookings_df["total_amount"].isNotNull())
print(teaching_bookings_df.count(), missing_amount_df.count(), present_amount_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell gives no error but produces a wrong result (the comparison with None never finds any rows): `0`.

# COMMAND ----------

# SILENT ERROR – the comparison with None never finds any rows
wrong_missing_df = teaching_bookings_df.filter(teaching_bookings_df["total_amount"] == None)
print(wrong_missing_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `isNull()`. Expected result: `30`.

# COMMAND ----------

# Fix: missing values are found with isNull()
print(teaching_bookings_df.filter(teaching_bookings_df["total_amount"].isNull()).count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 13
# MAGIC 43
# MAGIC ```

# COMMAND ----------

amount_problems_df = teaching_bookings_df.filter(
    (teaching_bookings_df["total_amount"].isNull())
    | (teaching_bookings_df["total_amount"] < 0)
)
print(teaching_bookings_df.filter(teaching_bookings_df["total_amount"] < 0).count())
print(amount_problems_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `8 40`.

# COMMAND ----------

inverted_df = teaching_bookings_df.filter(teaching_bookings_df["check_out"] < teaching_bookings_df["check_in"])
duplicate_rows = teaching_bookings_df.count() - teaching_bookings_df.distinct().count()
print(inverted_df.count(), duplicate_rows)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC row_count  missing_amounts  negative_amounts  inverted_dates  duplicate_rows
# MAGIC 72287      30               13                8               40
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)                                                     AS row_count,
# MAGIC        SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END)        AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END)            AS negative_amounts,
# MAGIC        SUM(CASE WHEN check_out < check_in THEN 1 ELSE 0 END)        AS inverted_dates,
# MAGIC        COUNT(*) - (SELECT COUNT(*) FROM (SELECT DISTINCT * FROM workspace.python_book.b_bookings)) AS duplicate_rows
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.8 Sorting and Limiting: orderBy and limit

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  title                  base_price
# MAGIC 11670        Historic Inn in Rome   284.97
# MAGIC 16225        Beach House in Amalfi  236.95
# MAGIC 16317        Bungalow in Sardinia   213.91
# MAGIC ```

# COMMAND ----------

guide_df = properties_df.filter(
    (properties_df["property_id"] == 11670)
    | (properties_df["property_id"] == 16317)
    | (properties_df["property_id"] == 16225)
)
display(guide_df.select("property_id", "title", "base_price").orderBy("base_price", ascending=False))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC +------------+
# MAGIC |total_amount|
# MAGIC +------------+
# MAGIC |        NULL|
# MAGIC |        NULL|
# MAGIC |        NULL|
# MAGIC +------------+
# MAGIC only showing top 3 rows
# MAGIC ```

# COMMAND ----------

amounts_df = teaching_bookings_df.select("total_amount")
amounts_df.orderBy("total_amount").show(3)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination_id  destination  country
# MAGIC 1100            Amalfi       Italy
# MAGIC 2300            Florence     Italy
# MAGIC
# MAGIC 2
# MAGIC ```

# COMMAND ----------

first_italian_df = italy_df.orderBy("destination").limit(2)
display(first_italian_df)
print(first_italian_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.9 Chaining Operations

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, title, property_type, base_price
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id = 11670 OR property_id = 16317 OR property_id = 16225
# MAGIC ORDER BY base_price DESC
# MAGIC LIMIT 3

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  title                  property_type     base_price
# MAGIC 11670        Historic Inn in Rome   Historical Place  284.97
# MAGIC 16225        Beach House in Amalfi  Summer Getaway    236.95
# MAGIC 16317        Bungalow in Sardinia   Summer Getaway    213.91
# MAGIC ```

# COMMAND ----------

guide_report_df = (
    properties_df
    .filter(
        (properties_df["property_id"] == 11670)
        | (properties_df["property_id"] == 16317)
        | (properties_df["property_id"] == 16225)
    )
    .select("property_id", "title", "property_type", "base_price")
    .orderBy("base_price", ascending=False)
    .limit(3)
)
display(guide_report_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 18163
# MAGIC 3
# MAGIC 18163
# MAGIC ```

# COMMAND ----------

print(properties_df.count())
print(guide_report_df.count())
print(properties_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell gives no error but produces a wrong result (the result of filter() isn't put into a variable): `18163`.

# COMMAND ----------

# SILENT ERROR – the result of filter() isn't put into a variable
ski_df = properties_df
ski_df.filter(ski_df["property_type"] == "Ski Resort")
print(ski_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the result is assigned. Expected result: `185`.

# COMMAND ----------

# Fix: the result of filter() is put into a variable
ski_df = properties_df.filter(properties_df["property_type"] == "Ski Resort")
print(ski_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.10 From Spark to Python and Back: collect and createDataFrame

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC <class 'list'> 3
# MAGIC Row(property_id=11670, title='Historic Inn in Rome', property_type='Historical Place', base_price=284.9700012207031)
# MAGIC ```

# COMMAND ----------

guide_rows = guide_report_df.collect()
print(type(guide_rows), len(guide_rows))
print(guide_rows[0])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Historic Inn in Rome
# MAGIC 284.9700012207031
# MAGIC 284.97
# MAGIC {'property_id': 11670, 'title': 'Historic Inn in Rome', 'property_type': 'Historical Place', 'base_price': 284.9700012207031}
# MAGIC ```

# COMMAND ----------

first_row = guide_rows[0]
print(first_row["title"])
print(first_row["base_price"])
print(f"{first_row['base_price']:.2f}")
print(first_row.asDict())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Row(first_check_in=datetime.date(2022, 12, 29), last_check_in=datetime.date(2025, 7, 30))
# MAGIC <class 'datetime.date'>
# MAGIC Arrivals from 29/12/2022 to 30/07/2025: 944 days
# MAGIC ```

# COMMAND ----------

period_row = spark.sql(f"""
SELECT MIN(check_in) AS first_check_in, MAX(check_in) AS last_check_in
FROM {SOURCE_BOOKINGS_TABLE}
""").collect()[0]
print(period_row)
first_check_in = period_row["first_check_in"]
last_check_in = period_row["last_check_in"]
print(type(first_check_in))
print(f"Arrivals from {first_check_in.strftime('%d/%m/%Y')} to {last_check_in.strftime('%d/%m/%Y')}: {(last_check_in - first_check_in).days} days")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 11670: 6 bookings, 0 canceled, rate 0.0% (ok), revenue 3966.21
# MAGIC 16317: 7 bookings, 1 canceled, rate 14.3% (ok), revenue 5139.59
# MAGIC 16225: 4 bookings, 2 canceled, rate 50.0% (critical), revenue 2896.92
# MAGIC ```

# COMMAND ----------

guide_results = []
for property_id in GUIDE_PROPERTY_IDS:
    rows_2024 = (
        bookings_df
        .filter(
            (bookings_df["property_id"] == property_id)
            & (bookings_df["check_in"] >= date(ANALYSIS_YEAR, 1, 1))
            & (bookings_df["check_in"] <= date(ANALYSIS_YEAR, 12, 31))
        )
        .select("status", "total_amount")
        .collect()
    )
    booking_total = len(rows_2024)
    cancelled_total = 0
    revenue_total = 0
    for row in rows_2024:
        revenue_total = revenue_total + row["total_amount"]
        if row["status"] == "cancelled":
            cancelled_total = cancelled_total + 1
    rate = cancelled_total / booking_total * 100
    status = classify_cancellation_rate(rate)
    print(f"{property_id}: {booking_total} bookings, {cancelled_total} canceled, rate {rate:.1f}% ({status}), revenue {revenue_total:.2f}")
    guide_results.append({
        "property_id": property_id,
        "bookings_2024": booking_total,
        "cancelled_2024": cancelled_total,
        "cancellation_rate": round(rate, 1),
        "cancellation_status": status,
        "revenue_2024": round(revenue_total, 2),
    })

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `['bookings_2024', 'cancellation_rate', 'cancellation_status', 'cancelled_2024', 'property_id', 'revenue_2024']`.

# COMMAND ----------

results_df = spark.createDataFrame(guide_results)
print(results_df.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  bookings_2024  cancelled_2024  cancellation_rate  cancellation_status  revenue_2024
# MAGIC 16225        4              2               50.0               critical             2896.92
# MAGIC 16317        7              1               14.3               ok                   5139.59
# MAGIC 11670        6              0               0.0                ok                   3966.21
# MAGIC ```

# COMMAND ----------

results_df = results_df.select(
    "property_id", "bookings_2024", "cancelled_2024", "cancellation_rate", "cancellation_status", "revenue_2024"
)
display(results_df.orderBy("cancellation_rate", ascending=False))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC property_id  bookings_2024  cancelled_2024  revenue_2024
# MAGIC 11670        6              0               3966.21
# MAGIC 16225        4              2               2896.92
# MAGIC 16317        7              1               5139.59
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                                  AS bookings_2024,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)     AS cancelled_2024,
# MAGIC        ROUND(SUM(total_amount), 2)                               AS revenue_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8.11 Common Mistakes with PySpark

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the table is called bookings, not booking).

# COMMAND ----------

# INTENTIONAL ERROR – the table is called bookings, not booking
wrong_df = spark.sql("SELECT * FROM samples.wanderbricks.booking")
print(wrong_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the constant from the setup cell. Expected result: `72247`.

# COMMAND ----------

# Fix: the table name from the constant
right_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
print(right_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (show() returns None, not a DataFrame).

# COMMAND ----------

# INTENTIONAL ERROR – show() returns None, not a DataFrame
italy_shown_df = italy_df.show()
print(italy_shown_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: save the DataFrame without `show()`. Expected result: the grid of the four destinations and `4`.

# COMMAND ----------

# Fix: save the DataFrame, then call show() on its own
italy_shown_df = italy_df
italy_shown_df.show()
print(italy_shown_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell gives no error but produces a wrong result (count without parentheses doesn't count the rows): `<bound method DataFrame.count of DataFrame[destination_id: bigint, destination: string, country: string]>`.

# COMMAND ----------

# SILENT ERROR – count without parentheses doesn't count the rows
print(italy_df.count)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the parentheses. Expected result: `4`.

# COMMAND ----------

# Fix: count() with parentheses
print(italy_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - `spark.sql(text)` runs a query and returns a **DataFrame**; you build the query with f-strings (text values between quotes).
# MAGIC - A DataFrame is a **recipe**: `select`, `distinct`, `filter`, `orderBy`, `limit` prepare; `display`, `show`, `count`, `collect` are **actions**.
# MAGIC - `display()` interactive grid; `show(n, truncate=False)` text grid; both return `None`. `printSchema()` like `DESCRIBE TABLE`; `count()` gives an `int`; `columns` is a list.
# MAGIC - Filters in text form (`"status = 'cancelled'"`) or column form (`df["status"] == "cancelled"`); `&` `|` `~` with each condition between parentheses; `isNull()` / `isNotNull()`, never `== None`.
# MAGIC - `orderBy(..., ascending=False)` or `.desc()`; in Spark, `NULL` values go to the top in ascending order; `limit()` always after `orderBy()`.
# MAGIC - Chains between parentheses, one operation per line; the starting DataFrame doesn't change: assign the result.
# MAGIC - `collect()` → list of `Row` objects (like dictionaries, `asDict()`), only for small results; `spark.createDataFrame(list)` puts the columns in alphabetical order: reorder them with `select()`.
