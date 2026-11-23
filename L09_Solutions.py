# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 9 – Exercise Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in Chapter 9 (the same as in Appendix A).
# MAGIC Prerequisites: notebook attached to **Serverless**; `L00_Prepare_Data` already run. No cell writes tables.
# MAGIC Run the setup cell first, then one cell at a time. In exercise 8, every cell with an error is followed by its fix.

# COMMAND ----------

# Setup cell: imports, constants, DataFrames, and values used in the exercises
import pyspark.sql.functions as F
from datetime import date, timedelta, datetime

# Schemas and tables: samples is read-only, workspace.python_book is the working schema
SOURCE_SCHEMA = "samples.wanderbricks"
WORK_SCHEMA = "workspace.python_book"
SOURCE_BOOKINGS_TABLE = f"{SOURCE_SCHEMA}.bookings"   # original bookings
PROPERTIES_TABLE = f"{SOURCE_SCHEMA}.properties"
DESTINATIONS_TABLE = f"{SOURCE_SCHEMA}.destinations"
COUNTRIES_TABLE = f"{SOURCE_SCHEMA}.countries"
SUPPORT_LOGS_TABLE = f"{SOURCE_SCHEMA}.customer_support_logs"
BOOKINGS_TABLE = f"{WORK_SCHEMA}.b_bookings"           # teaching copy with anomalies (Chapter 0)

ANALYSIS_YEAR = 2024
CANCELLATION_RATE_THRESHOLD = 30.0   # cancellation rate threshold, in %
MIN_BOOKINGS = 20                    # minimum bookings for a rate to be assessable (section 9.8)

# Guide properties, always in the order Rome, Sardinia, Amalfi
GUIDE_PROPERTY_IDS = [11670, 16317, 16225]

# DataFrames of the tables (recipes: no data is read yet)
bookings_df = spark.sql(f"SELECT * FROM {SOURCE_BOOKINGS_TABLE}")
properties_df = spark.sql(f"SELECT * FROM {PROPERTIES_TABLE}")
destinations_df = spark.sql(f"SELECT * FROM {DESTINATIONS_TABLE}")
countries_df = spark.sql(f"SELECT * FROM {COUNTRIES_TABLE}")
teaching_bookings_df = spark.sql(f"SELECT * FROM {BOOKINGS_TABLE}")

# 2024 bookings of the Sardinia property (16317), written as text (exercises 2 and 8f)
raw_sardinia_rows = [
    {"booking_id": 49395, "check_in": "06/08/2024", "check_out": "06/11/2024", "total_amount": "647.01"},
    {"booking_id": 59901, "check_in": "07/12/2024", "check_out": "07/17/2024", "total_amount": "590.95"},
    {"booking_id": 68070, "check_in": "07/17/2024", "check_out": "07/22/2024", "total_amount": "900.47"},
    {"booking_id": 688, "check_in": "07/31/2024", "check_out": "08/05/2024", "total_amount": "635.51"},
    {"booking_id": 9842, "check_in": "08/18/2024", "check_out": "08/23/2024", "total_amount": "759.63"},
    {"booking_id": 23944, "check_in": "08/23/2024", "check_out": "08/28/2024", "total_amount": "623.81"},
    {"booking_id": 64865, "check_in": "09/07/2024", "check_out": "09/08/2024", "total_amount": "982.21"},
]

