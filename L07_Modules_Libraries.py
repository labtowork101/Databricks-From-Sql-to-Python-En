# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 7 – Modules and Libraries
# MAGIC
# MAGIC Notebook for Chapter 7 of the book. The sections have the same numbers as in the text.
# MAGIC
# MAGIC **Goals**
# MAGIC - Tell built-in functions apart from those that must be loaded with `import`
# MAGIC - Use `import module`, `from module import name`, and the `as` alias
# MAGIC - Create and read dates with `date`, convert between text and dates (`fromisoformat`, `strptime`, `strftime`)
# MAGIC - Calculate with dates (`timedelta`, differences, comparisons, sequences of days) and use `datetime` for date and time
# MAGIC - Recognize the typical errors of `import` and of dates
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Chapters 0–6; notebook attached to **Serverless** compute
# MAGIC - `L00_Prepare_Data` already run (one `%sql` cell in section 7.9 reads `workspace.python_book.b_bookings`); no cell writes tables
# MAGIC
# MAGIC **This chapter's exception**: the `import` statements aren't in the setup cell but in the sections, because they're the topic of the chapter. From Chapter 8 on, they go back into the setup cell.
# MAGIC
# MAGIC **How to run this notebook**: one cell at a time, with Shift+Enter, **from top to bottom**. **Don't use Run all**: some cells contain intentional errors.
# MAGIC Run the **setup cell** first. The cells come in pairs:
# MAGIC - the cell marked **INTENTIONAL ERROR** must fail: read the type, the message, and the line;
# MAGIC - the cell marked **SILENT ERROR** gives no errors but produces a wrong result;
# MAGIC - the **Fix** cell (or the cell indicated in the note) must work **without errors**, with the result indicated.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Setup cell: constants and collections used in the sections
# In this chapter the imports aren't here: they're the topic of the sections
ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %

# Guide properties, always in the order Rome, Sardinia, Amalfi
property_titles = ["Historic Inn in Rome", "Bungalow in Sardinia", "Beach House in Amalfi"]
base_prices = [284.97, 213.91, 236.95]
bookings_2024 = [6, 7, 4]

# Names of the days in English: the position in the list is the number of the day (0 = Monday)
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Example bookings for the Amalfi property, with the dates received as text
raw_bookings = [
    {"booking_id": 1001, "check_in": "2024-03-15", "check_out": "2024-03-18"},
    {"booking_id": 1002, "check_in": "2024-05-31", "check_out": "2024-06-07"},
    {"booking_id": 1003, "check_in": "2024-06-10", "check_out": "2024-06-14"},
    {"booking_id": 1004, "check_in": "2024-02-30", "check_out": "2024-03-02"},
    {"booking_id": 1005, "check_in": "2024-08-10", "check_out": "2024-08-08"},
    {"booking_id": 1006, "check_in": "2024-08-14", "check_out": ""},
    {"booking_id": 1007, "check_in": "2024-12-28", "check_out": "2025-01-02"},
]
print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.1 Always-Available Functions and Functions to Load
# MAGIC **SQL Bridge**: in SQL all functions are available without any declaration. Expected result: `2`, `284`, `2024`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ceil(9 / 7)             AS weeks_needed,
# MAGIC        floor(284.97)           AS price_floor,
# MAGIC        year(DATE'2024-03-15')  AS check_in_year

# COMMAND ----------

# MAGIC %md
# MAGIC Let's try `ceil` as in SQL: the cell must fail with a `NameError`, because `ceil` isn't a built-in function.

# COMMAND ----------

# INTENTIONAL ERROR – ceil isn't a Python built-in function
print(ceil(9 / 7))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.2 import: Loading a Module
# MAGIC `import math` loads the module; its functions are used with `math.` in front. Expected results: `2` and `1`.

# COMMAND ----------

import math

