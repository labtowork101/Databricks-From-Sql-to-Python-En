# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 3 – Exercises
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**. Exercises 2, 4, 5, 6, and 7 have a `%sql` check on `samples.wanderbricks`.
# MAGIC Difficulty: ★ basic, ★★ intermediate, ★★★ challenge. Solutions: Appendix A and the `L03_Solutions` notebook.
# MAGIC
# MAGIC Work in a copy created with **Clone** (for example `L03_Exercises_done`). Run the setup cell first, then one cell at a time (exercise 8 contains intentional errors).
# MAGIC Each exercise has a **check** cell that prints the expected result, to compare with your own output.
# MAGIC
# MAGIC | property_id | title | destination_id | property_type | base_price | 2024 Bookings | Canceled | 2024 Revenue |
# MAGIC |---|---|---|---|---|---|---|---|
# MAGIC | 11670 | Historic Inn in Rome | 3900 | Historical Place | 284.97 | 6 | 0 | 3966.21 |
# MAGIC | 16317 | Bungalow in Sardinia | 4200 | Summer Getaway | 213.91 | 7 | 1 | 5139.59 |
# MAGIC | 16225 | Beach House in Amalfi | 1100 | Summer Getaway | 236.95 | 4 | 2 | 2896.92 |

# COMMAND ----------

# Setup cell: the book's constants
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Lists of the Guide Properties
# MAGIC Create the lists `bookings_2024 = [6, 7, 4]` and `revenues_2024 = [3966.21, 5139.59, 2896.92]` (Rome, Sardinia, Amalfi). Print:
# MAGIC 1. using indexes, the bookings of the first and the last property;
# MAGIC 2. using `len()`, `sum()`, `min()`, `max()`, the number of properties, the total, and the extremes of the bookings;
# MAGIC 3. the total revenue, the average revenue per property, and the average revenue per booking, with two decimal places.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("First: 6 - last: 4")
print("Properties: 3 - bookings: 17 - minimum: 4 - maximum: 7")
print("Total revenue: 12002.72")
print("Average revenue per property: 4000.91")
print("Average revenue per booking: 706.04")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Indexes and Slicing on Property Types
# MAGIC The four property types in `properties`, from most to least frequent: `"Urban Year-Round"` (9264), `"Summer Getaway"` (7068), `"Historical Place"` (1646), `"Ski Resort"` (185).
# MAGIC Create the lists `type_names` and `type_counts` and print: the most frequent type; the least frequent (with a negative index); the two most frequent and the two least frequent (with slicing); the total number of properties; the share of `"Ski Resort"` with one decimal place.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Urban Year-Round")
print("Ski Resort")
print(['Urban Year-Round', 'Summer Getaway'])
print(['Historical Place', 'Ski Resort'])
print(18163)
print("Ski Resort: 1.0%")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: properties by type (9264, 7068, 1646, 185)
# MAGIC SELECT property_type, COUNT(*) AS property_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY property_type
# MAGIC ORDER BY property_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – The Dictionary of a Property
# MAGIC Create the dictionary `sardinia` with the keys `property_id` (16317), `title` (`"Bungalow in Sardinia"`), `destination_id` (4200), `property_type` (`"Summer Getaway"`), `base_price` (213.91).
# MAGIC 1. Print the title and the price in an f-string (`Bungalow in Sardinia: 213.91`).
# MAGIC 2. Update the price to 219.0, add the key `bookings_2024` with the value 7, and print the new price.
# MAGIC 3. Print the result of `get("max_guests")`, the check `"rating" in sardinia`, and the number of pairs.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Bungalow in Sardinia: 213.91")
print(219.0)
print(None)
print(False)
print(6)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Active Statuses and Distinct Values
# MAGIC Given the lists below:
# MAGIC 1. check with `in` whether the first and the third status of the sample are active;
# MAGIC 2. check whether `"refunded"` appears in the sample;
# MAGIC 3. calculate the number of distinct statuses in the sample with a set;
# MAGIC 4. calculate from the `status_counts` list the number of active bookings (`confirmed` and `completed`) and compare it with the `%sql` check.

# COMMAND ----------

