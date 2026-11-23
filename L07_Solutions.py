# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 7 – Exercise Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in Chapter 7 (the same as in Appendix A). Prerequisites: notebook attached to **Serverless**.
# MAGIC Run the setup cell first, then **one cell at a time**: the cells of exercise 8 marked **INTENTIONAL ERROR** and **SILENT ERROR** are shown as in the exercise notebook, with the solution right below. Don't use Run all.

# COMMAND ----------

# Setup cell: imports, constants, and collections used in the exercises
# The math module isn't loaded here: exercises 1 and 2 load it
from datetime import date, timedelta, datetime

ANALYSIS_YEAR = 2024

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]

# Names of the days in English: the position in the list is the number of the day (0 = Monday)
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – Rounding with math
# MAGIC The `stay_nights` list (cell below) contains the nights of five example stays.
# MAGIC 1. Load the `math` module with `import math`.
# MAGIC 2. With two list comprehensions, calculate the weeks **occupied** by each stay (`math.ceil` of the nights divided by 7) and the **full** weeks (floor division `//`).
# MAGIC 3. Print the base prices of the guide properties rounded down (`math.floor`) and rounded up (`math.ceil`).
# MAGIC 4. For the example refund `refund = -15.5`, print `int(refund)`, `math.floor(refund)`, and `math.ceil(refund)` on the same line.

# COMMAND ----------

stay_nights = [3, 7, 9, 14, 2]   # example values

# COMMAND ----------

# The module is loaded once; the functions are used with the math. prefix
import math

