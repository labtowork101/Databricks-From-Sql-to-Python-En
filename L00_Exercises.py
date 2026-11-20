# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 0 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run (exercise 7).
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L00_Solutions` notebook.
# MAGIC
# MAGIC Run one cell at a time (exercise 8 contains intentional errors).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – A Tidy Notebook
# MAGIC In the `Python_Book` folder, create a new notebook `L00_First_Notebook` (default language Python).
# MAGIC The first cell must be a Markdown cell with the first-level heading `L00 – First notebook` and, below it, a line with today's date.
# MAGIC
# MAGIC **Expected result**: when you run the cell, the formatted heading appears and the `%md` code is no longer visible.
# MAGIC
# MAGIC (You do this exercise in the new notebook, not here.)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Exploring a Table in Catalog Explorer
# MAGIC Using only Catalog Explorer: how many columns does `samples.wanderbricks.properties` have? What type is `base_price`?
# MAGIC Then check with `DESCRIBE TABLE` in the cell below.
# MAGIC
# MAGIC **Expected result**: the same list of columns in both tools; `base_price` is a number with decimals (`float`).

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Write the DESCRIBE TABLE query here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Python as a Calculator
# MAGIC In 2024 the three guide properties had 6, 7, and 4 bookings, with revenue of 3966.21, 5139.59, and 2896.92.
# MAGIC In two separate Python cells, calculate the total number of bookings and the total revenue.
# MAGIC
# MAGIC **Expected result**: `17` and `12002.72`.

# COMMAND ----------

# Total number of bookings


# COMMAND ----------

# Total revenue


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Counting Destinations and Countries
# MAGIC With a single query on `samples.wanderbricks.destinations`, calculate the number of destinations and the number of distinct countries.
# MAGIC
# MAGIC **Expected result**: 42 destinations, 18 countries.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Write the query here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – One Cell, Two Lines
# MAGIC In the cell below, write on two lines the cancellation rate (× 100) of the Beach House in Amalfi (2 out of 4) and of the Bungalow in Sardinia (1 out of 7).
# MAGIC Run it and explain why only one result appears. Then move the two calculations into two separate cells.
# MAGIC
# MAGIC **Expected result**: in the single cell, only `14.285714285714285`; in the two cells, `50.0` and `14.285714285714285`. Compared with the 30% threshold, only Amalfi exceeds it.

# COMMAND ----------

# Two calculations in the same cell


# COMMAND ----------

# Amalfi


# COMMAND ----------

# Sardinia


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Your First Chart
# MAGIC Count the properties by `property_type` in `samples.wanderbricks.properties` and turn the result into a bar chart with **+ → Visualization**.
# MAGIC
# MAGIC **Expected result**: Urban Year-Round 9264, Summer Getaway 7068, Historical Place 1646, Ski Resort 185 (total 18163).

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Write the query here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Profiling the Working Copy
# MAGIC 1. With a single query on `workspace.python_book.b_bookings`, calculate: rows, distinct `booking_id` values, missing amounts, negative amounts, bookings with `check_out` earlier than `check_in`.
# MAGIC 2. With a second query, count the rows of `workspace.python_book.b_bookings_changes` by `change_type`.
# MAGIC 3. Explain why the negative amounts don't match in the two queries.
# MAGIC
# MAGIC **Expected result**: 72287 / 72247 / 30 / 13 / 8; changes: null_amount 30, negative_amount 12, swapped_dates 8, duplicate_row 40.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query 1: profile of b_bookings


# COMMAND ----------

# MAGIC %sql
# MAGIC -- Query 2: changes by type


# COMMAND ----------

# MAGIC %md
# MAGIC Explanation (step 3):
# MAGIC
# MAGIC ...

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC Each of the following three cells produces an error. Run them one at a time, note the name of the error and the part of the code it points to, and write the corrected version below.
# MAGIC
# MAGIC **Expected result**: the corrected cells return 42 rows, the value 18163, and five bookings.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
SELECT destination, country FROM samples.wanderbricks.destinations

# COMMAND ----------

# Fix 8a (error name: ...)


# COMMAND ----------

# MAGIC %sql
# MAGIC -- INTENTIONAL ERROR – cell 8b
# MAGIC SELECT COUNT(*) FROM samples.wanderbrick.properties

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix 8b (error name: ...)


# COMMAND ----------

# MAGIC %sql
# MAGIC -- INTENTIONAL ERROR – cell 8c
# MAGIC SELECT booking_id, amount
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC LIMIT 5

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix 8c (error name: ...)
