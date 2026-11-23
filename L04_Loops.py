# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 4 – Loops
# MAGIC
# MAGIC Notebook for Chapter 4 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Repeat a block of code for each value of a list with the `for` loop
# MAGIC - Add up, count, and build lists with an accumulator; filter and classify with an `if` inside the loop
# MAGIC - Calculate sums and averages on the present values only, like `SUM` and `AVG`
# MAGIC - Use `range()`, loop over dictionaries and lists of dictionaries
# MAGIC - Recognize `while`, `break`, `continue`, and the list comprehension in its simple form
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–3; notebook attached to **Serverless** compute
# MAGIC - The `%sql` cells read `samples.wanderbricks`; one cell in section 4.4 reads `workspace.python_book.b_bookings`, created by `L00_Prepare_Data` (Chapter 0)
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter. **Don't use Run all**: section 4.11 contains intentional errors, silent errors, and an infinite loop to stop with **Interrupt**.
# MAGIC Run the **setup cell** first: it creates the constants and collections used in the sections.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Setup cell: constants and collections used in the sections
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]
bookings_2024 = [6, 7, 4]
ratings_with_gap = [3.2, None, 3.0]   # Sardinia's rating not available (example)

# Bookings by status in the bookings table
status_counts_by_name = {
    "pending": 31575,
    "confirmed": 17948,
    "cancelled": 15285,
    "completed": 7439,
}

# Lookup table of the Italian destinations
destination_names = {
    1100: "Amalfi",
    2300: "Florence",
    3900: "Rome",
    4200: "Sardinia",
}

# Sample of example amounts, with one negative value and two missing ones
sample_amounts = [879.15, None, 412.5, -42.76, 655.0, None]

# The guide properties as a small table (Chapter 3)
guide_properties = [
    {"property_id": 11670, "title": "Historic Inn in Rome", "bookings_2024": 6, "cancelled_2024": 0, "revenue_2024": 3966.21},
    {"property_id": 16317, "title": "Bungalow in Sardinia", "bookings_2024": 7, "cancelled_2024": 1, "revenue_2024": 5139.59},
    {"property_id": 16225, "title": "Beach House in Amalfi", "bookings_2024": 4, "cancelled_2024": 2, "revenue_2024": 2896.92},
]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.1 The for Loop
# MAGIC The indented block is repeated once for each value of the list (one **iteration** per value). Expected results: `284.97`, `213.91`, `236.95`.

# COMMAND ----------

for price in base_prices:
    print(price)

# COMMAND ----------

# MAGIC %md
# MAGIC Inside and outside the loop: the indented lines are repeated, the ones before and after run once. Expected results: `284.97 -> 299.22`, `213.91 -> 224.61`, `236.95 -> 248.80`, between a heading and a final line.

# COMMAND ----------

print("Base prices with a 5% increase:")
for price in base_prices:
    new_price = price * 1.05
    print(f"{price} -> {new_price:.2f}")
print("End of list")

# COMMAND ----------

# MAGIC %md
# MAGIC After the loop, the loop variable holds the last value. Expected result: the three titles, then `After the loop, title is: Beach House in Amalfi`.

# COMMAND ----------

for title in property_titles:
    print(title)
print(f"After the loop, title is: {title}")

# COMMAND ----------

# MAGIC %md
# MAGIC With an empty list, the block never runs. Expected result: only `The loop has ended`.

# COMMAND ----------

flagged_properties = []
for title in flagged_properties:
    print(title)
print("The loop has ended")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: SQL calculates the column for all the rows at once. Expected result: 11670 284.97 299.22; 16225 236.95 248.8; 16317 213.91 224.61.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, base_price, ROUND(base_price * 1.05, 2) AS new_price
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.2 The Accumulator: Adding Up, Counting, Building a List
# MAGIC Three-step pattern: before the loop you prepare the total, inside you update it, after you use it. Expected result: `Total bookings: 17`.

# COMMAND ----------

total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# MAGIC %md
# MAGIC The same loop with the running totals, iteration by iteration. Expected results: `6`, `13`, `17`, then the total.

# COMMAND ----------

total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
    print(f"added {bookings}, running total {total_bookings}")
print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# MAGIC %md
# MAGIC Accumulator with decimals: the raw result may differ from `sum()` in the last digits. Expected results: `735.8299999999999`, `735.83`, `Sum of the base prices: 735.83`.

# COMMAND ----------

total_price = 0
for price in base_prices:
    total_price = total_price + price
