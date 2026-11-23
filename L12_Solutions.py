# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 12 – Exercise Solutions
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; the `L11_Final_Project` notebook run at least once (`g_updated_cancellations_destination_month` table); the `utils` notebook in the same `Python_Book` folder. Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Comments on the solutions: Appendix A.
# MAGIC
# MAGIC The solutions contain the notebook part of each exercise; the dashboard part is described in the text cells. The notebook **doesn't write tables**. Run the `%run ./utils` cell and the setup cell first, then the solutions in order. Exercise 8 contains a cell that must fail (**INTENTIONAL ERROR**) and two cells that produce a wrong result (**SILENT ERROR**), each with its fix in the cell right below. Don't use Run all: it would stop at cell 8a.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC
# MAGIC Expected result: `317` and `Setup complete`.

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# Setup cell: the report table and the query with two parameters
PROJECT_REPORT_TABLE = build_table_name("updated_cancellations", "destination_month", layer="g")
report_df = spark.table(PROJECT_REPORT_TABLE)

exercise_query = f"""SELECT destination, country, check_in_month,
       booking_count, cancelled_count, revenue, cancellation_rate,
       CASE WHEN booking_count < :min_bookings THEN 'not assessable'
            WHEN cancellation_rate > :threshold THEN 'critical'
            ELSE 'ok' END AS cancellation_status
FROM {PROJECT_REPORT_TABLE}"""

print(report_df.count())
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Revenue Counter
# MAGIC
# MAGIC Dashboard: **Add a visualization** → **Counter** → **Value** `revenue` (**SUM**); in the field, **Format** → **Custom**, **Abbreviation** → **None**; title **Revenue**. Values: `7,529,860.44` (Country **All**) and `408,538.77` (Country **Italy**).
# MAGIC
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 7529860.44 408538.77
# MAGIC ```

# COMMAND ----------

total_revenue = report_df.agg(F.round(F.sum("revenue"), 2)).collect()[0][0]
italy_revenue = (
    report_df
    .filter(F.col("country") == "Italy")
    .agg(F.round(F.sum("revenue"), 2))
    .collect()[0][0]
)
print(total_revenue, italy_revenue)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – A Filter on the Destination
# MAGIC
# MAGIC Dashboard: **Add a filter (field/parameter)** → **Multiple values** → **Fields** `destination`; title **Destination**; value **Amalfi**. Counters: `51`, `41.2`, `1`, `29,503.96`.
# MAGIC
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Bookings                              51        51  OK
# MAGIC Cancellation Rate (%)               41.2      41.2  OK
# MAGIC Critical Combinations                  1         1  OK
# MAGIC Revenue                         29503.96  29503.96  OK
# MAGIC ```

# COMMAND ----------

amalfi = (
    report_df
    .filter(F.col("destination") == "Amalfi")
    .agg(
        F.sum("booking_count").alias("booking_count"),
        F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1).alias("overall_cancellation_rate"),
        F.sum(F.when(F.col("cancellation_status") == "critical", 1).otherwise(0)).alias("critical_count"),
        F.round(F.sum("revenue"), 2).alias("revenue"),
    )
    .collect()[0]
)

amalfi_dashboard = {
    "Bookings": 51,
    "Cancellation Rate (%)": 41.2,
    "Critical Combinations": 1,
    "Revenue": 29503.96,
}
amalfi_expected = {
    "Bookings": amalfi["booking_count"],
    "Cancellation Rate (%)": amalfi["overall_cancellation_rate"],
    "Critical Combinations": amalfi["critical_count"],
    "Revenue": amalfi["revenue"],
}

