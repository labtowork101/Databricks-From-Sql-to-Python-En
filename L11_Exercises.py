# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 11 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run; the `utils` notebook in the same `Python_Book` folder. The exercises **write tables** in the `workspace.python_book` schema.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L11_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L11_Exercises_done`) **in the same folder**, because the first cell loads `utils` with `%run ./utils`. Each exercise has a **check** cell with the expected result.
# MAGIC
# MAGIC The exercises retrace the chapter's project on the 2024 bookings of the four Italian destinations (Amalfi, Florence, Rome, Sardinia). Run the `%run` cell and the setup cell first, then **one cell at a time and in order**: exercises 2 through 8 use the tables written in the previous exercises. Exercise 8 contains cells that must fail (**INTENTIONAL ERROR**) or that produce a wrong result (**SILENT ERROR**); cells 8e and 8f modify the Italian clean table, and the fix of cell 8f repairs it. Don't use Run all.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC The first cell contains only `%run ./utils`; the second defines the constants of the exercises, the DataFrames of the Italian bookings and updates, and the chapter's two functions. Expected result: `Setup complete`.

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# Setup cell: the tables the exercises write
ITALY_CLEAN_TABLE = build_table_name("italy_clean_bookings", "booking")
ITALY_UPDATES_TABLE = build_table_name("italy_clean_updates", "booking")
ITALY_REPORT_TABLE = build_table_name("italy_cancellations", "destination_arrival_type", layer="g")
CHECKS_TABLE = build_table_name("italy_checks", "check")

# Italian properties with their destination
properties_df = spark.table(PROPERTIES_TABLE)
destinations_df = spark.table(DESTINATIONS_TABLE)
italy_properties_df = (
    properties_df.select("property_id", "destination_id")
    .join(
        destinations_df.filter(F.col("country") == "Italy").select("destination_id", "destination"),
        on="destination_id",
        how="inner",
    )
    .select("property_id", "destination")
)

# Italian bookings of the teaching copy (all years) and Italian updates for 2024
italy_bookings_df = spark.table(BOOKINGS_TABLE).join(italy_properties_df.select("property_id"), on="property_id", how="inner")
italy_updates_df = (
    spark.table(BOOKING_UPDATES_TABLE)
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .join(italy_properties_df.select("property_id"), on="property_id", how="inner")
)


# The two functions of Chapter 11 (section 11.4)
def quality_note_column():
    """Quality note of a booking, calculated on the values not yet corrected."""
    return (
        F.when(F.col("total_amount").isNull(), "missing amount")
        .when(F.col("total_amount") < 0, "negative amount")
        .when(F.col("check_out") < F.col("check_in"), "swapped dates")
        .otherwise("ok")
    )


def clean_booking_values(df, source):
    """Applies the project's cleaning rules to a DataFrame of bookings."""
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


