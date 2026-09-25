# Module 1 — Data Pipeline

## Zepto Data & AI Platform

This module implements a Python-based data pipeline that scrapes book information from the Books to Scrape website, cleans and transforms the collected data, converts book prices from GBP to INR, and stores the final dataset in a normalized SQLite database.

The module also demonstrates SQL querying and data analysis using Pandas.

---

## 1. Objective

The objective of this module is to build an end-to-end data pipeline consisting of:

1. Web scraping using `requests` and `BeautifulSoup`
2. Data cleaning using Pandas
3. GBP to INR price conversion
4. Data validation
5. SQLite database creation
6. Normalized relational database design
7. SQL querying
8. SQL integration with Pandas

---

## 2. Project Structure

```text
data_pipeline/
│
├── scraper.py
├── cleaner.py
├── database.py
├── queries.py
├── raw_books.csv
├── cleaned_books.csv
├── zepto_books.db
└── README.md
```

### File Description

| File | Description |
|---|---|
| `scraper.py` | Scrapes book information from Books to Scrape |
| `cleaner.py` | Cleans, transforms, validates, and converts the scraped data |
| `database.py` | Creates the normalized SQLite database and inserts cleaned data |
| `queries.py` | Executes SQL queries against the SQLite database |
| `raw_books.csv` | Raw data collected by the web scraper |
| `cleaned_books.csv` | Cleaned and transformed book dataset |
| `zepto_books.db` | SQLite database containing categories and books |
| `README.md` | Documentation for Module 1 |

---

## 3. Technologies Used

- Python
- Pandas
- Requests
- BeautifulSoup4
- SQLite
- SQL

Python's built-in `sqlite3` module is used to communicate with the SQLite database.

---

## 4. Data Source

The dataset is collected from:

**Books to Scrape**

`https://books.toscrape.com/`

Books to Scrape is a sandbox website designed for practicing web scraping.

The scraper collects books from multiple categories and ensures that the final dataset contains at least:

- 60 books
- 3 book categories

---

## 5. Data Collected

For each book, the following raw information is collected:

| Column | Description |
|---|---|
| `title` | Book title |
| `price` | Listed book price in GBP |
| `star_rating` | Rating represented as text |
| `availability` | Stock availability text |
| `category` | Book category |

Example raw record:

```text
title: A Light in the Attic
price: £51.77
star_rating: Three
availability: In stock
category: Travel
```

---

## 6. Web Scraping

The web scraper is implemented in:

```text
scraper.py
```

The following Python libraries are used:

```python
import requests
from bs4 import BeautifulSoup
```

`requests` downloads the HTML pages from the website.

`BeautifulSoup` parses the HTML and extracts the required book information.

The scraper discovers category pages and continues scraping until the dataset contains at least three categories and at least 60 books.

The raw scraped data is stored in:

```text
raw_books.csv
```

---

## 7. Data Cleaning

Data cleaning is implemented in:

```text
cleaner.py
```

The raw data is transformed into the following final columns:

| Column | Data Type | Description |
|---|---|---|
| `title` | String | Book title |
| `price_gbp` | Float | Book price in GBP |
| `price_inr` | Float | Converted book price in INR |
| `rating` | Integer | Rating from 1 to 5 |
| `in_stock` | Boolean | Whether the book is currently in stock |
| `category` | String | Book category |

---

## 8. Price Cleaning

The raw price contains a currency symbol.

For example:

```text
£51.77
```

The cleaning process extracts the numeric portion and converts it into a floating-point value:

```text
£51.77
    ↓
51.77
```

Numeric conversion uses Pandas and invalid numeric values are converted to missing values so that unexpected parsing problems do not crash the complete pipeline.

---

## 9. Rating Conversion

The scraped star ratings are represented as text.

The following mapping is used:

| Raw Rating | Clean Rating |
|---|---:|
| One | 1 |
| Two | 2 |
| Three | 3 |
| Four | 4 |
| Five | 5 |

The final `rating` column is stored as an integer.

---

## 10. Availability Conversion

The raw availability field is converted into a Boolean value.

Example:

```text
In stock → True
```

The final `in_stock` column therefore contains Boolean values rather than availability text.

---

## 11. Handling Invalid Numeric Values

Unexpected or malformed numeric values are first converted to missing values.

For numeric parsing failures, median imputation is used when valid observations are available.

Median imputation was selected because it is less sensitive to extreme values than mean imputation and allows isolated malformed records to be handled without causing the complete pipeline to fail.

The pipeline also validates the cleaned dataset after processing.

---

## 12. GBP to INR Conversion

The project-defined fixed conversion rate is:

```text
1 GBP = 105.50 INR
```

The INR price is calculated using:

```text
price_inr = price_gbp × 105.50
```

For example:

```text
10 GBP × 105.50 = 1055.00 INR
```

A live currency API is not used because the project uses the fixed conversion rate above as its baseline.

---

## 13. Data Validation

After cleaning, the pipeline performs validation checks.

The checks include:

- Dataset contains at least 60 books
- Dataset contains at least 3 categories
- `price_gbp` contains no missing values
- `price_inr` contains no missing values
- Ratings are between 1 and 5
- `in_stock` is Boolean
- Titles are present
- Categories are present

