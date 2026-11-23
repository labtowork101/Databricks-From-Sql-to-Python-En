# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 10 – Exercise Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in `L10_Exercises` (also in Appendix A of the book).
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run; `utils` in the same folder. The notebook **writes tables** in the `workspace.python_book` schema.
# MAGIC Run one cell at a time, from top to bottom: the cells of exercise 8 marked **INTENTIONAL ERROR** must fail, and those marked **SILENT ERROR** produce a wrong result; the fix is in the cell below. Exercise 6 needs the `my_utils` notebook (its content is in the section of the exercise).
# MAGIC If the notebook has already been run, the history of exercise 4 shows more versions and the MERGE of exercise 7 no longer inserts rows (counters `5 5 0 0`).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC The first cell contains only `%run ./utils` and shows only the opening text cell of `utils`; the second defines the constants of the exercises. Expected result: `Setup complete`.

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# Setup cell: the tables the exercises write and the DataFrames of the source tables
ITALY_TABLE = build_table_name("italy_bookings", "destination_month")
QUARTER_TABLE = build_table_name("quarter_bookings", "daily")
TYPE_MONTH_TABLE = build_table_name("bookings_type", "month", layer="g")
ABU_DHABI_BOOKINGS_TABLE = build_table_name("abu_dhabi_properties", "bookings")
ABU_DHABI_UPDATES_TABLE = build_table_name("abu_dhabi_properties", "updates")

bookings_df = spark.table(SOURCE_BOOKINGS_TABLE)
properties_df = spark.table(PROPERTIES_TABLE)
destinations_df = spark.table(DESTINATIONS_TABLE)

print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – Reading with spark.table
# MAGIC 1. Read the `PROPERTIES_TABLE` and `DESTINATIONS_TABLE` tables with `spark.table()` and print, for each one, the number of rows and the number of columns (`len()` of the `columns` list).
# MAGIC 2. Print the comparison between the columns of `spark.table(PROPERTIES_TABLE)` and those of `spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")`.
# MAGIC 3. With `DESCRIBE DETAIL` on the `BOOKINGS_TABLE` table, print the value of the `format` column (hint: `collect()[0]["format"]`).

# COMMAND ----------

# Solution 1: spark.table, columns, DESCRIBE DETAIL
properties_table_df = spark.table(PROPERTIES_TABLE)
destinations_table_df = spark.table(DESTINATIONS_TABLE)
print(properties_table_df.count(), len(properties_table_df.columns))
print(destinations_table_df.count(), len(destinations_table_df.columns))
print(properties_table_df.columns == spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}").columns)
detail_row = spark.sql(f"DESCRIBE DETAIL {BOOKINGS_TABLE}").collect()[0]
print(detail_row["format"])

# COMMAND ----------

# Check: expected result
print("18163 13")
print("42 6")
print("True")
print("delta")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Table Names
# MAGIC 1. With `build_table_name`, build and print the names of two tables: the working data with the bookings summarized by property (topic `bookings`, granularity `property`) and the report for a dashboard with the revenue by country and year (topic `revenue`, granularity `country_year`, layer `g`).
# MAGIC 2. Print the five constants of the setup cell.
# MAGIC 3. In a comment, say which of these names follow the book's convention and why the others don't: `s_bookings_daily`, `S_Bookings`, `g-revenue-country-year`, `final_table`.

# COMMAND ----------

# Solution 2: names built with build_table_name
print(build_table_name("bookings", "property"))
print(build_table_name("revenue", "country_year", layer="g"))
print(ITALY_TABLE)
print(QUARTER_TABLE)
print(TYPE_MONTH_TABLE)
print(ABU_DHABI_BOOKINGS_TABLE)
print(ABU_DHABI_UPDATES_TABLE)
# s_bookings_daily: correct (prefix, topic, granularity; lowercase letters and underscores)
# S_Bookings: uppercase letters and missing granularity
# g-revenue-country-year: hyphens instead of underscores (not allowed in the book's names)
# final_table: the prefix is missing, the topic doesn't say what it's about, the granularity is missing

# COMMAND ----------

