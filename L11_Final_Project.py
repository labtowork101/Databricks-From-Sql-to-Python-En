# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 11 – Final Project
# MAGIC
# MAGIC Notebook for Chapter 11 of *Beyond SELECT*. Goals: profile, clean, update with a `MERGE`, aggregate, and check the 2024 bookings, up to the `g_updated_cancellations_destination_month` report.
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run; the `utils` notebook in the same `Python_Book` folder. The notebook **writes tables** in the `workspace.python_book` schema: `s_clean_bookings_booking`, `s_clean_updates_booking`, `g_updated_cancellations_destination_month`.
# MAGIC
# MAGIC Run **one cell at a time**, from top to bottom: section 11.12 contains cells that must fail (**INTENTIONAL ERROR**) or that produce a wrong result (**SILENT ERROR**), each with its fix in the cell right below; some of them write to the clean table and repair it. Don't use Run all. If the compute stops, run the `%run ./utils` cell, the constants cell, and the cells that create the variables used further on again.
# MAGIC
# MAGIC The expected results are those of the notebook's **first run**; if you run it again, only the history changes (more versions) and, if you run the `MERGE` cell again by itself, its counters (`9133 9133 0 0`).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Introduction

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Setup Cell

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC workspace.python_book.s_clean_bookings_booking
# MAGIC workspace.python_book.s_clean_updates_booking
# MAGIC workspace.python_book.g_updated_cancellations_destination_month
# MAGIC ```

# COMMAND ----------

# Chapter constants: the tables the project writes and the MERGE key
CLEAN_BOOKINGS_TABLE = build_table_name("clean_bookings", "booking")
CLEAN_UPDATES_TABLE = build_table_name("clean_updates", "booking")
PROJECT_REPORT_TABLE = build_table_name("updated_cancellations", "destination_month", layer="g")
MERGE_KEY = "t.booking_id = s.booking_id"

# Lookup tables, read once
properties_df = spark.table(PROPERTIES_TABLE)
destinations_df = spark.table(DESTINATIONS_TABLE)

