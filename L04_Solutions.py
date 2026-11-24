# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 4 – Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in `L04_Exercises` (the same as in Appendix A). Run the setup cell first, then one cell at a time.
# MAGIC In exercise 8 the cells with the errors aren't repeated: here there are only the fixes, with the name of the error in the comment.

# COMMAND ----------

# Setup cell: constants and collections used in the exercises
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]
bookings_2024 = [6, 7, 4]

# The guide properties as a small table (Chapter 3)
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – A Loop over the Bookings

# COMMAND ----------

bookings_2024 = [6, 7, 4]
revenues_2024 = [3966.21, 5139.59, 2896.92]

# 1. One iteration for each value of the list
for bookings in bookings_2024:
    print(f"Bookings: {bookings}")

# 2. Before the loop: the accumulators start from zero
property_count = 0
total_bookings = 0
for bookings in bookings_2024:
    # Inside the loop: a counter and a total
    property_count = property_count + 1
    total_bookings = total_bookings + bookings

total_revenue = 0
for revenue in revenues_2024:
    total_revenue = total_revenue + revenue

# 3. After the loops: the results are used (decimals always formatted)
revenue_per_booking = total_revenue / total_bookings
print(f"Properties: {property_count} - bookings: {total_bookings}")
print(f"Total revenue: {total_revenue:.2f}")
print(f"Average revenue per booking: {revenue_per_booking:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Nights and Positions with range()

# COMMAND ----------

# 1. range(1, 10): from 1 to 9, the end is excluded
possible_nights = list(range(1, 10))
print(possible_nights)
print(f"Possible nights: {len(possible_nights)}")

# 2. Step 2: 1, 3, 5, 7, 9
amalfi_price = 236.95
for nights in range(1, 10, 2):
    cost = amalfi_price * nights
    print(f"nights: {nights} - cost: {cost:.2f}")

# 3. Positions start from 0: to number from 1, print position + 1
for position in range(len(property_titles)):
    print(f"{position + 1} - {property_titles[position]}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: cost of 1, 3, 5, 7, 9 nights at the base price of the Amalfi property
# MAGIC SELECT id AS nights, ROUND(id * 236.95, 2) AS cost
# MAGIC FROM range(1, 10, 2)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Property Types in a Dictionary

# COMMAND ----------

type_counts_by_name = {
    "Urban Year-Round": 9264,
    "Summer Getaway": 7068,
    "Historical Place": 1646,
    "Ski Resort": 185,
}

# 1. values(): the counts are enough
total_properties = 0
for count in type_counts_by_name.values():
    total_properties = total_properties + count
print(f"Total properties: {total_properties}")

# 2. items(): key and value in two loop variables
for property_type, count in type_counts_by_name.items():
    share = count / total_properties * 100
    print(f"{property_type}: {count} ({share:.1f}%)")

# 3. A filter inside the loop: only the types with more than 5000 properties
large_types = []
for property_type, count in type_counts_by_name.items():
    if count > 5000:
        large_types.append(property_type)
print(large_types)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: properties and shares by type (51.0, 38.9, 9.1, 1.0)
# MAGIC SELECT property_type,
# MAGIC        COUNT(*)                           AS property_count,
# MAGIC        ROUND(COUNT(*) * 100.0 / 18163, 1) AS share
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY property_type
# MAGIC ORDER BY property_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – A Sample of Amounts with Anomalies

# COMMAND ----------

amounts_sample = [512.4, -80.0, None, 1250.75, 333.3, None, -15.5, 968.1]

missing_count = 0
negative_count = 0
valid_count = 0
valid_total = 0
negative_amounts = []
for amount in amounts_sample:
    # The check on None first: a comparison None < 0 would produce a TypeError
    if amount is None:
        missing_count = missing_count + 1
    elif amount < 0:
        negative_count = negative_count + 1
        negative_amounts.append(amount)
    else:
        valid_count = valid_count + 1
        valid_total = valid_total + amount

# The average is divided by the number of valid amounts, not by the length of the list
valid_average = valid_total / valid_count
print(f"Missing: {missing_count} - negative: {negative_count} - valid: {valid_count}")
print(f"Negative amounts: {negative_amounts}")
print(f"Valid total: {valid_total:.2f}")
print(f"Valid average: {valid_average:.2f}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same classification on the whole b_bookings teaching copy (30 nulls, 13 negatives)
# MAGIC SELECT COUNT(*) - COUNT(total_amount)                    AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – Price Bands for Each Row

# COMMAND ----------

guide_rows = [
    {"title": "Historic Inn in Rome", "base_price": 284.97, "bookings_2024": 6, "revenue_2024": 3966.21},
    {"title": "Bungalow in Sardinia", "base_price": 213.91, "bookings_2024": 7, "revenue_2024": 5139.59},
    {"title": "Beach House in Amalfi", "base_price": 236.95, "bookings_2024": 4, "revenue_2024": 2896.92},
]

# Two new columns for each row: the classification (like CASE WHEN) and a calculation
for row in guide_rows:
    if row["base_price"] >= 250:
        row["price_band"] = "high"
    elif row["base_price"] >= 200:
        row["price_band"] = "medium"
    else:
        row["price_band"] = "low"
    row["revenue_per_booking"] = row["revenue_2024"] / row["bookings_2024"]
    print(f"{row['title']}: {row['price_band']} - {row['revenue_per_booking']:.2f} per booking")

# A second loop filters the rows with the new column
medium_titles = []
for row in guide_rows:
    if row["price_band"] == "medium":
        medium_titles.append(row["title"])
print(medium_titles)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: price bands of the guide properties (high, medium, medium)
# MAGIC SELECT property_id, title, base_price,
# MAGIC        CASE WHEN base_price >= 250 THEN 'high'
# MAGIC             WHEN base_price >= 200 THEN 'medium'
# MAGIC             ELSE 'low'
# MAGIC        END AS price_band
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – How Many Years Does It Take?

# COMMAND ----------

ROME_PRICE = 284.97

# 1. while: repeat as long as the price doesn't exceed Rome's
projected_price = 213.91
years = 0
while projected_price <= ROME_PRICE:
    projected_price = projected_price * 1.08   # the block updates the condition variable
    years = years + 1
print(f"8%: {years} years - price {projected_price:.2f}")

# 2. The same calculation with a growth of 3%
projected_price = 213.91
years = 0
while projected_price <= ROME_PRICE:
    projected_price = projected_price * 1.03
    years = years + 1
print(f"3%: {years} years - price {projected_price:.2f}")

# 3. for with a maximum number of iterations and break: it can't loop forever
projected_price = 213.91
for year in range(1, 21):
    projected_price = projected_price * 1.08
    if projected_price > ROME_PRICE:
        break
print(f"With for and break: {year} years - price {projected_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – Counting by Category

# COMMAND ----------

sample_statuses = ["confirmed", "cancelled", "pending", "pending", "completed", "cancelled", "pending", "confirmed", "cancelled", "pending"]

# 1. A dictionary as accumulator: status -> count
status_counts = {}
for status in sample_statuses:
    if status in status_counts:
        status_counts[status] = status_counts[status] + 1   # status already seen: increase
    else:
        status_counts[status] = 1                           # first time: new key
print(status_counts)

# 2. Total with items() and cancellation rate of the sample
total_count = 0
for status, count in status_counts.items():
    total_count = total_count + count
cancellation_rate = status_counts["cancelled"] / total_count * 100

# 30.0 isn't greater than 30.0: the threshold is exceeded only by a higher value
if cancellation_rate > CANCELLATION_RATE_THRESHOLD:
    cancellation_status = "critical"
else:
    cancellation_status = "ok"
print(f"Total: {total_count}")
print(f"Sample cancellation rate: {cancellation_rate:.1f}% ({cancellation_status})")

# 3. The position of the first completed booking: stop at the first result
for position in range(len(sample_statuses)):
    if sample_statuses[position] == "completed":
        break
print(f"First completed booking at position: {position}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same count by status, done by GROUP BY on the whole table
# MAGIC SELECT status, COUNT(*) AS bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC GROUP BY status
# MAGIC ORDER BY bookings DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors (Fixes)

# COMMAND ----------

# Fix 8a – SyntaxError: expected ':'
# The for line ends with a colon
for title in property_titles:
    print(title)

# COMMAND ----------

# Fix 8b – IndentationError: unexpected indent
# The print was indented more than the block: the total is printed once, after the loop
total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
print(total_bookings)

# COMMAND ----------

# Fix 8c – TypeError: 'int' object is not iterable
# len() returns a number: the positions are looped over with range(len(...))
for position in range(len(property_titles)):
    print(property_titles[position])

# COMMAND ----------

# Fix 8d – KeyError: 'Bookings_2024'
# Keys distinguish uppercase from lowercase: the key is "bookings_2024"
total_bookings = 0
for row in guide_properties:
    total_bookings = total_bookings + row["bookings_2024"]
print(total_bookings)

# COMMAND ----------

# Fix 8e – silent error: counter reset at each iteration (Canceled: 0)
# The counter is prepared once, before the loop
sample_statuses = ["confirmed", "cancelled", "pending", "completed", "cancelled", "pending"]
cancelled_count = 0
for status in sample_statuses:
    if status == "cancelled":
        cancelled_count = cancelled_count + 1
print(f"Canceled: {cancelled_count}")

# COMMAND ----------

# Fix 8f – silent error: the end of range() is excluded (2025 is missing)
for year in range(2022, 2026):
    print(year)