# Check: expected result
print("workspace.python_book.s_bookings_property")
print("workspace.python_book.g_revenue_country_year")
print("workspace.python_book.s_italy_bookings_destination_month")
print("workspace.python_book.s_quarter_bookings_daily")
print("workspace.python_book.g_bookings_type_month")
print("workspace.python_book.s_abu_dhabi_properties_bookings")
print("workspace.python_book.s_abu_dhabi_properties_updates")
print("Correct names: only s_bookings_daily")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Writing a Table
# MAGIC 1. Build the summary of the 2024 bookings of the Italian destinations (`country` = `Italy`) by destination and check-in month, with the columns `destination`, `country`, `check_in_month`, `booking_count`, and `cancelled_count`, in this order (bookings → properties → destinations, with `select` before the joins).
# MAGIC 2. Write it to the `ITALY_TABLE` table with `overwrite`, printing the name of the table first.
# MAGIC 3. Read the table back with `spark.table()` and print the number of rows.

# COMMAND ----------

# Solution 3: Italian summary by destination and month, written with overwrite
italy_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .select("booking_id", "property_id", "check_in", "status")
    .join(properties_df.select("property_id", "destination_id"), on="property_id", how="inner")
    .join(destinations_df.select("destination_id", "destination", "country"), on="destination_id", how="inner")
    .filter(F.col("country") == "Italy")
    .withColumn("check_in_month", F.month(F.col("check_in")))
    .groupBy("destination", "country", "check_in_month")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
    )
)
print(f"Writing {ITALY_TABLE}")
(
    italy_df.write
    .mode("overwrite")
    .saveAsTable(ITALY_TABLE)
)
print(spark.table(ITALY_TABLE).count())

# COMMAND ----------

# Check: totals of the table that was written (expected: 29 714 142)
display(spark.sql(f"""
    SELECT COUNT(*) AS row_count, SUM(booking_count) AS booking_count, SUM(cancelled_count) AS cancelled_count
    FROM {ITALY_TABLE}
"""))

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Independent check: 2024 bookings and cancellations in Italy (714, 142)
# MAGIC SELECT COUNT(*)                                                AS booking_count,
# MAGIC        SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
# MAGIC FROM samples.wanderbricks.bookings b
# MAGIC JOIN samples.wanderbricks.properties p USING (property_id)
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC WHERE year(b.check_in) = 2024 AND d.country = 'Italy'

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Append, Repair, and History
# MAGIC 1. Prepare `quarter_daily_df`, the daily summary of the first quarter of 2024 (`check_in`, `booking_count`, `cancelled_count`, rounded `revenue`), and write it to the `QUARTER_TABLE` table one month at a time: January with `overwrite`, February with `append`, March with `append`. Print the rows of the table.
# MAGIC 2. In a new cell, run the March `append` again (as if the cell had been run twice) and print `count()` and `distinct().count()` of the table.
# MAGIC 3. Repair the table with an `overwrite` of the complete quarter and print the two counts again.
# MAGIC 4. Show the history (`version`, `operation`, in order of version) and, with a loop and `VERSION AS OF`, the number of rows of versions 0 to 4.

# COMMAND ----------

# Solution 4a: the quarter one month at a time (January overwrite, February and March append)
quarter_daily_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .filter(F.month(F.col("check_in")) <= 3)
    .groupBy("check_in")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
)
print(f"Writing {QUARTER_TABLE}")
(
    quarter_daily_df.filter(F.month(F.col("check_in")) == 1).write
    .mode("overwrite")
    .saveAsTable(QUARTER_TABLE)
)
(
    quarter_daily_df.filter(F.month(F.col("check_in")) == 2).write
    .mode("append")
    .saveAsTable(QUARTER_TABLE)
)
(
    quarter_daily_df.filter(F.month(F.col("check_in")) == 3).write
    .mode("append")
    .saveAsTable(QUARTER_TABLE)
)
print(spark.table(QUARTER_TABLE).count())

# COMMAND ----------

# Solution 4b: the March append run again by mistake, discovered with count and distinct
(
    quarter_daily_df.filter(F.month(F.col("check_in")) == 3).write
    .mode("append")
    .saveAsTable(QUARTER_TABLE)
)
quarter_table_df = spark.table(QUARTER_TABLE)
print(quarter_table_df.count(), quarter_table_df.distinct().count())

# COMMAND ----------

# Solution 4c: repair with an overwrite of the complete quarter
print(f"Writing {QUARTER_TABLE}")
(
    quarter_daily_df.write
    .mode("overwrite")
    .saveAsTable(QUARTER_TABLE)
)
quarter_table_df = spark.table(QUARTER_TABLE)
print(quarter_table_df.count(), quarter_table_df.distinct().count())

