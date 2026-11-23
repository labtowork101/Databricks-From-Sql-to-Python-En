# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 12 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; the `L11_Final_Project` notebook run at least once (`g_updated_cancellations_destination_month` table); the `utils` notebook in the same `Python_Book` folder; the **Cancellations by Destination 2024** dashboard built by following Chapter 12. Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L12_Solutions` notebook.
# MAGIC
# MAGIC Work in a **copy** of this notebook, created with **Clone** (for example `L12_Exercises_done`). Each exercise has a part in the dashboard and a part in the notebook, which calculates the values to compare with the dashboard. The notebook **doesn't write tables**.
# MAGIC
# MAGIC Run the `%run ./utils` cell and the setup cell first, then one exercise at a time. Exercise 8 contains a cell that must fail (**INTENTIONAL ERROR**) and two cells that produce a wrong result (**SILENT ERROR**): write the fix below each one. Don't use Run all.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC
# MAGIC The first cell contains only `%run ./utils`; the second reads the report table and defines `exercise_query`, the dataset query with the two parameters `:threshold` and `:min_bookings` (exercise 5). Expected result: `317` and `Setup complete`.

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
# MAGIC **Dashboard.** On the **Overview** page, add a **Revenue** counter with the sum of `revenue` (**Value** → `revenue`, aggregation **SUM**), with **Format** → **Custom**, **Abbreviation** → **None**. Read the value with the **Country** filter on **All** and on **Italy**.
# MAGIC
# MAGIC **Notebook.** Calculate the total revenue and the revenue of Italy, rounded to two decimal places, and print them on the same line.
# MAGIC
# MAGIC *Expected result:* on the dashboard `7,529,860.44` and `408,538.77`; in the notebook `7529860.44 408538.77`.

# COMMAND ----------

# Exercise 1 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – A Filter on the Destination
# MAGIC
# MAGIC **Dashboard.** Add to the page a **Multiple values** filter on the `destination` field, with the title **Destination**, and choose **Amalfi** (with **Country** on **All**). Read the four counters.
# MAGIC
# MAGIC **Notebook.** Write the values you read in the `amalfi_dashboard` dictionary (keys: `Bookings`, `Cancellation Rate (%)`, `Critical Combinations`, `Revenue`), calculate the same values in `amalfi_expected`, and compare them with a loop, as in section 12.12.
# MAGIC
# MAGIC *Expected result:* on the dashboard `51`, `41.2`, `1`, `29,503.96`; in the notebook four rows with outcome `OK`.

# COMMAND ----------

# Exercise 2 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – The Moving Threshold
# MAGIC
# MAGIC **Dashboard.** With **Destination** and **Country** on **All**, enter the values 25, 35, 45, and 50 in the **Threshold (%)** parameter, noting the **Critical Combinations** counter each time. At the end, set the threshold back to 30.
# MAGIC
# MAGIC **Notebook.** With a loop on the list `[25.0, 35.0, 45.0, 50.0]`, run `exercise_query` with `args={"threshold": ..., "min_bookings": MIN_BOOKINGS}` and print the threshold and the number of critical combinations.
# MAGIC
# MAGIC *Expected result:* `157`, `115`, `32`, `6`.

# COMMAND ----------

# Exercise 3 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Chart by Country
# MAGIC
# MAGIC **Dashboard.** Add a bar chart with `country` on the X axis and the `overall_cancellation_rate` measure on the Y axis, with **Labels** on and the title **Cancellation Rate by Country (%)**.
# MAGIC
# MAGIC **Notebook.** For each country, calculate the overall rate (`overall_cancellation_rate`) and the average of the rates (`average_of_rates`), show the result in descending order of rate (with equal rates, by country name), and print the country with the highest rate and the one with the lowest rate.
# MAGIC
# MAGIC *Expected result:* 18 rows; the highest `China 44.6`, the lowest `Canada 29.6`; Egypt `40.7`, average of the rates `36.2`.

# COMMAND ----------