print("Setup complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – New Columns on the Guide Properties
# MAGIC 1. From `properties_df`, keep the three guide properties (column form with `F.col` and `|`) and the columns `property_id`, `title`, `base_price`, `max_guests`.
# MAGIC 2. Add with `withColumn`: `price_per_guest` (base price divided by `max_guests`, rounded to two decimal places), `title_upper` (the title in uppercase), and `source` (the fixed value `wanderbricks`).
# MAGIC 3. Show the result with `display()`, sorted by `property_id`.

# COMMAND ----------

# Exercise 1: three calculated columns with withColumn
guide_columns_df = (
    properties_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .select("property_id", "title", "base_price", "max_guests")
    .withColumn("price_per_guest", F.round(F.col("base_price") / F.col("max_guests"), 2))  # one column divided by another
    .withColumn("title_upper", F.upper(F.col("title")))                                    # like UPPER(title)
    .withColumn("source", F.lit("wanderbricks"))                                           # fixed value: F.lit is needed
    .orderBy("property_id")
)
display(guide_columns_df)

# COMMAND ----------

# Check: expected result (grid)
print("property_id  title                  base_price  max_guests  price_per_guest  title_upper            source")
print("11670        Historic Inn in Rome   284.97      8           35.62            HISTORIC INN IN ROME   wanderbricks")
print("16225        Beach House in Amalfi  236.95      1           236.95           BEACH HOUSE IN AMALFI  wanderbricks")
print("16317        Bungalow in Sardinia   213.91      4           53.48            BUNGALOW IN SARDINIA   wanderbricks")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: price per guest 35.62, 236.95, 53.48
# MAGIC SELECT property_id, title, base_price, max_guests,
# MAGIC        ROUND(base_price / max_guests, 2) AS price_per_guest,
# MAGIC        UPPER(title)                      AS title_upper,
# MAGIC        'wanderbricks'                    AS source
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_id IN (11670, 16317, 16225)
# MAGIC ORDER BY property_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Dates and Amounts Written as Text
# MAGIC 1. Turn `raw_sardinia_rows` into a DataFrame with `spark.createDataFrame()`.
# MAGIC 2. Convert `check_in` and `check_out` to dates with `F.to_date` and the right format, and `total_amount` to `double` with `cast`; add the `nights` column with `F.datediff`.
# MAGIC 3. With `agg`, calculate `booking_count`, `total_nights`, and `revenue` (revenue rounded to two decimal places).
# MAGIC 4. From `customer_support_logs` (constant `SUPPORT_LOGS_TABLE`), count the requests by year, with the year obtained from `F.to_date(F.col("created_at"))`, in order of year.

# COMMAND ----------

# Exercise 2: type conversion, then aggregation
sardinia_df = (
    spark.createDataFrame(raw_sardinia_rows)
    .withColumn("check_in", F.to_date(F.col("check_in"), "MM/dd/yyyy"))     # MM = month
    .withColumn("check_out", F.to_date(F.col("check_out"), "MM/dd/yyyy"))
    .withColumn("total_amount", F.col("total_amount").cast("double"))      # text -> number
    .withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in")))
)
display(
    sardinia_df.agg(
        F.count("*").alias("booking_count"),
        F.sum("nights").alias("total_nights"),
        F.round(F.sum("total_amount"), 2).alias("revenue"),
    )
)

# Support requests by year: created_at is a text in ISO form, F.to_date reads it without a format
logs_by_year_df = (
    spark.sql(f"SELECT ticket_id, created_at FROM {SUPPORT_LOGS_TABLE}")
    .withColumn("created_year", F.year(F.to_date(F.col("created_at"))))
    .groupBy("created_year")
    .agg(F.count("*").alias("ticket_count"))
    .orderBy("created_year")
)
display(logs_by_year_df)

# COMMAND ----------

# Check: expected result (two grids)
print("booking_count  total_nights  revenue")
print("7              29            5139.59")
print()
print("created_year  ticket_count")
print("2022          150")
print("2023          696")
print("2024          658")
print("2025          396")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 2024 bookings in Sardinia (7, 29 nights, 5139.59)
# MAGIC SELECT COUNT(*)                                AS booking_count,
# MAGIC        SUM(datediff(check_out, check_in))      AS total_nights,
# MAGIC        ROUND(SUM(total_amount), 2)             AS revenue
# MAGIC FROM samples.wanderbricks.bookings
# MAGIC WHERE property_id = 16317 AND year(check_in) = 2024

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: requests by year (150, 696, 658, 396)
# MAGIC SELECT year(to_date(created_at)) AS created_year, COUNT(*) AS ticket_count
# MAGIC FROM samples.wanderbricks.customer_support_logs
# MAGIC GROUP BY year(to_date(created_at))
# MAGIC ORDER BY created_year

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – Grouping the Properties
# MAGIC For each property type, calculate with `groupBy` and `agg`: `property_count` (number of properties), `destination_count` (number of distinct destinations where the type is present), and `avg_max_guests` (average of `max_guests`, rounded to two decimal places). Show the result in descending order of `property_count`.

# COMMAND ----------

# Exercise 3: a groupBy with three aggregations
type_summary_df = (
    properties_df
    .groupBy("property_type")
    .agg(
        F.count("*").alias("property_count"),
        F.countDistinct("destination_id").alias("destination_count"),   # COUNT(DISTINCT destination_id)
        F.round(F.avg("max_guests"), 2).alias("avg_max_guests"),
    )
    .orderBy(F.col("property_count").desc())
)
display(type_summary_df)

# COMMAND ----------

# Check: expected result (grid)
print("property_type     property_count  destination_count  avg_max_guests")
print("Urban Year-Round  9264            12                 2.48")
print("Summer Getaway    7068            10                 2.48")
print("Historical Place  1646            10                 2.42")
print("Ski Resort        185             10                 2.35")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check
# MAGIC SELECT property_type,
# MAGIC        COUNT(*)                        AS property_count,
# MAGIC        COUNT(DISTINCT destination_id)  AS destination_count,
# MAGIC        ROUND(AVG(max_guests), 2)       AS avg_max_guests
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY property_type
# MAGIC ORDER BY property_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Price Bands of All Properties
# MAGIC 1. Add to `properties_df` the `price_band` column from section 9.4: `high` from 250, `medium` from 200, otherwise `low`.
# MAGIC 2. Count the properties by band (`property_count`), in alphabetical order of band.
# MAGIC 3. Do the same count for the `Ski Resort` properties only.

# COMMAND ----------

# Exercise 4: F.when for the band, then groupBy on the new column
banded_df = properties_df.withColumn(
    "price_band",
    F.when(F.col("base_price") >= 250, "high")      # from the narrowest condition
    .when(F.col("base_price") >= 200, "medium")
    .otherwise("low")
)
display(banded_df.groupBy("price_band").agg(F.count("*").alias("property_count")).orderBy("price_band"))
display(
    banded_df
    .filter(F.col("property_type") == "Ski Resort")      # WHERE: before the groupBy
    .groupBy("price_band")
    .agg(F.count("*").alias("property_count"))
    .orderBy("price_band")
)

# COMMAND ----------

# Check: expected result (two grids)
print("price_band  property_count")
print("high        1894")
print("low         12647")
print("medium      3622")
print()
print("price_band  property_count   (Ski Resort only)")
print("high        106")
print("low         15")
print("medium      64")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: all properties (1894, 12647, 3622)
# MAGIC SELECT CASE WHEN base_price >= 250 THEN 'high'
# MAGIC             WHEN base_price >= 200 THEN 'medium'
# MAGIC             ELSE 'low' END AS price_band,
# MAGIC        COUNT(*) AS property_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC GROUP BY 1
# MAGIC ORDER BY price_band

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: Ski Resort only (106, 15, 64)
# MAGIC SELECT CASE WHEN base_price >= 250 THEN 'high'
# MAGIC             WHEN base_price >= 200 THEN 'medium'
# MAGIC             ELSE 'low' END AS price_band,
# MAGIC        COUNT(*) AS property_count
# MAGIC FROM samples.wanderbricks.properties
# MAGIC WHERE property_type = 'Ski Resort'
# MAGIC GROUP BY 1
# MAGIC ORDER BY price_band

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – A Filter on the Groups
# MAGIC 1. Count the destinations by country (`destination_count`) and keep, with a `filter` after `agg`, the countries with at least 4 destinations, in alphabetical order.
# MAGIC 2. Count how many countries have only one destination and print the number.

# COMMAND ----------

# Exercise 5: the filter after agg is a HAVING
countries_count_df = (
    destinations_df
    .groupBy("country")
    .agg(F.count("*").alias("destination_count"))
)
display(countries_count_df.filter(F.col("destination_count") >= 4).orderBy("country"))
print(countries_count_df.filter(F.col("destination_count") == 1).count())

# COMMAND ----------

# Check: expected result
print("country        destination_count")
print("Italy          4")
print("Spain          4")
print("United States  4")
print()
print(1)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: countries with at least 4 destinations
# MAGIC SELECT country, COUNT(*) AS destination_count
# MAGIC FROM samples.wanderbricks.destinations
# MAGIC GROUP BY country
# MAGIC HAVING COUNT(*) >= 4
# MAGIC ORDER BY country

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Bookings by Continent
# MAGIC 1. With three joins (2024 bookings → properties → destinations → countries), each with `on=` and `how="inner"` and with a `select` of the useful columns before the join, count the 2024 bookings by continent (`booking_count`), in descending order.
# MAGIC 2. Count the 2024 bookings by `destination_id`; with a left join, join the destinations (columns `destination_id`, `destination`, `country`) to this count and show the destinations with no bookings in 2024.

# COMMAND ----------

# Exercise 6: three joins to get to the continent
bookings_2024_df = bookings_df.filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
property_places_df = properties_df.select("property_id", "destination_id")
destination_countries_df = destinations_df.select("destination_id", "country")
country_continents_df = countries_df.select("country", "continent")

continent_df = (
    bookings_2024_df
    .select("booking_id", "property_id")
    .join(property_places_df, on="property_id", how="inner")
    .join(destination_countries_df, on="destination_id", how="inner")
    .join(country_continents_df, on="country", how="inner")
    .groupBy("continent")
    .agg(F.count("*").alias("booking_count"))
    .orderBy(F.col("booking_count").desc())
)
display(continent_df)

# Destinations with no bookings in 2024: left join and NULL in the count
destination_counts_df = (
    bookings_2024_df
    .select("property_id")
    .join(property_places_df, on="property_id", how="inner")
    .groupBy("destination_id")
    .agg(F.count("*").alias("booking_count"))
)
no_bookings_df = (
    destinations_df
    .select("destination_id", "destination", "country")
    .join(destination_counts_df, on="destination_id", how="left")
    .filter(F.col("booking_count").isNull())
)
display(no_bookings_df)

# COMMAND ----------

# Check: expected result (two grids)
print("continent      booking_count")
print("Europe         5556")
print("Asia           5287")
print("Oceania        1246")
print("North America  1212")
print("Africa         285")
print()
print("destination_id  destination  country  booking_count")
print("2100            Courchevel   France   null")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: 2024 bookings by continent
# MAGIC SELECT c.continent, COUNT(*) AS booking_count
# MAGIC FROM samples.wanderbricks.bookings b
# MAGIC JOIN samples.wanderbricks.properties p USING (property_id)
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC JOIN samples.wanderbricks.countries c USING (country)
# MAGIC WHERE year(b.check_in) = 2024
# MAGIC GROUP BY c.continent
# MAGIC ORDER BY booking_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – The Report by Country
# MAGIC As in section 9.8, but by country and for all of 2024:
# MAGIC 1. build a report with `country`, `continent`, `booking_count`, `cancelled_count`, `cancellation_rate` (in %, one decimal place), and `cancellation_status` (`not assessable` below `MIN_BOOKINGS`, `critical` above `CANCELLATION_RATE_THRESHOLD`, otherwise `ok`);
# MAGIC 2. show it in descending order of rate and then by country;
# MAGIC 3. count the countries by status (`country_count`), in alphabetical order of status.

# COMMAND ----------

# Exercise 7: the complete transformation from section 9.8, by country
cancellation_status = (
    F.when(F.col("booking_count") < MIN_BOOKINGS, "not assessable")              # the minimum volume first
    .when(F.col("cancellation_rate") > CANCELLATION_RATE_THRESHOLD, "critical")
    .otherwise("ok")
)
country_report_df = (
    bookings_df
    .filter(F.year(F.col("check_in")) == ANALYSIS_YEAR)
    .select("booking_id", "property_id", "status")
    .join(properties_df.select("property_id", "destination_id"), on="property_id", how="inner")
    .join(destinations_df.select("destination_id", "country"), on="destination_id", how="inner")
    .join(countries_df.select("country", "continent"), on="country", how="inner")
    .groupBy("country", "continent")
    .agg(
        F.count("*").alias("booking_count"),
        F.sum(F.when(F.col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_count"),
    )
    .withColumn("cancellation_rate", F.round(F.col("cancelled_count") / F.col("booking_count") * 100, 1))
    .withColumn("cancellation_status", cancellation_status)
    .orderBy(F.col("cancellation_rate").desc(), "country")
)
display(country_report_df)
display(country_report_df.groupBy("cancellation_status").agg(F.count("*").alias("country_count")).orderBy("cancellation_status"))

# COMMAND ----------

# Check: expected result (18 rows; shown here: the first two, Italy, and the count by status)
print("country      continent  booking_count  cancelled_count  cancellation_rate  cancellation_status")
print("Egypt        Africa     285            66               23.2               ok")
print("Switzerland  Europe     13             3                23.1               not assessable")
print("...")
print("Italy        Europe     714            142              19.9               ok")
print("...")
print("Austria      Europe     14             2                14.3               not assessable")
print("Canada       North America  54         5                9.3                ok")
print()
print("cancellation_status  country_count")
print("not assessable       2")
print("ok                   16")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check: the report by country
# MAGIC SELECT d.country, c.continent,
# MAGIC        COUNT(*)                                                AS booking_count,
# MAGIC        SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
# MAGIC        ROUND(SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) AS cancellation_rate
# MAGIC FROM samples.wanderbricks.bookings b
# MAGIC JOIN samples.wanderbricks.properties p USING (property_id)
# MAGIC JOIN samples.wanderbricks.destinations d USING (destination_id)
# MAGIC JOIN samples.wanderbricks.countries c USING (country)
# MAGIC WHERE year(b.check_in) = 2024
# MAGIC GROUP BY d.country, c.continent
# MAGIC ORDER BY cancellation_rate DESC, d.country

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC The first four cells below produce an error, the last two a **silent error**. Run them one at a time, note the type of the error and the message (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC **Expected result of the fixes**: `1070`; the average prices by type (147.46, 266.49, 198.54, 173.04 in alphabetical order of type); `1008`; Italy, Spain, United States; `1894`; `29` nights.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a (the expensive Summer Getaway properties)
flagged_df = properties_df.withColumn(
    "expensive_summer",
    F.when((F.col("property_type") == "Summer Getaway") and (F.col("base_price") >= 250), "yes").otherwise("no")
)
print(flagged_df.filter(F.col("expensive_summer") == "yes").count())

# COMMAND ----------

# Fix 8a (error type: CANNOT_CONVERT_COLUMN_INTO_BOOL): & instead of and
flagged_df = properties_df.withColumn(
    "expensive_summer",
    F.when((F.col("property_type") == "Summer Getaway") & (F.col("base_price") >= 250), "yes").otherwise("no")
)
print(flagged_df.filter(F.col("expensive_summer") == "yes").count())   # expected: 1070

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b (the average price by type)
type_avg_df = properties_df.groupBy("property_type").agg(round(F.avg("base_price"), 2).alias("avg_price"))
display(type_avg_df)

# COMMAND ----------

# Fix 8b (error type: TypeError): F.round, not Python's round
type_avg_df = properties_df.groupBy("property_type").agg(F.round(F.avg("base_price"), 2).alias("avg_price"))
display(type_avg_df.orderBy("property_type"))   # expected: 147.46, 266.49, 198.54, 173.04

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c (the Italian properties)
places_df = properties_df.join(destinations_df, properties_df["destination_id"] == destinations_df["destination_id"], how="inner")
print(places_df.filter(F.col("country") == "Italy").select("property_id", "destination_id").count())

# COMMAND ----------

# Fix 8c (error type: AMBIGUOUS_REFERENCE): on= and select before the join
places_df = properties_df.join(destinations_df.select("destination_id", "country"), on="destination_id", how="inner")
print(places_df.filter(F.col("country") == "Italy").select("property_id", "destination_id").count())   # expected: 1008

# COMMAND ----------

# INTENTIONAL ERROR – cell 8d (the countries with at least 4 destinations)
big_countries_df = destinations_df.groupBy("country").filter(F.count("*") >= 4)
display(big_countries_df)

# COMMAND ----------

# Fix 8d (error type: AttributeError): first agg, then the filter (HAVING)
big_countries_df = (
    destinations_df
    .groupBy("country")
    .agg(F.count("*").alias("destination_count"))
    .filter(F.col("destination_count") >= 4)
)
display(big_countries_df.orderBy("country"))   # expected: Italy, Spain, United States

# COMMAND ----------

# SILENT ERROR – cell 8e (the properties in the high band)
bands_df = properties_df.withColumn(
    "price_band",
    F.when(F.col("base_price") >= 200, "medium")
    .when(F.col("base_price") >= 250, "high")
    .otherwise("low")
)
print(bands_df.filter(F.col("price_band") == "high").count())

# COMMAND ----------

# Fix 8e (what's wrong: the broadest condition is written first)
bands_df = properties_df.withColumn(
    "price_band",
    F.when(F.col("base_price") >= 250, "high")
    .when(F.col("base_price") >= 200, "medium")
    .otherwise("low")
)
print(bands_df.filter(F.col("price_band") == "high").count())   # expected: 1894

# COMMAND ----------

# SILENT ERROR – cell 8f (the nights of the Sardinia property)
sardinia_df = (
    spark.createDataFrame(raw_sardinia_rows)
    .withColumn("check_in", F.to_date(F.col("check_in"), "mm/dd/yyyy"))
    .withColumn("check_out", F.to_date(F.col("check_out"), "mm/dd/yyyy"))
)
display(sardinia_df.agg(F.sum(F.datediff(F.col("check_out"), F.col("check_in"))).alias("total_nights")))

# COMMAND ----------

# Fix 8f (what's wrong: mm means minutes; the month is MM)
sardinia_df = (
    spark.createDataFrame(raw_sardinia_rows)
    .withColumn("check_in", F.to_date(F.col("check_in"), "MM/dd/yyyy"))
    .withColumn("check_out", F.to_date(F.col("check_out"), "MM/dd/yyyy"))
)
display(sardinia_df.agg(F.sum(F.datediff(F.col("check_out"), F.col("check_in"))).alias("total_nights")))   # expected: 29
