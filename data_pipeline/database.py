import sqlite3
import pandas as pd


# ============================================================
# FILE PATHS
# ============================================================

CSV_FILE = "data_pipeline/cleaned_books.csv"

DATABASE_FILE = "data_pipeline/zepto_books.db"


# ============================================================
# CREATE DATABASE CONNECTION
# ============================================================

def create_connection():
    """
    Create and return a connection to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE_FILE)

    # Enable foreign key support in SQLite
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables(connection):
    """
    Create normalized categories and books tables.
    """

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Drop old tables
    # --------------------------------------------------------
    # We drop books first because books depends on categories.

    cursor.execute("DROP TABLE IF EXISTS books")

    cursor.execute("DROP TABLE IF EXISTS categories")

    # --------------------------------------------------------
    # Create categories table
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)

    # --------------------------------------------------------
    # Create books table
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,

            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    connection.commit()

    print("Database tables created successfully.")


# ============================================================
# INSERT CATEGORIES
# ============================================================

def insert_categories(connection, df):
    """
    Insert unique categories into categories table.
    """

    unique_categories = (
        df["category"]
        .drop_duplicates()
        .sort_values()
    )

    cursor = connection.cursor()

    for category in unique_categories:

        cursor.execute(
            """
            INSERT INTO categories (category_name)
            VALUES (?)
            """,
            (category,)
        )

    connection.commit()

    print(
        f"{len(unique_categories)} categories inserted successfully."
    )


# ============================================================
# GET CATEGORY MAPPING
# ============================================================

def get_category_mapping(connection):
    """
    Get category name -> category ID mapping.
    """

    category_df = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        """,
        connection
    )

    category_mapping = dict(
        zip(
            category_df["category_name"],
            category_df["category_id"]
        )
    )

    return category_mapping


# ============================================================
# INSERT BOOKS
# ============================================================

def insert_books(connection, df):
    """
    Insert cleaned book data into books table.
    """

    category_mapping = get_category_mapping(
        connection
    )

    cursor = connection.cursor()

    for _, row in df.iterrows():

        category_id = category_mapping[
            row["category"]
        ]

        cursor.execute(
            """
            INSERT INTO books
            (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(row["in_stock"]),
                int(category_id)
            )
        )

    connection.commit()

    print(
        f"{len(df)} books inserted successfully."
    )


# ============================================================
# VALIDATE DATABASE
# ============================================================

def validate_database(connection):
    """
    Check that data was inserted correctly.
    """

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Count books
    # --------------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM books"
    )

    book_count = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Count categories
    # --------------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM categories"
    )

    category_count = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Check foreign key problems
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA foreign_key_check"
    )

    foreign_key_errors = cursor.fetchall()

    print("\n========================================")
    print("DATABASE VALIDATION")
    print("========================================")

    print(
        f"Books in database: {book_count}"
    )

    print(
        f"Categories in database: {category_count}"
    )

    print(
        f"Foreign key errors: {len(foreign_key_errors)}"
    )

    # Project requirements
    assert book_count >= 60, (
        "Database must contain at least 60 books."
    )

    assert category_count >= 3, (
        "Database must contain at least 3 categories."
    )

    assert len(foreign_key_errors) == 0, (
        "Foreign key validation failed."
    )

    print("\nAll database validation checks passed!")


# ============================================================
# DISPLAY SAMPLE DATA
# ============================================================

def display_sample_data(connection):
    """
    Display sample records using a SQL JOIN.
    """

    query = """
        SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books AS b
        INNER JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.book_id
        LIMIT 10
    """

    sample_df = pd.read_sql(
        query,
        connection
    )

    print("\n========================================")
    print("SAMPLE DATABASE RECORDS")
    print("========================================")

    print(sample_df.to_string(index=False))


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("ZEPTO DATA PIPELINE - SQLITE DATABASE")
    print("========================================")

    # --------------------------------------------------------
    # Load cleaned CSV
    # --------------------------------------------------------

    print(
        f"\nLoading cleaned data from: {CSV_FILE}"
    )

    try:

        df = pd.read_csv(
            CSV_FILE
        )

    except FileNotFoundError:

        print("\nERROR:")
        print(
            "cleaned_books.csv was not found."
        )

        print(
            "\nRun cleaner.py first:"
        )

        print(
            "python data_pipeline\\cleaner.py"
        )

        raise SystemExit(1)

    print(
        "Cleaned dataset loaded successfully."
    )

    print(
        "Dataset shape:",
        df.shape
    )

    # --------------------------------------------------------
    # Connect to database
    # --------------------------------------------------------

    connection = create_connection()

    try:

        # Create database schema
        create_tables(
            connection
        )

        # Insert categories
        insert_categories(
            connection,
            df
        )

        # Insert books
        insert_books(
            connection,
            df
        )

        # Validate database
        validate_database(
            connection
        )

        # Display sample records
        display_sample_data(
            connection
        )

    finally:

        connection.close()

        print(
            "\nDatabase connection closed."
        )

    print("\n========================================")
    print("SUCCESS")
    print("========================================")

    print(
        f"SQLite database created at: "
        f"{DATABASE_FILE}"
    )

    print(
        "\nDatabase stage completed successfully!"
    )