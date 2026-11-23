# Databricks notebook source
# MAGIC %md
# MAGIC # Chapter 13 – Exercises
# MAGIC
# MAGIC Exercises for Chapter 13 of *Beyond SELECT* (Introduction to Machine Learning). Work in a copy created with **Clone** (for example `L13_Exercises_done`), in the `Python_Book` folder. Prerequisites: Serverless; `L11_Final_Project` run at least once; `utils` in the same folder.
# MAGIC
# MAGIC Run the `%run ./utils` cell first, then the setup cell, then the exercises, one cell at a time. The solutions are in Appendix A and in the `L13_Solutions` notebook.

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

# Write your solution here


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

# Write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 3 ★ – The Median as a Baseline
# MAGIC
# MAGIC With the chapter's split (20% for the test set), calculate the mean and the **median** (the `median()` method of a Series) of the training prices, and the MAE of the two baseline models that give all the properties one or the other. Which of the two makes smaller errors? *Expected result:* `181.53 171.71`; MAE `40.6` with the mean and `39.95` with the median. The median is lower than the mean because a few very high prices pull the mean up; for the MAE, it's the better choice.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 4 ★★ – The Bathrooms Model
# MAGIC
# MAGIC Train a linear regression with the `bathrooms` feature alone and print its intercept, its coefficient, and its evaluation on the test set. Is it better or worse than the bedrooms model? *Expected result:* intercept `139.27`, coefficient `33.57`, `{'mae': 38.36, 'r2': 0.126}`: worse than the bedrooms model (33.94 and 0.326), because almost eight properties out of ten have only one bathroom.

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 5 ★★ – The Destination Instead of the Country
# MAGIC
# MAGIC Build the feature table with the three numeric features, the property type, and the **destination** instead of the country; split it, train the model, and evaluate it. Then calculate the predictions for the three guide properties, preparing them with `pd.get_dummies` and `reindex` on the columns of the new table. *Expected result:* `(18163, 47)`; `{'mae': 10.73, 'r2': 0.925}`; predictions `287.09` (Rome), `237.65` (Amalfi), `224.43` (Sardinia). With the destination, the model tells Amalfi apart from the rest of Italy, and the prediction for the Amalfi house comes very close to the actual price (236.95).

# COMMAND ----------

# Write your solution here


# COMMAND ----------

# Write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 6 ★★ – Three Runs in MLflow
# MAGIC
# MAGIC With the `train_and_log` function, log three runs in the chapter's experiment: `bathrooms_only` (the `bathrooms` feature alone), `numeric_and_type` (the three numeric features and the property type, encoded with `pd.get_dummies`), and `numeric_type_destination` (the table from exercise 5). Open the runs in the user interface and compare them; in the notebook, read the last three runs with `mlflow.search_runs`. *Expected result:* `bathrooms_only 1 38.36 0.126`, `numeric_and_type 6 28.52 0.506`, `numeric_type_destination 47 10.73 0.925`; the check prints `True` and the grid of the three runs, most recent first.

# COMMAND ----------

# Write your solution here


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

# Write your solution here


# COMMAND ----------

# Write your solution here


# COMMAND ----------

# MAGIC %md
# MAGIC ## Exercise 8 ★★★ – Find the Errors
# MAGIC
# MAGIC The notebook contains three cells that produce an error and three that produce a silent error. For each one, run the cell, note the type of the error and the message (or the wrong result), and write the corrected version below.
# MAGIC
# MAGIC *Expected result:* 8a `KeyError: "['bedroom'] not in index"`; 8b `ValueError: could not convert string to float: 'Spain'`; 8c `ValueError: Expected a 2-dimensional container but got  instead...` (the warning `UserWarning: X does not have valid feature names, but LinearRegression was fitted with feature names` may appear above the message); 8d no error, but `{'mae': 0.0, 'r2': 1.0}`, a perfect model because the price itself is among the features; 8e no error, but `-0.803` instead of `0.326`, because the actual values and the predictions are swapped; 8f no error, but `{'mae': 33.24, 'r2': 0.369}`, the evaluation on the training data, better than the real one. The corrected cells return: 8a `(18163, 3)`; 8b `(18163, 18)` (the table with the bedrooms and the 17 encoded countries); 8c `[198.27 235.68]`; 8d `{'mae': 12.67, 'r2': 0.89}`; 8e `0.326`; 8f `{'mae': 33.94, 'r2': 0.326}`.

# COMMAND ----------

# INTENTIONAL ERROR – cell 8a
X_rooms = properties_pd[["bedroom", "bathrooms", "max_guests"]]

# COMMAND ----------

# Fix 8a


# COMMAND ----------

# INTENTIONAL ERROR – cell 8b
country_X = properties_pd[["bedrooms", "country"]]
LinearRegression().fit(country_X, y)

# COMMAND ----------

# Fix 8b


# COMMAND ----------

# INTENTIONAL ERROR – cell 8c
rooms_model = LinearRegression().fit(properties_pd[["bedrooms"]], y)
new_rooms = pd.DataFrame({"bedrooms": [2, 3]})
rooms_model.predict(new_rooms["bedrooms"])

# COMMAND ----------

# Fix 8c


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

# Fix 8d


# COMMAND ----------

# SILENT ERROR – cell 8e
X_train, X_test, y_train, y_test = train_test_split(
    properties_pd[["bedrooms"]], y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
rooms_model = LinearRegression().fit(X_train, y_train)
rooms_predictions = rooms_model.predict(X_test)
print(round(r2_score(rooms_predictions, y_test), 3))

# COMMAND ----------

# Fix 8e


# COMMAND ----------

# SILENT ERROR – cell 8f
print(evaluate_regression(rooms_model, X_train, y_train))

# COMMAND ----------

# Fix 8f

