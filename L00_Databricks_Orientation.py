# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 0 – Finding Your Way Around Databricks
# MAGIC
# MAGIC Notebook for Chapter 0 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Run SQL, Markdown, and Python cells in the same notebook
# MAGIC - Refer to tables by their three-level name `catalog.schema.table`
# MAGIC - Read the output of a cell and the first line of an error message
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Notebook attached to **Serverless** compute (selector in the upper-right corner)
# MAGIC - `L00_Prepare_Data` notebook already run with Run all (section 0.7), needed for the cells on `b_bookings`
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: section 0.9 contains intentional errors, and Run all would stop at the first one.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0.3 Notebooks and Cells
# MAGIC A cell that starts with `%sql` contains a SQL query; the output is a grid, as in a SQL client.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS bookings_count
# MAGIC FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: **72247**.
# MAGIC
# MAGIC This cell is a Markdown cell (`%md`): when you run it, the code disappears and the formatted text remains.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0.4 Where the Data Lives: Catalog, Schema, Table
# MAGIC Three-level name: `samples` (catalog) . `wanderbricks` (schema) . `bookings` (table).
# MAGIC The same information as the columns page in Catalog Explorer is returned by `DESCRIBE TABLE`.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: 10 columns (booking_id, user_id, property_id, check_in, check_out, guests_count, total_amount, status, created_at, updated_at).
# MAGIC
# MAGIC ## 0.5 Running, Interrupting, and Reading the Output
# MAGIC Try the three ways to run a cell: the button, Ctrl/Cmd+Enter (stays on the cell), Shift+Enter (moves to the next one).
# MAGIC During a long run, the cell's stop button or the **Interrupt** command at the top stops the computation.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0.6 Python on the Same Page: The Calculator and the Last Line
# MAGIC **SQL Bridge**: a SELECT without FROM computes an expression; in Python, the expression is written on its own in the cell.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 3966.21 + 5139.59 AS total_revenue

# COMMAND ----------

3966.21 + 5139.59

# COMMAND ----------

# 2024 cancellation rate of the Beach House in Amalfi: 2 canceled out of 4 bookings
2 / 4 * 100

# COMMAND ----------

"Summer Getaway"

# COMMAND ----------

# MAGIC %md
# MAGIC **Only the last line**: the next cell runs both lines, but the output shows only the value of the last one (1173.38).

# COMMAND ----------

3966.21 + 5139.59
5139.59 - 3966.21

# COMMAND ----------

# 2024 revenue of the three guide properties
3966.21 + 5139.59 + 2896.92

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0.7 Preparing the Book's Data
# MAGIC Before you continue, the `L00_Prepare_Data` notebook must have been run **once** with Run all.
# MAGIC The next cell checks that the two tables it creates exist in the working schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN workspace.python_book

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result: at least the `b_bookings` and `b_bookings_changes` tables. If the cell returns an error, run `L00_Prepare_Data`.
# MAGIC
# MAGIC ## 0.8 A First Look at the Data

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status, COUNT(*) AS bookings_count
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC GROUP BY status
# MAGIC ORDER BY bookings_count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT MIN(check_in) AS first_check_in,
# MAGIC        MAX(check_in) AS last_check_in
# MAGIC FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_type, COUNT(*) AS properties_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY property_type
# MAGIC ORDER BY properties_count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT destination_id, destination, country
# MAGIC FROM samples.wanderbricks.destinations
# MAGIC WHERE country = 'Italy'
# MAGIC ORDER BY destination_id

# COMMAND ----------

# MAGIC %md
# MAGIC **Original and working copy**: `b_bookings` has 40 more rows (the duplicate rows) but the same number of distinct bookings.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS rows_count,
# MAGIC        COUNT(DISTINCT booking_id) AS distinct_bookings
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) AS missing_amount,
# MAGIC   SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END)     AS negative_amount
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC **A first chart**: after running the next cell, choose **+ → Visualization** above the results, type **Bar**, X axis `check_in_month`, Y axis `bookings_count`, then **Save**.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT month(check_in) AS check_in_month,
# MAGIC        COUNT(*) AS bookings_count
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE year(check_in) = 2024
# MAGIC GROUP BY month(check_in)
# MAGIC ORDER BY check_in_month

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0.9 Reading an Error Message
# MAGIC The following cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the name of the error and the sentence that describes it;
# MAGIC - the **Fix** cell right below must run **without errors** and show the result.
# MAGIC
# MAGIC Expected results of the fixes: a grid with only the `status` column (72,247 rows in all, the first ones are shown); the value 72247; a grid with `property_id`, `title`, `base_price`.

# COMMAND ----------

# INTENTIONAL ERROR – query in a Python cell (%sql is missing)
SELECT status FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix: %sql on the first line
# MAGIC SELECT status FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC -- INTENTIONAL ERROR – table that doesn't exist (booking instead of bookings)
# MAGIC SELECT COUNT(*) FROM samples.wanderbricks.booking

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix
# MAGIC SELECT COUNT(*) FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %sql
# MAGIC -- INTENTIONAL ERROR – column that doesn't exist (price instead of base_price)
# MAGIC SELECT property_id, title, price
# MAGIC FROM samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix
# MAGIC SELECT property_id, title, base_price
# MAGIC FROM samples.wanderbricks.properties

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - Notebook = a sequence of cells; default language Python; `%sql` and `%md` on the first line change the cell's language.
# MAGIC - Serverless compute runs the cells; after a period of inactivity the session closes: the outputs remain, the compute memory doesn't.
# MAGIC - Tables by three-level name; `samples` is read-only, the book writes only to `workspace.python_book`.
# MAGIC - Output of a Python cell = value of the last line.
# MAGIC - Run all stops at the first error: run the chapter notebooks one cell at a time.
# MAGIC - When you hit an error: first the name of the error, then the sentence that describes it.