sample_statuses = ["confirmed", "cancelled", "pending", "completed", "cancelled"]
active_statuses = ["confirmed", "completed"]
status_names = ["pending", "confirmed", "cancelled", "completed"]
status_counts = [31575, 17948, 15285, 7439]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("confirmed active: True")
print("pending active: False")
print("refunded present: False")
print("Distinct statuses: 4")
print("Active bookings: 25387")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: active bookings (25387)
# MAGIC SELECT COUNT(*) AS active_bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE status IN ('confirmed', 'completed')

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – Decoding the Destinations
# MAGIC 1. With `destination_names` and `guide_destination_ids` (cell below), print the name of the destination of each guide property, reading the codes from the list by index and using them as keys of the dictionary.
# MAGIC 2. Add the code 9999 at the end of the list with `append()` and print its decoding with `get()`, writing `n/a` when the destination isn't known (format `9999: n/a`).

# COMMAND ----------

destination_names = {
    1100: "Amalfi",
    2300: "Florence",
    3900: "Rome",
    4200: "Sardinia",
}
guide_destination_ids = [3900, 4200, 1100]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Rome")
print("Sardinia")
print("Amalfi")
print("9999: n/a")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the Italian destinations
# MAGIC SELECT destination_id, destination
# MAGIC FROM samples.wanderbricks.destinations
# MAGIC WHERE country = 'Italy'
# MAGIC ORDER BY destination_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – A Small Table
# MAGIC With the list of dictionaries `guide_properties` (cell below) and the double access row → key:
# MAGIC 1. calculate the total bookings by adding up the three values;
# MAGIC 2. calculate and print the cancellation rate of Sardinia and of Amalfi, with one decimal place (`Bungalow in Sardinia: 14.3%`);
# MAGIC 3. add to the Amalfi row the key `is_critical` with the result of comparing its rate with `CANCELLATION_RATE_THRESHOLD`, and print it.

# COMMAND ----------

guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Total bookings: 17")
print("Bungalow in Sardinia: 14.3%")
print("Beach House in Amalfi: 50.0%")
print(True)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the three rows recalculated from the bookings table
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                              AS bookings_2024,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_2024,
# MAGIC        ROUND(SUM(total_amount), 2)                           AS revenue_2024
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – The Overall Cancellation Rate
# MAGIC 1. Create the dictionary `status_counts_by_name` with the four statuses as keys and the counts as values (pending 31575, confirmed 17948, cancelled 15285, completed 7439).
# MAGIC 2. Reading the values by key, calculate the total bookings, the overall cancellation rate, and the share of active bookings (`confirmed` and `completed`), with one decimal place.
# MAGIC 3. Read the `"refunded"` status with `get()`, printing `n/a` if it's missing.
# MAGIC 4. Classify the overall rate with the four states of Chapter 2 (`"missing data"`, `"impossible value"`, `"critical"`, `"ok"`) and compare it with the `%sql` check.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Check: expected result
print("Total: 72247")
print("Cancellation rate: 21.2% (ok)")
print("Active share: 35.1%")
print("refunded: n/a")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: overall cancellation rate (21.2)
# MAGIC SELECT ROUND(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS cancellation_rate
# MAGIC FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one at a time, note the name of the error (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `Beach House in Amalfi`, `Bungalow in Sardinia`, `6`, `{1100: 'Amalfi', 2300: 'Florence'}`, `16332`, `[11670, 16317, 16225]`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
print(property_titles[3])

# COMMAND ----------

# Fix 8a (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
sardinia = {"property_id": 16317, "title": "Bungalow in Sardinia", "base_price": 213.91}
print(sardinia["Title"])

# COMMAND ----------

# Fix 8b (error name: ...)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
bookings_2024 = [6, None, 4]
print(max(bookings_2024))

# COMMAND ----------

# Fix 8c (error name: ...; print the maximum of only the values that are present, read with indexes)


# COMMAND ----------

# INTENTIONAL ERROR – cell 8d
destination_names = {1100: "Amalfi" 2300: "Florence"}

# COMMAND ----------

# Fix 8d (error name: ...; print the corrected dictionary)


# COMMAND ----------

# SILENT ERROR – cell 8e (total of the two most frequent types)
type_counts = [9264, 7068, 1646, 185]
first_two_total = type_counts[1] + type_counts[2]
print(first_two_total)

# COMMAND ----------

# Fix 8e (what's wrong: ...)


# COMMAND ----------

# SILENT ERROR – cell 8f
guide_ids = [11670, 16317]
guide_ids = guide_ids.append(16225)
print(guide_ids)

# COMMAND ----------

# Fix 8f (what's wrong: ...)