# COMMAND ----------

# Solution 4d: history and rows of each version
display(spark.sql(f"DESCRIBE HISTORY {QUARTER_TABLE}").select("version", "operation").orderBy("version"))
for version in range(5):
    version_query = f"SELECT COUNT(*) AS row_count FROM {QUARTER_TABLE} VERSION AS OF {version}"
    print(version, spark.sql(version_query).collect()[0]["row_count"])

# COMMAND ----------

# Check: expected result (on the first run of the exercise)
print("item 1: 90")
print("item 2: 121 90")
print("item 3: 90 90")
print("item 4: versions 0 CREATE OR REPLACE TABLE AS SELECT, 1 WRITE, 2 WRITE, 3 WRITE, 4 CREATE OR REPLACE TABLE AS SELECT")
print("        rows: 0 30 / 1 59 / 2 90 / 3 121 / 4 90")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Report with write_table
# MAGIC 1. Build the 2024 report by property type and check-in month with `property_type`, `check_in_month`, `booking_count`, `cancelled_count`, `cancellation_rate` (in %, one decimal place), and `cancellation_status` (with `cancellation_status_column()` from `utils`).
# MAGIC 2. Write it to the `TYPE_MONTH_TABLE` table with `write_table`.
# MAGIC 3. Reading the table back, count the rows by status (`combination_count`), in alphabetical order of status.

# COMMAND ----------

# Solution 5: report by property type and month, written with write_table
type_month_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .select("booking_id", "property_id", "check_in", "status")
    .join(properties_df.select("property_id", "property_type"), on="property_id", how="inner")
    .withColumn("check_in_month", F.month(F.col("check_in")))
    .groupBy("property_type", "check_in_month")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .withColumn("cancellation_status", cancellation_status_column())
)
write_table(type_month_df, TYPE_MONTH_TABLE)
display(
    spark.table(TYPE_MONTH_TABLE)
    .groupBy("cancellation_status")
    .agg(F.count("*").alias("combination_count"))
    .orderBy("cancellation_status")
)

# COMMAND ----------

# Check: expected result
print("Writing workspace.python_book.g_bookings_type_month (mode=overwrite)")
print("Rows in the table: 32")
print("cancellation_status  combination_count")
print("not assessable       2")
print("ok                   30")

# COMMAND ----------