If an important validation rule fails, the program raises an error instead of silently producing an invalid dataset.

---

## 14. SQLite Database

The cleaned dataset is stored in:

```text
zepto_books.db
```

The database is created using Python's built-in:

```python
sqlite3
```

The database uses a normalized relational design containing two tables:

```text
categories
books
```

---

## 15. Database Schema

### Categories Table

```text
categories
-------------------------
category_id     INTEGER PK
category_name   TEXT
```

`category_id` is the primary key.

### Books Table

```text
books
-------------------------
book_id         INTEGER PK
title           TEXT
price_gbp       REAL
price_inr       REAL
rating          INTEGER
in_stock        INTEGER
category_id     INTEGER FK
```

`book_id` is the primary key.

`category_id` is a foreign key referencing:

```text
categories.category_id
```

The relationship can be represented as:

```text
categories
┌────────────────────────┐
│ category_id   PK       │
│ category_name          │
└───────────┬────────────┘
            │
            │
            │ Foreign Key
            ↓
books
┌────────────────────────┐
│ book_id       PK       │
│ title                  │
│ price_gbp              │
│ price_inr              │
│ rating                 │
│ in_stock               │
│ category_id   FK       │
└────────────────────────┘
```

This design avoids unnecessarily repeating category information for every book.

---

## 16. SQL Queries

The SQL queries are implemented in:

```text
queries.py
```

The queries demonstrate the following SQL concepts:

- `SELECT`
- `WHERE`
- `ORDER BY`
- `LIMIT`
- `DISTINCT`
- `BETWEEN`
- `IN`
- `INNER JOIN`

### Query 1 — Five-Star Books

Demonstrates:

```sql
SELECT
WHERE
```

It retrieves books having a rating of 5.

### Query 2 — Most Expensive Books

Demonstrates:

```sql
ORDER BY
LIMIT
```

It retrieves the top 10 most expensive books.

### Query 3 — Distinct Ratings

Demonstrates:

```sql
DISTINCT
```

It retrieves the unique ratings available in the dataset.

### Query 4 — Price Range

Demonstrates:

```sql
BETWEEN
```

It retrieves books whose GBP price is between 20 and 40.

### Query 5 — Multiple Ratings

Demonstrates:

```sql
IN
```

It retrieves books having ratings of either 4 or 5.

### Query 6 — Books and Categories

Demonstrates:

```sql
INNER JOIN
```

The `books` and `categories` tables are joined using:

```text
books.category_id = categories.category_id
```

This produces book information together with the corresponding category name.

---

## 17. Pandas and SQL

SQL query results are loaded into Pandas DataFrames using:

```python
pd.read_sql()
```

This allows SQL database results to be analyzed using Pandas.

The relationship between the `books` and `categories` tables can also be reproduced using:

```python
pd.merge()
```

The SQL `JOIN` result and Pandas `merge` result can then be compared to verify that they represent the same relational operation.

---

## 18. Installation

Create and activate a Python virtual environment.

### Windows PowerShell

```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

The Module 1 dependencies include:

```text
requests
beautifulsoup4
pandas
```

SQLite support is available through Python's built-in `sqlite3` module and therefore does not require a separate installation.

---

## 19. How to Run Module 1

Run all commands from the root of the repository.

### Step 1 — Scrape Data

```powershell
python data_pipeline\scraper.py
```

Output:

```text
data_pipeline/raw_books.csv
```

### Step 2 — Clean Data

```powershell
python data_pipeline\cleaner.py
```

Output:

```text
data_pipeline/cleaned_books.csv
```

The cleaner also performs validation of the processed dataset.

### Step 3 — Create SQLite Database

```powershell
python data_pipeline\database.py
```

Output:

```text
data_pipeline/zepto_books.db
```

This creates and populates the `categories` and `books` tables.

### Step 4 — Execute SQL Queries

```powershell
python data_pipeline\queries.py
```

This executes and displays the required SQL query results.

---

## 20. Pipeline Architecture

The complete Module 1 pipeline is:

```text
Books to Scrape Website
          │
          ↓
      scraper.py
          │
          ↓
    raw_books.csv
          │
          ↓
      cleaner.py
          │
          ├── Price cleaning
          ├── Rating conversion
          ├── Availability conversion
          ├── Missing value handling
          ├── GBP → INR conversion
          └── Data validation
          │
          ↓
 cleaned_books.csv
          │
          ↓
     database.py
          │
          ↓
    zepto_books.db
          │
     ┌────┴─────┐
     ↓          ↓
categories    books
     │          │
     └────┬─────┘
          ↓
      queries.py
          │
          ↓
     SQL Results
```

---

## 21. Final Output

At the completion of Module 1, the project produces:

- Raw scraped book dataset
- Cleaned book dataset
- GBP and INR prices
- Integer star ratings
- Boolean stock availability
- Normalized SQLite database
- Primary key and foreign key relationship
- Multiple SQL query examples
- Pandas integration with SQLite

Module 1 therefore demonstrates an end-to-end workflow from web data collection through data cleaning, transformation, relational storage, SQL querying, and Pandas-based analysis.

### Step 5 — Pandas and SQL Integration

Run:

```powershell
python data_pipeline\pandas_sql.py