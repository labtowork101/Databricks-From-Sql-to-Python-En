# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 10 – Reading and Writing Delta Tables
# MAGIC
# MAGIC Notebook for Chapter 10 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Read a table with `spark.table()` and recognize the features of a Delta table
# MAGIC - Name tables (prefix, topic, granularity) and write them with `saveAsTable`, in `overwrite` or `append` mode
# MAGIC - Read the history (`DESCRIBE HISTORY`, `VERSION AS OF`) and understand schema enforcement
# MAGIC - Update a table with `MERGE` (SQL and `DeltaTable`)
# MAGIC - Load the shared `utils` notebook with `%run ./utils` and write a report in four steps
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–9; notebook attached to **Serverless** compute
# MAGIC - `L00_Prepare_Data` already run; the `utils` notebook in the same `Python_Book` folder (it arrives with the Git folder's **Pull**)
# MAGIC - This notebook **writes tables** in the `workspace.python_book` schema: `s_bookings_daily`, `s_bookings_amounts_daily`, `s_guide_properties_bookings`, `s_guide_properties_updates`, `g_cancellations_destination_month`
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter, **from top to bottom**. **Don't use Run all**: some cells contain intentional errors, and many cells write tables that later cells read back.
# MAGIC Run the **setup cell** first (written by hand: `%run ./utils` is introduced in section 10.9; from Chapter 11 on, the setup will be `%run ./utils`). The cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the type, the message, and the line;
# MAGIC - the cell marked **SILENT ERROR** gives no error but produces a wrong result;
# MAGIC - the **Fix** cell below must work **without errors**, with the result indicated.
# MAGIC
# MAGIC For Spark errors (name in square brackets and `SQLSTATE`), read the **summary line**; in the traceback, look for the line of the cell and skip the blocks of the library.
# MAGIC
# MAGIC **If the notebook has already been run**: the first write in section 10.4 fails too, with `TABLE_OR_VIEW_ALREADY_EXISTS` (that's normal; continue), and the history in section 10.6 shows more versions than the text.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `Setup complete`.

# COMMAND ----------

# Setup cell: imports and constants (from Chapter 11: %run ./utils, section 10.9)
import pyspark.sql.functions as F
from datetime import date, timedelta, datetime
from delta.tables import DeltaTable

# Schemas and tables: samples is read-only, workspace.python_book is the working schema
SOURCE_SCHEMA = "samples.wanderbricks"
WORK_SCHEMA = "workspace.python_book"
SOURCE_BOOKINGS_TABLE = f"{SOURCE_SCHEMA}.bookings"           # original bookings
BOOKING_UPDATES_TABLE = f"{SOURCE_SCHEMA}.booking_updates"    # booking updates
PROPERTIES_TABLE = f"{SOURCE_SCHEMA}.properties"
DESTINATIONS_TABLE = f"{SOURCE_SCHEMA}.destinations"
BOOKINGS_TABLE = f"{WORK_SCHEMA}.b_bookings"                  # teaching copy with anomalies (Chapter 0)

ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
MIN_BOOKINGS = 20                    # minimum bookings for a rate to be assessable

# Guide properties, always in the order Rome, Sardinia, Amalfi
GUIDE_PROPERTY_IDS = [11670, 16317, 16225]

print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.1 Delta Tables

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC format  name
# MAGIC delta   workspace.python_book.b_bookings
# MAGIC ```

# COMMAND ----------

display(spark.sql(f"DESCRIBE DETAIL {BOOKINGS_TABLE}").select("format", "name"))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the full row of `DESCRIBE DETAIL` (among the columns, `format` = `delta`).

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE DETAIL workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.2 Reading a Table: spark.table

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `72247 72287`.

# COMMAND ----------

bookings_df = spark.table(SOURCE_BOOKINGS_TABLE)
properties_df = spark.table(PROPERTIES_TABLE)
destinations_df = spark.table(DESTINATIONS_TABLE)
teaching_bookings_df = spark.table(BOOKINGS_TABLE)
print(bookings_df.count(), teaching_bookings_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `True`.

# COMMAND ----------

print(bookings_df.columns == spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}").columns)

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the table is called booking_updates, not bookings_updates; the traceback points to line 3, the one with count(), and then to line 2, where the DataFrame is created).

