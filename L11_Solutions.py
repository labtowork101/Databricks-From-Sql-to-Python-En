# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 11 – Exercise Solutions
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run; the `utils` notebook in the same `Python_Book` folder. The exercises **write tables** in the `workspace.python_book` schema.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Comments on the solutions: Appendix A.
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

# Solution
italy_bookings_2024_df = italy_bookings_df.filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)

italy_profile = {
    "rows": italy_bookings_2024_df.count(),
    "distinct rows": italy_bookings_2024_df.distinct().count(),
    "keys (booking_id)": italy_bookings_2024_df.select("booking_id").distinct().count(),
    "missing amount": italy_bookings_2024_df.filter(F.col("total_amount").isNull()).count(),
    "negative amount": italy_bookings_2024_df.filter(F.col("total_amount") < 0).count(),
    "swapped dates": italy_bookings_2024_df.filter(F.col("check_out") < F.col("check_in")).count(),
}

for check_name, value in italy_profile.items():
    print(f"{check_name:<25}{value:>8}")

# Distinct rows (714) = keys (714): the 2 extra rows are identical copies, so distinct() is enough.

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

# Solution
italy_clean_df = (
    clean_booking_values(italy_bookings_df.distinct(), "original")
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
write_table(italy_clean_df, ITALY_CLEAN_TABLE)
display(
    spark.table(ITALY_CLEAN_TABLE)
    .groupBy("quality_note")
    .agg(F.count("*").alias("booking_count"))
    .orderBy("quality_note")
)

italy_clean_table_df = spark.table(ITALY_CLEAN_TABLE)
italy_clean_checks = {
    "rows": (italy_clean_table_df.count(), italy_profile["keys (booking_id)"]),
    "keys (booking_id)": (italy_clean_table_df.select("booking_id").distinct().count(), italy_profile["keys (booking_id)"]),
    "negative amount": (italy_clean_table_df.filter(F.col("total_amount") < 0).count(), 0),
    "swapped dates": (italy_clean_table_df.filter(F.col("check_out") < F.col("check_in")).count(), 0),
}
for check_name, (value, expected) in italy_clean_checks.items():
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    print(f"{check_name:<25}{value:>8}{expected:>8}  {outcome}")

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

# Solution
print(italy_updates_df.count(), italy_updates_df.select("booking_id").distinct().count())

italy_last_update_df = (
    italy_updates_df
    .groupBy("booking_id")
    .agg(F.max("updated_at").alias("last_updated_at"))
)
italy_latest_updates_df = (
    italy_updates_df
    .join(italy_last_update_df, on="booking_id", how="inner")
    .filter(F.col("updated_at") == F.col("last_updated_at"))
)
print(italy_latest_updates_df.count(), italy_latest_updates_df.select("booking_id").distinct().count())

italy_last_update_id_df = (
    italy_latest_updates_df
    .groupBy("booking_id")
    .agg(F.max("booking_update_id").alias("booking_update_id"))
)
italy_chosen_updates_df = italy_latest_updates_df.join(
    italy_last_update_id_df,
    on=["booking_id", "booking_update_id"],
    how="inner",
)
print(italy_chosen_updates_df.count(), italy_chosen_updates_df.select("booking_id").distinct().count())

write_table(clean_booking_values(italy_chosen_updates_df, "update"), ITALY_UPDATES_TABLE)

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

# Solution
italy_merge_query = f"""
MERGE INTO {ITALY_CLEAN_TABLE} AS t
USING {ITALY_UPDATES_TABLE} AS s
ON t.booking_id = s.booking_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
display(spark.sql(italy_merge_query))

italy_merged_df = spark.table(ITALY_CLEAN_TABLE)
print(italy_merged_df.count(), italy_merged_df.select("booking_id").distinct().count())
print(
    italy_clean_df.filter(F.col("status") == "cancelled").count(),
    italy_merged_df.filter(F.col("status") == "cancelled").count(),
)

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

# Solution
weekend_arrival = (F.dayofweek(F.col("check_in")) == 6) | (F.dayofweek(F.col("check_in")) == 7)

italy_report_df = (
    spark.table(ITALY_CLEAN_TABLE)
    .select("booking_id", "property_id", "check_in", "status", "total_amount")
    .join(italy_properties_df, on="property_id", how="inner")
    .withColumn("arrival_type", F.when(weekend_arrival, "weekend").otherwise("weekday"))
    .groupBy("destination", "arrival_type")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .withColumn("cancellation_status", cancellation_status_column())
)
write_table(italy_report_df, ITALY_REPORT_TABLE)
display(spark.table(ITALY_REPORT_TABLE).orderBy("destination", "arrival_type"))

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

# Solution
italy_check_query = f"""
SELECT d.destination,
       CASE WHEN dayofweek(b.check_in) IN (6, 7) THEN 'weekend' ELSE 'weekday' END AS arrival_type,
       COUNT(*)                                                AS chk_booking_count,
       SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS chk_cancelled_count,
       ROUND(SUM(b.total_amount), 2)                           AS chk_revenue
FROM {ITALY_CLEAN_TABLE} b
JOIN {PROPERTIES_TABLE} p ON b.property_id = p.property_id
JOIN {DESTINATIONS_TABLE} d ON p.destination_id = d.destination_id
GROUP BY d.destination, arrival_type
"""
italy_check_df = spark.sql(italy_check_query)
italy_report_table_df = spark.table(ITALY_REPORT_TABLE)

italy_comparison_df = italy_report_table_df.join(italy_check_df, on=["destination", "arrival_type"], how="inner")
italy_differences_df = italy_comparison_df.filter(
    (F.col("booking_count") != F.col("chk_booking_count"))
    | (F.col("cancelled_count") != F.col("chk_cancelled_count"))
    | (F.col("revenue") != F.col("chk_revenue"))
)
print(italy_report_table_df.count(), italy_check_df.count(), italy_comparison_df.count(), italy_differences_df.count())

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

# Solution
italy_update_keys = italy_updates_df.select("booking_id").distinct().count()
italy_new_bookings = (
    italy_updates_df.select("booking_id").distinct()
    .join(
        italy_clean_df.select("booking_id").withColumn("is_known_booking", F.lit(True)),
        on="booking_id",
        how="left",
    )
    .filter(F.col("is_known_booking").isNull())
    .count()
)
italy_merged_df = spark.table(ITALY_CLEAN_TABLE)
italy_final_checks = {
    "clean rows = keys": (italy_clean_df.count(), italy_profile["keys (booking_id)"]),
    "negative amount": (italy_merged_df.filter(F.col("total_amount") < 0).count(), 0),
    "swapped dates": (italy_merged_df.filter(F.col("check_out") < F.col("check_in")).count(), 0),
    "update rows": (spark.table(ITALY_UPDATES_TABLE).count(), italy_update_keys),
    "rows after the MERGE": (italy_merged_df.count(), italy_profile["keys (booking_id)"] + italy_new_bookings),
    "bookings in the report": (
        spark.table(ITALY_REPORT_TABLE).agg(F.sum("booking_count")).collect()[0][0],
        italy_merged_df.count(),
    ),
}

check_rows = []
for check_name, (value, expected) in italy_final_checks.items():
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    check_rows.append({"check_name": check_name, "value": value, "expected": expected, "outcome": outcome})

checks_df = spark.createDataFrame(check_rows).select("check_name", "value", "expected", "outcome")
write_table(checks_df, CHECKS_TABLE)
display(spark.table(CHECKS_TABLE))

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

# Fix 8a – DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE: the source has 485 rows for 484 bookings
# (a tie on the last update). Use the source with the tie-breaking rule (exercise 3).
print(italy_latest_df.count(), italy_latest_df.select("booking_id").distinct().count())
display(spark.sql(italy_merge_query))

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

# Fix 8b – AMBIGUOUS_REFERENCE: after the join there are two booking_count columns.
# The columns of the check have the chk_ prefix.
italy_check_df = spark.sql(f"""
SELECT destination,
       CASE WHEN dayofweek(check_in) IN (6, 7) THEN 'weekend' ELSE 'weekday' END AS arrival_type,
       COUNT(*) AS chk_booking_count
FROM {ITALY_CLEAN_TABLE} JOIN {PROPERTIES_TABLE} USING (property_id) JOIN {DESTINATIONS_TABLE} USING (destination_id)
GROUP BY destination, arrival_type
""")
italy_comparison_df = spark.table(ITALY_REPORT_TABLE).join(italy_check_df, on=["destination", "arrival_type"], how="inner")
print(italy_comparison_df.filter(F.col("booking_count") != F.col("chk_booking_count")).count())

# COMMAND ----------

# SILENT ERROR – cell 8c (the notes of the Italian bookings)
italy_late_note_df = (
    clean_booking_values(italy_bookings_df.distinct(), "original")
    .withColumn("quality_note", quality_note_column())
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
)
display(italy_late_note_df.groupBy("quality_note").agg(F.count("*").alias("booking_count")).orderBy("quality_note"))

# COMMAND ----------

# Fix 8c – the note recalculated after the corrections sees amounts already NULL and dates already swapped
# (missing amount 2, ok 712). The note is calculated only once, inside clean_booking_values.
display(italy_clean_df.groupBy("quality_note").agg(F.count("*").alias("booking_count")).orderBy("quality_note"))

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

# Fix 8d – the filter removes the 2 bookings with a negative amount (712 instead of 714).
# Guiding rule: the amount becomes NULL, the booking stays.
print(italy_clean_df.count(), italy_clean_df.filter(F.col("total_amount").isNull()).count())

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

# Fix 8e – the second withColumn reads the check_in already modified: 1 booking with zero nights.
# The swap is done in a single select, as in clean_booking_values.
print(italy_clean_df.filter(F.col("check_in") == F.col("check_out")).count())

# COMMAND ----------

# SILENT ERROR – cell 8f (the updates applied again)
write_table(spark.table(ITALY_UPDATES_TABLE), ITALY_CLEAN_TABLE, mode="append")
italy_appended_df = spark.table(ITALY_CLEAN_TABLE)
print(italy_appended_df.count(), italy_appended_df.select("booking_id").distinct().count())

# COMMAND ----------

# Fix 8f – append adds the 484 rows without looking at the key (1198 rows, 714 keys).
# Repair it the way you build it: overwrite from the source, then the MERGE.
write_table(italy_clean_df, ITALY_CLEAN_TABLE)
display(spark.sql(italy_merge_query))
italy_repaired_df = spark.table(ITALY_CLEAN_TABLE)
print(italy_repaired_df.count(), italy_repaired_df.select("booking_id").distinct().count())