print(math.ceil(9 / 7))
print(9 // 7)

# COMMAND ----------

# MAGIC %md
# MAGIC `floor` and `ceil` on prices; `int()` and `floor()` on negative numbers. Expected results: `284`, `285`, `-42`, `-43`.

# COMMAND ----------

print(math.floor(284.97))
print(math.ceil(284.97))
print(int(-42.76))
print(math.floor(-42.76))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `CAST` to an integer truncates, `floor` goes down. Expected result: `284`, `285`, `-42`, `-43`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT floor(284.97)         AS price_floor,
# MAGIC        ceil(284.97)          AS price_ceil,
# MAGIC        CAST(-42.76 AS INT)   AS amount_int,
# MAGIC        floor(-42.76)         AS amount_floor

# COMMAND ----------

# MAGIC %md
# MAGIC `help()` works on the functions of modules too.

# COMMAND ----------

help(math.ceil)

# COMMAND ----------

# MAGIC %md
# MAGIC After `import math`, the name `ceil` on its own still doesn't exist. The cell must fail with a `NameError`.

# COMMAND ----------

# INTENTIONAL ERROR – import math loads the name math, not the name ceil
import math
print(ceil(9 / 7))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the function is reached through the module. Expected result: `2`.

# COMMAND ----------

# Fix: the name of the module, a dot, the name of the function
print(math.ceil(9 / 7))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.3 from ... import and Aliases
# MAGIC `from math import ceil, floor` loads two names, which are used without `math.`. Expected results: `2` and `-43`.

# COMMAND ----------

from math import ceil, floor

print(ceil(9 / 7))
print(floor(-42.76))

# COMMAND ----------

# MAGIC %md
# MAGIC An alias with `as`: the `math` module loaded with the name `m`. Expected result: `285`.

# COMMAND ----------

import math as m

print(m.ceil(284.97))

# COMMAND ----------

# MAGIC %md
# MAGIC A loaded name reused as a variable: the second call must fail with a `TypeError`. Expected output before the message: `2`.

# COMMAND ----------

# INTENTIONAL ERROR – the name ceil is reused for a variable
ceil = ceil(9 / 7)
print(ceil)
print(ceil(10 / 7))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: load `ceil` again and put the result into a variable with a different name. Expected results: `2` and `2`.

# COMMAND ----------

# Fix: load the function again and use a different name for the result
from math import ceil

weeks_needed = ceil(9 / 7)
print(weeks_needed)
print(ceil(10 / 7))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.4 The date Type
# MAGIC The `date` type is loaded from the `datetime` module. Expected results: `2024-03-15` and `<class 'datetime.date'>`.

# COMMAND ----------

from datetime import date

check_in = date(2024, 3, 15)
print(check_in)
print(type(check_in))

# COMMAND ----------

# MAGIC %md
# MAGIC A date inside a list is shown in the long form `datetime.date(...)`, like text with quotes in Chapter 3.

# COMMAND ----------

stay_dates = [date(2024, 3, 15), date(2024, 3, 18)]
print(stay_dates)

# COMMAND ----------

# MAGIC %md
# MAGIC The **attributes** `year`, `month`, `day` are written after the dot, **without parentheses**. Expected results: `2024`, `3`, `15`.

# COMMAND ----------

print(check_in.year)
print(check_in.month)
print(check_in.day)

# COMMAND ----------

# MAGIC %md
# MAGIC The `weekday()` method returns the day of the week, from **0 = Monday** to 6 = Sunday. With the `WEEKDAY_NAMES` list you get the name. Expected results: `4` and `Friday`.

# COMMAND ----------

print(check_in.weekday())
print(WEEKDAY_NAMES[check_in.weekday()])

# COMMAND ----------

# MAGIC %md
# MAGIC Parentheses after an attribute: the cell must fail with a `TypeError`.

# COMMAND ----------

# INTENTIONAL ERROR – year is an attribute, not a method
print(check_in.year())

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the attribute is read without parentheses. Expected result: `2024`.

# COMMAND ----------

# Fix: year is an attribute, without parentheses
print(check_in.year)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `weekday` starts from 0 = Monday, `dayofweek` from 1 = Sunday. Expected result: `2024`, `3`, `15`, `4`, `6`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT year(DATE'2024-03-15')       AS check_in_year,
# MAGIC        month(DATE'2024-03-15')      AS check_in_month,
# MAGIC        day(DATE'2024-03-15')        AS check_in_day,
# MAGIC        weekday(DATE'2024-03-15')    AS weekday_num,
# MAGIC        dayofweek(DATE'2024-03-15')  AS dayofweek_num

# COMMAND ----------

# MAGIC %md
# MAGIC `date.today()` returns today's date, like `current_date()` in SQL: the output depends on the day you run the cell.

# COMMAND ----------

today = date.today()
print(today)
print(today.year)

# COMMAND ----------

# MAGIC %md
# MAGIC A date that doesn't exist: the cell must fail with a `ValueError`.

# COMMAND ----------

# INTENTIONAL ERROR – February doesn't have 30 days
deadline = date(2024, 2, 30)
print(deadline)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the last day of February 2024 is the 29th (leap year). Expected result: `2024-02-29`.

# COMMAND ----------

# Fix: 2024 is a leap year, February has 29 days
deadline = date(2024, 2, 29)
print(deadline)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.5 The datetime Module: From Text to Date and Back
# MAGIC The book's standard form for dates: the three types loaded with a single line. The cell produces no output.

# COMMAND ----------

from datetime import date, timedelta, datetime

# COMMAND ----------

# MAGIC %md
# MAGIC From text to date with `date.fromisoformat()`: this closes the reference left open in Chapter 1. Expected results: `2024-03-15 <class 'datetime.date'>` and `Friday`.

# COMMAND ----------

check_in_text = "2024-03-15"   # the date from the Rome card in Chapter 1
check_in = date.fromisoformat(check_in_text)
print(check_in, type(check_in))
print(WEEKDAY_NAMES[check_in.weekday()])

# COMMAND ----------

# MAGIC %md
# MAGIC From text in US format (month/day/year) to date with `datetime.strptime()` and `.date()`. Expected results: `2024-03-15 00:00:00` and `2024-03-15`.

# COMMAND ----------

us_text = "03/15/2024"
check_in_with_time = datetime.strptime(us_text, "%m/%d/%Y")
print(check_in_with_time)
check_in = check_in_with_time.date()
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC From date to text: `strftime()` with a format, `str()` and f-strings with the ISO format. Expected results: `03/15/2024`, `2024-03-15`, `Arrival: 2024-03-15`.

# COMMAND ----------

print(check_in.strftime("%m/%d/%Y"))
print(str(check_in))
print(f"Arrival: {check_in}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `to_date` and `date_format` with the format codes of Databricks SQL. Expected result: `2024-03-15` and `03/15/2024`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT to_date('03/15/2024', 'MM/dd/yyyy')          AS check_in,
# MAGIC        date_format(DATE'2024-03-15', 'MM/dd/yyyy')  AS check_in_text

# COMMAND ----------

# MAGIC %md
# MAGIC A text in US format passed to `fromisoformat()`: the cell must fail with a `ValueError`.

# COMMAND ----------

# INTENTIONAL ERROR – fromisoformat() accepts only the ISO format
check_in = date.fromisoformat("03/15/2024")
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the text in US format is converted with `strptime()`. Expected result: `2024-03-15`.

# COMMAND ----------

# Fix: for the US format, use strptime() with the right format
check_in = datetime.strptime("03/15/2024", "%m/%d/%Y").date()
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC A text that doesn't match the format of `strptime()`: the cell must fail with a `ValueError`. The traceback has two blocks: the second (`File /usr/lib/python3.12/_strptime.py`) is code from the module, not ours.

# COMMAND ----------

# INTENTIONAL ERROR – the text uses hyphens, the format uses slashes
check_in = datetime.strptime("03-15-2024", "%m/%d/%Y").date()
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the format describes the text, with hyphens. Expected result: `2024-03-15`.

# COMMAND ----------

# Fix: the format uses hyphens, like the text
check_in = datetime.strptime("03-15-2024", "%m-%d-%Y").date()
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.6 Calculating with Dates
# MAGIC Date + `timedelta` = date. Expected results: `2024-03-18` and `2024-03-01`.

# COMMAND ----------

check_in = date(2024, 3, 15)
nights = 3
check_out = check_in + timedelta(days=nights)
print(check_out)

free_cancellation_until = check_in - timedelta(days=14)
print(free_cancellation_until)

# COMMAND ----------

# MAGIC %md
# MAGIC A date plus a number: the cell must fail with a `TypeError`.

# COMMAND ----------

# INTENTIONAL ERROR – you add a timedelta to a date, not a number
check_out = check_in + 3
print(check_out)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: days are added with a `timedelta`. Expected result: `2024-03-18`.

# COMMAND ----------

# Fix: add a timedelta to a date
check_out = check_in + timedelta(days=3)
print(check_out)

# COMMAND ----------

# MAGIC %md
# MAGIC Date − date = `timedelta`; the `days` attribute contains the number of days. Expected results: `3 days, 0:00:00`, `<class 'datetime.timedelta'>`, `3`.

# COMMAND ----------

stay_length = check_out - check_in
print(stay_length)
print(type(stay_length))
print(stay_length.days)

# COMMAND ----------

# MAGIC %md
# MAGIC Days in 2024: the difference counts the intervals; for a period with both ends included, add 1. Expected results: `365` and `366`.

# COMMAND ----------

first_day = date(ANALYSIS_YEAR, 1, 1)
last_day = date(ANALYSIS_YEAR, 12, 31)
print((last_day - first_day).days)
print((last_day - first_day).days + 1)

# COMMAND ----------

# MAGIC %md
# MAGIC Comparisons between dates, chained too, like `BETWEEN`. Expected results: `True`, `True`, `True`.

# COMMAND ----------

print(check_in < date(2024, 6, 1))
print(first_day <= check_in <= last_day)
print(check_in.year == ANALYSIS_YEAR)

# COMMAND ----------

# MAGIC %md
# MAGIC A date compared with a text: the cell must fail with a `TypeError`.

# COMMAND ----------

# INTENTIONAL ERROR – a date is compared with a date, not with a text
print(check_in < "2024-06-01")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: compare two dates. Expected results: `True` and `True`.

# COMMAND ----------

# Fix: the text is converted into a date before the comparison
print(check_in < date(2024, 6, 1))
print(check_in < date.fromisoformat("2024-06-01"))

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the same calculations with `date_add`, `date_sub`, `datediff`, and `BETWEEN`. Expected result: `2024-03-18`, `2024-03-01`, `3`, `366`, `true`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT date_add(DATE'2024-03-15', 3)                       AS check_out,
# MAGIC        date_sub(DATE'2024-03-15', 14)                      AS free_cancellation_until,
# MAGIC        datediff(DATE'2024-03-18', DATE'2024-03-15')        AS nights,
# MAGIC        datediff(DATE'2024-12-31', DATE'2024-01-01') + 1    AS days_2024,
# MAGIC        DATE'2024-03-15' BETWEEN DATE'2024-01-01' AND DATE'2024-12-31' AS in_2024

# COMMAND ----------

# MAGIC %md
# MAGIC The same functions on the columns of `bookings`. Expected result: `2022-12-29`, `2025-07-30`, `9`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT MIN(check_in)                        AS first_check_in,
# MAGIC        MAX(check_in)                        AS last_check_in,
# MAGIC        MAX(datediff(check_out, check_in))   AS max_nights
# MAGIC FROM samples.wanderbricks.bookings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.7 The Sequence of Days in a Stay
# MAGIC The nights of a stay with `range()` and `timedelta`: one date per iteration. Expected result: seven lines, from `2024-05-31 Friday` to `2024-06-06 Thursday`.

# COMMAND ----------

check_in = date(2024, 5, 31)
check_out = date(2024, 6, 7)
nights = (check_out - check_in).days

for i in range(nights):
    night = check_in + timedelta(days=i)
    print(night, WEEKDAY_NAMES[night.weekday()])

# COMMAND ----------

# MAGIC %md
# MAGIC A counter of weekend nights (Friday and Saturday, `weekday()` 4 and 5). Expected results: `Nights: 7 - of which on the weekend: 2` and `Cost at the Amalfi base price: 1658.65`.

# COMMAND ----------

weekend_nights = 0
for i in range(nights):
    night = check_in + timedelta(days=i)
    if night.weekday() in (4, 5):   # Friday or Saturday
        weekend_nights = weekend_nights + 1

print(f"Nights: {nights} - of which on the weekend: {weekend_nights}")
print(f"Cost at the Amalfi base price: {nights * base_prices[2]:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the sequence of nights with `range(7)`. Expected result: seven rows from `2024-05-31` (weekday 4) to `2024-06-06` (weekday 3).

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT date_add(DATE'2024-05-31', CAST(id AS INT))           AS night,
# MAGIC        weekday(date_add(DATE'2024-05-31', CAST(id AS INT)))  AS weekday_num
# MAGIC FROM range(7)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.8 Date and Time: The datetime Type
# MAGIC **SQL Bridge**: the type of the date columns and of the date-and-time columns. Expected result: `date` and `timestamp`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT typeof(check_in)    AS check_in_type,
# MAGIC        typeof(created_at)  AS created_at_type
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC LIMIT 1

# COMMAND ----------

# MAGIC %md
# MAGIC A `datetime`: date and time. Attributes `hour` and `minute`; the `date()` method extracts the date. Expected results: `2024-02-20 14:35:00`, `14 35`, `2024-02-20`.

# COMMAND ----------

created_at = datetime(2024, 2, 20, 14, 35)
print(created_at)
print(created_at.hour, created_at.minute)
print(created_at.date())

# COMMAND ----------

# MAGIC %md
# MAGIC A date minus a `datetime`: the cell must fail with a `TypeError`.

# COMMAND ----------

# INTENTIONAL ERROR – a date and a datetime can't be subtracted
check_in = date(2024, 3, 15)
lead_time = check_in - created_at
print(lead_time)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: subtract two dates. Expected result: `Booking lead time: 24 days`.

# COMMAND ----------

# Fix: the creation date without the time
lead_time = check_in - created_at.date()
print(f"Booking lead time: {lead_time.days} days")

# COMMAND ----------

# MAGIC %md
# MAGIC Difference between two `datetime` values and duration in hours with `total_seconds()`. Expected results: `1 day, 18:30:00` and `Updated after 42.5 hours`.

# COMMAND ----------

updated_at = datetime(2024, 2, 22, 9, 5)
time_to_update = updated_at - created_at
print(time_to_update)
print(f"Updated after {time_to_update.total_seconds() / 3600} hours")

# COMMAND ----------

# MAGIC %md
# MAGIC `datetime.now()` returns the date and time of the compute, usually in UTC: the output depends on the moment you run the cell.

# COMMAND ----------

now = datetime.now()
print(now)
print(now.hour)

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: date and time of the SQL session. Expected result: date and time of the run, `Etc/UTC` (usually), and `14`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT current_timestamp()  AS now,
# MAGIC        current_timezone()   AS timezone,
# MAGIC        hour(TIMESTAMP'2024-02-20 14:35:00') AS created_hour

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.9 A Conversion Function: to_date
# MAGIC `to_date`, the twin of `to_float` from Chapter 6: like `try_cast(... AS DATE)` in SQL. The cell produces no output.

# COMMAND ----------

def to_date(text):
    """Converts a text in ISO format (YYYY-MM-DD) into a date, like try_cast in SQL.

    Returns None if the text is missing (None) or isn't a valid date.
    """
    if text is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None

# COMMAND ----------

# MAGIC %md
# MAGIC Five tests with a known result. Expected results: `2024-03-15`, `None`, `None`, `None`, `None`.

# COMMAND ----------

print(to_date("2024-03-15"))
print(to_date("2024-02-30"))
print(to_date(""))
print(to_date("03/15/2024"))
print(to_date(None))

# COMMAND ----------

# MAGIC %md
# MAGIC Conversion of the dates in `raw_bookings`, with discarded rows and swapped dates counted. Expected results: two discarded rows (1004, 1006), one to check (1005, -2 nights), `Valid stays: 4 - discarded: 2 - swapped dates: 1`.

# COMMAND ----------

valid_stays = []
rejected_count = 0
inverted_count = 0
for row in raw_bookings:
    check_in = to_date(row["check_in"])
    check_out = to_date(row["check_out"])
    if check_in is None or check_out is None:
        rejected_count = rejected_count + 1
        print(f"Discarded {row['booking_id']}: missing or invalid dates")
        continue
    nights = (check_out - check_in).days
    if nights < 0:
        inverted_count = inverted_count + 1
        print(f"To check {row['booking_id']}: swapped dates ({nights} nights)")
        continue
    valid_stays.append({"booking_id": row["booking_id"], "check_in": check_in, "nights": nights})

print(f"Valid stays: {len(valid_stays)} - discarded: {rejected_count} - swapped dates: {inverted_count}")

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: the bookings with swapped dates in the teaching copy. Expected result: `8`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS inverted_dates
# MAGIC FROM workspace.python_book.b_bookings
# MAGIC WHERE check_out < check_in

# COMMAND ----------

# MAGIC %md
# MAGIC **SQL Bridge**: `try_cast` like `to_date`. Expected result: four rows; `null` for the nonexistent date and for the empty text; `-2` nights for 1005.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT booking_id,
# MAGIC        try_cast(check_in AS DATE)   AS check_in,
# MAGIC        try_cast(check_out AS DATE)  AS check_out,
# MAGIC        datediff(try_cast(check_out AS DATE), try_cast(check_in AS DATE)) AS nights
# MAGIC FROM VALUES (1001, '2024-03-15', '2024-03-18'),
# MAGIC             (1004, '2024-02-30', '2024-03-02'),
# MAGIC             (1005, '2024-08-10', '2024-08-08'),
# MAGIC             (1006, '2024-08-14', '')
# MAGIC      AS t(booking_id, check_in, check_out)

# COMMAND ----------

# MAGIC %md
# MAGIC The report of the valid stays: date in US format, day of arrival, nights, weekend arrivals. Expected result: four lines, `Total nights: 19 - weekend arrivals: 3`.

# COMMAND ----------

total_nights = 0
weekend_arrivals = 0
for stay in valid_stays:
    arrival = stay["check_in"]
    weekday_name = WEEKDAY_NAMES[arrival.weekday()]
    print(f"{stay['booking_id']}: arrival {arrival.strftime('%m/%d/%Y')} ({weekday_name}), {stay['nights']} nights")
    total_nights = total_nights + stay["nights"]
    if arrival.weekday() in (4, 5):
        weekend_arrivals = weekend_arrivals + 1

print(f"Total nights: {total_nights} - weekend arrivals: {weekend_arrivals}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7.10 Common Mistakes with Modules and Dates
# MAGIC A module with the wrong name: the cell must fail with a `ModuleNotFoundError`.

# COMMAND ----------

# INTENTIONAL ERROR – the module is called math, not maths
import maths

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: the name of the module is `math`. Expected result: `2`.

# COMMAND ----------

# Fix: the module is called math
import math
print(math.ceil(9 / 7))

# COMMAND ----------

# MAGIC %md
# MAGIC `import datetime` after the standard form: the name `datetime` goes back to meaning the module. The cell must fail with an `AttributeError`.

# COMMAND ----------

# INTENTIONAL ERROR – import datetime replaces the datetime type with the module
import datetime
created_at = datetime.strptime("2024-02-20 14:35", "%Y-%m-%d %H:%M")
print(created_at)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: run the standard form again. Expected result: `2024-02-20 14:35:00`.

# COMMAND ----------

# Fix: the standard form puts the type back into the name datetime
from datetime import date, timedelta, datetime

created_at = datetime.strptime("2024-02-20 14:35", "%Y-%m-%d %H:%M")
print(created_at)

# COMMAND ----------

# MAGIC %md
# MAGIC The name `date` used for a variable: the second assignment must fail with a `TypeError`.

# COMMAND ----------

# INTENTIONAL ERROR – the name date is reused for a text
date = "2024-03-15"
check_out = date(2024, 3, 18)
print(check_out)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: a name that describes the date, and the standard form run again. Expected result: `2024-03-15 2024-03-18`.

# COMMAND ----------

# Fix: load the date type again and use a descriptive name
from datetime import date, timedelta, datetime

check_in_text = "2024-03-15"
check_out = date(2024, 3, 18)
print(check_in_text, check_out)

# COMMAND ----------

# MAGIC %md
# MAGIC Day and month swapped: the cell must fail with a `ValueError`.

# COMMAND ----------

# INTENTIONAL ERROR – the order of the arguments is year, month, day
check_in = date(2024, 15, 3)
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: year, month, day. Expected result: `2024-03-15`.

# COMMAND ----------

# Fix: the order is year, month, day
check_in = date(2024, 3, 15)
print(check_in)

# COMMAND ----------

# MAGIC %md
# MAGIC A date compared with a text using `==`: no error, but the result is always `False`.

# COMMAND ----------

# SILENT ERROR – a date and a text are never equal
check_in = date(2024, 3, 15)
if check_in == "2024-03-15":
    print("March 15 arrival")
print(check_in == "2024-03-15")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: compare two dates. Expected results: `March 15 arrival` and `True`.

# COMMAND ----------

# Fix: a date is compared with a date
check_in = date(2024, 3, 15)
if check_in == date(2024, 3, 15):
    print("March 15 arrival")
print(check_in == date(2024, 3, 15))

# COMMAND ----------

# MAGIC %md
# MAGIC `%M` (minutes) instead of `%m` (month): no error, but the month becomes `00`.

# COMMAND ----------

# SILENT ERROR – %M is the minutes, %m is the month
check_in = date(2024, 3, 15)
print(check_in.strftime("%M/%d/%Y"))

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: `%m` is the month. Expected result: `03/15/2024`.

# COMMAND ----------

# Fix: %m is the month
check_in = date(2024, 3, 15)
print(check_in.strftime("%m/%d/%Y"))

# COMMAND ----------

# MAGIC %md
# MAGIC The days in June without +1: no error, but one day short.

# COMMAND ----------

# SILENT ERROR – the difference counts the intervals, not the days of the period
first_day = date(2024, 6, 1)
last_day = date(2024, 6, 30)
print(f"Days in June: {(last_day - first_day).days}")

# COMMAND ----------

# MAGIC %md
# MAGIC Fix: for a period with both ends included, add 1. Expected result: `Days in June: 30`.

# COMMAND ----------

# Fix: the days of a period with both ends included
first_day = date(2024, 6, 1)
last_day = date(2024, 6, 30)
print(f"Days in June: {(last_day - first_day).days + 1}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC - **Built-in functions** (`print`, `len`, `round`...) are always available; the others live in **modules** and are loaded with `import`. A name that hasn't been loaded gives `NameError`, a module that doesn't exist `ModuleNotFoundError`.
# MAGIC - `import math` → `math.ceil(...)`; `from math import ceil` → `ceil(...)`; `import math as m` → alias, only if it's a widespread convention. Imports live in compute memory: they're written in the setup cell (exception in this chapter).
# MAGIC - A loaded name or a type reassigned to a variable: `'int' object is not callable`, `'str' object is not callable`.
# MAGIC - Standard form for dates: `from datetime import date, timedelta, datetime`. `date(year, month, day)`; attributes `year`, `month`, `day` without parentheses; `weekday()` from 0 = Monday (in SQL, `dayofweek` starts from 1 = Sunday).
# MAGIC - Text → date: `date.fromisoformat()` (ISO format), `datetime.strptime(text, format).date()`. Date → text: `strftime(format)`. Codes `%d %m %Y %H %M %S`; in SQL the codes are different.
# MAGIC - Date ± `timedelta(days=n)`; date − date = `timedelta`, `days` attribute. Nights = difference; days of a period = difference + 1. Dates are compared with dates, never with text.
# MAGIC - `datetime` for date and time; `date()` extracts the date from it; `total_seconds()` for durations; `datetime.now()` uses the compute's clock (usually UTC).
# MAGIC - `to_date` is the book's `try_cast` for dates; swapped dates are counted separately.