print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Profile of the Italian Bookings
# MAGIC 1. From `italy_bookings_df`, keep the bookings with a check-in in 2024 (`italy_bookings_2024_df`).
# MAGIC 2. Build the `italy_profile` dictionary with the entries `rows`, `distinct rows`, `keys (booking_id)`, `missing amount`, `negative amount`, `swapped dates`, and print it with a loop on `items()` (format `{name:<25}{value:>8}`).
# MAGIC 3. In a comment: is `distinct()` enough for the duplicates?

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("rows                          716")
print("distinct rows                 714")
print("keys (booking_id)             714")
print("missing amount                  0")
print("negative amount                 2")
print("swapped dates                   1")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SQL check (expected: 716 714 0 2 1)
# MAGIC SELECT COUNT(*)                                              AS row_count,
# MAGIC        COUNT(DISTINCT b.booking_id)                          AS key_count,
# MAGIC        SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) AS missing_amount,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END)     AS negative_amount,
# MAGIC        SUM(CASE WHEN check_out < check_in THEN 1 ELSE 0 END) AS inverted_dates
# MAGIC FROM workspace.python_book.b_bookings b
# MAGIC JOIN samples.wanderbricks.properties p USING (property_id)
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC WHERE year(b.check_in) = 2024 AND d.country = 'Italy'

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – The Italian Clean Table
# MAGIC 1. Prepare `italy_clean_df`: `italy_bookings_df` with `distinct()`, then `clean_booking_values(..., "original")`, then the filter on the year `ANALYSIS_YEAR`.
# MAGIC 2. Write it to `ITALY_CLEAN_TABLE` with `write_table` and show the number of rows by `quality_note` (column `booking_count`), in order of note.
# MAGIC 3. With a dictionary of checks (measured value, expected value), check that: rows of the table = keys of the profile; keys of the table = keys of the profile; negative amounts = 0; swapped dates = 0. Print `OK` or `MISMATCH` for each check.

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("Writing workspace.python_book.s_italy_clean_bookings_booking (mode=overwrite)")
print("Rows in the table: 714")
print("quality_note     booking_count")
print("negative amount  2")
print("ok               711")
print("swapped dates    1")
print("rows                          714     714  OK")
print("keys (booking_id)             714     714  OK")
print("negative amount                 0       0  OK")
print("swapped dates                   0       0  OK")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – The Italian Updates
# MAGIC 1. Print the rows and the distinct bookings of `italy_updates_df`.
# MAGIC 2. Apply the most-recent-update rule (`italy_latest_updates_df`) and print rows and keys.
# MAGIC 3. Apply the tie-breaking rule with a join on `["booking_id", "booking_update_id"]` (`italy_chosen_updates_df`) and print rows and keys.
# MAGIC 4. Clean the result with `clean_booking_values(..., "update")` and write it to `ITALY_UPDATES_TABLE` with `write_table`.

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("791 484")
print("485 484")
print("484 484")
print("Writing workspace.python_book.s_italy_clean_updates_booking (mode=overwrite)")
print("Rows in the table: 484")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Italian MERGE
# MAGIC 1. With `spark.sql()`, run the `MERGE` of `ITALY_UPDATES_TABLE` into `ITALY_CLEAN_TABLE` (key `booking_id`, `UPDATE SET *`, `INSERT *`) and show its counters.
# MAGIC 2. Print the rows and the keys of the Italian clean table.
# MAGIC 3. Print the canceled bookings before the `MERGE` (from the `italy_clean_df` recipe of exercise 2) and after it (from the table).

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("num_affected_rows 484, num_updated_rows 484, num_deleted_rows 0, num_inserted_rows 0")
print("714 714")
print("142 270")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – The Report by Arrival Type
# MAGIC 1. From the Italian clean table, with a join on `italy_properties_df`, build the report by `destination` and `arrival_type` (`weekend` if `F.dayofweek(check_in)` is 6 or 7, otherwise `weekday`) with `booking_count`, `cancelled_count`, `revenue` (rounded to 2 decimal places), `cancellation_rate` (in %, one decimal place), and `cancellation_status` (with `cancellation_status_column()`).
# MAGIC 2. Write it to `ITALY_REPORT_TABLE` with `write_table` and show it in order of destination and arrival type.

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("Writing workspace.python_book.g_italy_cancellations_destination_arrival_type (mode=overwrite)")
print("Rows in the table: 8")
print("destination  arrival_type  booking_count  cancelled_count  revenue    cancellation_rate  cancellation_status")
print("Amalfi       weekday       37             15               21948.84   40.5               critical")
print("Amalfi       weekend       14             6                7555.12    42.9               not assessable")
print("Florence     weekday       43             16               26210.82   37.2               critical")
print("Florence     weekend       15             4                6880.48    26.7               not assessable")
print("Rome         weekday       214            78               122433.9   36.4               critical")
print("Rome         weekend       80             30               47311.96   37.5               critical")
print("Sardinia     weekday       206            77               117521.1   37.4               critical")
print("Sardinia     weekend       105            44               58676.55   41.9               critical")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – The Independent Check
# MAGIC 1. Write from scratch a SQL query that recalculates from the Italian clean table the bookings, the canceled bookings, and the revenue by destination and arrival type, with the columns `chk_booking_count`, `chk_cancelled_count`, `chk_revenue`; run it with `spark.sql()`.
# MAGIC 2. Join the report (read back from the table) and the check with a join on `["destination", "arrival_type"]`, filter the rows with at least one difference, and print the rows of the report, of the check, of the comparison, and of the differences.

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("8 8 8 0")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – The Check Log
# MAGIC 1. Collect six checks (measured value, expected value) in an `italy_final_checks` dictionary: clean rows before the `MERGE` (from the `italy_clean_df` recipe) = keys of the profile; negative amounts in the table = 0; swapped dates in the table = 0; rows of `ITALY_UPDATES_TABLE` = keys of `italy_updates_df`; rows of the table after the `MERGE` = keys of the profile + new bookings (the keys of the updates that aren't among those of the profile: 0); bookings in the report = rows of the clean table.
# MAGIC 2. With a loop, build a list of dictionaries with the keys `check_name`, `value`, `expected`, `outcome`, turn it into a DataFrame with `spark.createDataFrame()`, reorder the columns with `select`, and write it to `CHECKS_TABLE` with `write_table`.
# MAGIC 3. Show the table.

