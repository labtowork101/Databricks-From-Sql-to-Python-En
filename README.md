# Beyond SELECT – notebooks for the book

Notebooks for the book *Beyond SELECT: Learning Python with Databricks, Starting from What You Already Know*: chapter code, exercises, and solutions.
All the examples use the `samples.wanderbricks` dataset, which is already available in every
Databricks Free Edition account.

## How to get the notebooks into your workspace

1. In Databricks, open **Workspace → Users →** *your email address*.
2. Choose **Create → Git folder**.
3. In **Git repository URL**, paste the address of this repository
   (`https://github.com/labtowork101/Databricks-From-Sql-to-Python-En.git`); the provider is **GitHub**.
4. In **Git folder name**, type `Python_Book` instead of the suggested name, then confirm
   with **Create Git folder**.

You don't need GitHub credentials: the repository is public.

## Before you start

Open `L00_Prepare_Data` and run it **only once** with **Run all** (Chapter 0, section 0.7).
Run the other notebooks one cell at a time.

## Contents

| Notebook | Chapter |
|-|-|
| `L00_Prepare_Data` | Data preparation (run once) |
| `utils` | Shared notebook with imports, constants, and functions (from Chapter 10 on, loaded with `%run ./utils`) |
| `L00_Databricks_Orientation`, `L00_Exercises`, `L00_Solutions` | Chapter 0 – Finding Your Way Around Databricks |
| `L01_First_Steps_Python`, `L01_Exercises`, `L01_Solutions` | Chapter 1 – First Steps with Python |
| `L02_Operators_Conditions`, `L02_Exercises`, `L02_Solutions` | Chapter 2 – Operators and Conditions |
| `L03_Lists_Dictionaries`, `L03_Exercises`, `L03_Solutions` | Chapter 3 – Collections: Lists and Dictionaries |
| `L04_Loops`, `L04_Exercises`, `L04_Solutions` | Chapter 4 – Loops |
| `L05_Functions`, `L05_Exercises`, `L05_Solutions` | Chapter 5 – Functions |
| `L06_Errors_Debugging`, `L06_Exercises`, `L06_Solutions` | Chapter 6 – Errors and Debugging |
| `L07_Modules_Libraries`, `L07_Exercises`, `L07_Solutions` | Chapter 7 – Modules and Libraries |
| `L08_From_SQL_to_PySpark`, `L08_Exercises`, `L08_Solutions` | Chapter 8 – From SQL to PySpark |
| `L09_PySpark_Transformations`, `L09_Exercises`, `L09_Solutions` | Chapter 9 – Transformations with PySpark |
| `L10_Delta_Tables`, `L10_Exercises`, `L10_Solutions` | Chapter 10 – Reading and Writing Delta Tables |
| `L11_Final_Project`, `L11_Exercises`, `L11_Solutions` | Chapter 11 – Final Project |
| `L12_Dashboard`, `L12_Exercises`, `L12_Solutions` | Chapter 12 – From Table to Dashboard (you build the dashboard in the user interface, from **Dashboards**) |
| `L13_Machine_Learning`, `L13_Exercises`, `L13_Solutions` | Chapter 13 – Introduction to Machine Learning (logs the runs to MLflow, in the `python_book_chapter_13` experiment in your personal folder) |

To get updates, open the Git folder and use **Pull**.

## A note on the exercises

Before you work on the exercises, make a copy with a different name in the same folder
(notebook menu → **Clone**, for example `L00_Exercises_done`). Work on the copy: the original
stays intact, and a later **Pull** won't conflict with your changes. The copy must be in the same
folder because, from Chapter 10 on, the notebooks load `utils` with `%run ./utils`.

From Chapter 10 on, the notebooks write tables, and only in the `workspace.python_book` schema.
The `utils` notebook is shared by all chapters and should not be modified: write your own constants
and functions in your own notebook, after the `%run ./utils` cell.
