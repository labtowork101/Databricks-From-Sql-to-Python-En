# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 9 – Transformations with PySpark
# MAGIC
# MAGIC Notebook for Chapter 9 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Use Spark's functions with `import pyspark.sql.functions as F` and refer to columns with `F.col()`
# MAGIC - Add columns with `withColumn`, `F.lit`, `alias`; convert with `F.to_date` and `cast`
# MAGIC - Classify with `F.when` / `otherwise`
# MAGIC - Aggregate with `groupBy` + `agg` (WHERE and HAVING), on dirty data too
# MAGIC - Join tables with `join` and build the report of the cancellation rate by destination and month
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–8; notebook attached to **Serverless** compute
# MAGIC - `L00_Prepare_Data` already run (section 9.6 reads `workspace.python_book.b_bookings`); no cell writes tables
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

# MAGIC %md
# MAGIC Expected result: `Setup complete`.

# COMMAND ----------

# Setup cell: imports, constants, and DataFrames used in the sections
import pyspark.sql.functions as F
from datetime import date, timedelta, datetime

# Schemas and tables: samples is read-only, workspace.python_book is the working schema
SOURCE_SCHEMA = "samples.wanderbricks"
WORK_SCHEMA = "workspace.python_book"
SOURCE_BOOKINGS_TABLE = f"{SOURCE_SCHEMA}.bookings"   # original bookings
PROPERTIES_TABLE = f"{SOURCE_SCHEMA}.properties"
DESTINATIONS_TABLE = f"{SOURCE_SCHEMA}.destinations"
COUNTRIES_TABLE = f"{SOURCE_SCHEMA}.countries"
SUPPORT_LOGS_TABLE = f"{SOURCE_SCHEMA}.customer_support_logs"
BOOKINGS_TABLE = f"{WORK_SCHEMA}.b_bookings"           # teaching copy with anomalies (Chapter 0)

ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
MIN_BOOKINGS = 20                    # minimum bookings for a rate to be assessable (section 9.8)

# Guide properties, always in the order Rome, Sardinia, Amalfi
GUIDE_PROPERTY_IDS = [11670, 16317, 16225]

# DataFrames of the tables (recipes: no data is read yet)
bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
properties_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
destinations_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE}")
countries_df = spark.sql(f"SELECT * FROM {COUNTRIES_TABLE}")
teaching_bookings_df = spark.sql(f"SELECT * FROM {BOOKINGS_TABLE}")

print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.1 Spark's Functions: F and F.col

# COMMAND ----------

import pyspark.sql.functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 735.83
# MAGIC Column<'sum(base_price)'>
# MAGIC ```

# COMMAND ----------

print(sum([284.97, 213.91, 236.95]))
print(F.sum("base_price"))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Column<'base_price'>
# MAGIC Column<'base_price'>
# MAGIC ```

# COMMAND ----------

print(F.col("base_price"))
print(properties_df["base_price"])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 4
# MAGIC 185
# MAGIC ```

# COMMAND ----------

