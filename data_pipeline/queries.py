import sqlite3
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "zepto_books.db"

OUTPUT_DIR = BASE_DIR / "query_results"
OUTPUT_DIR.mkdir(exist_ok=True)

QUERY_FILE = BASE_DIR / "sql_queries.txt"


# ============================================================
# SQL QUERIES
# ============================================================

queries = {
    "query_1_five_star_books": """
        SELECT
            title,
            price_gbp,
            rating
        FROM books
        WHERE rating = 5;
    """,

    "query_2_expensive_books": """
        SELECT
            title,
            price_gbp
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10;
    """,

    "query_3_distinct_ratings": """
        SELECT DISTINCT
            rating
        FROM books
        ORDER BY rating;
    """,

    "query_4_price_between": """
        SELECT
            title,
            price_gbp
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp;
    """,

    "query_5_rating_in": """
        SELECT
            title,
            rating
        FROM books
        WHERE rating IN (4, 5)
        ORDER BY rating DESC;
    """,

    "query_6_join_categories": """
        SELECT
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books AS b
        INNER JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY c.category_name, b.title;
    """
}


def main():

    connection = sqlite3.connect(DB_PATH)

    try:

        # ----------------------------------------------------
        # SAVE ALL SQL QUERY STRINGS
        # ----------------------------------------------------

        with open(
            QUERY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            for query_name, query in queries.items():

                file.write(
                    f"===== {query_name} =====\n"
                )

                file.write(
                    query.strip()
                )

                file.write(
                    "\n\n"
                )

        print(
            f"SQL query strings saved to: "
            f"{QUERY_FILE}"
        )


        # ----------------------------------------------------
        # EXECUTE AND SAVE EACH QUERY RESULT
        # ----------------------------------------------------

        for query_name, query in queries.items():

            result = pd.read_sql_query(
                query,
                connection
            )

            output_path = (
                OUTPUT_DIR /
                f"{query_name}.csv"
            )

            result.to_csv(
                output_path,
                index=False
            )

            print(
                f"\n{query_name}"
            )

            print(
                "-" * 60
            )

            print(
                result.head(10)
            )

            print(
                f"Saved output: {output_path}"
            )


        print(
            "\nAll SQL queries and outputs "
            "saved successfully."
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()