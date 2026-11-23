# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 12 – From Table to Dashboard
# MAGIC
# MAGIC Notebook for Chapter 12 of *Beyond SELECT*. Goals: prepare and test the queries of the **Cancellations by Destination 2024** dashboard, calculate in the notebook the values that the dashboard must show, and compare them with the values read on the dashboard.
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; the `L11_Final_Project` notebook run at least once (the `g_updated_cancellations_destination_month` table must exist); the `utils` notebook in the same `Python_Book` folder. The notebook **doesn't write tables**: the dashboard is built in the user interface (sidebar → **Dashboards**), following the text of the chapter.
# MAGIC
# MAGIC Run **one cell at a time**, from top to bottom. Section 12.5 contains a cell that must fail (**INTENTIONAL ERROR**) and section 12.13 a cell that produces a wrong result (**SILENT ERROR**), each with its fix in the cell right below. Don't use Run all. If the compute stops, run again the `%run ./utils` cell, the constants cell, and the cells that create the variables used further on.

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
# MAGIC workspace.python_book.g_updated_cancellations_destination_month
# MAGIC 317
# MAGIC ['destination', 'country', 'check_in_month', 'booking_count', 'cancelled_count', 'revenue', 'cancellation_rate', 'cancellation_status']
# MAGIC ```

# COMMAND ----------

# Chapter constants: the report table from Chapter 11, the source of the dashboard
PROJECT_REPORT_TABLE = build_table_name("updated_cancellations", "destination_month", layer="g")
DASHBOARD_THRESHOLDS = [30.0, 40.0]

# The report table, read once
report_df = spark.table(PROJECT_REPORT_TABLE)

print(PROJECT_REPORT_TABLE)
print(report_df.count())
print(report_df.columns)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.1 What a Dashboard Is

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

# MAGIC %sql
# MAGIC SELECT cancellation_status, COUNT(*) AS combination_count
# MAGIC FROM workspace.python_book.g_updated_cancellations_destination_month
# MAGIC GROUP BY cancellation_status
# MAGIC ORDER BY cancellation_status

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.2 Creating the Dashboard and the First Dataset

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output: the text of the query (to copy into the dataset editor), then the number of rows.
# MAGIC ```
# MAGIC SELECT destination, country, check_in_month,
# MAGIC        booking_count, cancelled_count, revenue,
# MAGIC        cancellation_rate, cancellation_status
# MAGIC FROM workspace.python_book.g_updated_cancellations_destination_month
# MAGIC 317
# MAGIC ```

# COMMAND ----------

dataset_query = f"""SELECT destination, country, check_in_month,
       booking_count, cancelled_count, revenue,
       cancellation_rate, cancellation_status
FROM {PROJECT_REPORT_TABLE}"""

