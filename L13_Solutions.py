# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 13 – Exercise Solutions
# MAGIC
# MAGIC Commented solutions to the exercises in Chapter 13 of *Beyond SELECT* (Introduction to Machine Learning). Prerequisites: Serverless; `L11_Final_Project` run at least once; `utils` in the same folder. Exercise 6 logs three runs in the `python_book_chapter_13` MLflow experiment.
# MAGIC
# MAGIC Run **one cell at a time**. In exercise 8, the **INTENTIONAL ERROR** cells must fail (Run all stops at cell 8a) and the **SILENT ERROR** cells give a wrong result; below each one is the fix.

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (the very first time `set_experiment` runs, the `INFO` line that creates the experiment may also appear):
# MAGIC ```
# MAGIC (18163, 9) (18163, 23)
# MAGIC ```

# COMMAND ----------

# Libraries, constants, and data for the exercises (as in the chapter notebook)
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
import mlflow

PRICE_TARGET = "base_price"
NUMERIC_FEATURES = ["bedrooms", "bathrooms", "max_guests"]
CATEGORICAL_FEATURES = ["property_type", "country"]
TEST_SIZE = 0.2
RANDOM_STATE = 42
current_user = spark.sql("SELECT current_user()").collect()[0][0]
EXPERIMENT_PATH = f"/Users/{current_user}/python_book_chapter_13"

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
properties_pd = properties_ml_df.toPandas()
y = properties_pd[PRICE_TARGET]
X_full = pd.get_dummies(
    properties_pd[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
    columns=CATEGORICAL_FEATURES,
    drop_first=True,
    dtype=int,
)

def evaluate_regression(model, X_eval, y_eval):
    """Returns the MAE and R² of a regression model on a dataset."""
    predictions = model.predict(X_eval)
    return {
        "mae": round(mean_absolute_error(y_eval, predictions), 2),
        "r2": round(r2_score(y_eval, predictions), 3),
    }

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
    print(f"{run_name:<28}{features_df.shape[1]:>4}{metrics['mae']:>8}{metrics['r2']:>8}")

mlflow.set_experiment(EXPERIMENT_PATH)
print(properties_pd.shape, X_full.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 1 ★ – The Italian Properties in pandas
# MAGIC
# MAGIC In Spark, filter the properties with `country` equal to `Italy`, bring them into pandas in `italy_pd`, and print the shape of the table and the average base price (rounded to two decimal places), the minimum, and the maximum. *Expected result:* `(1008, 9)` and `192.34 110.06 517.6`; the check cell in Spark returns `1008` and `192.34`.

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC (1008, 9)
# MAGIC 192.34 110.06 517.6
# MAGIC ```

# COMMAND ----------

italy_pd = properties_ml_df.filter(F.col("country") == "Italy").toPandas()

print(italy_pd.shape)
italy_prices = italy_pd["base_price"]
print(round(italy_prices.mean(), 2), italy_prices.min(), italy_prices.max())

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC property_count  average_price
# MAGIC 1008            192.34
# MAGIC ```

# COMMAND ----------

# Check
display(
    properties_ml_df
    .filter(F.col("country") == "Italy")
    .agg(F.count("*").alias("property_count"), F.round(F.avg("base_price"), 2).alias("average_price"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 2 ★ – Another Split
# MAGIC
# MAGIC With the three numeric features, split the data, keeping 25% of the rows for the test set (with `random_state=RANDOM_STATE`). Print the shapes of the feature tables, the average price of the training data, and the MAE of the baseline model. *Expected result:* `(13622, 3) (4541, 3)`, `181.72`, `40.46`.

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC (13622, 3) (4541, 3)
# MAGIC 181.72
# MAGIC 40.46
# MAGIC ```

# COMMAND ----------

X = properties_pd[NUMERIC_FEATURES]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=RANDOM_STATE
)
print(X_train.shape, X_test.shape)

mean_price = y_train.mean()
print(round(mean_price, 2))
print(round(mean_absolute_error(y_test, [mean_price] * len(y_test)), 2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – The Median as a Baseline
# MAGIC
# MAGIC With the chapter's split (20% for the test set), calculate the mean and the **median** (the `median()` method of a Series) of the training prices, and the MAE of the two baseline models that give all the properties one or the other. Which of the two makes smaller errors? *Expected result:* `181.53 171.71`; MAE `40.6` with the mean and `39.95` with the median. The median is lower than the mean because a few very high prices pull the mean up; for the MAE, it's the better choice.

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 181.53 171.71
# MAGIC 40.6
# MAGIC 39.95
# MAGIC ```

# COMMAND ----------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
mean_price = y_train.mean()
median_price = y_train.median()
print(round(mean_price, 2), round(median_price, 2))
print(round(mean_absolute_error(y_test, [mean_price] * len(y_test)), 2))
print(round(mean_absolute_error(y_test, [median_price] * len(y_test)), 2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Bathrooms Model
# MAGIC
# MAGIC Train a linear regression with the `bathrooms` feature alone and print its intercept, its coefficient, and its evaluation on the test set. Is it better or worse than the bedrooms model? *Expected result:* intercept `139.27`, coefficient `33.57`, `{'mae': 38.36, 'r2': 0.126}`: worse than the bedrooms model (33.94 and 0.326), because almost eight properties out of ten have only one bathroom.

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC Intercept: 139.27
# MAGIC Coefficient of bathrooms: 33.57
# MAGIC {'mae': 38.36, 'r2': 0.126}
# MAGIC ```

# COMMAND ----------

bathrooms_model = LinearRegression()
bathrooms_model.fit(X_train[["bathrooms"]], y_train)

print(f"Intercept: {bathrooms_model.intercept_:.2f}")
print(f"Coefficient of bathrooms: {bathrooms_model.coef_[0]:.2f}")
print(evaluate_regression(bathrooms_model, X_test[["bathrooms"]], y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – The Destination Instead of the Country
# MAGIC
# MAGIC Build the feature table with the three numeric features, the property type, and the **destination** instead of the country; split it, train the model, and evaluate it. Then calculate the predictions for the three guide properties, preparing them with `pd.get_dummies` and `reindex` on the columns of the new table. *Expected result:* `(18163, 47)`; `{'mae': 10.73, 'r2': 0.925}`; predictions `287.09` (Rome), `237.65` (Amalfi), `224.43` (Sardinia). With the destination, the model tells Amalfi apart from the rest of Italy, and the prediction for the Amalfi house comes very close to the actual price (236.95).

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC (18163, 47)
# MAGIC {'mae': 10.73, 'r2': 0.925}
# MAGIC ```

# COMMAND ----------

X_destination = pd.get_dummies(
    properties_pd[NUMERIC_FEATURES + ["property_type", "destination"]],
    columns=["property_type", "destination"],
    drop_first=True,
    dtype=int,
)
print(X_destination.shape)

d_X_train, d_X_test, d_y_train, d_y_test = train_test_split(
    X_destination, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
destination_model = LinearRegression()
destination_model.fit(d_X_train, d_y_train)
print(evaluate_regression(destination_model, d_X_test, d_y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (grid):
# MAGIC ```
# MAGIC property_id  destination  base_price  predicted_price
# MAGIC 11670        Rome         284.97      287.09
# MAGIC 16225        Amalfi       236.95      237.65
# MAGIC 16317        Sardinia     213.91      224.43
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
guide_X = (
    pd.get_dummies(guide_pd[NUMERIC_FEATURES + ["property_type", "destination"]],
                   columns=["property_type", "destination"], dtype=int)
    .reindex(columns=X_destination.columns, fill_value=0)
)
guide_pd["predicted_price"] = destination_model.predict(guide_X).round(2)
display(guide_pd[["property_id", "destination", "base_price", "predicted_price"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Three Runs in MLflow
# MAGIC
# MAGIC With the `train_and_log` function, log three runs in the chapter's experiment: `bathrooms_only` (the `bathrooms` feature alone), `numeric_and_type` (the three numeric features and the property type, encoded with `pd.get_dummies`), and `numeric_type_destination` (the table from exercise 5). Open the runs in the user interface and compare them; in the notebook, read the last three runs with `mlflow.search_runs`. *Expected result:* `bathrooms_only 1 38.36 0.126`, `numeric_and_type 6 28.52 0.506`, `numeric_type_destination 47 10.73 0.925`; the check prints `True` and the grid of the three runs, most recent first.

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output (possibly interleaved with MLflow's `WARNING` lines, one per run, to be ignored): the MLflow box with the three logged runs, then:
# MAGIC ```
# MAGIC bathrooms_only                 1   38.36   0.126
# MAGIC numeric_and_type               6   28.52   0.506
# MAGIC numeric_type_destination      47   10.73   0.925
# MAGIC ```

# COMMAND ----------

X_type = pd.get_dummies(
    properties_pd[NUMERIC_FEATURES + ["property_type"]],
    columns=["property_type"],
    drop_first=True,
    dtype=int,
)

train_and_log(properties_pd[["bathrooms"]], y, "bathrooms_only")
train_and_log(X_type, y, "numeric_and_type")
train_and_log(X_destination, y, "numeric_type_destination")

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output: `True`, then the grid of the three most recent runs (if you ran the exercise only once):
# MAGIC ```
# MAGIC tags.mlflow.runName       params.n_features  metrics.mae  metrics.r2
# MAGIC numeric_type_destination  47                 10.73        0.925
# MAGIC numeric_and_type          6                  28.52        0.506
# MAGIC bathrooms_only            1                  38.36        0.126
# MAGIC ```

# COMMAND ----------

# Check: the experiment's runs, most recent first
runs_pd = mlflow.search_runs(experiment_names=[EXPERIMENT_PATH])
print(len(runs_pd) >= 3)
display(runs_pd[["tags.mlflow.runName", "params.n_features", "metrics.mae", "metrics.r2"]].head(3))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 7 ★★★ – A Classification That Works
# MAGIC
# MAGIC Build the target `is_high_price`, 1 for the properties with a base price of at least 250 (the high band from Chapter 2) and 0 for the others, with a list comprehension. Split `X_full` with this target, calculate the accuracy of the baseline model, train a logistic regression, and calculate its accuracy, the number of properties predicted in the high band, and the number of those correctly predicted in the high band. Compare the result with the one for cancellations. *Expected result:* `1894 10.4` (properties in the high band and percentage); `389 3633` in the test data; baseline accuracy `0.8929`, model accuracy `0.9557`; `288` predicted in the high band, `258` of them correct. Here the model beats the baseline, because the features contain information about the price; but the baseline accuracy, already at 89%, shows how misleading this measure is when one of the two answers is rare.

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 1894 10.4
# MAGIC 389 3633
# MAGIC ```

# COMMAND ----------

is_high_price = [1 if price >= 250 else 0 for price in y]
print(sum(is_high_price), round(sum(is_high_price) / len(is_high_price) * 100, 1))

h_X_train, h_X_test, h_y_train, h_y_test = train_test_split(
    X_full, is_high_price, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
print(sum(h_y_test), len(h_y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC 0.8929
# MAGIC 0.9557
# MAGIC 288
# MAGIC 258
# MAGIC ```

# COMMAND ----------

high_price_model = LogisticRegression()
high_price_model.fit(h_X_train, h_y_train)
h_predictions = high_price_model.predict(h_X_test)

print(round(accuracy_score(h_y_test, [0] * len(h_y_test)), 4))
print(round(accuracy_score(h_y_test, h_predictions), 4))
print(h_predictions.sum())

correct_high = 0
for prediction, actual in zip(h_predictions, h_y_test):
    if prediction == 1 and actual == 1:
        correct_high = correct_high + 1
print(correct_high)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC
# MAGIC The notebook contains three cells that produce an error and three that produce a silent error. For each one, run the cell, note the type of the error and the message (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC *Expected result:* 8a `KeyError: "['bedroom'] not in index"`; 8b `ValueError: could not convert string to float: 'Spain'`; 8c `ValueError: Expected a 2-dimensional container but got  instead...` (the warning `UserWarning: X does not have valid feature names, but LinearRegression was fitted with feature names` may appear above the message); 8d no error, but `{'mae': 0.0, 'r2': 1.0}`, a perfect model because the price itself is among the features; 8e no error, but `-0.803` instead of `0.326`, because the actual values and the predictions are swapped; 8f no error, but `{'mae': 33.24, 'r2': 0.369}`, the evaluation on the training data, better than the real one. The corrected cells return: 8a `(18163, 3)`; 8b `(18163, 18)` (the table with the bedrooms and the 17 encoded countries); 8c `[198.27 235.68]`; 8d `{'mae': 12.67, 'r2': 0.89}`; 8e `0.326`; 8f `{'mae': 33.94, 'r2': 0.326}`.

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message:
# MAGIC ```
# MAGIC KeyError: "['bedroom'] not in index"
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
X_rooms = properties_pd[["bedroom", "bathrooms", "max_guests"]]

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC (18163, 3)
# MAGIC ```

# COMMAND ----------

# Fix 8a
X_rooms = properties_pd[["bedrooms", "bathrooms", "max_guests"]]
print(X_rooms.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message:
# MAGIC ```
# MAGIC ValueError: could not convert string to float: 'Spain'
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
country_X = properties_pd[["bedrooms", "country"]]
LinearRegression().fit(country_X, y)

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC (18163, 18)
# MAGIC ```

# COMMAND ----------

# Fix 8b
country_X = pd.get_dummies(properties_pd[["bedrooms", "country"]], columns=["country"], drop_first=True, dtype=int)
country_model = LinearRegression().fit(country_X, y)
print(country_X.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC **INTENTIONAL ERROR**: the following cell must fail; the *Fix* cell below must work.
# MAGIC Expected result – message (summary line; the warning `UserWarning: X does not have valid feature names, but LinearRegression was fitted with feature names` may appear above it; under the cell the text `<class 'pandas.core.series.Series'>` doesn't appear):
# MAGIC ```
# MAGIC ValueError: Expected a 2-dimensional container but got  instead. Pass a DataFrame containing a single row (i.e. single sample) or a single column (i.e. single feature) instead.
# MAGIC ```

# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
rooms_model = LinearRegression().fit(properties_pd[["bedrooms"]], y)
new_rooms = pd.DataFrame({"bedrooms": [2, 3]})
rooms_model.predict(new_rooms["bedrooms"])

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC [198.27 235.68]
# MAGIC ```

# COMMAND ----------

# Fix 8c
print(rooms_model.predict(new_rooms[["bedrooms"]]).round(2))

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the following cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC {'mae': 0.0, 'r2': 1.0}
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – cell 8d
target_X = X_full.copy()
target_X["base_price"] = y
t_X_train, t_X_test, t_y_train, t_y_test = train_test_split(
    target_X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
target_model = LinearRegression().fit(t_X_train, t_y_train)
print(evaluate_regression(target_model, t_X_test, t_y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC {'mae': 12.67, 'r2': 0.89}
# MAGIC ```

# COMMAND ----------

# Fix 8d
f_X_train, f_X_test, f_y_train, f_y_test = train_test_split(
    X_full, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
full_model = LinearRegression().fit(f_X_train, f_y_train)
print(evaluate_regression(full_model, f_X_test, f_y_test))

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the following cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC -0.803
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – cell 8e
X_train, X_test, y_train, y_test = train_test_split(
    properties_pd[["bedrooms"]], y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
rooms_model = LinearRegression().fit(X_train, y_train)
rooms_predictions = rooms_model.predict(X_test)
print(round(r2_score(rooms_predictions, y_test), 3))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC 0.326
# MAGIC ```

# COMMAND ----------

# Fix 8e
print(round(r2_score(y_test, rooms_predictions), 3))

# COMMAND ----------

# MAGIC %md
# MAGIC **SILENT ERROR**: the following cell works but gives a wrong result; the *Fix* cell below gives the right one.
# MAGIC Expected result – output:
# MAGIC ```
# MAGIC {'mae': 33.24, 'r2': 0.369}
# MAGIC ```

# COMMAND ----------

# SILENT ERROR – cell 8f
print(evaluate_regression(rooms_model, X_train, y_train))

# COMMAND ----------

# MAGIC %md
# MAGIC Expected result of the fix – output:
# MAGIC ```
# MAGIC {'mae': 33.94, 'r2': 0.326}
# MAGIC ```

# COMMAND ----------

# Fix 8f
print(evaluate_regression(rooms_model, X_test, y_test))