# COMMAND ----------

# Write your solution here

# COMMAND ----------

# Check: expected result
print("Writing workspace.python_book.s_italy_checks_check (mode=overwrite)")
print("Rows in the table: 6")
print("check_name              value  expected  outcome")
print("clean rows = keys       714    714       OK")
print("negative amount         0      0         OK")
print("swapped dates           0      0         OK")
print("update rows             484    484       OK")
print("rows after the MERGE    714    714       OK")
print("bookings in the report  714    714       OK")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC Cells 8a and 8b produce an error, cells 8c through 8f a **silent error**. Run them one at a time, note the type of the error and the message (or the wrong result), and write the corrected version below. Cells 8e and 8f use or modify the Italian clean table: the fix of cell 8f repairs it.
# MAGIC
# MAGIC **Expected result of the fixes**: 8a counters `484 484 0 0`; 8b `0` differences; 8c notes `negative amount 2`, `ok 711`, `swapped dates 1`; 8d `714`; 8e `0`; 8f `714 714`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (the MERGE with the most recent update)
italy_latest_df = (
    italy_updates_df
    .join(italy_updates_df.groupBy("booking_id").agg(F.max("updated_at").alias("last_updated_at")), on="booking_id", how="inner")
    .filter(F.col("updated_at") == F.col("last_updated_at"))
)
italy_clean_table = DeltaTable.forName(spark, ITALY_CLEAN_TABLE)
(
    italy_clean_table.alias("t")
    .merge(clean_booking_values(italy_latest_df, "update").alias("s"), "t.booking_id = s.booking_id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

# COMMAND ----------

# Fix 8a (error type or what's wrong: ...)

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b (the comparison with the check)
italy_check_df = spark.sql(f"""
SELECT destination,
       CASE WHEN dayofweek(check_in) IN (6, 7) THEN 'weekend' ELSE 'weekday' END AS arrival_type,
       COUNT(*) AS booking_count
FROM {ITALY_CLEAN_TABLE} JOIN {PROPERTIES_TABLE} USING (property_id) JOIN {DESTINATIONS_TABLE} USING (destination_id)
GROUP BY destination, arrival_type
""")
italy_comparison_df = spark.table(ITALY_REPORT_TABLE).join(italy_check_df, on=["destination", "arrival_type"], how="inner")
print(italy_comparison_df.filter(F.col("booking_count") != F.col("booking_count")).count())

# COMMAND ----------

# Fix 8b (error type or what's wrong: ...)

# COMMAND ----------

# SILENT ERROR – cell 8c (the notes of the Italian bookings)
italy_late_note_df = (
    clean_booking_values(italy_bookings_df.distinct(), "original")
    .withColumn("quality_note", quality_note_column())
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
display(italy_late_note_df.groupBy("quality_note").agg(F.count("*").alias("booking_count")).orderBy("quality_note"))

# COMMAND ----------

# Fix 8c (error type or what's wrong: ...)

# COMMAND ----------

# SILENT ERROR – cell 8d (the Italian bookings with a valid amount)
italy_filtered_df = (
    italy_bookings_df
    .distinct()
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .filter(F.col("total_amount") >= 0)
)
print(italy_filtered_df.count())

# COMMAND ----------

# Fix 8d (error type or what's wrong: ...)

# COMMAND ----------

# SILENT ERROR – cell 8e (the swapped dates)
italy_dates_inverted = F.col("check_out") < F.col("check_in")
italy_swapped_df = (
    italy_bookings_df
    .distinct()
    .withColumn("check_in", F.when(italy_dates_inverted, F.col("check_out")).otherwise(F.col("check_in")))
    .withColumn("check_out", F.when(italy_dates_inverted, F.col("check_in")).otherwise(F.col("check_out")))
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
print(italy_swapped_df.filter(F.col("check_in") == F.col("check_out")).count())

# COMMAND ----------

# Fix 8e (error type or what's wrong: ...)

# COMMAND ----------

# SILENT ERROR – cell 8f (the updates applied again)
write_table(spark.table(ITALY_UPDATES_TABLE), ITALY_CLEAN_TABLE, mode="append")
italy_appended_df = spark.table(ITALY_CLEAN_TABLE)
print(italy_appended_df.count(), italy_appended_df.select("booking_id").distinct().count())

# COMMAND ----------

# Fix 8f (error type or what's wrong: ...)