# COMMAND ----------

# INTENTIONAL ERROR – the table is called booking_updates, not bookings_updates
updates_df = spark.table(f"{SOURCE_SCHEMA}.bookings_updates")
print(updates_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the right name, from the `BOOKING_UPDATES_TABLE` constant. Expected result: `83068`.

# COMMAND ----------

# Fix: the name of the table from the constant
updates_df = spark.table(BOOKING_UPDATES_TABLE)
print(updates_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.3 Naming Tables

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result (on the first run; later, the tables of the chapter appear too):
# MAGIC ```
# MAGIC database     tableName           isTemporary
# MAGIC python_book  b_bookings          false
# MAGIC python_book  b_bookings_changes  false
# MAGIC ```

# COMMAND ----------

display(spark.sql(f"SHOW TABLES IN {WORK_SCHEMA}"))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC workspace.python_book.s_bookings_daily
# MAGIC workspace.python_book.s_bookings_amounts_daily
# MAGIC workspace.python_book.s_guide_properties_bookings
# MAGIC workspace.python_book.s_guide_properties_updates
# MAGIC workspace.python_book.g_cancellations_destination_month
# MAGIC ```

# COMMAND ----------

def build_table_name(topic, granularity, layer="s"):
    """Builds the full name of a table in the working schema."""
    return f"{WORK_SCHEMA}.{layer}_{topic}_{granularity}"


DAILY_BOOKINGS_TABLE = build_table_name("bookings", "daily")
DAILY_AMOUNTS_TABLE = build_table_name("bookings_amounts", "daily")
GUIDE_BOOKINGS_TABLE = build_table_name("guide_properties", "bookings")
GUIDE_UPDATES_TABLE = build_table_name("guide_properties", "updates")
CANCELLATION_REPORT_TABLE = build_table_name("cancellations", "destination_month", layer="g")

print(DAILY_BOOKINGS_TABLE)
print(DAILY_AMOUNTS_TABLE)
print(GUIDE_BOOKINGS_TABLE)
print(GUIDE_UPDATES_TABLE)
print(CANCELLATION_REPORT_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC **Silent error (described only)**: the constants of the reference tables (`SOURCE_BOOKINGS_TABLE`, `BOOKINGS_TABLE`, ...) are never used in a write. On `b_bookings` the write would succeed without warnings and the teaching copy would be lost: you repair it by running `L00_Prepare_Data` again. In writes, use only the constants built with `build_table_name`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.4 Writing a Table: saveAsTable

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `30 29`.

# COMMAND ----------

daily_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .groupBy("check_in")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
)
january_df = daily_df.filter(F.month(F.col("check_in")) == 1)
february_df = daily_df.filter(F.month(F.col("check_in")) == 2)
print(january_df.count(), february_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result (if the notebook has already been run, this cell fails with TABLE_OR_VIEW_ALREADY_EXISTS: that's normal; continue):
# MAGIC ```
# MAGIC Writing workspace.python_book.s_bookings_daily
# MAGIC ```

# COMMAND ----------

print(f"Writing {DAILY_BOOKINGS_TABLE}")
january_df.write.saveAsTable(DAILY_BOOKINGS_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 30
# MAGIC
# MAGIC check_in    booking_count  cancelled_count  revenue
# MAGIC 2024-01-01  16             4                8221.8
# MAGIC 2024-01-03  1              0                880.12
# MAGIC ```

# COMMAND ----------

daily_table_df = spark.table(DAILY_BOOKINGS_TABLE)
print(daily_table_df.count())
display(daily_table_df.orderBy("check_in").limit(2))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC day_count  booking_count  cancelled_count  revenue
# MAGIC 30         204            40               108766.13
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)                    AS day_count,
# MAGIC        SUM(booking_count)          AS booking_count,
# MAGIC        SUM(cancelled_count)        AS cancelled_count,
# MAGIC        ROUND(SUM(revenue), 2)      AS revenue
# MAGIC FROM workspace.python_book.s_bookings_daily

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the table already exists and the mode isn't specified).

# COMMAND ----------

# INTENTIONAL ERROR – the table already exists and the mode isn't specified
january_df.write.saveAsTable(DAILY_BOOKINGS_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the write mode, in section 10.5.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.5 Write Modes: overwrite and append

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_bookings_daily
# MAGIC 30
# MAGIC
# MAGIC 30
# MAGIC ```

# COMMAND ----------

print(f"Writing {DAILY_BOOKINGS_TABLE}")
(
    january_df.write
    .mode("overwrite")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)
print(spark.table(DAILY_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_bookings_daily
# MAGIC 59
# MAGIC
# MAGIC 59
# MAGIC ```

# COMMAND ----------

print(f"Writing {DAILY_BOOKINGS_TABLE}")
(
    february_df.write
    .mode("append")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)
print(spark.table(DAILY_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell gives no error but produces a wrong result (the append cell run a second time): `88 59`.

# COMMAND ----------

# SILENT ERROR – the append cell run a second time
(
    february_df.write
    .mode("append")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)
daily_table_df = spark.table(DAILY_BOOKINGS_TABLE)
print(daily_table_df.count(), daily_table_df.distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC Check in SQL on the key of the table. Expected result:
# MAGIC ```
# MAGIC row_count  day_count  booking_count
# MAGIC 88         59         626
# MAGIC ```

# COMMAND ----------

display(spark.sql(f"""
    SELECT COUNT(*)                 AS row_count,
           COUNT(DISTINCT check_in) AS day_count,
           SUM(booking_count)       AS booking_count
    FROM {DAILY_BOOKINGS_TABLE}
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: overwrite with the complete DataFrame of the two months. Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_bookings_daily
# MAGIC 59 59
# MAGIC ```

# COMMAND ----------

# Fix: overwrite with the complete DataFrame, from a known state
two_months_df = daily_df.filter(F.month(F.col("check_in")) <= 2)
print(f"Writing {DAILY_BOOKINGS_TABLE}")
(
    two_months_df.write
    .mode("overwrite")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)
daily_table_df = spark.table(DAILY_BOOKINGS_TABLE)
print(daily_table_df.count(), daily_table_df.distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the mode is written overwrite, not overwrites; the traceback points to line 5, the one with saveAsTable).

# COMMAND ----------

# INTENTIONAL ERROR – the mode is written overwrite, not overwrites
(
    two_months_df.write
    .mode("overwrites")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the mode written exactly, `"overwrite"`, as in the previous cells. The table wasn't touched, and there's no need to write it again. Expected result: `59`.

# COMMAND ----------

# Fix: the table hasn't changed (the right mode is "overwrite")
print(spark.table(DAILY_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.6 The Version History

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC version  operation
# MAGIC 0        CREATE TABLE AS SELECT
# MAGIC 1        CREATE OR REPLACE TABLE AS SELECT
# MAGIC 2        WRITE
# MAGIC 3        WRITE
# MAGIC 4        CREATE OR REPLACE TABLE AS SELECT
# MAGIC ```

# COMMAND ----------

history_df = spark.sql(f"DESCRIBE HISTORY {DAILY_BOOKINGS_TABLE}")
display(history_df.select("version", "operation").orderBy("version"))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the full history, from the most recent version.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY workspace.python_book.s_bookings_daily

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 0 30
# MAGIC 1 30
# MAGIC 2 59
# MAGIC 3 88
# MAGIC 4 59
# MAGIC ```

# COMMAND ----------

for version in range(5):
    version_query = f"SELECT COUNT(*) AS row_count FROM {DAILY_BOOKINGS_TABLE} VERSION AS OF {version}"
    row_count = spark.sql(version_query).collect()[0]["row_count"]
    print(version, row_count)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: expected result
# MAGIC ```
# MAGIC row_count
# MAGIC 88
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS row_count
# MAGIC FROM workspace.python_book.s_bookings_daily VERSION AS OF 3

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.7 The Table Schema

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 90 31
# MAGIC ['check_in', 'booking_count', 'cancelled_count', 'revenue', 'avg_amount']
# MAGIC ```

# COMMAND ----------

daily_amounts_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .filter(F.month(F.col("check_in")) <= 3)
    .groupBy("check_in")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
        F.round(F.avg("total_amount"), 2).alias("avg_amount"),
    )
)
march_amounts_df = daily_amounts_df.filter(F.month(F.col("check_in")) == 3)
print(daily_amounts_df.count(), march_amounts_df.count())
print(march_amounts_df.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the DataFrame has a column that the table doesn't have; also read Table schema and Data schema in the message).

# COMMAND ----------

# INTENTIONAL ERROR – the DataFrame has a column that the table doesn't have
(
    march_amounts_df.write
    .mode("append")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)

# COMMAND ----------

# MAGIC %md
# MAGIC The table hasn't changed. Expected result:
# MAGIC ```
# MAGIC 59
# MAGIC ['check_in', 'booking_count', 'cancelled_count', 'revenue']
# MAGIC ```

# COMMAND ----------

print(spark.table(DAILY_BOOKINGS_TABLE).count())
print(spark.table(DAILY_BOOKINGS_TABLE).columns)

# COMMAND ----------

# MAGIC %md
# MAGIC Recommended solution: a new table. Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_bookings_amounts_daily
# MAGIC 90
# MAGIC ```

# COMMAND ----------

print(f"Writing {DAILY_AMOUNTS_TABLE}")
(
    daily_amounts_df.write
    .mode("overwrite")
    .saveAsTable(DAILY_AMOUNTS_TABLE)
)
print(spark.table(DAILY_AMOUNTS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC Changing the schema of an existing table (only if agreed): `overwrite` with `overwriteSchema`. Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_bookings_daily
# MAGIC 90
# MAGIC ['check_in', 'booking_count', 'cancelled_count', 'revenue', 'avg_amount']
# MAGIC ```

# COMMAND ----------

print(f"Writing {DAILY_BOOKINGS_TABLE}")
(
    daily_amounts_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(DAILY_BOOKINGS_TABLE)
)
print(spark.table(DAILY_BOOKINGS_TABLE).count())
print(spark.table(DAILY_BOOKINGS_TABLE).columns)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.8 Updating a Table: MERGE

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_guide_properties_bookings
# MAGIC 17
# MAGIC ```

# COMMAND ----------

guide_bookings_df = (
    bookings_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
print(f"Writing {GUIDE_BOOKINGS_TABLE}")
(
    guide_bookings_df.write
    .mode("overwrite")
    .saveAsTable(GUIDE_BOOKINGS_TABLE)
)
print(spark.table(GUIDE_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC Summary by property **before** the MERGE. Expected result:
# MAGIC ```
# MAGIC property_id  booking_count  cancelled_count  revenue
# MAGIC 11670        6              0                3966.21
# MAGIC 16225        4              2                2896.92
# MAGIC 16317        7              1                5139.59
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                              AS booking_count,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
# MAGIC        ROUND(SUM(total_amount), 2)                           AS revenue
# MAGIC FROM workspace.python_book.s_guide_properties_bookings
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC 20 13
# MAGIC
# MAGIC booking_id  booking_update_id  status     total_amount  updated_at
# MAGIC 49395       17570289837900     confirmed  647.01        2024-03-26T07:15:08.000Z
# MAGIC 49395       17570290017629     cancelled  647.01        2024-06-07T02:14:15.000Z
# MAGIC ```

# COMMAND ----------

updates_df = spark.table(BOOKING_UPDATES_TABLE)
guide_updates_df = (
    updates_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
print(guide_updates_df.count(), guide_updates_df.select("booking_id").distinct().count())
display(
    guide_updates_df
    .filter(F.col("booking_id") == 49395)
    .select("booking_id", "booking_update_id", "status", "total_amount", "updated_at")
    .orderBy("updated_at")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: `13 13`.

# COMMAND ----------

last_update_df = (
    guide_updates_df
    .groupBy("booking_id")
    .agg(F.max("updated_at").alias("last_updated_at"))
)
latest_updates_df = (
    guide_updates_df
    .join(last_update_df, on="booking_id", how="inner")
    .filter(F.col("updated_at") == F.col("last_updated_at"))
    .select(guide_bookings_df.columns)
)
print(latest_updates_df.count(), latest_updates_df.select("booking_id").distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_guide_properties_updates
# MAGIC 13
# MAGIC ```

# COMMAND ----------

print(f"Writing {GUIDE_UPDATES_TABLE}")
(
    latest_updates_df.write
    .mode("overwrite")
    .saveAsTable(GUIDE_UPDATES_TABLE)
)
print(spark.table(GUIDE_UPDATES_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC The MERGE in SQL. Expected result (the print of the query, then the counters):
# MAGIC ```
# MAGIC MERGE INTO workspace.python_book.s_guide_properties_bookings AS t
# MAGIC USING workspace.python_book.s_guide_properties_updates AS s
# MAGIC ON t.booking_id = s.booking_id
# MAGIC WHEN MATCHED THEN UPDATE SET *
# MAGIC WHEN NOT MATCHED THEN INSERT *
# MAGIC
# MAGIC num_affected_rows  num_updated_rows  num_deleted_rows  num_inserted_rows
# MAGIC 13                 13                0                 0
# MAGIC ```

# COMMAND ----------

MERGE_KEY = "t.booking_id = s.booking_id"

merge_query = f"""
MERGE INTO {GUIDE_BOOKINGS_TABLE} AS t
USING {GUIDE_UPDATES_TABLE} AS s
ON {MERGE_KEY}
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
print(merge_query)
display(spark.sql(merge_query))

# COMMAND ----------

# MAGIC %md
# MAGIC Summary by property **after** the MERGE (the same query as before). Expected result:
# MAGIC ```
# MAGIC property_id  booking_count  cancelled_count  revenue
# MAGIC 11670        6              0                4065.21
# MAGIC 16225        4              2                2911.92
# MAGIC 16317        7              2                5139.59
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                              AS booking_count,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
# MAGIC        ROUND(SUM(total_amount), 2)                           AS revenue
# MAGIC FROM workspace.python_book.s_guide_properties_bookings
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC If you run the MERGE cell again, the counters stay `13 13 0 0` and the table doesn't change: the MERGE is re-runnable.

# COMMAND ----------

# MAGIC %md
# MAGIC The MERGE in Python with `DeltaTable`. Expected result: `17`.

# COMMAND ----------

guide_table = DeltaTable.forName(spark, GUIDE_BOOKINGS_TABLE)
(
    guide_table.alias("t")
    .merge(latest_updates_df.alias("s"), MERGE_KEY)
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)
print(spark.table(GUIDE_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (the source has more than one row for the same booking).

# COMMAND ----------

# INTENTIONAL ERROR – the source has more than one row for the same booking
(
    guide_table.alias("t")
    .merge(guide_updates_df.select(guide_bookings_df.columns).alias("s"), MERGE_KEY)
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

# COMMAND ----------

# MAGIC %md
# MAGIC The table stayed intact (all or nothing). Expected result:
# MAGIC ```
# MAGIC 17
# MAGIC version  operation
# MAGIC 0        CREATE OR REPLACE TABLE AS SELECT
# MAGIC 1        MERGE
# MAGIC 2        OPTIMIZE
# MAGIC 3        MERGE
# MAGIC 4        OPTIMIZE
# MAGIC ```
# MAGIC Databricks adds the OPTIMIZE versions on its own after the MERGEs. If the notebook has been run more than once, there are more versions.

# COMMAND ----------

# Check: rows and history of the table after the failed MERGE
print(spark.table(GUIDE_BOOKINGS_TABLE).count())
display(spark.sql(f"DESCRIBE HISTORY {GUIDE_BOOKINGS_TABLE}").select("version", "operation").orderBy("version"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.9 Reusing Code: %run and the utils Notebook

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell contains only `%run ./utils` and shows only the opening text cell of `utils`. The `utils` notebook must be in the same folder as this notebook.

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC workspace.python_book.g_cancellations_destination_month
# MAGIC 20 30.0 [11670, 16317, 16225]
# MAGIC Help on function write_table in module __main__:
# MAGIC
# MAGIC write_table(df, table_name, mode='overwrite')
# MAGIC     Writes a DataFrame to a Delta table, then reads it back and prints its row count.
# MAGIC
# MAGIC ```

# COMMAND ----------

print(build_table_name("cancellations", "destination_month", layer="g"))
print(MIN_BOOKINGS, CANCELLATION_RATE_THRESHOLD, GUIDE_PROPERTY_IDS)
help(write_table)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.10 A Complete Example in Four Steps

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC Writing workspace.python_book.g_cancellations_destination_month (mode=overwrite)
# MAGIC Rows in the table: 317
# MAGIC ```

# COMMAND ----------

# 1. Read: bookings without repeated rows, with negative amounts turned into NULL
clean_bookings_df = read_clean_bookings()
property_places_df = spark.table(PROPERTIES_TABLE).select("property_id", "destination_id")
destination_names_df = spark.table(DESTINATIONS_TABLE).select("destination_id", "destination", "country")

# 2. Transform: the Chapter 9 report, with the revenue
report_df = (
    clean_bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .select("booking_id", "property_id", "check_in", "status", "total_amount")
    .join(property_places_df, on="property_id", how="inner")
    .join(destination_names_df, on="destination_id", how="inner")
    .withColumn("check_in_month", F.month(F.col("check_in")))
    .groupBy("destination", "country", "check_in_month")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .withColumn("cancellation_status", cancellation_status_column())
)

# 3. Write
write_table(report_df, CANCELLATION_REPORT_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC cancellation_status  combination_count
# MAGIC critical             8
# MAGIC not assessable       152
# MAGIC ok                   157
# MAGIC ```

# COMMAND ----------

# 4. Check: reading back the table that was written
report_table_df = spark.table(CANCELLATION_REPORT_TABLE)
display(
    report_table_df
    .groupBy("cancellation_status")
    .agg(F.count("*").alias("combination_count"))
    .orderBy("cancellation_status")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Independent check in SQL: the two rows must match. Expected result:
# MAGIC ```
# MAGIC source      booking_count  cancelled_count  revenue
# MAGIC g_ table    13586          2647             7477734.15
# MAGIC b_bookings  13586          2647             7477734.15
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'g_ table' AS source,
# MAGIC        SUM(booking_count)   AS booking_count,
# MAGIC        SUM(cancelled_count) AS cancelled_count,
# MAGIC        ROUND(SUM(revenue), 2) AS revenue
# MAGIC FROM workspace.python_book.g_cancellations_destination_month
# MAGIC UNION ALL
# MAGIC SELECT 'b_bookings' AS source,
# MAGIC        COUNT(*),
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END),
# MAGIC        ROUND(SUM(CASE WHEN total_amount >= 0 THEN total_amount END), 2)
# MAGIC FROM (SELECT DISTINCT * FROM workspace.python_book.b_bookings)
# MAGIC WHERE year(check_in) = 2024

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result:
# MAGIC ```
# MAGIC destination  country               check_in_month  booking_count  cancelled_count  revenue   cancellation_rate  cancellation_status
# MAGIC Cairo        Egypt                 9               35             13               18543.88  37.1               critical
# MAGIC London       United Kingdom        9               35             13               20159.36  37.1               critical
# MAGIC Madrid       Spain                 4               21             7                12162.47  33.3               critical
# MAGIC London       United Kingdom        11              37             12               21052.88  32.4               critical
# MAGIC Dubai        United Arab Emirates  3               25             8                14315.84  32                 critical
# MAGIC Barcelona    Spain                 8               44             14               25647.98  31.8               critical
# MAGIC Cairo        Egypt                 12              45             14               27447.89  31.1               critical
# MAGIC Byron Bay    Australia             8               53             16               27598.21  30.2               critical
# MAGIC ```

# COMMAND ----------

display(
    report_table_df
    .filter(F.col("cancellation_status") == "critical")
    .orderBy(F.col("cancellation_rate").desc(), "destination", "check_in_month")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10.11 Common Mistakes with Tables

# COMMAND ----------

# MAGIC %md
# MAGIC The following cell must fail (saveAsTable doesn't return a DataFrame).

# COMMAND ----------

# INTENTIONAL ERROR – saveAsTable doesn't return a DataFrame
result_df = daily_amounts_df.write.mode("overwrite").saveAsTable(DAILY_BOOKINGS_TABLE)
print(result_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the write isn't assigned; read the table back. Expected result: `90`.

# COMMAND ----------

# Fix: read back the table that was written
print(spark.table(DAILY_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Errors That Produce No Messages
# MAGIC
# MAGIC
# MAGIC Three errors in this chapter can't be shown with a cell, because they give no messages, and it's worth knowing them before you run into them.
# MAGIC
# MAGIC - **Writing to a reference table.** A wrong constant in a write, for example `BOOKINGS_TABLE` instead of a constant built with `build_table_name`, overwrites the teaching copy `b_bookings` without any warning (section 10.3). The remedy is to run `L00_Prepare_Data` again; the prevention is to use in writes only the constants of your own notebook, and to reread carefully the line printed before every write.
# MAGIC - **Modifying `utils` without running `%run` again.** The notebook keeps using the definitions loaded before the change (section 10.9). After every change to `utils`, and after every restart of the compute, run the `%run ./utils` cell again.
# MAGIC - **Running a cell with `append` again.** It's the error from section 10.5, the most frequent of the three: rows repeated silently. You prevent it with `overwrite` in re-runnable notebooks and you discover it by comparing `count()` with `distinct().count()`, or with the history.
# MAGIC
# MAGIC If the `%run` cell doesn't find the notebook, because `utils` isn't in the same folder or the name is spelled differently, the command stops with a message saying that the notebook wasn't found: check the path and the folder. If instead the `%run` cell hasn't been run, the functions of `utils` don't exist, and the first one you use produces a `NameError` from Chapter 6, for example `NameError: name 'write_table' is not defined`.
# MAGIC
# MAGIC ## Common Mistakes
# MAGIC
# MAGIC | Type of error | Typical message | Meaning | First thing to check |
# MAGIC | --- | --- | --- | --- |
# MAGIC | `TABLE_OR_VIEW_NOT_FOUND` | ``The table or view `...` cannot be found`` | the table to read doesn't exist | the name in the constant; Catalog Explorer |
# MAGIC | `TABLE_OR_VIEW_ALREADY_EXISTS` | ``Cannot create table or view `...` because it already exists`` | `saveAsTable` without a mode on an existing table | `mode("overwrite")` or `mode("append")` |
# MAGIC | `UNSUPPORTED_OPERATION` | `overwrites is not supported` | a misspelled mode | the text of the mode: `"overwrite"`, `"append"` |
# MAGIC | `DELTA_METADATA_MISMATCH` | `A schema mismatch detected when writing to the Delta table` | the DataFrame has columns or types different from the table | `Table schema` and `Data schema` in the message; a new table |
# MAGIC | `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` | `multiple source rows matched ... the same target row` | the source of the `MERGE` has more than one row per key | rows versus distinct keys of the source; the rule for choosing the row |
# MAGIC | `AttributeError` | `'NoneType' object has no attribute 'count'` | the result of a write used as a DataFrame | the write isn't assigned; read it back with `spark.table` |
# MAGIC | `NameError` | `name 'write_table' is not defined` | `utils` not loaded | the `%run ./utils` cell |
# MAGIC | (no error) | repeated rows, inflated sums | an `append` run again | `count()` versus `distinct().count()`; `DESCRIBE HISTORY` |
# MAGIC | (no error) | a reference table that changed | a write with the wrong constant | the line printed before the write; `L00_Prepare_Data` |
# MAGIC | (no error) | a fix to `utils` that has no effect | `%run` not run again | run the `%run ./utils` cell again |