print(CLEAN_BOOKINGS_TABLE)
print(CLEAN_UPDATES_TABLE)
print(PROJECT_REPORT_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.1 Reading and Profiling the Bookings

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC rows                        13626
# MAGIC distinct rows               13586
# MAGIC keys (booking_id)           13586
# MAGIC missing amount                 30
# MAGIC negative amount                12
# MAGIC swapped dates                   8
# MAGIC unknown property                0
# MAGIC ```

# COMMAND ----------

bookings_2024_df = (
    spark.table(BOOKINGS_TABLE)
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
known_properties_df = properties_df.select("property_id").withColumn("is_known_property", F.lit(True))

booking_profile = {
    "rows": bookings_2024_df.count(),
    "distinct rows": bookings_2024_df.distinct().count(),
    "keys (booking_id)": bookings_2024_df.select("booking_id").distinct().count(),
    "missing amount": bookings_2024_df.filter(F.col("total_amount").isNull()).count(),
    "negative amount": bookings_2024_df.filter(F.col("total_amount") < 0).count(),
    "swapped dates": bookings_2024_df.filter(F.col("check_out") < F.col("check_in")).count(),
    "unknown property": (
        bookings_2024_df
        .join(known_properties_df, on="property_id", how="left")
        .filter(F.col("is_known_property").isNull())
        .count()
    ),
}

for check_name, value in booking_profile.items():
    print(f"{check_name:<25}{value:>8}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Distinct Rows and Keys

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)                                                 AS row_count,
# MAGIC        (SELECT COUNT(*) FROM (SELECT DISTINCT *
# MAGIC                               FROM workspace.python_book.b_bookings
# MAGIC                               WHERE year(check_in) = 2024))     AS distinct_row_count,
# MAGIC        COUNT(DISTINCT booking_id)                               AS key_count,
# MAGIC        SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END)    AS missing_amount,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END)        AS negative_amount,
# MAGIC        SUM(CASE WHEN check_out < check_in THEN 1 ELSE 0 END)    AS inverted_dates
# MAGIC FROM workspace.python_book.b_bookings
# MAGIC WHERE year(check_in) = 2024

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.2 Profiling the Updates

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC rows                        15820
# MAGIC distinct rows               15820
# MAGIC keys (booking_id)            9133
# MAGIC ties on updated_at             57
# MAGIC missing amount                  0
# MAGIC negative amount                 4
# MAGIC swapped dates                   0
# MAGIC new bookings                    4
# MAGIC ```

# COMMAND ----------

updates_2024_df = (
    spark.table(BOOKING_UPDATES_TABLE)
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
ties_df = (
    updates_2024_df
    .groupBy("booking_id", "updated_at")
    .agg(F.count("*").alias("row_count"))
    .filter(F.col("row_count") > 1)
)
known_bookings_df = bookings_2024_df.select("booking_id").distinct().withColumn("is_known_booking", F.lit(True))

update_profile = {
    "rows": updates_2024_df.count(),
    "distinct rows": updates_2024_df.distinct().count(),
    "keys (booking_id)": updates_2024_df.select("booking_id").distinct().count(),
    "ties on updated_at": ties_df.count(),
    "missing amount": updates_2024_df.filter(F.col("total_amount").isNull()).count(),
    "negative amount": updates_2024_df.filter(F.col("total_amount") < 0).count(),
    "swapped dates": updates_2024_df.filter(F.col("check_out") < F.col("check_in")).count(),
    "new bookings": (
        updates_2024_df
        .join(known_bookings_df, on="booking_id", how="left")
        .filter(F.col("is_known_booking").isNull())
        .select("booking_id")
        .distinct()
        .count()
    ),
}

for check_name, value in update_profile.items():
    print(f"{check_name:<25}{value:>8}")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC booking_id  booking_update_id  status     total_amount      updated_at
# MAGIC 2563        17570289891300     pending    776.260009765625  2024-07-13T23:59:59.000+00:00
# MAGIC 2563        17570289907102     cancelled  776.260009765625  2024-07-13T23:59:59.000+00:00
# MAGIC ```

# COMMAND ----------

display(
    updates_2024_df
    .filter(F.col("booking_id") == 2563)
    .select("booking_id", "booking_update_id", "status", "total_amount", "updated_at")
    .orderBy("booking_update_id")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.3 The Cleaning Rules

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Tracking Columns

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.4 The Rules in a Function

# COMMAND ----------

def quality_note_column():
    """Quality note of a booking, calculated on the values not yet corrected."""
    return (
        F.when(F.col("total_amount").isNull(), "missing amount")
        .when(F.col("total_amount") < 0, "negative amount")
        .when(F.col("check_out") < F.col("check_in"), "swapped dates")
        .otherwise("ok")
    )

# COMMAND ----------

def clean_booking_values(df, source):
    """Applies the project's cleaning rules to a DataFrame of bookings.

    Adds quality_note (calculated before the corrections) and source;
    swaps check_in and check_out if they are inverted; rounds the amount
    to 2 decimal places as a double and makes negative amounts NULL.
    """
    dates_inverted = F.col("check_out") < F.col("check_in")
    rounded_amount = F.round(F.col("total_amount").cast("double"), 2)
    return (
        df
        .withColumn("quality_note", quality_note_column())
        .select(
            "booking_id",
            "user_id",
            "property_id",
            F.when(dates_inverted, F.col("check_out")).otherwise(F.col("check_in")).alias("check_in"),
            F.when(dates_inverted, F.col("check_in")).otherwise(F.col("check_out")).alias("check_out"),
            "guests_count",
            F.when(rounded_amount >= 0, rounded_amount).alias("total_amount"),
            "status",
            "created_at",
            "updated_at",
            "quality_note",
            F.lit(source).alias("source"),
        )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC quality_note     booking_count
# MAGIC missing amount   30
# MAGIC negative amount  12
# MAGIC ok               13536
# MAGIC swapped dates    8
# MAGIC ```

# COMMAND ----------

clean_bookings_df = (
    clean_booking_values(spark.table(BOOKINGS_TABLE).distinct(), "original")
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
display(
    clean_bookings_df
    .groupBy("quality_note")
    .agg(F.count("*").alias("booking_count"))
    .orderBy("quality_note")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.5 Writing the Clean Table

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_clean_bookings_booking (mode=overwrite)
# MAGIC Rows in the table: 13,586
# MAGIC ```

# COMMAND ----------

write_table(clean_bookings_df, CLEAN_BOOKINGS_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC rows                        13586   13586  OK
# MAGIC keys (booking_id)           13586   13586  OK
# MAGIC negative amount                 0       0  OK
# MAGIC swapped dates                   0       0  OK
# MAGIC ```

# COMMAND ----------

clean_table_df = spark.table(CLEAN_BOOKINGS_TABLE)
clean_checks = {
    "rows": (clean_table_df.count(), booking_profile["keys (booking_id)"]),
    "keys (booking_id)": (clean_table_df.select("booking_id").distinct().count(), booking_profile["keys (booking_id)"]),
    "negative amount": (clean_table_df.filter(F.col("total_amount") < 0).count(), 0),
    "swapped dates": (clean_table_df.filter(F.col("check_out") < F.col("check_in")).count(), 0),
}

for check_name, (value, expected) in clean_checks.items():
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    print(f"{check_name:<25}{value:>8}{expected:>8}  {outcome}")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS booking_count,
# MAGIC        SUM(CASE WHEN c.check_in <> o.check_in OR c.check_out <> o.check_out THEN 1 ELSE 0 END) AS different_dates
# MAGIC FROM workspace.python_book.s_clean_bookings_booking c
# MAGIC JOIN samples.wanderbricks.bookings o USING (booking_id)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.6 One Row per Booking: Versions and Ties

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 9188 9133
# MAGIC ```

# COMMAND ----------

last_update_df = (
    updates_2024_df
    .groupBy("booking_id")
    .agg(F.max("updated_at").alias("last_updated_at"))
)
latest_updates_df = (
    updates_2024_df
    .join(last_update_df, on="booking_id", how="inner")
    .filter(F.col("updated_at") == F.col("last_updated_at"))
)
print(latest_updates_df.count(), latest_updates_df.select("booking_id").distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 9133 9133
# MAGIC ```

# COMMAND ----------

last_update_id_df = (
    latest_updates_df
    .groupBy("booking_id")
    .agg(F.max("booking_update_id").alias("booking_update_id"))
)
chosen_updates_df = latest_updates_df.join(
    last_update_id_df,
    on=["booking_id", "booking_update_id"],
    how="inner",
)
print(chosen_updates_df.count(), chosen_updates_df.select("booking_id").distinct().count())

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH updates_2024 AS (
# MAGIC   SELECT * FROM samples.wanderbricks.booking_updates WHERE year(check_in) = 2024
# MAGIC ),
# MAGIC last_update AS (
# MAGIC   SELECT booking_id, MAX(updated_at) AS updated_at FROM updates_2024 GROUP BY booking_id
# MAGIC ),
# MAGIC latest AS (
# MAGIC   SELECT * FROM updates_2024 JOIN last_update USING (booking_id, updated_at)
# MAGIC ),
# MAGIC last_update_id AS (
# MAGIC   SELECT booking_id, MAX(booking_update_id) AS booking_update_id FROM latest GROUP BY booking_id
# MAGIC )
# MAGIC SELECT COUNT(*) AS row_count, COUNT(DISTINCT booking_id) AS key_count
# MAGIC FROM latest JOIN last_update_id USING (booking_id, booking_update_id)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC booking_id  booking_update_id  status     updated_at
# MAGIC 2563        17570289907102     cancelled  2024-07-13T23:59:59.000+00:00
# MAGIC ```

# COMMAND ----------

display(
    chosen_updates_df
    .filter(F.col("booking_id") == 2563)
    .select("booking_id", "booking_update_id", "status", "updated_at")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (the two lines from `write_table`, then the grid, then `True`):
# MAGIC ```
# MAGIC Writing workspace.python_book.s_clean_updates_booking (mode=overwrite)
# MAGIC Rows in the table: 9,133
# MAGIC
# MAGIC quality_note     booking_count
# MAGIC negative amount  1
# MAGIC ok               9132
# MAGIC
# MAGIC True
# MAGIC ```

# COMMAND ----------

clean_updates_df = clean_booking_values(chosen_updates_df, "update")
write_table(clean_updates_df, CLEAN_UPDATES_TABLE)
display(
    spark.table(CLEAN_UPDATES_TABLE)
    .groupBy("quality_note")
    .agg(F.count("*").alias("booking_count"))
    .orderBy("quality_note")
)
print(spark.table(CLEAN_UPDATES_TABLE).columns == spark.table(CLEAN_BOOKINGS_TABLE).columns)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.7 Applying the Updates: The MERGE

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC num_affected_rows  num_updated_rows  num_deleted_rows  num_inserted_rows
# MAGIC 9133               9129              0                 4
# MAGIC ```

# COMMAND ----------

merge_query = f"""
MERGE INTO {CLEAN_BOOKINGS_TABLE} AS t
USING {CLEAN_UPDATES_TABLE} AS s
ON {MERGE_KEY}
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
display(spark.sql(merge_query))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 13590 13590
# MAGIC ```
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC source    quality_note     booking_count
# MAGIC original  missing amount   13
# MAGIC original  negative amount  2
# MAGIC original  ok               4440
# MAGIC original  swapped dates    2
# MAGIC update    negative amount  1
# MAGIC update    ok               9132
# MAGIC ```

# COMMAND ----------

merged_df = spark.table(CLEAN_BOOKINGS_TABLE)
print(merged_df.count(), merged_df.select("booking_id").distinct().count())
display(
    merged_df
    .groupBy("source", "quality_note")
    .agg(F.count("*").alias("booking_count"))
    .orderBy("source", "quality_note")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC status     before_merge  after_merge
# MAGIC cancelled  2647          5123
# MAGIC completed  1433          7090
# MAGIC confirmed  3491          1156
# MAGIC pending    6015          221
# MAGIC ```

# COMMAND ----------

before_df = clean_bookings_df.groupBy("status").agg(F.count("*").alias("before_merge"))
after_df = merged_df.groupBy("status").agg(F.count("*").alias("after_merge"))
display(before_df.join(after_df, on="status", how="inner").orderBy("status"))

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status, before_merge, after_merge
# MAGIC FROM (SELECT status, COUNT(*) AS before_merge
# MAGIC       FROM (SELECT DISTINCT * FROM workspace.python_book.b_bookings)
# MAGIC       WHERE year(CASE WHEN check_out < check_in THEN check_out ELSE check_in END) = 2024
# MAGIC       GROUP BY status)
# MAGIC JOIN (SELECT status, COUNT(*) AS after_merge
# MAGIC       FROM workspace.python_book.s_clean_bookings_booking
# MAGIC       GROUP BY status)
# MAGIC USING (status)
# MAGIC ORDER BY status

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.8 The Report

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Writing workspace.python_book.g_updated_cancellations_destination_month (mode=overwrite)
# MAGIC Rows in the table: 317
# MAGIC ```

# COMMAND ----------

report_df = (
    spark.table(CLEAN_BOOKINGS_TABLE)
    .select("booking_id", "property_id", "check_in", "status", "total_amount")
    .join(properties_df.select("property_id", "destination_id"), on="property_id", how="inner")
    .join(destinations_df.select("destination_id", "destination", "country"), on="destination_id", how="inner")
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
write_table(report_df, PROJECT_REPORT_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC cancellation_status  combination_count
# MAGIC critical             147
# MAGIC not assessable       152
# MAGIC ok                   18
# MAGIC ```

# COMMAND ----------

report_table_df = spark.table(PROJECT_REPORT_TABLE)
display(
    report_table_df
    .groupBy("cancellation_status")
    .agg(F.count("*").alias("combination_count"))
    .orderBy("cancellation_status")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC destination  country  check_in_month  booking_count  cancelled_count  revenue  cancellation_rate  cancellation_status
# MAGIC Amalfi       Italy    6               13             6                7356     46.2               not assessable
# MAGIC Amalfi       Italy    7               9              3                6918.84  33.3               not assessable
# MAGIC Amalfi       Italy    8               20             10               11138.2  50                 critical
# MAGIC Amalfi       Italy    9               9              2                4090.92  22.2               not assessable
# MAGIC ```

# COMMAND ----------

display(report_table_df.filter(F.col("destination") == "Amalfi").orderBy("check_in_month"))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC destination  country         check_in_month  booking_count  cancelled_count  revenue   cancellation_rate  cancellation_status
# MAGIC Singapore    Singapore       4               20             11               10950.05  55                 critical
# MAGIC Ibiza        Spain           6               68             37               39895.55  54.4               critical
# MAGIC London       United Kingdom  11              37             20               21075.88  54.1               critical
# MAGIC Cairo        Egypt           10              30             16               15458.08  53.3               critical
# MAGIC Paris        France          4               54             28               27885.04  51.9               critical
# MAGIC ```

# COMMAND ----------

display(
    report_table_df
    .filter(F.col("cancellation_status") == "critical")
    .orderBy(F.col("cancellation_rate").desc(), "destination", "check_in_month")
    .limit(5)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Threshold Is a Decision

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC status_threshold_40  combination_count
# MAGIC critical             59
# MAGIC not assessable       152
# MAGIC ok                   106
# MAGIC ```

# COMMAND ----------

display(
    report_table_df
    .withColumn("status_threshold_40", cancellation_status_column(threshold=40.0))
    .groupBy("status_threshold_40")
    .agg(F.count("*").alias("combination_count"))
    .orderBy("status_threshold_40")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.9 The Independent Check

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 317 317 317 0
# MAGIC ```

# COMMAND ----------

check_query = f"""
SELECT d.destination,
       month(b.check_in)                                       AS check_in_month,
       COUNT(*)                                                AS chk_booking_count,
       SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS chk_cancelled_count,
       ROUND(SUM(b.total_amount), 2)                           AS chk_revenue
FROM {CLEAN_BOOKINGS_TABLE} b
JOIN {PROPERTIES_TABLE} p ON b.property_id = p.property_id
JOIN {DESTINATIONS_TABLE} d ON p.destination_id = d.destination_id
GROUP BY d.destination, month(b.check_in)
"""
check_df = spark.sql(check_query)

comparison_df = report_table_df.join(check_df, on=["destination", "check_in_month"], how="inner")
differences_df = comparison_df.filter(
    (F.col("booking_count") != F.col("chk_booking_count"))
    | (F.col("cancelled_count") != F.col("chk_cancelled_count"))
    | (F.col("revenue") != F.col("chk_revenue"))
)
print(report_table_df.count(), check_df.count(), comparison_df.count(), differences_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.10 The Final Checks and the History

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC rows = keys                 13590   13590  OK
# MAGIC rows = keys + new           13590   13590  OK
# MAGIC rows from updates            9133    9133  OK
# MAGIC negative amount                 0       0  OK
# MAGIC swapped dates                   0       0  OK
# MAGIC bookings in the report      13590   13590  OK
# MAGIC ```

# COMMAND ----------

final_checks = {
    "rows = keys": (merged_df.count(), merged_df.select("booking_id").distinct().count()),
    "rows = keys + new": (
        merged_df.count(),
        booking_profile["keys (booking_id)"] + update_profile["new bookings"],
    ),
    "rows from updates": (
        merged_df.filter(F.col("source") == "update").count(),
        update_profile["keys (booking_id)"],
    ),
    "negative amount": (merged_df.filter(F.col("total_amount") < 0).count(), 0),
    "swapped dates": (merged_df.filter(F.col("check_out") < F.col("check_in")).count(), 0),
    "bookings in the report": (
        report_table_df.agg(F.sum("booking_count")).collect()[0][0],
        merged_df.count(),
    ),
}

for check_name, (value, expected) in final_checks.items():
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    print(f"{check_name:<25}{value:>8}{expected:>8}  {outcome}")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC version  operation
# MAGIC 0        CREATE OR REPLACE TABLE AS SELECT
# MAGIC 1        MERGE
# MAGIC 2        OPTIMIZE
# MAGIC ```

# COMMAND ----------

display(
    spark.sql(f"DESCRIBE HISTORY {CLEAN_BOOKINGS_TABLE}")
    .select("version", "operation")
    .orderBy("version")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.11 A Re-runnable Notebook and a First Chart

# COMMAND ----------

# MAGIC %md
# MAGIC ### A First Chart

# COMMAND ----------

display(
    report_table_df
    .filter(F.col("country") == "Italy")
    .select("destination", "check_in_month", "booking_count", "cancellation_rate", "cancellation_status")
    .orderBy("destination", "check_in_month")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11.12 Common Mistakes in the Project

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Note Calculated After the Corrections

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC quality_note    booking_count
# MAGIC missing amount  42
# MAGIC ok              13544
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – the note is calculated after the values have been corrected
late_note_df = (
    clean_booking_values(spark.table(BOOKINGS_TABLE).distinct(), "original")
    .withColumn("quality_note", quality_note_column())
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
display(late_note_df.groupBy("quality_note").agg(F.count("*").alias("booking_count")).orderBy("quality_note"))

# COMMAND ----------

# Fix: the note calculated by the function, before the corrections
display(clean_bookings_df.groupBy("quality_note").agg(F.count("*").alias("booking_count")).orderBy("quality_note"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### A Filter Instead of the Rule

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 13544
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – the invalid amounts removed with a filter
filtered_df = (
    spark.table(BOOKINGS_TABLE)
    .distinct()
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .filter(F.col("total_amount") >= 0)
)
print(filtered_df.count())

# COMMAND ----------

# Fix: the invalid amounts become NULL, the bookings stay
print(clean_bookings_df.count(), clean_bookings_df.filter(F.col("total_amount").isNull()).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Swapping the Dates with Two withColumn Calls

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 8
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – the dates swapped with two withColumn calls
dates_inverted = F.col("check_out") < F.col("check_in")
swapped_df = (
    spark.table(BOOKINGS_TABLE)
    .distinct()
    .withColumn("check_in", F.when(dates_inverted, F.col("check_out")).otherwise(F.col("check_in")))
    .withColumn("check_out", F.when(dates_inverted, F.col("check_in")).otherwise(F.col("check_out")))
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
print(swapped_df.filter(F.col("check_in") == F.col("check_out")).count())

# COMMAND ----------

# Fix: the swap done in a single select, in the function
print(clean_bookings_df.filter(F.col("check_in") == F.col("check_out")).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### The MERGE with Ties

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the next cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message (summary line):
# MAGIC ```
# MAGIC [DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE] Cannot perform Merge as multiple source rows matched and attempted to modify the same
# MAGIC target row in the Delta table in possibly conflicting ways. By SQL semantics of Merge,
# MAGIC when multiple source rows match on the same target row, the result may be ambiguous
# MAGIC as it is unclear which source row should be used to update or delete the matching
# MAGIC target row. You can preprocess the source table to eliminate the possibility of
# MAGIC multiple matches. Please refer to
# MAGIC https://docs.databricks.com/delta/merge.html#merge-error
# MAGIC  SQLSTATE: 21506
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – the source still has the ties on the last update
clean_table = DeltaTable.forName(spark, CLEAN_BOOKINGS_TABLE)
(
    clean_table.alias("t")
    .merge(clean_booking_values(latest_updates_df, "update").alias("s"), MERGE_KEY)
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

# COMMAND ----------

# Fix: the source with one row per booking
(
    clean_table.alias("t")
    .merge(spark.table(CLEAN_UPDATES_TABLE).alias("s"), MERGE_KEY)
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)
print(spark.table(CLEAN_BOOKINGS_TABLE).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### A Check with the Same Names as the Report

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the next cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message (summary line):
# MAGIC ```
# MAGIC [AMBIGUOUS_REFERENCE] Reference `booking_count` is ambiguous, could be: [`booking_count`, `workspace`.`python_book`.`g_updated_cancellations_destination_month`.`booking_count`]. SQLSTATE: 42704
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – the columns of the check have the same names as the report
same_names_df = spark.sql(f"""
SELECT d.destination, month(b.check_in) AS check_in_month, COUNT(*) AS booking_count
FROM {CLEAN_BOOKINGS_TABLE} b
JOIN {PROPERTIES_TABLE} p ON b.property_id = p.property_id
JOIN {DESTINATIONS_TABLE} d ON p.destination_id = d.destination_id
GROUP BY d.destination, month(b.check_in)
""")
same_names_comparison_df = report_table_df.join(same_names_df, on=["destination", "check_in_month"], how="inner")
print(same_names_comparison_df.filter(F.col("booking_count") != F.col("booking_count")).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### An append Instead of the MERGE

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_clean_bookings_booking (mode=append)
# MAGIC Rows in the table: 22,723
# MAGIC 22723 13590
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – the updates added with append instead of with the MERGE
write_table(clean_updates_df, CLEAN_BOOKINGS_TABLE, mode="append")
appended_df = spark.table(CLEAN_BOOKINGS_TABLE)
print(appended_df.count(), appended_df.select("booking_id").distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Writing workspace.python_book.s_clean_bookings_booking (mode=overwrite)
# MAGIC Rows in the table: 13,586
# MAGIC +-----------------+----------------+----------------+-----------------+
# MAGIC |num_affected_rows|num_updated_rows|num_deleted_rows|num_inserted_rows|
# MAGIC +-----------------+----------------+----------------+-----------------+
# MAGIC |             9133|            9129|               0|                4|
# MAGIC +-----------------+----------------+----------------+-----------------+
# MAGIC
# MAGIC 13590 13590
# MAGIC ```

# COMMAND ----------

# Fix: the table rewritten from the source, then the MERGE
write_table(clean_bookings_df, CLEAN_BOOKINGS_TABLE)
spark.sql(merge_query).show()
repaired_df = spark.table(CLEAN_BOOKINGS_TABLE)
print(repaired_df.count(), repaired_df.select("booking_id").distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### An Error the Notebook Doesn't Show
