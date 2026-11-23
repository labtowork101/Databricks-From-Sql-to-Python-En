# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 3 – Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in `L03_Exercises` (the same as in Appendix A). Run the setup cell first, then one cell at a time.
# MAGIC In exercise 8 the cells with the errors aren't repeated: here there are only the fixes, with the name of the error in the comment.

# COMMAND ----------

# Setup cell: the book's constants
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Lists of the Guide Properties

# COMMAND ----------

bookings_2024 = [6, 7, 4]
revenues_2024 = [3966.21, 5139.59, 2896.92]

# First property: index 0; last: index -1
print(f"First: {bookings_2024[0]} - last: {bookings_2024[-1]}")

# Count, sum, minimum, and maximum
print(f"Properties: {len(bookings_2024)} - bookings: {sum(bookings_2024)} - minimum: {min(bookings_2024)} - maximum: {max(bookings_2024)}")

# Revenue: total, average per property (sum / number of properties),
# average per booking (sum of revenue / sum of bookings)
total_revenue = sum(revenues_2024)
average_revenue = total_revenue / len(revenues_2024)
revenue_per_booking = total_revenue / sum(bookings_2024)
print(f"Total revenue: {total_revenue:.2f}")
print(f"Average revenue per property: {average_revenue:.2f}")
print(f"Average revenue per booking: {revenue_per_booking:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Indexes and Slicing on Property Types

# COMMAND ----------

type_names = ["Urban Year-Round", "Summer Getaway", "Historical Place", "Ski Resort"]
type_counts = [9264, 7068, 1646, 185]

print(type_names[0])      # the most frequent: the list is sorted from most frequent
print(type_names[-1])     # the least frequent: the last value
print(type_names[:2])     # the first two (like LIMIT 2)
print(type_names[-2:])    # the last two

total_properties = sum(type_counts)
ski_share = type_counts[-1] / total_properties * 100
print(total_properties)
print(f"{type_names[-1]}: {ski_share:.1f}%")

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

# COMMAND ----------

sardinia = {
    "property_id": 16317,
    "title": "Bungalow in Sardinia",
    "destination_id": 4200,
    "property_type": "Summer Getaway",
    "base_price": 213.91,
}
# In f-strings, keys go between single quotes
print(f"{sardinia['title']}: {sardinia['base_price']}")

# The same notation updates an existing key and adds a new one
sardinia["base_price"] = 219.0
sardinia["bookings_2024"] = 7
print(sardinia["base_price"])

print(sardinia.get("max_guests"))   # missing key: None
print("rating" in sardinia)         # in checks the keys
print(len(sardinia))                # 5 initial keys + bookings_2024

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Active Statuses and Distinct Values

# COMMAND ----------

sample_statuses = ["confirmed", "cancelled", "pending", "completed", "cancelled"]
active_statuses = ["confirmed", "completed"]
status_names = ["pending", "confirmed", "cancelled", "completed"]
status_counts = [31575, 17948, 15285, 7439]

# First status: index 0; third status: index 2
print(f"{sample_statuses[0]} active: {sample_statuses[0] in active_statuses}")
print(f"{sample_statuses[2]} active: {sample_statuses[2] in active_statuses}")
print(f"refunded present: {'refunded' in sample_statuses}")

# The set removes the repetitions ("cancelled" appears twice)
print(f"Distinct statuses: {len(set(sample_statuses))}")

# confirmed at position 1, completed at position 3
print(f"Active bookings: {status_counts[1] + status_counts[3]}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: active bookings (25387)
# MAGIC SELECT COUNT(*) AS active_bookings
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE status IN ('confirmed', 'completed')

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – Decoding the Destinations

# COMMAND ----------

destination_names = {
    1100: "Amalfi",
    2300: "Florence",
    3900: "Rome",
    4200: "Sardinia",
}
guide_destination_ids = [3900, 4200, 1100]

# The value read from the list becomes the key of the dictionary
print(destination_names[guide_destination_ids[0]])
print(destination_names[guide_destination_ids[1]])
print(destination_names[guide_destination_ids[2]])

# A code that isn't there: get() returns None instead of a KeyError
guide_destination_ids.append(9999)
last_id = guide_destination_ids[-1]
last_name = destination_names.get(last_id)
if last_name is None:
    last_name = "n/a"
print(f"{last_id}: {last_name}")

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

# COMMAND ----------

guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]

# First the row (index), then the column (key)
total_bookings = guide_properties[0]["bookings_2024"] + guide_properties[1]["bookings_2024"] + guide_properties[2]["bookings_2024"]
print(f"Total bookings: {total_bookings}")

sardinia_row = guide_properties[1]
sardinia_rate = sardinia_row["cancelled_2024"] / sardinia_row["bookings_2024"] * 100
print(f"{sardinia_row['title']}: {sardinia_rate:.1f}%")

amalfi_row = guide_properties[2]
amalfi_rate = amalfi_row["cancelled_2024"] / amalfi_row["bookings_2024"] * 100
print(f"{amalfi_row['title']}: {amalfi_rate:.1f}%")

# amalfi_row and guide_properties[2] are the same dictionary
amalfi_row["is_critical"] = amalfi_rate > CANCELLATION_RATE_THRESHOLD
print(guide_properties[2]["is_critical"])

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

# COMMAND ----------

status_counts_by_name = {
    "pending": 31575,
    "confirmed": 17948,
    "cancelled": 15285,
    "completed": 7439,
}

# Total: sum of the four values read by key
total_bookings = (
    status_counts_by_name["pending"]
    + status_counts_by_name["confirmed"]
    + status_counts_by_name["cancelled"]
    + status_counts_by_name["completed"]
)
cancellation_rate = status_counts_by_name["cancelled"] / total_bookings * 100
active_share = (status_counts_by_name["confirmed"] + status_counts_by_name["completed"]) / total_bookings * 100

# Classification into four states (Chapter 2): the None check first
if cancellation_rate is None:
    cancellation_status = "missing data"
elif cancellation_rate < 0 or cancellation_rate > 100:
    cancellation_status = "impossible value"
elif cancellation_rate > CANCELLATION_RATE_THRESHOLD:
    cancellation_status = "critical"
else:
    cancellation_status = "ok"

# A status that isn't there: get() returns None
refunded_count = status_counts_by_name.get("refunded")
if refunded_count is None:
    refunded_text = "n/a"
else:
    refunded_text = str(refunded_count)

print(f"Total: {total_bookings}")
print(f"Cancellation rate: {cancellation_rate:.1f}% ({cancellation_status})")
print(f"Active share: {active_share:.1f}%")
print(f"refunded: {refunded_text}")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: overall cancellation rate (21.2)
# MAGIC SELECT ROUND(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS cancellation_rate
# MAGIC FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors (Fixes)

# COMMAND ----------

# Fix 8a – IndexError: list index out of range
# The list has three values: the last index is 2, or -1
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
print(property_titles[-1])

# COMMAND ----------

# Fix 8b – KeyError: 'Title'
# Keys distinguish uppercase and lowercase: the key is "title"
sardinia = {"property_id": 16317, "title": "Bungalow in Sardinia", "base_price": 213.91}
print(sardinia["title"])

# COMMAND ----------

# Fix 8c – TypeError: '>' not supported between instances of 'NoneType' and 'int'
# max() can't compare None with a number: use only the values that are present
bookings_2024 = [6, None, 4]
print(max([bookings_2024[0], bookings_2024[2]]))

# COMMAND ----------

# Fix 8d – SyntaxError: invalid syntax. Perhaps you forgot a comma?
# A comma is needed between two key: value pairs
destination_names = {1100: "Amalfi", 2300: "Florence"}
print(destination_names)

# COMMAND ----------

# Fix 8e – silent error: indexes counted from 1 (result 8714)
# The two most frequent types are at positions 0 and 1
type_counts = [9264, 7068, 1646, 185]
first_two_total = type_counts[0] + type_counts[1]
print(first_two_total)

# COMMAND ----------

# Fix 8f – silent error: append() returns None (output None)
# append() changes the list: it's written on a line of its own, without assignment
guide_ids = [11670, 16317]
guide_ids.append(16225)
print(guide_ids)