# Exercise 4 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – The Minimum Volume as a Parameter
# MAGIC
# MAGIC **Dashboard.** In the query of the **Cancellation report** dataset, replace the number 20 with the `:min_bookings` parameter (the query becomes the one in `exercise_query`); in the parameter settings, choose **Type** → **Numeric**, **Numeric type** → **Integer**, **Display name** `Minimum volume`, and the value 20. Add it to the page with a **Single value** filter. With the threshold at 30%, read the critical combinations with the minimum volume at 10 and at 30, then set it back to 20.
# MAGIC
# MAGIC **Notebook.** For the minimum volumes 10 and 30, run `exercise_query` with the threshold 30 and count each status (`groupBy` + `count`), printing a list of (status, number) pairs.
# MAGIC
# MAGIC *Expected result:* with 10, `critical 190`, `not assessable 93`, `ok 34`; with 30, `critical 114`, `not assessable 191`, `ok 12`.

# COMMAND ----------

# Exercise 5 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – A Page by Continent
# MAGIC
# MAGIC **Dashboard.** Create a second dataset, **Report by continent**, with a query that joins the report table to `samples.wanderbricks.countries` on the country name and adds the `continent` column; in the new dataset, define a measure with the overall rate. Create a second page, **Continents**, with a bar chart of the rate by continent and a table with bookings and canceled bookings by continent.
# MAGIC
# MAGIC **Notebook.** Write the same query in `continent_query` (with the constants `PROJECT_REPORT_TABLE` and `COUNTRIES_TABLE`), count its rows, and show bookings, canceled bookings, and overall rate by continent, in descending order of bookings.
# MAGIC
# MAGIC *Expected result:* `317` rows (none lost in the join); Europe `5557 2110 38`, Asia `5290 1969 37.2`, Oceania `1246 481 38.6`, North America `1212 447 36.9`, Africa `285 116 40.7`.

# COMMAND ----------

# Exercise 6 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Checking a Filtered View
# MAGIC
# MAGIC **Dashboard.** Set up the **Overview** page with **Country** on **Italy**, **Destination** on **All**, threshold 40, and minimum volume 20, and read the **Bookings**, **Cancellation Rate (%)**, **Critical Combinations**, and **Revenue** counters. At the end, use **Reset all to default**.
# MAGIC
# MAGIC **Notebook.** Write the values you read in a dictionary; run `exercise_query` with the same parameters, apply the same filter on the country, calculate the four values, and compare them with a loop.
# MAGIC
# MAGIC *Expected result:* `714`, `37.8`, `4`, `408538.77`; four rows with outcome `OK`.

# COMMAND ----------

# Exercise 7 – write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC
# MAGIC **Notebook.** For each of the next three cells: run the cell, note the type of the error and the message (or the wrong result), and write the fix in the empty cell below.
# MAGIC
# MAGIC **Dashboard.** Reproduce and fix three mistakes: **8d** a counter with `AVG(cancellation_rate)` instead of the measure; **8e** the chart by month with `check_in_month` on the X axis left with the **Continuous** scale and the **SUM** aggregation; **8f** a change to a title in the draft, then the published version opened with **View published** without publishing again.
# MAGIC
# MAGIC *Expected result:* 8a `UNBOUND_SQL_PARAMETER` on `min_bookings`; 8b no error, but `31.9` instead of `35.0`; 8c no error, but `False` instead of `True`; 8d `37.3` instead of `37.7`; 8e a single bar, `2,164` long, instead of the 12 bars of the rate; 8f the old title in the published version.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (the query with two parameters)
print(spark.sql(exercise_query, args={"threshold": 30.0}).count())

# COMMAND ----------

# Fix 8a – write your solution here


# COMMAND ----------

# SILENT ERROR – cell 8b (the rate of the United Kingdom)
uk_df = report_df.filter(F.col("country") == "United Kingdom")
print(uk_df.agg(F.round(F.avg("cancellation_rate"), 1)).collect()[0][0])

# COMMAND ----------

# Fix 8b – write your solution here


# COMMAND ----------

# SILENT ERROR – cell 8c (the value read on the dashboard)
dashboard_bookings = 13.590
print(dashboard_bookings == 13590)

# COMMAND ----------

# Fix 8c – write your solution here