print(dataset_query)
print(spark.sql(dataset_query).count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.3 The First Widgets: Counters

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 13590 5123 7529860.44
# MAGIC ```

# COMMAND ----------

totals = report_df.agg(
    F.sum("booking_count").alias("booking_count"),
    F.sum("cancelled_count").alias("cancelled_count"),
    F.round(F.sum("revenue"), 2).alias("revenue"),
).collect()[0]

print(totals["booking_count"], totals["cancelled_count"], totals["revenue"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.4 Measures: The Overall Rate

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 37.7 37.3 11825.9
# MAGIC ```

# COMMAND ----------

rates = report_df.agg(
    F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1).alias("overall_cancellation_rate"),
    F.round(F.avg("cancellation_rate"), 1).alias("average_of_rates"),
    F.round(F.sum("cancellation_rate"), 1).alias("sum_of_rates"),
).collect()[0]

print(rates["overall_cancellation_rate"], rates["average_of_rates"], rates["sum_of_rates"])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC overall_cancellation_rate  average_of_rates
# MAGIC 37.7                       37.3
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(SUM(cancelled_count) / SUM(booking_count) * 100, 1) AS overall_cancellation_rate,
# MAGIC        ROUND(AVG(cancellation_rate), 1)                          AS average_of_rates
# MAGIC FROM workspace.python_book.g_updated_cancellations_destination_month

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 147
# MAGIC ```

# COMMAND ----------

critical_count = report_df.filter(F.col("cancellation_status") == "critical").count()
print(critical_count)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.5 The Threshold as a Parameter

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output: the text of the query with the `:threshold` parameter (to copy into the dataset editor in place of the first query).
# MAGIC ```
# MAGIC SELECT destination, country, check_in_month,
# MAGIC        booking_count, cancelled_count, revenue, cancellation_rate,
# MAGIC        CASE WHEN booking_count < 20 THEN 'not assessable'
# MAGIC             WHEN cancellation_rate > :threshold THEN 'critical'
# MAGIC             ELSE 'ok' END AS cancellation_status
# MAGIC FROM workspace.python_book.g_updated_cancellations_destination_month
# MAGIC ```

# COMMAND ----------

dashboard_query = f"""SELECT destination, country, check_in_month,
       booking_count, cancelled_count, revenue, cancellation_rate,
       CASE WHEN booking_count < {MIN_BOOKINGS} THEN 'not assessable'
            WHEN cancellation_rate > :threshold THEN 'critical'
            ELSE 'ok' END AS cancellation_status
FROM {PROJECT_REPORT_TABLE}"""

print(dashboard_query)

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Same Parameter in the Notebook

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the next cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message (summary line):
# MAGIC ```
# MAGIC [UNBOUND_SQL_PARAMETER] Found the unbound parameter: threshold. Please, fix `args` and provide a mapping of the parameter to either a SQL literal or collection constructor functions such as `map()`, `array()`, `struct()`. SQLSTATE: 42P02
# MAGIC ```
# MAGIC The traceback points to line 2 of the cell.

# COMMAND ----------

# INTENTIONAL ERROR – the query has a parameter, but no value
print(spark.sql(dashboard_query).count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC Threshold 30.0: 147 critical combinations
# MAGIC Threshold 40.0: 59 critical combinations
# MAGIC ```

# COMMAND ----------

# Fix: the value of the parameter passed with args
for threshold in DASHBOARD_THRESHOLDS:
    status_df = spark.sql(dashboard_query, args={"threshold": threshold})
    critical_count = status_df.filter(F.col("cancellation_status") == "critical").count()
    print(f"Threshold {threshold}: {critical_count} critical combinations")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 59
# MAGIC ```

# COMMAND ----------

print(report_df.filter(cancellation_status_column(threshold=40.0) == "critical").count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.6 Filters

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 714 37.8 11
# MAGIC ```

# COMMAND ----------

italy_totals = (
    report_df
    .filter(F.col("country") == "Italy")
    .agg(
        F.sum("booking_count").alias("booking_count"),
        F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1).alias("overall_cancellation_rate"),
        F.sum(F.when(F.col("cancellation_status") == "critical", 1).otherwise(0)).alias("critical_count"),
    )
    .collect()[0]
)

print(italy_totals["booking_count"], italy_totals["overall_cancellation_rate"], italy_totals["critical_count"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.7 A Bar Chart

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC check_in_month  booking_count  cancelled_count  cancellation_rate  average_of_rates
# MAGIC 1               204            68               33.3               29
# MAGIC 2               211            71               33.6               28.9
# MAGIC 3               319            125              39.2               43.1
# MAGIC 4               337            141              41.8               38.9
# MAGIC 5               379            154              40.6               43
# MAGIC 6               1661           639              38.5               37.6
# MAGIC 7               2050           750              36.6               40.6
# MAGIC 8               2431           904              37.2               36.8
# MAGIC 9               1577           594              37.7               33.9
# MAGIC 10              1163           436              37.5               38.3
# MAGIC 11              1396           529              37.9               38.2
# MAGIC 12              1862           712              38.2               40.9
# MAGIC ```

# COMMAND ----------

monthly_df = (
    report_df
    .groupBy("check_in_month")
    .agg(
        F.sum("booking_count").alias("booking_count"),
        F.sum("cancelled_count").alias("cancelled_count"),
        F.round(F.avg("cancellation_rate"), 1).alias("average_of_rates"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .select("check_in_month", "booking_count", "cancelled_count", "cancellation_rate", "average_of_rates")
    .orderBy("check_in_month")
)
display(monthly_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.8 The Table of Critical Combinations

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC destination  country               check_in_month  booking_count  cancelled_count  cancellation_rate
# MAGIC Singapore    Singapore             4               20             11               55
# MAGIC Ibiza        Spain                 6               68             37               54.4
# MAGIC London       United Kingdom        11              37             20               54.1
# MAGIC Cairo        Egypt                 10              30             16               53.3
# MAGIC Paris        France                4               54             28               51.9
# MAGIC Berlin       Germany               8               35             18               51.4
# MAGIC Abu Dhabi    United Arab Emirates  5               38             19               50
# MAGIC Amalfi       Italy                 8               20             10               50
# MAGIC ```

# COMMAND ----------

display(
    report_df
    .filter(F.col("cancellation_status") == "critical")
    .select("destination", "country", "check_in_month", "booking_count", "cancelled_count", "cancellation_rate")
    .orderBy(F.col("cancellation_rate").desc(), "destination", "check_in_month")
    .limit(8)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.9 Layout and Text

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.10 Publishing and Sharing

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.11 Refreshing the Data

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.12 Checking the Dashboard

# COMMAND ----------

# MAGIC %md
# MAGIC In the `dashboard_values` dictionary, write the values read on the dashboard (draft or published version, filters at their default value). Expected result – output:
# MAGIC ```
# MAGIC Bookings                           13590     13590  OK
# MAGIC Cancellation Rate (%)               37.7      37.7  OK
# MAGIC Critical Combinations                147       147  OK
# MAGIC ```

# COMMAND ----------

# The values read on the dashboard, written by hand (without thousands separators)
dashboard_values = {
    "Bookings": 13590,
    "Cancellation Rate (%)": 37.7,
    "Critical Combinations": 147,
}

# The same values calculated in the notebook
expected_values = {
    "Bookings": totals["booking_count"],
    "Cancellation Rate (%)": rates["overall_cancellation_rate"],
    "Critical Combinations": report_df.filter(F.col("cancellation_status") == "critical").count(),
}

for widget_name, value in dashboard_values.items():
    expected = expected_values[widget_name]
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    print(f"{widget_name:<30}{value:>10}{expected:>10}  {outcome}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12.13 Common Dashboard Mistakes

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Average of the Rates

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 35.4
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – the rate of Italy calculated as the average of the rates
italy_df = report_df.filter(F.col("country") == "Italy")
print(italy_df.agg(F.round(F.avg("cancellation_rate"), 1)).collect()[0][0])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC 37.8
# MAGIC ```

# COMMAND ----------

# Fix: total canceled bookings divided by total bookings
print(italy_df.agg(F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1)).collect()[0][0])
