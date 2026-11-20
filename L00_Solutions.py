# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 0 – Solutions
# MAGIC
# MAGIC Commented solutions to the Chapter 0 exercises (full text in Appendix A).
# MAGIC Run one cell at a time.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – A Tidy Notebook
# MAGIC Content of the first cell of `L00_First_Notebook` (the date is an example):
# MAGIC
# MAGIC ```
# MAGIC %md
# MAGIC # L00 – First notebook
# MAGIC November 20, 2026
# MAGIC ```
# MAGIC The `%md` command must be on the first line; `#` followed by a space creates the first-level heading.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Exploring a Table in Catalog Explorer
# MAGIC Catalog → samples → wanderbricks → properties, columns page. The check in SQL:

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC The number of columns is the number of rows in the output (one row per column); `base_price` has type `float`.
# MAGIC
# MAGIC ## Exercise 3 ★ – Python as a Calculator

# COMMAND ----------

# Total 2024 bookings of the three guide properties
6 + 7 + 4

# COMMAND ----------

# Total 2024 revenue of the three guide properties
3966.21 + 5139.59 + 2896.92

# COMMAND ----------

# MAGIC %md
# MAGIC Two cells, because the automatic output of a Python cell shows only the value of the last line.
# MAGIC
# MAGIC ## Exercise 4 ★★ – Counting Destinations and Countries

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS destinations_count,
# MAGIC        COUNT(DISTINCT country) AS countries_count
# MAGIC FROM samples.wanderbricks.destinations

# COMMAND ----------

# MAGIC %md
# MAGIC Expected: 42 and 18.
# MAGIC
# MAGIC ## Exercise 5 ★★ – One Cell, Two Lines

# COMMAND ----------

# Both lines are run, but the output shows only the last one
2 / 4 * 100
1 / 7 * 100

# COMMAND ----------

# Amalfi
2 / 4 * 100

# COMMAND ----------

# Sardinia
1 / 7 * 100

# COMMAND ----------

# MAGIC %md
# MAGIC `50.0` has a decimal because division always returns a number with decimals; `14.285714285714285` is not rounded
# MAGIC (rounding comes in Chapter 1). Only Amalfi (50%) exceeds the 30% threshold.
# MAGIC
# MAGIC ## Exercise 6 ★★ – Your First Chart

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_type, COUNT(*) AS properties_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY property_type
# MAGIC ORDER BY properties_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC After running the cell: **+ → Visualization**, type **Bar**, X axis `property_type`, Y axis `properties_count`, **Save**.
# MAGIC Total of the bars: 9264 + 7068 + 1646 + 185 = 18163, the number of rows in `properties`.
# MAGIC
# MAGIC ## Exercise 7 ★★★ – Profiling the Working Copy

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   COUNT(*)                                                AS rows_count,
# MAGIC   COUNT(DISTINCT booking_id)                              AS distinct_bookings,
# MAGIC   SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END)   AS missing_amount,
# MAGIC   SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END)       AS negative_amount,
# MAGIC   SUM(CASE WHEN check_out < check_in THEN 1 ELSE 0 END)   AS swapped_dates
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT change_type, COUNT(*) AS changes_count
# MAGIC FROM workspace.python_book.b_bookings_changes
# MAGIC GROUP BY change_type
# MAGIC ORDER BY change_type

# COMMAND ----------

# MAGIC %md
# MAGIC Expected: 72287 / 72247 / 30 / 13 / 8 and, by type, duplicate_row 40, negative_amount 12, null_amount 30, swapped_dates 8.
# MAGIC
# MAGIC There are 13 negative amounts in `b_bookings` but 12 in the changes: one booking already has a negative amount in the original data
# MAGIC of `samples.wanderbricks.bookings`, so it isn't a change. The 40 duplicate rows explain the difference between rows (72287) and distinct bookings (72247).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC **8a** – `SyntaxError: invalid syntax`: `%sql` is missing, so the query is read as Python.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT destination, country FROM samples.wanderbricks.destinations

# COMMAND ----------

# MAGIC %md
# MAGIC **8b** – `TABLE_OR_VIEW_NOT_FOUND`: the message shows `samples`.`wanderbrick`.`properties`; the schema is called `wanderbricks`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) FROM samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC **8c** – `UNRESOLVED_COLUMN`: the `amount` column doesn't exist in `bookings`; the message suggests `total_amount`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT booking_id, total_amount
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC LIMIT 5
