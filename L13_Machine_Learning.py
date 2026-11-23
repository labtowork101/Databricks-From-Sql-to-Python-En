# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 13 – Introduction to Machine Learning
# MAGIC
# MAGIC Notebook for Chapter 13 of *Beyond SELECT*. Goals: build a model that estimates the base price of a property from its characteristics (linear regression with scikit-learn), evaluate it with MAE and R² against a baseline model, log the experiments in MLflow, and try a classification of cancellations, which finds no signal.
# MAGIC
# MAGIC Prerequisites: notebook attached to **Serverless**; the `L11_Final_Project` notebook run at least once (the `s_clean_bookings_booking` table must exist); the `utils` notebook in the same `Python_Book` folder. The notebook **doesn't write tables**: it logs the runs in the `python_book_chapter_13` MLflow experiment, in your personal folder.
# MAGIC
# MAGIC Run **one cell at a time**, from top to bottom. The **INTENTIONAL ERROR** cells must fail, and the *Fix* cell below must work; the **SILENT ERROR** cell works but gives a wrong result. Don't use Run all. If the compute stops, run again the `%run ./utils` cell, the constants cell, and the cells that create the variables used later (`properties_ml_df`, `properties_pd`, `X_full`, `price_model`, and the functions).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Introduction

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Setup Cell

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (your account's address appears in place of `<email address>`):
# MAGIC ```
# MAGIC workspace.python_book.s_clean_bookings_booking
# MAGIC /Users/<email address>/python_book_chapter_13
# MAGIC ```

# COMMAND ----------

# Chapter libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
import mlflow

# Chapter constants
CLEAN_BOOKINGS_TABLE = build_table_name("clean_bookings", "booking")
PRICE_TARGET = "base_price"
NUMERIC_FEATURES = ["bedrooms", "bathrooms", "max_guests"]
CATEGORICAL_FEATURES = ["property_type", "country"]
TEST_SIZE = 0.2
RANDOM_STATE = 42

# The chapter's MLflow experiment, in your personal folder (section 13.10)
current_user = spark.sql("SELECT current_user()").collect()[0][0]
EXPERIMENT_PATH = f"/Users/{current_user}/python_book_chapter_13"

print(CLEAN_BOOKINGS_TABLE)
print(EXPERIMENT_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.1 From Written Rules to Learned Rules
# MAGIC
# MAGIC A section without code: the terms of Machine Learning (feature, target, model, training, prediction; regression and classification) are explained in the text of the chapter.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.2 The Problem and the Data

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 18163
# MAGIC ```

# COMMAND ----------

properties_ml_df = (
    spark.table(PROPERTIES_TABLE)
    .join(
        spark.table(DESTINATIONS_TABLE).select("destination_id", "destination", "country"),
        on="destination_id",
        how="inner",
    )
    .withColumn("base_price", F.round(F.col("base_price").cast("double"), 2))
    .select("property_id", "title", "property_type", "bedrooms", "bathrooms",
            "max_guests", "destination", "country", "base_price")
    .orderBy("property_id")
)
print(properties_ml_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC bedrooms  property_count  average_price
# MAGIC 1         11320           160.76
# MAGIC 2         4538            198.69
# MAGIC 3         1550            234.99
# MAGIC 4         584             273.66
# MAGIC 5         171             309.41
# MAGIC ```

# COMMAND ----------

display(
    properties_ml_df
    .groupBy("bedrooms")
    .agg(
        F.count("*").alias("property_count"),
        F.round(F.avg("base_price"), 2).alias("average_price"),
    )
    .orderBy("bedrooms")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC property_type     property_count  average_price
# MAGIC Historical Place  1646            147.46
# MAGIC Urban Year-Round  9264            173.04
# MAGIC Summer Getaway    7068            198.54
# MAGIC Ski Resort        185             266.49
# MAGIC ```

# COMMAND ----------

display(
    properties_ml_df
    .groupBy("property_type")
    .agg(
        F.count("*").alias("property_count"),
        F.round(F.avg("base_price"), 2).alias("average_price"),
    )
    .orderBy("average_price")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.3 From Spark to pandas

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC <class 'pandas.core.frame.DataFrame'>
# MAGIC (18163, 9)
# MAGIC ```

# COMMAND ----------

properties_pd = properties_ml_df.toPandas()

print(type(properties_pd))
print(properties_pd.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC property_id  title                    property_type     bedrooms  bathrooms  max_guests  destination  country   base_price
# MAGIC 1            Bungalow in Ibiza        Summer Getaway    3         1          5           Ibiza        Spain     275.61
# MAGIC 2            Hotel in Madrid          Urban Year-Round  1         1          1           Madrid       Spain     142.2
# MAGIC 3            Bungalow in Mallorca     Summer Getaway    4         3          6           Mallorca     Spain     345.43
# MAGIC 4            Beach House in Mallorca  Summer Getaway    1         1          2           Mallorca     Spain     191.29
# MAGIC 5            Bungalow in Phuket       Summer Getaway    1         1          1           Phuket       Thailand  115.91
# MAGIC ```

# COMMAND ----------

display(properties_pd.head())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC property_id        int64
# MAGIC title             object
# MAGIC property_type     object
# MAGIC bedrooms           int32
# MAGIC bathrooms          int32
# MAGIC max_guests         int32
# MAGIC destination       object
# MAGIC country           object
# MAGIC base_price       float64
# MAGIC dtype: object
# MAGIC ```

# COMMAND ----------

print(properties_pd.dtypes)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC <class 'pandas.core.series.Series'>
# MAGIC 181.6 55.93 561.97
# MAGIC <class 'pandas.core.frame.DataFrame'>
# MAGIC (18163, 2)
# MAGIC ```

# COMMAND ----------

prices = properties_pd["base_price"]
print(type(prices))
print(round(prices.mean(), 2), prices.min(), prices.max())

rooms = properties_pd[["bedrooms", "bathrooms"]]
print(type(rooms))
print(rooms.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.4 Features, Target, Training Data, and Test Data

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC (18163, 3) (18163,)
# MAGIC ```

# COMMAND ----------

X = properties_pd[NUMERIC_FEATURES]
y = properties_pd[PRICE_TARGET]
print(X.shape, y.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC (14530, 3) (3633, 3)
# MAGIC (14530,) (3633,)
# MAGIC ```

# COMMAND ----------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)

print(X_train.shape, X_test.shape)
print(y_train.shape, y_test.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC        bedrooms  bathrooms  max_guests
# MAGIC 18074         3          3           6
# MAGIC 509           2          1           4
# MAGIC 3410          1          1           2
# MAGIC 18074    250.00
# MAGIC 509      154.20
# MAGIC 3410     153.81
# MAGIC Name: base_price, dtype: float64
# MAGIC ```

# COMMAND ----------

print(X_train.head(3))
print(y_train.head(3))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.5 The Baseline Model

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 181.53
# MAGIC 40.6
# MAGIC ```

# COMMAND ----------

mean_price = y_train.mean()
print(round(mean_price, 2))

baseline_predictions = [mean_price] * len(y_test)
baseline_mae = mean_absolute_error(y_test, baseline_predictions)
print(round(baseline_mae, 2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.6 The First Model: Linear Regression

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Intercept: 122.60
# MAGIC Coefficient of bedrooms: 37.91
# MAGIC ```

# COMMAND ----------

rooms_model = LinearRegression()
rooms_model.fit(X_train[["bedrooms"]], y_train)

print(f"Intercept: {rooms_model.intercept_:.2f}")
print(f"Coefficient of bedrooms: {rooms_model.coef_[0]:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Bedrooms 1: 160.51
# MAGIC Bedrooms 2: 198.42
# MAGIC Bedrooms 3: 236.33
# MAGIC Bedrooms 4: 274.24
# MAGIC Bedrooms 5: 312.15
# MAGIC ```

# COMMAND ----------

new_rooms = pd.DataFrame({"bedrooms": [1, 2, 3, 4, 5]})
new_rooms_predictions = rooms_model.predict(new_rooms)
for bedrooms, prediction in zip(new_rooms["bedrooms"], new_rooms_predictions):
    print(f"Bedrooms {bedrooms}: {prediction:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC predicted  160.51   actual  206.93
# MAGIC predicted  160.51   actual  155.20
# MAGIC predicted  160.51   actual  131.89
# MAGIC predicted  236.33   actual  293.14
# MAGIC predicted  236.33   actual  321.21
# MAGIC 33.94
# MAGIC ```

# COMMAND ----------

rooms_predictions = rooms_model.predict(X_test[["bedrooms"]])

for prediction, actual in zip(rooms_predictions[:5], y_test.head(5)):
    print(f"predicted {prediction:7.2f}   actual {actual:7.2f}")

print(round(mean_absolute_error(y_test, rooms_predictions), 2))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC bedrooms  predicted_price
# MAGIC 1         160.51
# MAGIC 2         198.42
# MAGIC 3         236.33
# MAGIC 4         274.24
# MAGIC 5         312.15
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT bedrooms, ROUND(122.60 + 37.91 * bedrooms, 2) AS predicted_price
# MAGIC FROM (SELECT DISTINCT bedrooms FROM samples.wanderbricks.properties)
# MAGIC ORDER BY bedrooms

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.7 Evaluating a Model

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC {'mae': 33.94, 'r2': 0.326}
# MAGIC ```

# COMMAND ----------

def evaluate_regression(model, X_eval, y_eval):
    """Returns the MAE and R² of a regression model on a dataset."""
    predictions = model.predict(X_eval)
    return {
        "mae": round(mean_absolute_error(y_eval, predictions), 2),
        "r2": round(r2_score(y_eval, predictions), 3),
    }

print(evaluate_regression(rooms_model, X_test[["bedrooms"]], y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Coefficients:
# MAGIC   bedrooms       34.74
# MAGIC   bathrooms      22.32
# MAGIC   max_guests      0.09
# MAGIC Training: {'mae': 32.15, 'r2': 0.421}
# MAGIC Test:     {'mae': 32.71, 'r2': 0.383}
# MAGIC ```

# COMMAND ----------

numeric_model = LinearRegression()
numeric_model.fit(X_train, y_train)

print("Coefficients:")
for feature, coefficient in zip(X_train.columns, numeric_model.coef_):
    print(f"  {feature:<12}{coefficient:8.2f}")
print("Training:", evaluate_regression(numeric_model, X_train, y_train))
print("Test:    ", evaluate_regression(numeric_model, X_test, y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.8 Categorical Features

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message:
# MAGIC ```
# MAGIC ValueError: could not convert string to float: 'Urban Year-Round'
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – a text column among the features
text_X = properties_pd[NUMERIC_FEATURES + ["property_type"]]
text_X_train, text_X_test, text_y_train, text_y_test = train_test_split(
    text_X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
LinearRegression().fit(text_X_train, text_y_train)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC (18163, 23)
# MAGIC ['bedrooms', 'bathrooms', 'max_guests', 'property_type_Ski Resort', 'property_type_Summer Getaway', 'property_type_Urban Year-Round', 'country_Austria', 'country_Canada']
# MAGIC ```

# COMMAND ----------

# Fix: the categories become columns of 0s and 1s
X_full = pd.get_dummies(
    properties_pd[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
    columns=CATEGORICAL_FEATURES,
    drop_first=True,
    dtype=int,
)
print(X_full.shape)
print(list(X_full.columns[:8]))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid): 3 rows and 23 columns; the first seven are:
# MAGIC ```
# MAGIC bedrooms  bathrooms  max_guests  property_type_Ski Resort  property_type_Summer Getaway  property_type_Urban Year-Round  country_Austria
# MAGIC 3         1          5           0                         1                             0                               0
# MAGIC 1         1          1           0                         0                             1                               0
# MAGIC 4         3          6           0                         1                             0                               0
# MAGIC ```

# COMMAND ----------

display(X_full.head(3))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Training: {'mae': 12.54, 'r2': 0.898}
# MAGIC Test:     {'mae': 12.67, 'r2': 0.89}
# MAGIC ```

# COMMAND ----------

X_train, X_test, y_train, y_test = train_test_split(
    X_full, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)

price_model = LinearRegression()
price_model.fit(X_train, y_train)

print("Training:", evaluate_regression(price_model, X_train, y_train))
print("Test:    ", evaluate_regression(price_model, X_test, y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Intercept: 90.88
# MAGIC   bedrooms                           34.68
# MAGIC   bathrooms                          22.11
# MAGIC   max_guests                          0.06
# MAGIC   property_type_Ski Resort           64.97
# MAGIC   property_type_Summer Getaway       60.61
# MAGIC   property_type_Urban Year-Round     27.41
# MAGIC   country_Austria                   -45.71
# MAGIC   country_Canada                     81.36
# MAGIC   country_China                     -10.41
# MAGIC   country_Egypt                     -64.07
# MAGIC   country_France                    -20.31
# MAGIC   country_Germany                   -71.92
# MAGIC   country_Greece                      5.11
# MAGIC   country_India                     -88.99
# MAGIC   country_Italy                     -11.56
# MAGIC   country_Japan                     -42.75
# MAGIC   country_Singapore                 -21.09
# MAGIC   country_Spain                     -27.78
# MAGIC   country_Switzerland                29.46
# MAGIC   country_Thailand                  -81.82
# MAGIC   country_United Arab Emirates      -43.98
# MAGIC   country_United Kingdom              7.07
# MAGIC   country_United States              35.98
# MAGIC ```

# COMMAND ----------

print(f"Intercept: {price_model.intercept_:.2f}")
for feature, coefficient in zip(X_full.columns, price_model.coef_):
    print(f"  {feature:<32}{coefficient:8.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.9 Using the Model

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC True
# MAGIC ```

# COMMAND ----------

feature_columns = list(X_full.columns)

def prepare_features(df):
    """Turns the starting columns into the features of the price model."""
    return (
        pd.get_dummies(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES], columns=CATEGORICAL_FEATURES, dtype=int)
        .reindex(columns=feature_columns, fill_value=0)
    )

print(prepare_features(properties_pd).equals(X_full))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC property_id  title                  bedrooms  bathrooms  max_guests  base_price  predicted_price
# MAGIC 11670        Historic Inn in Rome   4         3          8           284.97      284.88
# MAGIC 16225        Beach House in Amalfi  1         1          1           236.95      196.79
# MAGIC 16317        Bungalow in Sardinia   2         1          4           213.91      231.66
# MAGIC ```

# COMMAND ----------

guide_pd = (
    properties_ml_df
    .filter(
        (F.col("property_id") == 11670)
        | (F.col("property_id") == 16317)
        | (F.col("property_id") == 16225)
    )
    .toPandas()
)

guide_pd["predicted_price"] = price_model.predict(prepare_features(guide_pd)).round(2)
display(guide_pd[["property_id", "title", "bedrooms", "bathrooms", "max_guests", "base_price", "predicted_price"]])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC (1, 23)
# MAGIC Suggested base price: 288.58
# MAGIC ```

# COMMAND ----------

new_property_pd = pd.DataFrame([
    {"bedrooms": 3, "bathrooms": 2, "max_guests": 6,
     "property_type": "Summer Getaway", "country": "Italy"},
])
new_property_X = prepare_features(new_property_pd)
print(new_property_X.shape)
print(f"Suggested base price: {price_model.predict(new_property_X)[0]:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message:
# MAGIC ```
# MAGIC ValueError: The feature names should match those that were passed during fit.
# MAGIC Feature names seen at fit time, yet now missing:
# MAGIC - country_Austria
# MAGIC - country_Canada
# MAGIC - country_China
# MAGIC - country_Egypt
# MAGIC - country_France
# MAGIC - ...
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – the features of the new property aren't those of the model
new_property_X = pd.get_dummies(new_property_pd, columns=CATEGORICAL_FEATURES, dtype=int)
price_model.predict(new_property_X)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC 288.58
# MAGIC ```

# COMMAND ----------

# Fix: the same preparation used for training
print(f"{price_model.predict(prepare_features(new_property_pd))[0]:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.10 Tracking Experiments with MLflow

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output. The first time you run it, an `INFO` line with the date and time appears first; from the second run on, it no longer appears:
# MAGIC ```
# MAGIC 2026/11/19 15:11:20 INFO mlflow.tracking.fluent: Experiment with name '/Users/<email address>/python_book_chapter_13' does not exist. Creating a new experiment.
# MAGIC /Users/<email address>/python_book_chapter_13
# MAGIC ```

# COMMAND ----------

experiment = mlflow.set_experiment(EXPERIMENT_PATH)
print(experiment.name)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output: the **MLflow run** box (*Logged 1 run to an experiment in MLflow*, with the table of the `full_price` run), then the output below. Under the box, lines like `WARNING mlflow.tracking.context.registry: Encountered unexpected error during resolving tags…` may appear, one per run: they're internal MLflow warnings on Serverless, the run is logged anyway, and you can ignore them.
# MAGIC ```
# MAGIC {'mae': 12.67, 'r2': 0.89}
# MAGIC ```

# COMMAND ----------

price_metrics = evaluate_regression(price_model, X_test, y_test)

with mlflow.start_run(run_name="full_price"):
    mlflow.log_param("model", "LinearRegression")
    mlflow.log_param("n_features", X_full.shape[1])
    mlflow.log_metric("mae", price_metrics["mae"])
    mlflow.log_metric("r2", price_metrics["r2"])

print(price_metrics)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output: the MLflow box with the three logged runs, then the three lines below, possibly interleaved with MLflow's `WARNING` lines (one per run, to be ignored):
# MAGIC ```
# MAGIC bedrooms_only              1   33.94   0.326
# MAGIC three_numeric              3   32.71   0.383
# MAGIC numeric_and_categories    23   12.67    0.89
# MAGIC ```

# COMMAND ----------

def train_and_log(features_df, target, run_name):
    """Splits the data, trains a linear regression, evaluates it on the test set, and logs the run in MLflow."""
    X_train, X_test, y_train, y_test = train_test_split(
        features_df, target, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    model = LinearRegression()
    model.fit(X_train, y_train)
    metrics = evaluate_regression(model, X_test, y_test)
    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("model", "LinearRegression")
        mlflow.log_param("n_features", features_df.shape[1])
        mlflow.log_metric("mae", metrics["mae"])
        mlflow.log_metric("r2", metrics["r2"])
    print(f"{run_name:<24}{features_df.shape[1]:>4}{metrics['mae']:>8}{metrics['r2']:>8}")

train_and_log(properties_pd[["bedrooms"]], y, "bedrooms_only")
train_and_log(properties_pd[NUMERIC_FEATURES], y, "three_numeric")
train_and_log(X_full, y, "numeric_and_categories")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.11 A Problem Without Signal: Cancellations

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC nights  booking_count  cancellation_rate
# MAGIC 1       663            38.6
# MAGIC 2       1376           38.9
# MAGIC 3       3093           38.4
# MAGIC 4       4163           37.1
# MAGIC 5       2979           37.2
# MAGIC 6       1088           37
# MAGIC 7       223            38.1
# MAGIC 8       5              40
# MAGIC ```

# COMMAND ----------

cancellation_df = (
    spark.table(CLEAN_BOOKINGS_TABLE)
    .withColumn("nights", F.datediff(F.col("check_out"), F.col("check_in")))
    .withColumn("lead_days", F.datediff(F.col("check_in"), F.col("created_at")))
    .withColumn("is_cancelled", F.when(F.col("status") == "cancelled", 1).otherwise(0))
    .select("booking_id", "guests_count", "nights", "lead_days", "total_amount", "is_cancelled")
)

display(
    cancellation_df
    .groupBy("nights")
    .agg(
        F.count("*").alias("booking_count"),
        F.round(F.avg("is_cancelled") * 100, 1).alias("cancellation_rate"),
    )
    .orderBy("nights")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC lead_band        booking_count  cancellation_rate
# MAGIC 1) up to 7 days  2412           37.1
# MAGIC 2) 8-30 days     3324           37.7
# MAGIC 3) 31-90 days    4051           38
# MAGIC 4) over 90 days  3803           37.8
# MAGIC ```

# COMMAND ----------

display(
    cancellation_df
    .withColumn("lead_band", F.when(F.col("lead_days") <= 7, "1) up to 7 days")
                .when(F.col("lead_days") <= 30, "2) 8-30 days")
                .when(F.col("lead_days") <= 90, "3) 31-90 days")
                .otherwise("4) over 90 days"))
    .groupBy("lead_band")
    .agg(
        F.count("*").alias("booking_count"),
        F.round(F.avg("is_cancelled") * 100, 1).alias("cancellation_rate"),
    )
    .orderBy("lead_band")
)

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message:
# MAGIC ```
# MAGIC ValueError: Input X contains NaN.
# MAGIC LogisticRegression does not accept missing values encoded as NaN natively. For supervised learning, you might want to consider sklearn.ensemble.HistGradientBoostingClassifier and Regressor which accept missing values encoded as NaNs natively. Alternatively, it is possible to preprocess the data, for instance by using an imputer transformer in a pipeline or drop samples with missing values. See https://scikit-learn.org/stable/modules/impute.html You can find a list of all estimators that handle NaN values at the following page: https://scikit-learn.org/stable/modules/impute.html#estimators-that-handle-nan-values
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – 16 bookings have a NULL amount
cancellation_pd = cancellation_df.orderBy("booking_id").toPandas()
CANCELLATION_FEATURES = ["guests_count", "nights", "lead_days", "total_amount"]

c_X_train, c_X_test, c_y_train, c_y_test = train_test_split(
    cancellation_pd[CANCELLATION_FEATURES], cancellation_pd["is_cancelled"],
    test_size=TEST_SIZE, random_state=RANDOM_STATE
)
LogisticRegression().fit(c_X_train, c_y_train)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC (13574, 6)
# MAGIC (10859, 4) (2715, 4)
# MAGIC 38.0
# MAGIC ```

# COMMAND ----------

# Fix: the rows without an amount are excluded in Spark, before toPandas()
cancellation_pd = (
    cancellation_df
    .filter(F.col("total_amount").isNotNull())
    .orderBy("booking_id")
    .toPandas()
)

c_X_train, c_X_test, c_y_train, c_y_test = train_test_split(
    cancellation_pd[CANCELLATION_FEATURES], cancellation_pd["is_cancelled"],
    test_size=TEST_SIZE, random_state=RANDOM_STATE
)
print(cancellation_pd.shape)
print(c_X_train.shape, c_X_test.shape)
print(round(c_y_test.mean() * 100, 1))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 0.6195
# MAGIC ```

# COMMAND ----------

baseline_accuracy = accuracy_score(c_y_test, [0] * len(c_y_test))
print(round(baseline_accuracy, 4))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 0.6195
# MAGIC 0
# MAGIC ```

# COMMAND ----------

cancellation_model = LogisticRegression()
cancellation_model.fit(c_X_train, c_y_train)
c_predictions = cancellation_model.predict(c_X_test)

print(round(accuracy_score(c_y_test, c_predictions), 4))
print(c_predictions.sum())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Cancellation probability: from 0.292 to 0.399
# MAGIC ```

# COMMAND ----------

probabilities = cancellation_model.predict_proba(c_X_test)[:, 1]
print(f"Cancellation probability: from {probabilities.min():.3f} to {probabilities.max():.3f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC guests_count  booking_count  cancellation_rate
# MAGIC 1             6879           38.4
# MAGIC 2             3929           37.2
# MAGIC 3             1557           36.4
# MAGIC 4             723            37.9
# MAGIC 5             279            36.9
# MAGIC 6             138            30.4
# MAGIC 7             57             33.3
# MAGIC 8             20             55
# MAGIC 9             4              25
# MAGIC 10            4              50
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT guests_count, COUNT(*) AS booking_count,
# MAGIC        ROUND(AVG(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100, 1) AS cancellation_rate
# MAGIC FROM workspace.python_book.s_clean_bookings_booking
# MAGIC GROUP BY guests_count
# MAGIC ORDER BY guests_count

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13.12 Common Machine Learning Mistakes

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message (summary line; under the cell the text `<class 'pandas.core.series.Series'>` doesn't appear, and two spaces remain after *got*):
# MAGIC ```
# MAGIC ValueError: Expected a 2-dimensional container but got  instead. Pass a DataFrame containing a single row (i.e. single sample) or a single column (i.e. single feature) instead.
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – a single feature passed as a Series
LinearRegression().fit(properties_pd["bedrooms"], properties_pd[PRICE_TARGET])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC [37.42]
# MAGIC ```

# COMMAND ----------

# Fix: double square brackets, a table with one column
print(LinearRegression().fit(properties_pd[["bedrooms"]], properties_pd[PRICE_TARGET]).coef_.round(2))

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message:
# MAGIC ```
# MAGIC KeyError: "['bedroom'] not in index"
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – a wrong column name
properties_pd[["bedroom", "bathrooms"]]

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC (18163, 2)
# MAGIC ```

# COMMAND ----------

# Fix: the exact name of the column
print(properties_pd[["bedrooms", "bathrooms"]].shape)

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the following cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC {'mae': 10.34, 'r2': 0.926}
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – a feature calculated from the target
def classify_price(price):
    """Price bands from Chapter 2."""
    if price >= 250:
        return "high"
    elif price >= 200:
        return "medium"
    return "low"

leaky_pd = properties_pd.copy()
leaky_pd["price_band"] = [classify_price(price) for price in leaky_pd["base_price"]]

leaky_X = pd.get_dummies(
    leaky_pd[NUMERIC_FEATURES + CATEGORICAL_FEATURES + ["price_band"]],
    columns=CATEGORICAL_FEATURES + ["price_band"], drop_first=True, dtype=int,
)
l_X_train, l_X_test, l_y_train, l_y_test = train_test_split(
    leaky_X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
leaky_model = LinearRegression().fit(l_X_train, l_y_train)
print(evaluate_regression(leaky_model, l_X_test, l_y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC {'mae': 12.67, 'r2': 0.89}
# MAGIC ```

# COMMAND ----------

# Fix: only features known before the price is known
print(evaluate_regression(price_model, X_test, y_test))