# SQL check: totals of the table (expected: 32 13586 2647)
display(spark.sql(f"""
    SELECT COUNT(*) AS row_count, SUM(booking_count) AS booking_count, SUM(cancelled_count) AS cancelled_count
    FROM {TYPE_MONTH_TABLE}
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – A Personal Notebook with %run
# MAGIC 1. In the `Python_Book` folder, create a notebook called `my_utils` (**Create → Notebook**) and write the following code in a cell:
# MAGIC ```python
# MAGIC # my_utils notebook: personal constants and functions (loaded after utils)
# MAGIC MY_PROPERTY_ID = 16225
# MAGIC
# MAGIC
# MAGIC def count_property_bookings(property_id, year=ANALYSIS_YEAR):
# MAGIC     """Counts the bookings of a property with check-in in the given year."""
# MAGIC     return (
# MAGIC         spark.table(SOURCE_BOOKINGS_TABLE)
# MAGIC         .filter((F.col("property_id") == property_id) & (F.year(F.col("check_in")) == year))
# MAGIC         .count()
# MAGIC     )
# MAGIC ```
# MAGIC 2. Run the `%run ./my_utils` cell below (the `%run ./utils` cell must already have been run: `my_utils` uses `F`, `SOURCE_BOOKINGS_TABLE`, and `ANALYSIS_YEAR`).
# MAGIC 3. Print `MY_PROPERTY_ID` with its count, and the counts of properties `11670` and `16317`.
# MAGIC 4. In `my_utils`, change the value of `MY_PROPERTY_ID` to `11670`. **Without** running the `%run` cell again, print `MY_PROPERTY_ID`; then run the second `%run ./my_utils` cell and print it again. At the end, set `my_utils` back to the value `16225`.

# COMMAND ----------

# MAGIC %run ./my_utils

# COMMAND ----------

# Solution 6a: the definitions of my_utils
print(MY_PROPERTY_ID, count_property_bookings(MY_PROPERTY_ID))
print(11670, count_property_bookings(11670))
print(16317, count_property_bookings(16317))

# COMMAND ----------

# Solution 6b: after changing MY_PROPERTY_ID in my_utils, without running %run again
print(MY_PROPERTY_ID)

# COMMAND ----------

# MAGIC %run ./my_utils

# COMMAND ----------

# Solution 6c: after running the %run ./my_utils cell again
print(MY_PROPERTY_ID, count_property_bookings(MY_PROPERTY_ID))

# COMMAND ----------

# Check: expected result
print("16225 4")
print("11670 6")
print("16317 7")
print("after the change, without %run: 16225")
print("after running %run again: 11670 6")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – A MERGE with Inserts
# MAGIC Properties `16047` and `5134`, in Abu Dhabi, have updates for 2024 bookings that don't appear in `bookings`.
# MAGIC 1. Write to the `ABU_DHABI_BOOKINGS_TABLE` table (with `write_table`) the 2024 bookings of the two properties taken from `bookings_df`.
# MAGIC 2. Read the 2024 updates of the two properties from `BOOKING_UPDATES_TABLE` and print the rows and the distinct bookings; choose the most recent update for each booking (as in section 10.8), with the columns of the target table; print the rows and the distinct keys; write the result to `ABU_DHABI_UPDATES_TABLE`.
# MAGIC 3. Run the `MERGE` in SQL with `spark.sql()` (`UPDATE SET *`, `INSERT *`, key `booking_id`) and show its counters.
# MAGIC 4. Show the final table (`booking_id`, `property_id`, `check_in`, `status`, `total_amount`, in order of `booking_id`) and, with `agg`, the number of bookings, the number of canceled ones, and the rounded revenue.

# COMMAND ----------

# Solution 7a: the target table with the 2024 bookings of the two properties
abu_dhabi_bookings_df = (
    bookings_df
    .filter((F.col("property_id") == 16047) | (F.col("property_id") == 5134))
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
write_table(abu_dhabi_bookings_df, ABU_DHABI_BOOKINGS_TABLE)

# COMMAND ----------

# Solution 7b: the most recent update per booking, with the rows = keys check
abu_dhabi_updates_df = (
    spark.table(BOOKING_UPDATES_TABLE)
    .filter((F.col("property_id") == 16047) | (F.col("property_id") == 5134))
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
print(abu_dhabi_updates_df.count(), abu_dhabi_updates_df.select("booking_id").distinct().count())
abu_dhabi_last_df = (
    abu_dhabi_updates_df
    .groupBy("booking_id")
    .agg(F.max("updated_at").alias("last_updated_at"))
)
abu_dhabi_latest_df = (
    abu_dhabi_updates_df
    .join(abu_dhabi_last_df, on="booking_id", how="inner")
    .filter(F.col("updated_at") == F.col("last_updated_at"))
    .select(abu_dhabi_bookings_df.columns)
)
print(abu_dhabi_latest_df.count(), abu_dhabi_latest_df.select("booking_id").distinct().count())
write_table(abu_dhabi_latest_df, ABU_DHABI_UPDATES_TABLE)

# COMMAND ----------

# Solution 7c: the MERGE in SQL and its counters
abu_dhabi_merge_query = f"""
MERGE INTO {ABU_DHABI_BOOKINGS_TABLE} AS t
USING {ABU_DHABI_UPDATES_TABLE} AS s
ON t.booking_id = s.booking_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
display(spark.sql(abu_dhabi_merge_query))

# COMMAND ----------

# Solution 7d: the table after the MERGE
abu_dhabi_table_df = spark.table(ABU_DHABI_BOOKINGS_TABLE)
display(abu_dhabi_table_df.select("booking_id", "property_id", "check_in", "status", "total_amount").orderBy("booking_id"))
display(
    abu_dhabi_table_df.agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
)

# COMMAND ----------

# Check: expected result (on the first run of the MERGE)
print("item 1: Rows in the table: 4")
print("item 2: 8 5, then 5 5; Rows in the table: 5")
print("item 3: num_affected_rows 5, num_updated_rows 3, num_deleted_rows 0, num_inserted_rows 2")
print("item 4:")
print("booking_id  property_id  check_in    status     total_amount")
print("682         16047        2024-12-24  completed  834.57")
print("3985        5134         2024-05-13  completed  664.28")
print("48985       16047        2024-09-04  completed  493.94")
print("51744       16047        2024-10-24  cancelled  486.32")
print("72662       16047        2024-12-10  cancelled  100.16")
print("72668       5134         2024-10-07  cancelled  695.94")
print("booking_count 6, cancelled_count 3, revenue 3275.21")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one by one, note the type of the error and the message (or the wrong result), and write the corrected version below. The cells use the tables of exercises 3 and 7; the first three write a copy of the Italian summary to the `ITALY_COPY_TABLE` table, defined in cell 8a.
# MAGIC
# MAGIC **Expected result of the fixes**: cells 8a, 8b, 8c, 8e, and 8f write or read back `29` rows; the corrected `MERGE` of cell 8d, run after exercise 7, updates `5` rows and inserts none (the table stays at `6` rows).

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (a copy of the Italian summary)
ITALY_COPY_TABLE = build_table_name("italy_bookings_copy", "destination_month")
italy_df = spark.table(ITALY_TABLE)
(
    italy_df.write
    .mode("replace")
    .saveAsTable(ITALY_COPY_TABLE)
)

# COMMAND ----------

# Fix 8a (UNSUPPORTED_OPERATION: the mode is written "overwrite")
ITALY_COPY_TABLE = build_table_name("italy_bookings_copy", "destination_month")
italy_df = spark.table(ITALY_TABLE)
(
    italy_df.write
    .mode("overwrite")
    .saveAsTable(ITALY_COPY_TABLE)
)
print(spark.table(ITALY_COPY_TABLE).count())

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b (the destinations of the copy)
result_df = italy_df.write.mode("overwrite").saveAsTable(ITALY_COPY_TABLE)
display(result_df.orderBy("destination"))

# COMMAND ----------

# Fix 8b (AttributeError: saveAsTable returns None; read the table back)
italy_df.write.mode("overwrite").saveAsTable(ITALY_COPY_TABLE)
display(spark.table(ITALY_COPY_TABLE).orderBy("destination"))

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c (the copy written again)
italy_df.write.saveAsTable(ITALY_COPY_TABLE)

# COMMAND ----------

# Fix 8c (TABLE_OR_VIEW_ALREADY_EXISTS: always specify the mode)
italy_df.write.mode("overwrite").saveAsTable(ITALY_COPY_TABLE)
print(spark.table(ITALY_COPY_TABLE).count())

# COMMAND ----------

# INTENTIONAL ERROR – cell 8d (the Abu Dhabi MERGE with all the updates)
abu_dhabi_updates_df = (
    spark.table(BOOKING_UPDATES_TABLE)
    .filter((F.col("property_id") == 16047) | (F.col("property_id") == 5134))
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
abu_dhabi_table = DeltaTable.forName(spark, ABU_DHABI_BOOKINGS_TABLE)
(
    abu_dhabi_table.alias("t")
    .merge(abu_dhabi_updates_df.select(spark.table(ABU_DHABI_BOOKINGS_TABLE).columns).alias("s"), "t.booking_id = s.booking_id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

# COMMAND ----------

# Fix 8d (DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE: one row per key,
# the most recent update from exercise 7)
(
    abu_dhabi_table.alias("t")
    .merge(abu_dhabi_latest_df.alias("s"), "t.booking_id = s.booking_id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)
print(spark.table(ABU_DHABI_BOOKINGS_TABLE).count())

# COMMAND ----------

# SILENT ERROR – cell 8e (only the Italian destinations)
all_destinations_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .select("booking_id", "property_id", "check_in", "status")
    .join(properties_df.select("property_id", "destination_id"), on="property_id", how="inner")
    .join(destinations_df.select("destination_id", "destination", "country"), on="destination_id", how="inner")
    .withColumn("check_in_month", F.month(F.col("check_in")))
    .groupBy("destination", "country", "check_in_month")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
    )
)
all_destinations_df.filter(F.col("country") == "Italy")
write_table(all_destinations_df, ITALY_TABLE)

# COMMAND ----------

# Fix 8e (the result of the filter wasn't saved: write_table wrote all the destinations)
italy_only_df = all_destinations_df.filter(F.col("country") == "Italy")
write_table(italy_only_df, ITALY_TABLE)

# COMMAND ----------

# SILENT ERROR – cell 8f (updating the Italian summary)
italy_only_df = all_destinations_df.filter(F.col("country") == "Italy")
write_table(italy_only_df, ITALY_TABLE, mode="append")

# COMMAND ----------

# Fix 8f (append in a re-runnable notebook: repeated rows; use overwrite)
write_table(italy_only_df, ITALY_TABLE)
