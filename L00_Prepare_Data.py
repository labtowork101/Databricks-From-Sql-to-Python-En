# Databricks notebook source
# MAGIC %md
# MAGIC # L00 – Prepare the book's data
# MAGIC
# MAGIC Run this notebook **only once**, at the start, with **Run all**, on Serverless compute.
# MAGIC
# MAGIC What it does:
# MAGIC 1. Creates the working schema `workspace.python_book`, the only one we write to.
# MAGIC 2. Creates `b_bookings`, the teaching copy of `samples.wanderbricks.bookings`, with amounts rounded to 2 decimal places.
# MAGIC 3. Adds a few **deterministic** anomalies to the copy (the same for every reader), which we need for the cleaning exercises.
# MAGIC 4. Creates `b_bookings_changes`, the list of modified rows, so it is always clear which data is original and which is not.
# MAGIC
# MAGIC The other tables (`properties`, `destinations`, `countries`, `reviews`, `booking_updates`) are read directly from `samples.wanderbricks`, without copying them.
# MAGIC
# MAGIC If `b_bookings` is overwritten by mistake, just run this notebook again: the result is always the same.

# COMMAND ----------

# Cell 1 – setup and working schema
import pyspark.sql.functions as F

SOURCE_SCHEMA = "samples.wanderbricks"
WORK_SCHEMA = "workspace.python_book"
BOOKINGS_TABLE = f"{WORK_SCHEMA}.b_bookings"
CHANGES_TABLE = f"{WORK_SCHEMA}.b_bookings_changes"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {WORK_SCHEMA}")
print(f"Working schema ready: {WORK_SCHEMA}")

# COMMAND ----------

# Cell 2 – copy of the original table with amounts rounded to 2 decimal places
# In the original, total_amount is a float (e.g., 879.1500244140625): rounding makes the outputs readable.
source_df = (
    spark.table(f"{SOURCE_SCHEMA}.bookings")
    .withColumn("total_amount", F.round(F.col("total_amount").cast("double"), 2))
)
original_columns = source_df.columns
print(f"Original rows: {source_df.count():,}")

# COMMAND ----------

# Cell 3 – deterministic choice of the rows to modify
# Only bookings with check-in in 2024 and a positive amount; disjoint groups (different remainder of the division by 13).
def pick_booking_ids(df, remainder, how_many):
    rows = (
        df
        .filter(
            (F.year("check_in") == 2024)
            & (F.col("total_amount") > 0)
            & (F.col("booking_id") % 13 == remainder)
        )
        .orderBy("booking_id")
        .limit(how_many)
        .select("booking_id")
        .collect()
    )
    return [row["booking_id"] for row in rows]

null_amount_ids = pick_booking_ids(source_df, 1, 30)
negative_amount_ids = pick_booking_ids(source_df, 2, 12)
swapped_dates_ids = pick_booking_ids(source_df, 3, 8)
duplicate_ids = pick_booking_ids(source_df, 4, 40)

print(f"Null amount:          {len(null_amount_ids)} bookings")
print(f"Negative amount:      {len(negative_amount_ids)} bookings")
print(f"Swapped dates:        {len(swapped_dates_ids)} bookings")
print(f"Duplicate rows:       {len(duplicate_ids)} bookings")

# COMMAND ----------

# Cell 4 – applying the anomalies and writing b_bookings
modified_df = (
    source_df
    .withColumn(
        "total_amount",
        F.when(F.col("booking_id").isin(null_amount_ids), F.lit(None).cast("double"))
        .when(F.col("booking_id").isin(negative_amount_ids), -F.col("total_amount"))
        .otherwise(F.col("total_amount"))
    )
    .withColumn(
        "new_check_in",
        F.when(F.col("booking_id").isin(swapped_dates_ids), F.col("check_out")).otherwise(F.col("check_in"))
    )
    .withColumn(
        "new_check_out",
        F.when(F.col("booking_id").isin(swapped_dates_ids), F.col("check_in")).otherwise(F.col("check_out"))
    )
    .drop("check_in", "check_out")
    .withColumnRenamed("new_check_in", "check_in")
    .withColumnRenamed("new_check_out", "check_out")
    .select(original_columns)
)

# The duplicate rows are identical copies of unmodified rows
duplicates_df = modified_df.filter(F.col("booking_id").isin(duplicate_ids))
bookings_df = modified_df.unionByName(duplicates_df)

print(f"Writing {BOOKINGS_TABLE}")
(
    bookings_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(BOOKINGS_TABLE)
)
print(f"Rows written: {spark.table(BOOKINGS_TABLE).count():,}")

# COMMAND ----------

# Cell 5 – list of changes (b_bookings_changes)
changes = (
    [(booking_id, "null_amount", "total_amount set to NULL") for booking_id in null_amount_ids]
    + [(booking_id, "negative_amount", "total_amount sign reversed") for booking_id in negative_amount_ids]
    + [(booking_id, "swapped_dates", "check_in and check_out swapped") for booking_id in swapped_dates_ids]
    + [(booking_id, "duplicate_row", "row copied twice, identical") for booking_id in duplicate_ids]
)
changes_df = spark.createDataFrame(changes, "booking_id bigint, change_type string, description string")

print(f"Writing {CHANGES_TABLE}")
(
    changes_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(CHANGES_TABLE)
)
print(f"Rows written: {spark.table(CHANGES_TABLE).count():,}")

# COMMAND ----------

# Cell 6 – final check: the values obtained must match the expected ones
check_df = spark.table(BOOKINGS_TABLE)

checks = {
    "rows":                          (check_df.count(), 72287),
    "distinct rows":                 (check_df.distinct().count(), 72247),
    "distinct booking_id":           (check_df.select("booking_id").distinct().count(), 72247),
    "null total_amount":             (check_df.filter(F.col("total_amount").isNull()).count(), 30),
    "negative total_amount":         (check_df.filter(F.col("total_amount") < 0).count(), 13),
    "check_out before check_in":     (check_df.filter(F.col("check_out") < F.col("check_in")).count(), 8),
    "recorded changes":              (spark.table(CHANGES_TABLE).count(), 90),
}

all_ok = True
for name, (value, expected) in checks.items():
    status = "OK" if value == expected else "MISMATCH"
    if value != expected:
        all_ok = False
    print(f"{name:<30} {value:>8,}   expected {expected:>8,}   {status}")

print()
print("Preparation complete." if all_ok else "WARNING: some values differ from the expected ones.")
# Note: of the 13 negative amounts, 1 is already in the original data and 12 are added by this notebook.