amalfi_2024_df = bookings_df.filter(
    (F.col("property_id") == 16225)
    & (F.col("check_in") >= date(ANALYSIS_YEAR, 1, 1))
    & (F.col("check_in") <= date(ANALYSIS_YEAR, 12, 31))
)
print(amalfi_2024_df.count())
print(properties_df.filter(F.col("property_type") == "Ski Resort").count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.2 New Columns: withColumn, F.lit, and alias

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_id  check_in    check_out   total_amount  status
# MAGIC 24996       2024-06-28  2024-07-01  914.47        pending
# MAGIC 52528       2024-07-21  2024-07-26  709.36        cancelled
# MAGIC 57340       2024-08-23  2024-08-26  865.17        pending
# MAGIC 12488       2024-08-30  2024-09-05  407.92        cancelled
# MAGIC ```

# COMMAND ----------

amalfi_df = (
    amalfi_2024_df
    .select("booking_id", "check_in", "check_out", "total_amount", "status")
    .orderBy("check_in")
)
display(amalfi_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_id  check_in    check_out   total_amount  status     nights
# MAGIC 24996       2024-06-28  2024-07-01  914.47        pending    3
# MAGIC 52528       2024-07-21  2024-07-26  709.36        cancelled  5
# MAGIC 57340       2024-08-23  2024-08-26  865.17        pending    3
# MAGIC 12488       2024-08-30  2024-09-05  407.92        cancelled  6
# MAGIC ```

# COMMAND ----------

amalfi_nights_df = amalfi_df.withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in")))
display(amalfi_nights_df)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT booking_id, check_in, check_out, total_amount, status,
# MAGIC        datediff(check_out, check_in) AS nights
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id = 16225
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC ORDER BY check_in

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_id  nights  amount_per_night  check_in_month  check_in_weekday  status_label  source
# MAGIC 24996       3       304.82            6               6                 PENDING       wanderbricks
# MAGIC 52528       5       141.87            7               1                 CANCELLED     wanderbricks
# MAGIC 57340       3       288.39            8               6                 PENDING       wanderbricks
# MAGIC 12488       6       67.99             8               6                 CANCELLED     wanderbricks
# MAGIC ```

# COMMAND ----------

amalfi_report_df = (
    amalfi_df
    .withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in")))
    .withColumn("amount_per_night", F.round(F.col("total_amount") / F.col("nights"), 2))
    .withColumn("check_in_month", F.month(F.col("check_in")))
    .withColumn("check_in_weekday", F.dayofweek(F.col("check_in")))
    .withColumn("status_label", F.upper(F.col("status")))
    .withColumn("source", F.lit("wanderbricks"))
)
display(amalfi_report_df.select("booking_id", "nights", "amount_per_night", "check_in_month", "check_in_weekday", "status_label", "source"))

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the second argument of withColumn must be a column).

# COMMAND ----------

# INTENTIONAL ERROR – the second argument of withColumn must be a column
amalfi_source_df = amalfi_df.withColumn("source", "wanderbricks")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the fixed value with `F.lit()`. Expected result: `['booking_id', 'check_in', 'check_out', 'total_amount', 'status', 'source']`.

# COMMAND ----------

# Fix: the fixed value becomes a column with F.lit()
amalfi_source_df = amalfi_df.withColumn("source", F.lit("wanderbricks"))
print(amalfi_source_df.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_id  check_in    check_out   total_amount  status
# MAGIC 24996       2024-06-28  2024-07-01  914           pending
# MAGIC 52528       2024-07-21  2024-07-26  709           cancelled
# MAGIC 57340       2024-08-23  2024-08-26  865           pending
# MAGIC 12488       2024-08-30  2024-09-05  408           cancelled
# MAGIC ```

# COMMAND ----------

rounded_df = amalfi_df.withColumn("total_amount", F.round(F.col("total_amount"), 0))
display(rounded_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_id  amount_with_fee  round((total_amount * 1.1), 2)
# MAGIC 24996       1005.92          1005.92
# MAGIC 52528       780.3            780.3
# MAGIC 57340       951.69           951.69
# MAGIC 12488       448.71           448.71
# MAGIC ```

# COMMAND ----------

display(
    amalfi_df.select(
        "booking_id",
        F.round(F.col("total_amount") * 1.1, 2).alias("amount_with_fee"),
        F.round(F.col("total_amount") * 1.1, 2),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.3 Dates and Types: F.to_date and cast

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC root
# MAGIC  |-- booking_id: long (nullable = true)
# MAGIC  |-- check_in: string (nullable = true)
# MAGIC  |-- check_out: string (nullable = true)
# MAGIC  |-- total_amount: string (nullable = true)
# MAGIC ```

# COMMAND ----------

raw_amalfi_df = spark.createDataFrame([
    {"booking_id": 24996, "check_in": "06/28/2024", "check_out": "07/01/2024", "total_amount": "914.47"},
    {"booking_id": 52528, "check_in": "07/21/2024", "check_out": "07/26/2024", "total_amount": "709.36"},
    {"booking_id": 57340, "check_in": "08/23/2024", "check_out": "08/26/2024", "total_amount": "865.17"},
    {"booking_id": 12488, "check_in": "08/30/2024", "check_out": "09/05/2024", "total_amount": "407.92"},
])
raw_amalfi_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC root
# MAGIC  |-- booking_id: long (nullable = true)
# MAGIC  |-- check_in: date (nullable = true)
# MAGIC  |-- check_out: date (nullable = true)
# MAGIC  |-- total_amount: double (nullable = true)
# MAGIC
# MAGIC booking_id  check_in    check_out   total_amount  nights
# MAGIC 24996       2024-06-28  2024-07-01  914.47        3
# MAGIC 52528       2024-07-21  2024-07-26  709.36        5
# MAGIC 57340       2024-08-23  2024-08-26  865.17        3
# MAGIC 12488       2024-08-30  2024-09-05  407.92        6
# MAGIC ```

# COMMAND ----------

amalfi_dates_df = (
    raw_amalfi_df
    .withColumn("check_in", F.to_date(F.col("check_in"), "MM/dd/yyyy"))
    .withColumn("check_out", F.to_date(F.col("check_out"), "MM/dd/yyyy"))
    .withColumn("total_amount", F.col("total_amount").cast("double"))
)
amalfi_dates_df.printSchema()
display(amalfi_dates_df.withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in"))))

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell gives no error but produces a wrong result (mm means minutes, not the month):
# MAGIC ```
# MAGIC booking_id  check_in    check_out   total_amount  nights
# MAGIC 24996       2024-01-28  2024-01-01  914.47        -27
# MAGIC 52528       2024-01-21  2024-01-26  709.36        5
# MAGIC 57340       2024-01-23  2024-01-26  865.17        3
# MAGIC 12488       2024-01-30  2024-01-05  407.92        -25
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – mm means minutes, not the month
wrong_dates_df = (
    raw_amalfi_df
    .withColumn("check_in", F.to_date(F.col("check_in"), "mm/dd/yyyy"))
    .withColumn("check_out", F.to_date(F.col("check_out"), "mm/dd/yyyy"))
)
display(wrong_dates_df.withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in"))))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the month is written `MM`. Expected result: the dates in June, July, August, and September and the nights `3 5 3 6`.

# COMMAND ----------

# Fix: MM is the month, mm the minutes
right_dates_df = (
    raw_amalfi_df
    .withColumn("check_in", F.to_date(F.col("check_in"), "MM/dd/yyyy"))
    .withColumn("check_out", F.to_date(F.col("check_out"), "MM/dd/yyyy"))
)
display(right_dates_df.withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in"))))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC root
# MAGIC  |-- ticket_id: string (nullable = true)
# MAGIC  |-- created_at: string (nullable = true)
# MAGIC
# MAGIC 1900 658
# MAGIC ```

# COMMAND ----------

logs_df = spark.sql(f"SELECT ticket_id, created_at FROM {SUPPORT_LOGS_TABLE}")
logs_df.printSchema()
logs_2024_count = (
    logs_df
    .withColumn("created_date", F.to_date(F.col("created_at")))
    .filter(F.year(F.col("created_date")) == ANALYSIS_YEAR)
    .count()
)
print(logs_df.count(), logs_2024_count)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC +-----------+----------+--------------+------------------+-------------+
# MAGIC |property_id|base_price|base_price_int| base_price_double|property_code|
# MAGIC +-----------+----------+--------------+------------------+-------------+
# MAGIC |      11670|    284.97|           284| 284.9700012207031|        11670|
# MAGIC |      16225|    236.95|           236| 236.9499969482422|        16225|
# MAGIC |      16317|    213.91|           213|213.91000366210938|        16317|
# MAGIC +-----------+----------+--------------+------------------+-------------+
# MAGIC
# MAGIC root
# MAGIC  |-- property_id: long (nullable = false)
# MAGIC  |-- base_price: float (nullable = true)
# MAGIC  |-- base_price_int: integer (nullable = true)
# MAGIC  |-- base_price_double: double (nullable = true)
# MAGIC  |-- property_code: string (nullable = true)
# MAGIC ```

# COMMAND ----------

guide_prices_df = (
    properties_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .select(
        "property_id",
        "base_price",
        F.col("base_price").cast("int").alias("base_price_int"),
        F.col("base_price").cast("double").alias("base_price_double"),
        F.col("property_id").cast("string").alias("property_code"),
    )
    .orderBy("property_id")
)
guide_prices_df.show()
guide_prices_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC ok_date     wrong_date  amount  price_int
# MAGIC 2024-06-28  2024-01-28  914.47  284
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT to_date('06/28/2024', 'MM/dd/yyyy') AS ok_date,
# MAGIC        to_date('06/28/2024', 'mm/dd/yyyy') AS wrong_date,
# MAGIC        CAST('914.47' AS DOUBLE)            AS amount,
# MAGIC        CAST(284.97 AS INT)                 AS price_int

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.4 Conditions on Columns: F.when and otherwise

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC property_id  base_price  price_band
# MAGIC 11670        284.97      high
# MAGIC 16225        236.95      medium
# MAGIC 16317        213.91      medium
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, base_price,
# MAGIC        CASE WHEN base_price >= 250 THEN 'high'
# MAGIC             WHEN base_price >= 200 THEN 'medium'
# MAGIC             ELSE 'low'
# MAGIC        END AS price_band
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  base_price  price_band
# MAGIC 11670        284.97      high
# MAGIC 16225        236.95      medium
# MAGIC 16317        213.91      medium
# MAGIC ```

# COMMAND ----------

guide_bands_df = (
    properties_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .select("property_id", "base_price")
    .withColumn(
        "price_band",
        F.when(F.col("base_price") >= 250, "high")
        .when(F.col("base_price") >= 200, "medium")
        .otherwise("low")
    )
    .orderBy("property_id")
)
display(guide_bands_df)

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell gives no error but produces a wrong result (the broadest condition is written first):
# MAGIC ```
# MAGIC property_id  base_price  price_band
# MAGIC 11670        284.97      medium
# MAGIC 16225        236.95      medium
# MAGIC 16317        213.91      medium
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – the broadest condition is written first
wrong_bands_df = guide_bands_df.withColumn(
    "price_band",
    F.when(F.col("base_price") >= 200, "medium")
    .when(F.col("base_price") >= 250, "high")
    .otherwise("low")
)
display(wrong_bands_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: from the narrowest condition to the broadest. Expected result: `high`, `medium`, `medium`.

# COMMAND ----------

# Fix: first >= 250, then >= 200
right_bands_df = guide_bands_df.withColumn(
    "price_band",
    F.when(F.col("base_price") >= 250, "high")
    .when(F.col("base_price") >= 200, "medium")
    .otherwise("low")
)
display(right_bands_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  base_price  price_band  is_expensive
# MAGIC 11670        284.97      high        yes
# MAGIC 16225        236.95      medium      null
# MAGIC 16317        213.91      medium      null
# MAGIC ```

# COMMAND ----------

display(guide_bands_df.withColumn("is_expensive", F.when(F.col("base_price") >= 250, "yes")))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_id  check_in    check_in_weekday  arrival_type
# MAGIC 24996       2024-06-28  6                 weekend
# MAGIC 52528       2024-07-21  1                 weekday
# MAGIC 57340       2024-08-23  6                 weekend
# MAGIC 12488       2024-08-30  6                 weekend
# MAGIC ```

# COMMAND ----------

weekend_arrival = (F.col("check_in_weekday") == 6) | (F.col("check_in_weekday") == 7)

amalfi_arrivals_df = amalfi_report_df.withColumn(
    "arrival_type",
    F.when(weekend_arrival, "weekend").otherwise("weekday")
)
display(amalfi_arrivals_df.select("booking_id", "check_in", "check_in_weekday", "arrival_type"))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  cancellation_rate  cancellation_status
# MAGIC 11670        0                  ok
# MAGIC 16317        14.3               ok
# MAGIC 16225        50                 critical
# MAGIC 99998        null               missing data
# MAGIC 99999        120                impossible value
# MAGIC ```

# COMMAND ----------

rates_df = spark.createDataFrame([
    {"property_id": 11670, "cancellation_rate": 0.0},
    {"property_id": 16317, "cancellation_rate": 14.3},
    {"property_id": 16225, "cancellation_rate": 50.0},
    {"property_id": 99998, "cancellation_rate": None},
    {"property_id": 99999, "cancellation_rate": 120.0},
]).select("property_id", "cancellation_rate")

rate_status = (
    F.when(F.col("cancellation_rate").isNull(), "missing data")
    .when((F.col("cancellation_rate") < 0) | (F.col("cancellation_rate") > 100), "impossible value")
    .when(F.col("cancellation_rate") > CANCELLATION_RATE_THRESHOLD, "critical")
    .otherwise("ok")
)
display(rates_df.withColumn("cancellation_status", rate_status))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.5 Grouping: groupBy and agg

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `13586`.

# COMMAND ----------

bookings_2024_df = bookings_df.filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
print(bookings_2024_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC status     booking_count
# MAGIC pending    6015
# MAGIC confirmed  3491
# MAGIC cancelled  2647
# MAGIC completed  1433
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status, COUNT(*) AS booking_count
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE year(check_in) = 2024
# MAGIC GROUP BY status
# MAGIC ORDER BY booking_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC status     booking_count
# MAGIC pending    6015
# MAGIC confirmed  3491
# MAGIC cancelled  2647
# MAGIC completed  1433
# MAGIC ```

# COMMAND ----------

status_2024_df = (
    bookings_2024_df
    .groupBy("status")
    .agg(F.count("*").alias("booking_count"))
    .orderBy(F.col("booking_count").desc())
)
display(status_2024_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC status     booking_count  property_count  revenue     avg_amount
# MAGIC pending    6015           3988            3305872.47  549.6
# MAGIC confirmed  3491           2754            1941435.37  556.13
# MAGIC cancelled  2647           2202            1462553     552.53
# MAGIC completed  1433           1311            791628.83   552.43
# MAGIC ```

# COMMAND ----------

status_summary_df = (
    bookings_2024_df
    .groupBy("status")
    .agg(
        F.count("*").alias("booking_count"),
        F.countDistinct("property_id").alias("property_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
        F.round(F.avg("total_amount"), 2).alias("avg_amount"),
    )
    .orderBy(F.col("booking_count").desc())
)
display(status_summary_df)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status,
# MAGIC        COUNT(*)                     AS booking_count,
# MAGIC        COUNT(DISTINCT property_id)  AS property_count,
# MAGIC        ROUND(SUM(total_amount), 2)  AS revenue,
# MAGIC        ROUND(AVG(total_amount), 2)  AS avg_amount
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE year(check_in) = 2024
# MAGIC GROUP BY status
# MAGIC ORDER BY booking_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_id  booking_count  cancelled_count  revenue  cancellation_rate
# MAGIC 11670        6              0                3966.21  0
# MAGIC 16225        4              2                2896.92  50
# MAGIC 16317        7              1                5139.59  14.3
# MAGIC ```

# COMMAND ----------

guide_summary_df = (
    bookings_2024_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .groupBy("property_id")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .orderBy("property_id")
)
display(guide_summary_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC property_type     property_count  avg_price  min_price  max_price
# MAGIC Urban Year-Round  9264            173.04     82.19999694824219   561.969970703125
# MAGIC Summer Getaway    7068            198.54     101.01000213623047  517.5999755859375
# MAGIC Historical Place  1646            147.46     55.93000030517578   330.19000244140625
# MAGIC Ski Resort        185             266.49     143.9499969482422   530.9600219726562
# MAGIC ```

# COMMAND ----------

type_prices_df = (
    properties_df
    .groupBy("property_type")
    .agg(
        F.count("*").alias("property_count"),
        F.round(F.avg("base_price"), 2).alias("avg_price"),
        F.min("base_price").alias("min_price"),
        F.max("base_price").alias("max_price"),
    )
    .orderBy(F.col("property_count").desc())
)
display(type_prices_df)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT destination_id, COUNT(*) AS property_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY destination_id
# MAGIC HAVING COUNT(*) > 1000
# MAGIC ORDER BY property_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination_id  property_count
# MAGIC 3800            1788
# MAGIC 3300            1626
# MAGIC 2400            1624
# MAGIC 3750            1440
# MAGIC 1000            1103
# MAGIC ```

# COMMAND ----------

large_destinations_df = (
    properties_df
    .groupBy("destination_id")
    .agg(F.count("*").alias("property_count"))
    .filter(F.col("property_count") > 1000)
    .orderBy(F.col("property_count").desc())
)
display(large_destinations_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `<class 'pyspark.sql.connect.group.GroupedData'>`.

# COMMAND ----------

grouped = bookings_2024_df.groupBy("status")
print(type(grouped))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.6 Aggregating Dirty Data

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC row_count  amount_count  avg_amount
# MAGIC 13626      13596         551.11
# MAGIC ```

# COMMAND ----------

teaching_2024_df = teaching_bookings_df.filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)

display(
    teaching_2024_df.agg(
        F.count("*").alias("row_count"),
        F.count("total_amount").alias("amount_count"),
        F.round(F.avg("total_amount"), 2).alias("avg_amount"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC avg_all  avg_valid  valid_count
# MAGIC 551.11   552.17     13584
# MAGIC ```

# COMMAND ----------

valid_amount = F.when(F.col("total_amount") >= 0, F.col("total_amount"))

display(
    teaching_2024_df.agg(
        F.round(F.avg("total_amount"), 2).alias("avg_all"),
        F.round(F.avg(valid_amount), 2).alias("avg_valid"),
        F.count(valid_amount).alias("valid_count"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC avg_all  avg_valid  valid_count
# MAGIC 551.11   552.17     13584
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(AVG(total_amount), 2)                                         AS avg_all,
# MAGIC        ROUND(AVG(CASE WHEN total_amount >= 0 THEN total_amount END), 2)    AS avg_valid,
# MAGIC        COUNT(CASE WHEN total_amount >= 0 THEN total_amount END)            AS valid_count
# MAGIC FROM workspace.python_book.b_bookings
# MAGIC WHERE year(check_in) = 2024

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC booking_count  booking_ids  valid_count  revenue     avg_amount
# MAGIC 13586          13586        13544        7477734.15  552.11
# MAGIC ```

# COMMAND ----------

clean_2024_df = teaching_2024_df.distinct()

display(
    clean_2024_df.agg(
        F.count("*").alias("booking_count"),
        F.countDistinct("booking_id").alias("booking_ids"),
        F.count(valid_amount).alias("valid_count"),
        F.round(F.sum(valid_amount), 2).alias("revenue"),
        F.round(F.avg(valid_amount), 2).alias("avg_amount"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.7 Joining Tables: join

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC property_id  title                  destination_id  destination  country
# MAGIC 11670        Historic Inn in Rome   3900            Rome         Italy
# MAGIC 16225        Beach House in Amalfi  1100            Amalfi       Italy
# MAGIC 16317        Bungalow in Sardinia   4200            Sardinia     Italy
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT p.property_id, p.title, p.destination_id, d.destination, d.country
# MAGIC FROM samples.wanderbricks.properties p
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC WHERE p.property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY p.property_id

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination_id  property_id  title                  destination  country
# MAGIC 3900            11670        Historic Inn in Rome   Rome         Italy
# MAGIC 1100            16225        Beach House in Amalfi  Amalfi       Italy
# MAGIC 4200            16317        Bungalow in Sardinia   Sardinia     Italy
# MAGIC ```

# COMMAND ----------

destination_names_df = destinations_df.select("destination_id", "destination", "country")

guide_places_df = (
    properties_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .select("property_id", "title", "destination_id")
    .join(destination_names_df, on="destination_id", how="inner")
    .orderBy("property_id")
)
display(guide_places_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 42 42
# MAGIC 18163 18163
# MAGIC ```

# COMMAND ----------

print(destination_names_df.count(), destination_names_df.select("destination_id").distinct().count())
print(properties_df.count(), properties_df.join(destination_names_df, on="destination_id", how="inner").count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination  country               booking_count  cancelled_count
# MAGIC Phuket       Thailand              1262           258
# MAGIC Paris        France                1149           225
# MAGIC Mallorca     Spain                 1126           217
# MAGIC Gold Coast   Australia             1069           214
# MAGIC Abu Dhabi    United Arab Emirates  871            166
# MAGIC
# MAGIC destination  country  booking_count  cancelled_count
# MAGIC Sardinia     Italy    311            63
# MAGIC Rome         Italy    294            56
# MAGIC Florence     Italy    58             11
# MAGIC Amalfi       Italy    51             12
# MAGIC ```

# COMMAND ----------

property_places_df = properties_df.select("property_id", "destination_id")

destination_2024_df = (
    bookings_2024_df
    .select("booking_id", "property_id", "status")
    .join(property_places_df, on="property_id", how="inner")
    .join(destination_names_df, on="destination_id", how="inner")
    .groupBy("destination", "country")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
    )
    .orderBy(F.col("booking_count").desc())
)
display(destination_2024_df.limit(5))
display(destination_2024_df.filter(F.col("country") == "Italy"))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT d.destination, d.country,
# MAGIC        COUNT(*)                                                AS booking_count,
# MAGIC        SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
# MAGIC FROM samples.wanderbricks.bookings b
# MAGIC JOIN samples.wanderbricks.properties p USING (property_id)
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC WHERE year(b.check_in) = 2024 AND d.country = 'Italy'
# MAGIC GROUP BY d.destination, d.country
# MAGIC ORDER BY booking_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `17724 439`.

# COMMAND ----------

booked_df = (
    bookings_df
    .select("property_id")
    .distinct()
    .withColumn("has_bookings", F.lit(True))
)

never_booked_df = (
    properties_df
    .select("property_id", "title", "property_type")
    .join(booked_df, on="property_id", how="left")
    .filter(F.col("has_bookings").isNull())
)
print(booked_df.count(), never_booked_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (with the == condition, the key appears twice).

# COMMAND ----------

# INTENTIONAL ERROR – with the == condition, the key appears twice
joined_df = bookings_2024_df.join(properties_df, bookings_2024_df["property_id"] == properties_df["property_id"], how="inner")
display(joined_df.select("booking_id", "property_id", "title"))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `on="property_id"` and `select` before the join. Expected result: 13586 rows; the first ones with `booking_id`, `property_id`, and `title`.

# COMMAND ----------

# Fix: key with on= and only the useful columns of the right-hand table
joined_df = bookings_2024_df.join(properties_df.select("property_id", "title"), on="property_id", how="inner")
print(joined_df.count())
display(joined_df.select("booking_id", "property_id", "title").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.8 A Complete Transformation

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 317
# MAGIC
# MAGIC cancellation_status  combination_count
# MAGIC critical             8
# MAGIC not assessable       152
# MAGIC ok                   157
# MAGIC ```

# COMMAND ----------

cancellation_status = (
    F.when(F.col("booking_count") < MIN_BOOKINGS, "not assessable")
    .when(F.col("cancellation_rate") > CANCELLATION_RATE_THRESHOLD, "critical")
    .otherwise("ok")
)

destination_month_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)                 # 1. 2024 rows (WHERE)
    .select("booking_id", "property_id", "check_in", "status")          # 2. only the useful columns
    .join(property_places_df, on="property_id", how="inner")           # 3. property → destination
    .join(destination_names_df, on="destination_id", how="inner")      # 4. destination → name and country
    .withColumn("check_in_month", F.month(F.col("check_in")))          # 5. check-in month
    .groupBy("destination", "country", "check_in_month")               # 6. one row per destination and month
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .withColumn("cancellation_status", cancellation_status)            # 7. status with the minimum volume
)
print(destination_month_df.count())
display(destination_month_df.groupBy("cancellation_status").agg(F.count("*").alias("combination_count")).orderBy("cancellation_status"))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination  country               check_in_month  booking_count  cancelled_count  cancellation_rate  cancellation_status
# MAGIC Cairo        Egypt                 9               35             13               37.1               critical
# MAGIC London       United Kingdom        9               35             13               37.1               critical
# MAGIC Madrid       Spain                 4               21             7                33.3               critical
# MAGIC London       United Kingdom        11              37             12               32.4               critical
# MAGIC Dubai        United Arab Emirates  3               25             8                32                 critical
# MAGIC Barcelona    Spain                 8               44             14               31.8               critical
# MAGIC Cairo        Egypt                 12              45             14               31.1               critical
# MAGIC Byron Bay    Australia             8               53             16               30.2               critical
# MAGIC ```

# COMMAND ----------

critical_df = (
    destination_month_df
    .filter(F.col("cancellation_status") == "critical")                  # 8. only the critical ones (HAVING)
    .orderBy(F.col("cancellation_rate").desc(), "destination", "check_in_month")
)
display(critical_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination  country  check_in_month  booking_count  cancelled_count  cancellation_rate  cancellation_status
# MAGIC Amalfi       Italy    6               13             5                38.5               not assessable
# MAGIC Amalfi       Italy    7               9              1                11.1               not assessable
# MAGIC Amalfi       Italy    8               20             5                25                 ok
# MAGIC Amalfi       Italy    9               9              1                11.1               not assessable
# MAGIC ```

# COMMAND ----------

display(destination_month_df.filter(F.col("destination") == "Amalfi").orderBy("check_in_month"))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT d.destination, d.country,
# MAGIC        month(b.check_in)                                       AS check_in_month,
# MAGIC        COUNT(*)                                                AS booking_count,
# MAGIC        SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
# MAGIC        ROUND(SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) AS cancellation_rate
# MAGIC FROM samples.wanderbricks.bookings b
# MAGIC JOIN samples.wanderbricks.properties p USING (property_id)
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC WHERE year(b.check_in) = 2024
# MAGIC GROUP BY d.destination, d.country, month(b.check_in)
# MAGIC HAVING COUNT(*) >= 20
# MAGIC    AND SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*) * 100 > 30
# MAGIC ORDER BY cancellation_rate DESC, d.destination, check_in_month

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9.9 Common Mistakes with Transformations

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (Python's and instead of &).

# COMMAND ----------

# INTENTIONAL ERROR – Python's and instead of &
ski_bands_df = properties_df.withColumn(
    "luxury_ski",
    F.when((F.col("property_type") == "Ski Resort") and (F.col("base_price") >= 250), "yes").otherwise("no")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `&` and every condition in parentheses. Expected result: `106`.

# COMMAND ----------

# Fix: & instead of and
ski_bands_df = properties_df.withColumn(
    "luxury_ski",
    F.when((F.col("property_type") == "Ski Resort") & (F.col("base_price") >= 250), "yes").otherwise("no")
)
print(ski_bands_df.filter(F.col("luxury_ski") == "yes").count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (Python's sum instead of F.sum).

# COMMAND ----------

# INTENTIONAL ERROR – Python's sum instead of F.sum
revenue_df = bookings_2024_df.groupBy("status").agg(sum("total_amount"))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `F.sum` with the prefix. Expected result: the revenue by status from section 9.5 (pending 3305872.47, confirmed 1941435.37, cancelled 1462553, completed 791628.83).

# COMMAND ----------

# Fix: Spark's sum, with the F. prefix
revenue_df = bookings_2024_df.groupBy("status").agg(F.round(F.sum("total_amount"), 2).alias("revenue"))
display(revenue_df.orderBy(F.col("revenue").desc()))

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (agg is missing after groupBy).

# COMMAND ----------

# INTENTIONAL ERROR – agg is missing after groupBy
status_df = bookings_2024_df.groupBy("status").orderBy("status")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: first `agg`, then `orderBy`. Expected result: `cancelled 2647`, `completed 1433`, `confirmed 3491`, `pending 6015`.

# COMMAND ----------

# Fix: groupBy followed by agg, then the DataFrame methods
status_df = bookings_2024_df.groupBy("status").agg(F.count("*").alias("booking_count")).orderBy("status")
display(status_df)

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the aggregation has no alias).

# COMMAND ----------

# INTENTIONAL ERROR – the aggregation has no alias
large_df = (
    properties_df
    .groupBy("destination_id")
    .agg(F.count("*"))
    .filter(F.col("property_count") > 1000)
)
display(large_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: an `alias` for the aggregation. Expected result: the five destinations with more than 1000 properties (3800, 3300, 2400, 3750, 1000).

# COMMAND ----------

# Fix: every aggregation with a name
large_df = (
    properties_df
    .groupBy("destination_id")
    .agg(F.count("*").alias("property_count"))
    .filter(F.col("property_count") > 1000)
)
display(large_df.orderBy(F.col("property_count").desc()))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary of Silent Errors
# MAGIC
# MAGIC The silent errors in this chapter all produce a plausible result: `mm` instead of `MM` in a format (dates moved to January, section 9.3); the conditions of `when` from the broadest to the narrowest (an empty band, section 9.4); a `filter` on the values instead of `F.when` without `otherwise` (lost rows, section 9.6); an aggregation on repeated rows, without `distinct()` (inflated counts and sums, section 9.6); a join with a lookup table that has repeated keys (multiplied rows, section 9.7); a rate assessed on few cases (false alarms, section 9.8). The defense is still the one from Chapters 6 and 8: know in advance what result to expect, count the rows before and after every join, and compare the result with a SQL query written separately.
# MAGIC
# MAGIC ## Common Mistakes
# MAGIC
# MAGIC | Type of error | Typical message | Meaning | First thing to check |
# MAGIC | --- | --- | --- | --- |
# MAGIC | `NOT_EXPECTED_TYPE` | ``Argument `col` should be Column, got str`` | a fixed value where a column is needed | `F.lit()` around the value |
# MAGIC | `CANNOT_CONVERT_COLUMN_INTO_BOOL` | `Cannot convert column into bool` | a column condition used as true/false | `&`, `\|`, `~` instead of `and`, `or`, `not`; the parentheses; an `if` instead of `F.when` |
# MAGIC | `TypeError` | `unsupported operand type(s) for +: 'int' and 'str'` | a Python function instead of the Spark one | the `F.` prefix (`F.sum`, `F.round`, `F.min`, `F.max`) |
# MAGIC | `AttributeError` | `'GroupedData' object has no attribute 'orderBy'` | `groupBy` without `agg` | the `agg()` after `groupBy()` |
# MAGIC | `UNRESOLVED_COLUMN` | ``... with name `property_count` cannot be resolved ... [`count(1)`, ...]`` | a column that doesn't exist, often an aggregation without a name | the `alias()` of every aggregation; the suggestions in the message |
# MAGIC | `AMBIGUOUS_REFERENCE` | ``Reference `property_id` is ambiguous`` | two columns with the same name after a join | `on="column"` instead of the `==` condition; `select` before the join |
# MAGIC | `CAST_INVALID_INPUT`, `CANNOT_PARSE_TIMESTAMP` | `... could not be parsed ...` | a text that can't be converted | the values in the column; the format of `F.to_date` |
# MAGIC | (no error) | all dates in January | minutes instead of the month | `MM` (month) and `mm` (minutes) in the format |
# MAGIC | (no error) | a band or a status that never appears | `when` conditions in the wrong order | from the narrowest condition to the broadest |
# MAGIC | (no error) | counts higher than expected | repeated rows or repeated keys in the join | `count()` versus `countDistinct` of the key; rows before and after the join |