print(total_price)
print(sum(base_prices))
print(f"Sum of the base prices: {total_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Counter: it goes up by 1 at each iteration. Expected results: `3` and `3`.

# COMMAND ----------

property_count = 0
for price in base_prices:
    property_count = property_count + 1
print(f"Properties counted: {property_count}")
print(f"len() returns: {len(base_prices)}")

# COMMAND ----------

# MAGIC %md
# MAGIC Building a list: you start from an empty list and add one value at each iteration. Expected result: `[299.22, 224.61, 248.8]`.

# COMMAND ----------

new_prices = []
for price in base_prices:
    new_prices.append(round(price * 1.05, 2))
print(new_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC The `+=` shorthand (the book uses the full form). Expected result: `17`.

# COMMAND ----------

total_bookings = 0
for bookings in bookings_2024:
    total_bookings += bookings
print(total_bookings)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.3 Conditions Inside the Loop
# MAGIC Filtering (like `WHERE`): only the prices above 230 end up in the new list. Expected results: `[284.97, 236.95]` and `Prices above 230: 2`.

# COMMAND ----------

high_prices = []
for price in base_prices:
    if price > 230:
        high_prices.append(price)
print(high_prices)
print(f"Prices above 230: {len(high_prices)}")

# COMMAND ----------

# MAGIC %md
# MAGIC Counting with a condition, also with `in`. Expected results: `Canceled: 2 of 6` and `Active: 2 of 6`.

# COMMAND ----------

sample_statuses = ["confirmed", "cancelled", "pending", "completed", "cancelled", "pending"]
active_statuses = ["confirmed", "completed"]
cancelled_count = 0
active_count = 0
for status in sample_statuses:
    if status == "cancelled":
        cancelled_count = cancelled_count + 1
    if status in active_statuses:
        active_count = active_count + 1
print(f"Canceled: {cancelled_count} of {len(sample_statuses)}")
print(f"Active: {active_count} of {len(sample_statuses)}")

# COMMAND ----------

# MAGIC %md
# MAGIC Classifying each value (like `CASE WHEN`): `if` / `elif` / `else` inside the loop. Expected results: `284.97: high`, `213.91: medium`, `236.95: medium`.

# COMMAND ----------

for price in base_prices:
    if price >= 250:
        price_band = "high"
    elif price >= 200:
        price_band = "medium"
    else:
        price_band = "low"
    print(f"{price}: {price_band}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same filter with `WHERE` and `COUNT(*)`. Expected result: `2`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS high_price_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND base_price > 230

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.4 Missing Values: Sums and Averages on the Present Values
# MAGIC Only the values other than `None` are added up and counted, as `SUM` and `AVG` do. Expected results: `Ratings present: 2 of 3` and `Sum: 6.2 - average: 3.1`.

# COMMAND ----------

total_rating = 0
rating_count = 0
for rating in ratings_with_gap:
    if rating is not None:
        total_rating = total_rating + rating
        rating_count = rating_count + 1
average_rating = total_rating / rating_count
print(f"Ratings present: {rating_count} of {len(ratings_with_gap)}")
print(f"Sum: {total_rating:.1f} - average: {average_rating:.1f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same three rows written with `VALUES`; `COUNT`, `SUM`, and `AVG` ignore the `NULL`. Expected result: `3`, `2`, `6.2`, `3.10000`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)      AS row_count,
# MAGIC        COUNT(rating) AS rating_count,
# MAGIC        SUM(rating)   AS rating_sum,
# MAGIC        AVG(rating)   AS rating_avg
# MAGIC FROM VALUES (3.2), (NULL), (3.0) AS t(rating)

# COMMAND ----------

# MAGIC %md
# MAGIC Three accumulators and a classification: missing, negative, sum of the valid amounts. Expected results: `2`, `1`, `1946.65`.

# COMMAND ----------

missing_count = 0
negative_count = 0
valid_total = 0
for amount in sample_amounts:
    if amount is None:
        missing_count = missing_count + 1
    elif amount < 0:
        negative_count = negative_count + 1
    else:
        valid_total = valid_total + amount
print(f"Missing amounts: {missing_count}")
print(f"Negative amounts: {negative_count}")
print(f"Total of the valid amounts: {valid_total:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same two counts on the whole `b_bookings` teaching copy (Chapter 0). Expected result: `30` and `13`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) - COUNT(total_amount)                    AS missing_amounts,
# MAGIC        SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts
# MAGIC FROM workspace.python_book.b_bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.5 range()
# MAGIC `range(5)` produces the numbers from 0 to 4: the end is excluded. Expected results: `0`, `1`, `2`, `3`, `4`.

# COMMAND ----------

for number in range(5):
    print(number)

# COMMAND ----------

# MAGIC %md
# MAGIC `list()` shows the numbers of a `range`; start, stop, and step. Expected results: `[0, 1, 2, 3, 4]`, `[1, 2, 3, 4, 5, 6, 7, 8, 9]`, `[1, 3, 5, 7, 9]`.

# COMMAND ----------

print(list(range(5)))
print(list(range(1, 10)))
print(list(range(1, 10, 2)))

# COMMAND ----------

# MAGIC %md
# MAGIC The years of the bookings (`check_in` from 2022 to 2025). Expected result: only 2024 is a leap year.

# COMMAND ----------

for year in range(2022, 2026):
    if year % 4 == 0:
        print(f"{year}: leap year")
    else:
        print(f"{year}: not a leap year")

# COMMAND ----------

# MAGIC %md
# MAGIC `range(len(list))` to work with the position and read two aligned lists. Expected results: `0: Historic Inn in Rome - 284.97` and the other two lines.

# COMMAND ----------

for position in range(len(property_titles)):
    print(f"{position}: {property_titles[position]} - {base_prices[position]}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: Databricks SQL also has a `range` function, with the end excluded. Expected results: `0`–`4` and `2022`–`2025`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT id FROM range(5)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT id FROM range(2022, 2026)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.6 Loops over Dictionaries
# MAGIC A loop over a dictionary returns the keys, in insertion order. Expected results: `pending`, `confirmed`, `cancelled`, `completed`.

# COMMAND ----------

for status in status_counts_by_name:
    print(status)

# COMMAND ----------

# MAGIC %md
# MAGIC `values()` returns the values. Expected result: `Total bookings: 72247`.

# COMMAND ----------

total_bookings = 0
for count in status_counts_by_name.values():
    total_bookings = total_bookings + count
print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# MAGIC %md
# MAGIC `items()` returns the pairs: two loop variables. Run the previous cell first (`total_bookings`). Expected results: `pending: 31575 (43.7%)`, `confirmed: 17948 (24.8%)`, `cancelled: 15285 (21.2%)`, `completed: 7439 (10.3%)`.

# COMMAND ----------

for status, count in status_counts_by_name.items():
    share = count / total_bookings * 100
    print(f"{status}: {count} ({share:.1f}%)")

# COMMAND ----------

# MAGIC %md
# MAGIC A lookup table used at each iteration, like a row-by-row `JOIN`. Expected results: `3900 -> Rome`, `4200 -> Sardinia`, `1100 -> Amalfi`.

# COMMAND ----------

guide_destination_ids = [3900, 4200, 1100]
for destination_id in guide_destination_ids:
    print(f"{destination_id} -> {destination_names[destination_id]}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: counts and shares by status. Expected result: pending 31575 43.7; confirmed 17948 24.8; cancelled 15285 21.2; completed 7439 10.3.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT status,
# MAGIC        COUNT(*)                           AS bookings,
# MAGIC        ROUND(COUNT(*) * 100.0 / 72247, 1) AS share
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC GROUP BY status
# MAGIC ORDER BY bookings DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.7 Loops over a List of Dictionaries
# MAGIC One iteration for each row of the small table. Expected results: `Total bookings: 17` and `Total revenue: 12002.72`.

# COMMAND ----------

total_bookings = 0
total_revenue = 0
for row in guide_properties:
    total_bookings = total_bookings + row["bookings_2024"]
    total_revenue = total_revenue + row["revenue_2024"]
print(f"Total bookings: {total_bookings}")
print(f"Total revenue: {total_revenue:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC A new column for each row: cancellation rate and status. Expected results: `Historic Inn in Rome: 0.0% (ok)`, `Bungalow in Sardinia: 14.3% (ok)`, `Beach House in Amalfi: 50.0% (critical)`.

# COMMAND ----------

for row in guide_properties:
    rate = row["cancelled_2024"] / row["bookings_2024"] * 100
    row["cancellation_rate"] = rate
    if rate > CANCELLATION_RATE_THRESHOLD:
        row["cancellation_status"] = "critical"
    else:
        row["cancellation_status"] = "ok"

for row in guide_properties:
    print(f"{row['title']}: {row['cancellation_rate']:.1f}% ({row['cancellation_status']})")

# COMMAND ----------

# MAGIC %md
# MAGIC Filtering the rows with the new column (run the previous cell first). Expected result: `['Beach House in Amalfi']`.

# COMMAND ----------

critical_titles = []
for row in guide_properties:
    if row["cancellation_status"] == "critical":
        critical_titles.append(row["title"])
print(critical_titles)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same table calculated from `bookings`, with rate and status. Expected result: 11670 6 0 0.0 ok; 16225 4 2 50.0 critical; 16317 7 1 14.3 ok.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id,
# MAGIC        COUNT(*)                                                           AS bookings_2024,
# MAGIC        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)              AS cancelled_2024,
# MAGIC        ROUND(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)
# MAGIC              * 100.0 / COUNT(*), 1)                                       AS cancellation_rate,
# MAGIC        CASE WHEN SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)
# MAGIC                  * 100.0 / COUNT(*) > 30 THEN 'critical'
# MAGIC             ELSE 'ok'
# MAGIC        END                                                                AS cancellation_status
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND check_in BETWEEN '2024-01-01' AND '2024-12-31'
# MAGIC GROUP BY property_id
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.8 The while Loop
# MAGIC The block is repeated as long as the condition stays true: the number of iterations isn't known in advance. Expected results: `Years needed: 5` and `Price reached: 302.41`.

# COMMAND ----------

projected_price = 236.95
years = 0
while projected_price <= 300:
    projected_price = projected_price * 1.05
    years = years + 1
print(f"Years needed: {years}")
print(f"Price reached: {projected_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.9 break and continue
# MAGIC `break` exits the loop immediately: 16225 isn't checked. Expected results: `Checking 11670`, `Checking 16317`, `Found: 16317`, `Search finished`.

# COMMAND ----------

guide_property_ids = [11670, 16317, 16225]
searched_id = 16317
for property_id in guide_property_ids:
    print(f"Checking {property_id}")
    if property_id == searched_id:
        print(f"Found: {property_id}")
        break
print("Search finished")

# COMMAND ----------

# MAGIC %md
# MAGIC The calculation from section 4.8 with `for`, `range`, and `break`: at most 20 iterations. Expected results: `Years needed: 5` and `Price reached: 302.41`.

# COMMAND ----------

projected_price = 236.95
for year in range(1, 21):
    projected_price = projected_price * 1.05
    if projected_price > 300:
        break
print(f"Years needed: {year}")
print(f"Price reached: {projected_price:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC `continue` jumps to the next iteration: the `None` values don't reach the sum. Expected result: `Total of the present amounts: 1903.89`.

# COMMAND ----------

present_total = 0
for amount in sample_amounts:
    if amount is None:
        continue
    present_total = present_total + amount
print(f"Total of the present amounts: {present_total:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.10 The List Comprehension
# MAGIC A list built from another one in a single line. Expected result: `[299.22, 224.61, 248.8]`, like the loop in section 4.2.

# COMMAND ----------

new_prices = [round(price * 1.05, 2) for price in base_prices]
print(new_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC With an `if` at the end, only some values are kept. Expected results: `[284.97, 236.95]`, then `[3.2, 3.0]` and `Average of the present ratings: 3.1`.

# COMMAND ----------

high_prices = [price for price in base_prices if price > 230]
print(high_prices)

# COMMAND ----------

present_ratings = [rating for rating in ratings_with_gap if rating is not None]
print(present_ratings)
print(f"Average of the present ratings: {sum(present_ratings) / len(present_ratings):.1f}")

# COMMAND ----------

# MAGIC %md
# MAGIC From a list of dictionaries, one column. Expected result: the three titles.

# COMMAND ----------

titles = [row["title"] for row in guide_properties]
print(titles)

# COMMAND ----------

# MAGIC %md
# MAGIC On several lines, like a query: expression, source, condition. Expected result: `[299.22, 248.8]`.

# COMMAND ----------

expensive_new_prices = [
    round(price * 1.05, 2)
    for price in base_prices
    if price > 230
]
print(expensive_new_prices)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `SELECT` (expression) / `FROM` (source) / `WHERE` (condition). Expected result: 11670 299.22; 16225 248.8.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT property_id, ROUND(base_price * 1.05, 2) AS new_price
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC   AND base_price > 230
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4.11 Reading the Chapter's Errors
# MAGIC The following cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the name of the error and the description;
# MAGIC - the **infinite loop** cell doesn't end on its own: stop it with **Interrupt**;
# MAGIC - the cell marked **SILENT ERROR** gives no error but produces a wrong result;
# MAGIC - the **Fix** cell right below must work **without errors**.
# MAGIC
# MAGIC Expected results of the fixes, in order: the three prices (twice); `0`, `1`, `2`; `Sum of the present ratings: 6.2`; the four status and count lines; `Years needed: 5`; `Total bookings: 17` (twice); `[299.22, 224.61, 248.8]`; the three titles.

# COMMAND ----------

# INTENTIONAL ERROR – missing colon after for
for price in base_prices
    print(price)

# COMMAND ----------

# Fix: the for line ends with a colon
for price in base_prices:
    print(price)

# COMMAND ----------

# INTENTIONAL ERROR – the loop block isn't indented
for price in base_prices:
print(price)

# COMMAND ----------

# Fix: the loop block is indented by 4 spaces
for price in base_prices:
    print(price)

# COMMAND ----------

# INTENTIONAL ERROR – len() returns a number, not a sequence
for position in len(base_prices):
    print(position)

# COMMAND ----------

# Fix: range(len(...)) produces the positions
for position in range(len(base_prices)):
    print(position)

# COMMAND ----------

# INTENTIONAL ERROR – the loop also adds the None value
total_rating = 0
for rating in ratings_with_gap:
    total_rating = total_rating + rating
print(total_rating)

# COMMAND ----------

# Fix: only the present values are added up
total_rating = 0
for rating in ratings_with_gap:
    if rating is not None:
        total_rating = total_rating + rating
print(f"Sum of the present ratings: {total_rating:.1f}")

# COMMAND ----------

# INTENTIONAL ERROR – without items() the loop returns only the keys
for status, count in status_counts_by_name:
    print(status, count)

# COMMAND ----------

# Fix: items() returns the key and value pairs
for status, count in status_counts_by_name.items():
    print(status, count)

# COMMAND ----------

# INTENTIONAL ERROR – infinite loop: the price never changes (stop the cell with Interrupt)
projected_price = 236.95
years = 0
while projected_price <= 300:
    years = years + 1

# COMMAND ----------

# Fix: at each iteration the condition variable is updated
projected_price = 236.95
years = 0
while projected_price <= 300:
    projected_price = projected_price * 1.05
    years = years + 1
print(f"Years needed: {years}")

# COMMAND ----------

# SILENT ERROR – the total is reset at each iteration
for bookings in bookings_2024:
    total_bookings = 0
    total_bookings = total_bookings + bookings
print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# Fix: the total is prepared only once, before the loop
total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# SILENT ERROR – the print is inside the loop
total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
    print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# Fix: the print of the final result is outside the loop
total_bookings = 0
for bookings in bookings_2024:
    total_bookings = total_bookings + bookings
print(f"Total bookings: {total_bookings}")

# COMMAND ----------

# SILENT ERROR – changing the loop variable doesn't change the list
for price in base_prices:
    price = round(price * 1.05, 2)
print(base_prices)

# COMMAND ----------

# Fix: the new values are collected in a new list
new_prices = []
for price in base_prices:
    new_prices.append(round(price * 1.05, 2))
print(new_prices)

# COMMAND ----------

# SILENT ERROR – range(1, ...) skips position 0
for position in range(1, len(property_titles)):
    print(property_titles[position])

# COMMAND ----------

# Fix: positions start from 0
for position in range(len(property_titles)):
    print(property_titles[position])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - `for variable in list:` repeats the indented block once per value (one iteration); the loop variable keeps the last value; empty list = no iterations.
# MAGIC - Three-step accumulator: before (total at 0, counter at 0, empty list), inside (update), after (use of the result). `float` totals always formatted.
# MAGIC - An `if` inside the loop filters (`WHERE`), counts, classifies (`CASE WHEN`); `is not None` to add up and count only the present values, like `SUM` and `AVG`.
# MAGIC - `range(n)`, `range(start, stop)`, `range(start, stop, step)`: end excluded; `list(range(...))`; `range(len(list))` for the position.
# MAGIC - Dictionaries: the loop gives the keys; `values()` the values; `items()` the pairs, with two loop variables.
# MAGIC - List of dictionaries: one iteration per row; `row["key"] = ...` adds a column to each row.
# MAGIC - `while condition:` for an unknown number of iterations; the condition must be able to become false (otherwise **Interrupt**). As a rule, `for` is preferred.
# MAGIC - `break` exits the loop (like `LIMIT 1`), `continue` jumps to the next iteration (like `WHERE ... IS NOT NULL`).
# MAGIC - List comprehension: `[expression for value in list if condition]`, like `SELECT` / `FROM` / `WHERE`.
