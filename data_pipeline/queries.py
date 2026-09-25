import sqlite3
import pandas as pd


DATABASE_FILE = "data_pipeline/zepto_books.db"


def run_query(connection, query_name, query):
    """
    Execute a SQL query and display the result.
    """

    print("\n")
    print("=" * 70)
    print(query_name)
    print("=" * 70)

    print("\nSQL Query:")
    print(query)

    result = pd.read_sql(
        query,
        connection
    )

    print("\nResult:")
    print(
        result.to_string(index=False)
    )

    return result


if __name__ == "__main__":

    print("========================================")
    print("ZEPTO DATA PIPELINE - SQL QUERIES")
    print("========================================")

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    try:

        # ====================================================
        # QUERY 1
        # SELECT + WHERE
        # ====================================================

        query_1 = """
            SELECT
                title,
                price_gbp,
                rating
            FROM books
            WHERE rating = 5
        """

        result_1 = run_query(
            connection,
            "QUERY 1 - Five Star Books",
            query_1
        )

        # ====================================================
        # QUERY 2
        # ORDER BY + LIMIT
        # ====================================================

        query_2 = """
            SELECT
                title,
                price_gbp,
                price_inr
            FROM books
            ORDER BY price_gbp DESC
            LIMIT 10
        """

        result_2 = run_query(
            connection,
            "QUERY 2 - Top 10 Most Expensive Books",
            query_2
        )

        # ====================================================
        # QUERY 3
        # DISTINCT
        # ====================================================

        query_3 = """
            SELECT DISTINCT
                rating
            FROM books
            ORDER BY rating
        """

        result_3 = run_query(
            connection,
            "QUERY 3 - Distinct Ratings",
            query_3
        )

        # ====================================================
        # QUERY 4
        # BETWEEN
        # ====================================================

        query_4 = """
            SELECT
                title,
                price_gbp,
                rating
            FROM books
            WHERE price_gbp BETWEEN 20 AND 40
            ORDER BY price_gbp
        """

        result_4 = run_query(
            connection,
            "QUERY 4 - Books Between GBP 20 and GBP 40",
            query_4
        )

        # ====================================================
        # QUERY 5
        # IN
        # ====================================================

        query_5 = """
            SELECT
                title,
                rating,
                price_gbp
            FROM books
            WHERE rating IN (4, 5)
            ORDER BY rating DESC
        """

        result_5 = run_query(
            connection,
            "QUERY 5 - Books Rated Four or Five Stars",
            query_5
        )

        # ====================================================
        # QUERY 6
        # JOIN
        # ====================================================

        query_6 = """
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
            ORDER BY
                c.category_name,
                b.title
        """

        result_6 = run_query(
            connection,
            "QUERY 6 - Books With Category JOIN",
            query_6
        )

        print("\n")
        print("=" * 70)
        print("SQL QUERY REQUIREMENTS COMPLETED")
        print("=" * 70)

        print(
            """
Demonstrated:
✓ SELECT
✓ WHERE
✓ ORDER BY
✓ LIMIT
✓ DISTINCT
✓ BETWEEN
✓ IN
✓ INNER JOIN
"""
        )

    finally:

        connection.close()

        print(
            "Database connection closed."
        )