# Weeks occupied (rounding up) and full weeks (floor division)
weeks_occupied = [math.ceil(nights / 7) for nights in stay_nights]
full_weeks = [nights // 7 for nights in stay_nights]
print(weeks_occupied)
print(full_weeks)

# Base prices rounded down and rounded up
print([math.floor(price) for price in base_prices])
print([math.ceil(price) for price in base_prices])

# With a negative number, int() truncates toward zero, floor() goes down
refund = -15.5
print(int(refund), math.floor(refund), math.ceil(refund))

# COMMAND ----------

# Check: expected result
print([1, 1, 2, 2, 1])
print([0, 1, 1, 2, 0])
print([284, 213, 236])
print([285, 214, 237])
print(-15, -16, -15)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same rounding in SQL (2, 1, 213, 214, -15, -16)
# MAGIC SELECT ceil(9 / 7)          AS weeks_occupied,
# MAGIC        9 div 7              AS full_weeks,
# MAGIC        floor(213.91)        AS price_floor,
# MAGIC        ceil(213.91)         AS price_ceil,
# MAGIC        CAST(-15.5 AS INT)   AS refund_int,
# MAGIC        floor(-15.5)         AS refund_floor

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Forms of import
# MAGIC Note: if in exercise 1 you loaded the name `floor` with `from math import floor`, cell 2a doesn't fail, because the name is already in compute memory (section 7.3).
# MAGIC 1. Run cells 2a and 2b and note the **type** of each error in the answer cell.
# MAGIC 2. Write in the fix cell: 2a fixed by loading `floor` with `from math import floor`; 2b fixed by using a variable with a different name for the result (`sardinia_floor`) and loading `floor` again.
# MAGIC 3. Finally, calculate `floor(236.95)` in the two forms: with `import math` and the prefix, and with the name loaded by `from math import floor`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 2a (the Sardinia base price rounded down)
print(floor(213.91))

# COMMAND ----------

# INTENTIONAL ERROR – cell 2b
from math import floor
floor = floor(213.91)
print(floor)
print(floor(236.95))

# COMMAND ----------

# 2a: NameError - floor isn't a built-in function and hasn't been loaded
from math import floor
print(floor(213.91))

# 2b: TypeError ('int' object is not callable) - the name floor was reassigned to a number
from math import floor           # load the function again
sardinia_floor = floor(213.91)   # the result goes into a variable with a different name
print(sardinia_floor)
print(floor(236.95))

# The two forms of import give the same result
import math
print(math.floor(236.95))   # form with the module prefix
print(floor(236.95))        # form with the loaded name

# COMMAND ----------

# Check: expected result
print("2a: NameError - 2b: TypeError ('int' object is not callable)")
print(213)
print(213)
print(236)
print(236)
print(236)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Ferragosto 2024
# MAGIC Ferragosto, August 15, is a national holiday in Italy and the peak of the summer season.
# MAGIC 1. Create the date August 15, 2024, with `date()` and print it.
# MAGIC 2. Print the year, month, and day on the same line, read with the attributes.
# MAGIC 3. Print on the same line the number of the day of the week (`weekday()`) and its name, read from `WEEKDAY_NAMES`.
# MAGIC 4. Print the date in US format with `strftime()`.
# MAGIC 5. Calculate the number of the day in the year (1 for January 1) and print `Day of the year: ...`.

# COMMAND ----------

ferragosto = date(2024, 8, 15)
print(ferragosto)

# Attributes: read without parentheses
print(ferragosto.year, ferragosto.month, ferragosto.day)

# Method: called with parentheses; 0 = Monday, so 3 = Thursday
print(ferragosto.weekday(), WEEKDAY_NAMES[ferragosto.weekday()])

# From date to text in US format
print(ferragosto.strftime("%m/%d/%Y"))

# The day of the year also counts January 1: difference + 1
day_of_year = (ferragosto - date(2024, 1, 1)).days + 1
print(f"Day of the year: {day_of_year}")

# COMMAND ----------

# Check: expected result
print("2024-08-15")
print(2024, 8, 15)
print(3, "Thursday")
print("08/15/2024")
print("Day of the year: 228")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 3, 5, 08/15/2024, 228 (dayofweek starts from 1 = Sunday)
# MAGIC SELECT weekday(DATE'2024-08-15')                    AS weekday_num,
# MAGIC        dayofweek(DATE'2024-08-15')                  AS dayofweek_num,
# MAGIC        date_format(DATE'2024-08-15', 'MM/dd/yyyy')  AS us_text,
# MAGIC        dayofyear(DATE'2024-08-15')                  AS day_of_year

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – Dates in US Format
# MAGIC The `us_dates` list (cell below) contains three dates written in US format (month/day/year).
# MAGIC 1. Convert the texts into dates with `datetime.strptime(...).date()`, collecting them in the `converted_dates` list.
# MAGIC 2. With a loop over `converted_dates`, print for each date: the date in ISO format, the name of the day, and the days elapsed since the first date in the list (0 for the first).

# COMMAND ----------

us_dates = ["06/01/2024", "08/15/2024", "12/31/2024"]   # example values

# COMMAND ----------

# From US text to date: strptime with the format, then date() to drop the time
converted_dates = []
for text in us_dates:
    converted_dates.append(datetime.strptime(text, "%m/%d/%Y").date())

first_date = converted_dates[0]
for converted in converted_dates:
    days_from_first = (converted - first_date).days
    print(converted, WEEKDAY_NAMES[converted.weekday()], days_from_first)

# COMMAND ----------

# Check: expected result
print("2024-06-01 Saturday 0")
print("2024-08-15 Thursday 75")
print("2024-12-31 Tuesday 213")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the same dates with to_date (weekday 5, 3, 1; days 0, 75, 213)
# MAGIC SELECT to_date(us_text, 'MM/dd/yyyy')                                AS converted,
# MAGIC        weekday(to_date(us_text, 'MM/dd/yyyy'))                       AS weekday_num,
# MAGIC        datediff(to_date(us_text, 'MM/dd/yyyy'), DATE'2024-06-01')    AS days_from_first
# MAGIC FROM VALUES ('06/01/2024'), ('08/15/2024'), ('12/31/2024') AS t(us_text)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Stay in Sardinia
# MAGIC An example stay at the Bungalow in Sardinia arrives on July 26, 2024, and lasts 9 nights.
# MAGIC 1. Calculate and print the departure date.
# MAGIC 2. Calculate and print the last day of free cancellation, 14 days before arrival.
# MAGIC 3. Print the cost of the stay at the Sardinia base price (`base_prices[1]`), with two decimal places.
# MAGIC 4. Print whether the arrival is in 2024, with a chained comparison between January 1 and December 31 of `ANALYSIS_YEAR`.
# MAGIC 5. Print the number of days in July 2024, calculated with a difference between July 1 and July 31.
# MAGIC 6. A second stay arrived as text: `"2024-09-02"` → `"2024-09-06"`. Convert the texts with `date.fromisoformat()` and print the nights.

# COMMAND ----------

check_in = date(2024, 7, 26)
nights = 9

# Departure and last day of free cancellation: date ± timedelta
check_out = check_in + timedelta(days=nights)
free_cancellation_until = check_in - timedelta(days=14)
print(check_out)
print(free_cancellation_until)

# Cost at the Sardinia base price
print(f"{nights * base_prices[1]:.2f}")

# Chained comparison, like BETWEEN with both ends included
print(date(ANALYSIS_YEAR, 1, 1) <= check_in <= date(ANALYSIS_YEAR, 12, 31))

# Days of a period with both ends included: difference + 1
print((date(2024, 7, 31) - date(2024, 7, 1)).days + 1)

# Nights from two dates received as text: difference, without +1
second_check_in = date.fromisoformat("2024-09-02")
second_check_out = date.fromisoformat("2024-09-06")
print((second_check_out - second_check_in).days)

# COMMAND ----------

# Check: expected result
print("2024-08-04")
print("2024-07-12")
print("1925.19")
print(True)
print(31)
print(4)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 2024-08-04, 2024-07-12, 31, 4
# MAGIC SELECT date_add(DATE'2024-07-26', 9)                       AS check_out,
# MAGIC        date_sub(DATE'2024-07-26', 14)                      AS free_cancellation_until,
# MAGIC        datediff(DATE'2024-07-31', DATE'2024-07-01') + 1    AS days_in_july,
# MAGIC        datediff(DATE'2024-09-06', DATE'2024-09-02')        AS second_stay_nights

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – A Stay Across the New Year
# MAGIC The chapter's example booking 1007 arrives in Amalfi on December 28, 2024, and leaves on January 2, 2025.
# MAGIC 1. With `range()` and `timedelta`, print each night of the stay with the name of the day.
# MAGIC 2. In the same loop, count the weekend nights (Friday and Saturday) and the nights that fall in `ANALYSIS_YEAR`.
# MAGIC 3. Print `Nights: ... - on the weekend: ...` and `Nights in 2024: ... (cost) - nights in 2025: ... (cost)`, with the cost at the Amalfi base price (`base_prices[2]`) and two decimal places.

# COMMAND ----------

check_in = date(2024, 12, 28)
check_out = date(2025, 1, 2)
nights = (check_out - check_in).days

weekend_nights = 0
nights_in_year = 0
for i in range(nights):
    night = check_in + timedelta(days=i)   # night number i of the stay
    print(night, WEEKDAY_NAMES[night.weekday()])
    if night.weekday() in (4, 5):          # Friday or Saturday
        weekend_nights = weekend_nights + 1
    if night.year == ANALYSIS_YEAR:
        nights_in_year = nights_in_year + 1

nights_next_year = nights - nights_in_year
price = base_prices[2]
print(f"Nights: {nights} - on the weekend: {weekend_nights}")
print(f"Nights in 2024: {nights_in_year} ({nights_in_year * price:.2f}) - nights in 2025: {nights_next_year} ({nights_next_year * price:.2f})")

# COMMAND ----------

# Check: expected result
print("2024-12-28 Saturday")
print("2024-12-29 Sunday")
print("2024-12-30 Monday")
print("2024-12-31 Tuesday")
print("2025-01-01 Wednesday")
print("Nights: 5 - on the weekend: 1")
print("Nights in 2024: 4 (947.80) - nights in 2025: 1 (236.95)")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: nights per year (2024: 4, 2025: 1)
# MAGIC SELECT year(date_add(DATE'2024-12-28', CAST(id AS INT)))  AS night_year,
# MAGIC        COUNT(*)                                           AS nights
# MAGIC FROM range(5)
# MAGIC GROUP BY 1
# MAGIC ORDER BY 1

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – The Lead Time of Requests
# MAGIC The `raw_requests` list (cell below) contains seven example booking requests, with the date and time of the request (`created_at`) and the arrival date (`check_in`) written in US format.
# MAGIC 1. Define `to_us_date(text)` and `to_us_datetime(text)`, twins of `to_date`: they convert a text with `strptime()` (formats `"%m/%d/%Y"` and `"%m/%d/%Y %H:%M"`; the first returns a `date`) and return `None` if the text is missing or isn't valid. Write a docstring for each one.
# MAGIC 2. With a loop, convert the two values of each row; if one of the two is `None`, print `Discarded ...` with the `booking_id`, count the discarded row, and move on to the next row.
# MAGIC 3. For the valid rows, calculate the lead time in days (arrival minus request date) and the band: `"last minute"` if the lead time is less than 7 days, otherwise `"early"`. Print `booking_id: lead days ... (band)`.
# MAGIC 4. Count the rows per band in a dictionary, count the evening requests (made from 6 p.m. on, that is, with an hour of 18 or more), and calculate the average lead time with one decimal place.

# COMMAND ----------

raw_requests = [   # example values
    {"booking_id": 1001, "created_at": "02/20/2024 14:35", "check_in": "03/15/2024"},
    {"booking_id": 1002, "created_at": "05/02/2024 09:10", "check_in": "05/31/2024"},
    {"booking_id": 1003, "created_at": "06/08/2024 22:45", "check_in": "06/10/2024"},
    {"booking_id": 1004, "created_at": "02/15/2024 11:00", "check_in": "02/30/2024"},
    {"booking_id": 1005, "created_at": "07/28/2024 08:20", "check_in": "08/10/2024"},
    {"booking_id": 1006, "created_at": "", "check_in": "08/14/2024"},
    {"booking_id": 1007, "created_at": "12/27/2024 19:05", "check_in": "12/28/2024"},
]

# COMMAND ----------

def to_us_date(text):
    """Converts a MM/DD/YYYY text into a date; None if missing or not a valid date."""
    if text is None:
        return None
    try:
        return datetime.strptime(text, "%m/%d/%Y").date()
    except ValueError:
        return None


def to_us_datetime(text):
    """Converts a MM/DD/YYYY HH:MM text into a datetime; None if missing or not valid."""
    if text is None:
        return None
    try:
        return datetime.strptime(text, "%m/%d/%Y %H:%M")
    except ValueError:
        return None


rejected_count = 0
lead_times = []
count_by_band = {}
evening_requests = 0
for row in raw_requests:
    created_at = to_us_datetime(row["created_at"])
    check_in = to_us_date(row["check_in"])
    if created_at is None or check_in is None:
        rejected_count = rejected_count + 1
        print(f"Discarded {row['booking_id']}")
        continue
    lead_days = (check_in - created_at.date()).days   # two dates: date() drops the time
    if lead_days < 7:
        band = "last minute"
    else:
        band = "early"
    print(f"{row['booking_id']}: lead days {lead_days} ({band})")
    lead_times.append(lead_days)
    if band in count_by_band:
        count_by_band[band] = count_by_band[band] + 1
    else:
        count_by_band[band] = 1
    if created_at.hour >= 18:
        evening_requests = evening_requests + 1

print(f"Valid: {len(lead_times)} - discarded: {rejected_count}")
print(count_by_band)
print(f"Evening requests (from 6 p.m.): {evening_requests}")
print(f"Average lead time: {sum(lead_times) / len(lead_times):.1f} days")

# COMMAND ----------

# Check: expected result
print("1001: lead days 24 (early)")
print("1002: lead days 29 (early)")
print("1003: lead days 2 (last minute)")
print("Discarded 1004")
print("1005: lead days 13 (early)")
print("Discarded 1006")
print("1007: lead days 1 (last minute)")
print("Valid: 5 - discarded: 2")
print({'early': 3, 'last minute': 2})
print("Evening requests (from 6 p.m.): 2")
print("Average lead time: 13.8 days")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check on the five valid rows: 5, 2, 2, 13.8
# MAGIC SELECT COUNT(*) AS valid_requests,
# MAGIC        SUM(CASE WHEN datediff(to_date(check_in, 'MM/dd/yyyy'), to_date(created_at, 'MM/dd/yyyy HH:mm')) < 7
# MAGIC                 THEN 1 ELSE 0 END) AS last_minute,
# MAGIC        SUM(CASE WHEN hour(to_timestamp(created_at, 'MM/dd/yyyy HH:mm')) >= 18
# MAGIC                 THEN 1 ELSE 0 END) AS evening_requests,
# MAGIC        ROUND(AVG(datediff(to_date(check_in, 'MM/dd/yyyy'), to_date(created_at, 'MM/dd/yyyy HH:mm'))), 1) AS avg_lead_days
# MAGIC FROM VALUES ('02/20/2024 14:35', '03/15/2024'),
# MAGIC             ('05/02/2024 09:10', '05/31/2024'),
# MAGIC             ('06/08/2024 22:45', '06/10/2024'),
# MAGIC             ('07/28/2024 08:20', '08/10/2024'),
# MAGIC             ('12/27/2024 19:05', '12/28/2024')
# MAGIC      AS t(created_at, check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one by one, note the type, the message, and the line (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `2`; `2024-06-14`; `12/31/2024`; `22`; `06/10/2024`; `June 10 arrivals: 2`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (the weeks occupied by 9 nights)
import Math
print(Math.ceil(9 / 7))

# COMMAND ----------

# Fix 8a - ModuleNotFoundError: module names are case-sensitive
import math
print(math.ceil(9 / 7))

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b (the departure after 4 nights)
check_in = date(2024, 6, 10)
check_out = check_in + 4
print(check_out)

# COMMAND ----------

# Fix 8b - TypeError: you add a timedelta to a date, not a number
check_in = date(2024, 6, 10)
check_out = check_in + timedelta(days=4)
print(check_out)

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c (December 31, 2024)
last_day = date(2024, 31, 12)
print(last_day.strftime("%m/%d/%Y"))

# COMMAND ----------

# Fix 8c - ValueError (month must be in 1..12): the order is year, month, day
last_day = date(2024, 12, 31)
print(last_day.strftime("%m/%d/%Y"))

# COMMAND ----------

# INTENTIONAL ERROR – cell 8d (the time of a request)
import datetime
created_at = datetime.strptime("06/08/2024 22:45", "%m/%d/%Y %H:%M")
print(created_at.hour)

# COMMAND ----------

# Fix 8d - AttributeError: import datetime put the module into the name datetime;
# the standard form puts the type back
from datetime import date, timedelta, datetime
created_at = datetime.strptime("06/08/2024 22:45", "%m/%d/%Y %H:%M")
print(created_at.hour)

# COMMAND ----------

# SILENT ERROR – cell 8e (the arrival date in US format)
check_in = date(2024, 6, 10)
print(check_in.strftime("%M/%d/%Y"))

# COMMAND ----------

# Fix 8e - %M is the minutes (00 for a date), %m is the month
check_in = date(2024, 6, 10)
print(check_in.strftime("%m/%d/%Y"))

# COMMAND ----------

# SILENT ERROR – cell 8f (how many arrivals on June 10, 2024)
arrivals = [date(2024, 6, 10), date(2024, 6, 14), date(2024, 6, 10)]
count = 0
for arrival in arrivals:
    if arrival == "2024-06-10":
        count = count + 1
print(f"June 10 arrivals: {count}")

# COMMAND ----------

# Fix 8f - a date is never equal to a text: compare it with a date
arrivals = [date(2024, 6, 10), date(2024, 6, 14), date(2024, 6, 10)]
count = 0
for arrival in arrivals:
    if arrival == date(2024, 6, 10):
        count = count + 1
print(f"June 10 arrivals: {count}")