for widget_name, value in amalfi_dashboard.items():
    expected = amalfi_expected[widget_name]
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    print(f"{widget_name:<30}{value:>10}{expected:>10}  {outcome}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – The Moving Threshold
# MAGIC
# MAGIC Dashboard: the **Critical Combinations** counter shows `157`, `115`, `32`, `6` with the thresholds 25, 35, 45, 50.
# MAGIC
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 25.0 157
# MAGIC 35.0 115
# MAGIC 45.0 32
# MAGIC 50.0 6
# MAGIC ```

# COMMAND ----------

for threshold in [25.0, 35.0, 45.0, 50.0]:
    status_df = spark.sql(exercise_query, args={"threshold": threshold, "min_bookings": MIN_BOOKINGS})
    print(threshold, status_df.filter(F.col("cancellation_status") == "critical").count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Chart by Country
# MAGIC
# MAGIC Dashboard: **Bar** chart, **X axis** `country` (a text, so already a category), **Y axis** the `overall_cancellation_rate` measure, **Labels** on.
# MAGIC
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC country               overall_cancellation_rate  average_of_rates
# MAGIC China                 44.6                       50.4
# MAGIC India                 42.7                       41.7
# MAGIC Egypt                 40.7                       36.2
# MAGIC France                40.1                       35.5
# MAGIC Greece                38.9                       35.9
# MAGIC Australia             38.6                       39.6
# MAGIC Singapore             37.9                       39
# MAGIC Italy                 37.8                       35.4
# MAGIC Germany               37.5                       37.7
# MAGIC Spain                 37.5                       37.9
# MAGIC United States         37.2                       40.3
# MAGIC United Arab Emirates  37                         37.3
# MAGIC Thailand              36.6                       37
# MAGIC Japan                 36.3                       37.8
# MAGIC Austria               35.7                       20.8
# MAGIC United Kingdom        35                         31.9
# MAGIC Switzerland           30.8                       30.7
# MAGIC Canada                29.6                       18.4
# MAGIC ```
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC China 44.6
# MAGIC Canada 29.6
# MAGIC ```

# COMMAND ----------

country_df = (
    report_df
    .groupBy("country")
    .agg(
        F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1).alias("overall_cancellation_rate"),
        F.round(F.avg("cancellation_rate"), 1).alias("average_of_rates"),
    )
    .orderBy(F.col("overall_cancellation_rate").desc(), "country")
)
display(country_df)

# COMMAND ----------

country_rows = country_df.collect()
print(country_rows[0]["country"], country_rows[0]["overall_cancellation_rate"])
print(country_rows[-1]["country"], country_rows[-1]["overall_cancellation_rate"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – The Minimum Volume as a Parameter
# MAGIC
# MAGIC Dashboard: in the dataset query, `20` becomes `:min_bookings`; in the box of the new parameter, gear icon → **Type** **Numeric**, **Numeric type** **Integer**, **Display name** `Minimum volume`, value 20; on the page, a **Single value** filter with **Parameters** → **Minimum volume**.
# MAGIC
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 10 [('critical', 190), ('not assessable', 93), ('ok', 34)]
# MAGIC 30 [('critical', 114), ('not assessable', 191), ('ok', 12)]
# MAGIC ```

# COMMAND ----------

for min_bookings in [10, 30]:
    status_df = spark.sql(exercise_query, args={"threshold": 30.0, "min_bookings": min_bookings})
    status_rows = status_df.groupBy("cancellation_status").count().orderBy("cancellation_status").collect()
    print(min_bookings, [(row["cancellation_status"], row["count"]) for row in status_rows])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – A Page by Continent
# MAGIC
# MAGIC Dashboard: **Data** → **+ Add SQL dataset** with the query printed below (name **Report by continent**); **+ Add custom calculation** with `ROUND(SUM(cancelled_count) / SUM(booking_count) * 100, 1)`; a new page with the **+** next to the pages, renamed **Continents**, with a **Bar** chart (`continent` on the X axis, the measure on the Y axis) and a **Table**.
# MAGIC
# MAGIC Expected result – output: the text of the query, `317`, then the grid.
# MAGIC ```
# MAGIC continent      booking_count  cancelled_count  overall_cancellation_rate
# MAGIC Europe         5557           2110             38
# MAGIC Asia           5290           1969             37.2
# MAGIC Oceania        1246           481              38.6
# MAGIC North America  1212           447              36.9
# MAGIC Africa         285            116              40.7
# MAGIC ```

# COMMAND ----------

continent_query = f"""SELECT r.destination, r.country, c.continent, r.check_in_month,
       r.booking_count, r.cancelled_count, r.revenue, r.cancellation_rate
FROM {PROJECT_REPORT_TABLE} r
JOIN {COUNTRIES_TABLE} c ON r.country = c.country"""

print(continent_query)
continent_df = spark.sql(continent_query)
print(continent_df.count())
display(
    continent_df
    .groupBy("continent")
    .agg(
        F.sum("booking_count").alias("booking_count"),
        F.sum("cancelled_count").alias("cancelled_count"),
        F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1).alias("overall_cancellation_rate"),
    )
    .orderBy(F.col("booking_count").desc())
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Checking a Filtered View
# MAGIC
# MAGIC Dashboard: **Country** **Italy**, threshold 40, minimum volume 20. Counters: `714`, `37.8`, `4`, `408,538.77`.
# MAGIC
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Bookings                             714       714  OK
# MAGIC Cancellation Rate (%)               37.8      37.8  OK
# MAGIC Critical Combinations                  4         4  OK
# MAGIC Revenue                        408538.77 408538.77  OK
# MAGIC ```

# COMMAND ----------

italy_view = (
    spark.sql(exercise_query, args={"threshold": 40.0, "min_bookings": 20})
    .filter(F.col("country") == "Italy")
    .agg(
        F.sum("booking_count").alias("booking_count"),
        F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1).alias("overall_cancellation_rate"),
        F.sum(F.when(F.col("cancellation_status") == "critical", 1).otherwise(0)).alias("critical_count"),
        F.round(F.sum("revenue"), 2).alias("revenue"),
    )
    .collect()[0]
)

italy_dashboard = {
    "Bookings": 714,
    "Cancellation Rate (%)": 37.8,
    "Critical Combinations": 4,
    "Revenue": 408538.77,
}
italy_expected = {
    "Bookings": italy_view["booking_count"],
    "Cancellation Rate (%)": italy_view["overall_cancellation_rate"],
    "Critical Combinations": italy_view["critical_count"],
    "Revenue": italy_view["revenue"],
}

for widget_name, value in italy_dashboard.items():
    expected = italy_expected[widget_name]
    if value == expected:
        outcome = "OK"
    else:
        outcome = "MISMATCH"
    print(f"{widget_name:<30}{value:>10}{expected:>10}  {outcome}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC
# MAGIC Dashboard: **8d** replace `AVG(cancellation_rate)` with the `overall_cancellation_rate` measure (37.7); **8e** in the X axis field, choose **Scale type** → **Categorical** (the 12 bars of section 12.7); **8f** click **Publish**, and the published version shows the new title.

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the next cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message (summary line):
# MAGIC ```
# MAGIC [UNBOUND_SQL_PARAMETER] Found the unbound parameter: min_bookings. Please, fix `args` and provide a mapping of the parameter to either a SQL literal or collection constructor functions such as `map()`, `array()`, `struct()`. SQLSTATE: 42P02
# MAGIC ```
# MAGIC Expected result of the fix: `317`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (the query with two parameters)
print(spark.sql(exercise_query, args={"threshold": 30.0}).count())

# COMMAND ----------

# Fix 8a: one value for each parameter of the query
print(spark.sql(exercise_query, args={"threshold": 30.0, "min_bookings": 20}).count())

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result: `31.9`; of the fix: `35.0`.

# COMMAND ----------

# SILENT ERROR – cell 8b (the rate of the United Kingdom)
uk_df = report_df.filter(F.col("country") == "United Kingdom")
print(uk_df.agg(F.round(F.avg("cancellation_rate"), 1)).collect()[0][0])

# COMMAND ----------

# Fix 8b: the rate from the sums, not the average of the rates
print(uk_df.agg(F.round(F.sum("cancelled_count") / F.sum("booking_count") * 100, 1)).collect()[0][0])

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the next cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result: `False`; of the fix: `True`.

# COMMAND ----------

# SILENT ERROR – cell 8c (the value read on the dashboard)
dashboard_bookings = 13.590
print(dashboard_bookings == 13590)

# COMMAND ----------

# Fix 8c: the number is transcribed without the thousands separator
dashboard_bookings = 13590
print(dashboard_bookings == 13590)
