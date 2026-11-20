# Databricks notebook source
# MAGIC %md
# MAGIC # utils – shared definitions for the book
# MAGIC
# MAGIC From Chapter 10 on, this notebook is loaded with a cell that contains only `%run ./utils`.
# MAGIC It contains **definitions only** (imports, constants, functions): no table writes,
# MAGIC because `%run` runs all of it every time.
# MAGIC
# MAGIC Prerequisite: you have run `L00_Prepare_Data` once.
# MAGIC Don't modify it for your own experiments: your own constants and functions go in the notebook that loads utils, after the `%run` cell.

# COMMAND ----------

# Imports
import pyspark.sql.functions as F
from datetime import date, timedelta, datetime
from delta.tables import DeltaTable

# COMMAND ----------

# Schemas
SOURCE_SCHEMA = "samples.wanderbricks"     # read-only
WORK_SCHEMA = "workspace.python_book"      # the reader's working schema

# Reference tables: we read them, we never use them in a write
SOURCE_BOOKINGS_TABLE = f"{SOURCE_SCHEMA}.bookings"           # original bookings
BOOKINGS_TABLE = f"{WORK_SCHEMA}.b_bookings"                  # teaching copy created by L00_Prepare_Data
BOOKING_UPDATES_TABLE = f"{SOURCE_SCHEMA}.booking_updates"
PROPERTIES_TABLE = f"{SOURCE_SCHEMA}.properties"
DESTINATIONS_TABLE = f"{SOURCE_SCHEMA}.destinations"
COUNTRIES_TABLE = f"{SOURCE_SCHEMA}.countries"
REVIEWS_TABLE = f"{SOURCE_SCHEMA}.reviews"
SUPPORT_LOGS_TABLE = f"{SOURCE_SCHEMA}.customer_support_logs"

# Analysis parameters
ANALYSIS_YEAR = 2024                 # window of the examples: check-ins in 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
MIN_BOOKINGS = 20                    # minimum bookings for a rate to be assessable

# Guide properties, always in the order Rome, Sardinia, Amalfi
GUIDE_PROPERTY_IDS = [11670, 16317, 16225]

# COMMAND ----------

def build_table_name(topic, granularity, layer="s"):
    """Builds the full name of a table in the working schema.
    Example: build_table_name("bookings", "daily") -> workspace.python_book.s_bookings_daily
    """
    return f"{WORK_SCHEMA}.{layer}_{topic}_{granularity}"


def read_clean_bookings():
    """Reads b_bookings and applies the basic cleaning rules:
    - identical repeated rows: removed with distinct();
    - negative amount: becomes NULL (the row stays).
    (Rules to be confirmed in Chapter 11, especially for swapped dates.)
    """
    return (
        spark.table(BOOKINGS_TABLE)
        .distinct()
        .withColumn(
            "total_amount",
            F.when(F.col("total_amount") >= 0, F.col("total_amount"))
        )
    )


def cancellation_status_column(threshold=CANCELLATION_RATE_THRESHOLD, min_bookings=MIN_BOOKINGS):
    """Status column computed from the booking_count and cancellation_rate columns:
    "not assessable" with fewer than min_bookings bookings,
    "critical" with the rate above the threshold, "ok" otherwise.
    """
    return (
        F.when(F.col("booking_count") < min_bookings, "not assessable")
        .when(F.col("cancellation_rate") > threshold, "critical")
        .otherwise("ok")
    )


def write_table(df, table_name, mode="overwrite"):
    """Writes a DataFrame to a Delta table, then reads it back and prints its row count."""
    print(f"Writing {table_name} (mode={mode})")
    (
        df.write
        .mode(mode)
        .saveAsTable(table_name)
    )
    print(f"Rows in the table: {spark.table(table_name).count():,}")
