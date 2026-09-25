import sqlite3
import pandas as pd


# ============================================================
# DATABASE PATH
# ============================================================

DATABASE_FILE = "data_pipeline/zepto_books.db"


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("PANDAS + SQL INTEGRATION")
    print("========================================")

    # --------------------------------------------------------
    # Connect to SQLite database
    # --------------------------------------------------------

    connection = sqlite3.connect(DATABASE_FILE)

    try:

        # ====================================================
        # PART 1 - FIRST pd.read_sql QUERY
        # ====================================================

        query_1 = """
            SELECT
                book_id,
                title,
                price_gbp,
                rating
            FROM books
            WHERE rating = 5
            ORDER BY price_gbp DESC
        """

        five_star_books = pd.read_sql(
            query_1,
            connection
        )

        print("\n========================================")
        print("QUERY 1 USING pd.read_sql()")
        print("========================================")

        print(
            five_star_books.head(10).to_string(
                index=False
            )
        )

        print(
            "\nNumber of five-star books:",
            len(five_star_books)
        )

        # ====================================================
        # PART 2 - SECOND pd.read_sql QUERY
        # ====================================================

        query_2 = """
            SELECT
                book_id,
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            FROM books
            ORDER BY book_id
        """

        books_df = pd.read_sql(
            query_2,
            connection
        )

        print("\n========================================")
        print("QUERY 2 USING pd.read_sql()")
        print("========================================")

        print(
            books_df.head().to_string(
                index=False
            )
        )

        # ====================================================
        # PART 3 - READ CATEGORIES TABLE
        # ====================================================

        category_query = """
            SELECT
                category_id,
                category_name
            FROM categories
            ORDER BY category_id
        """

        categories_df = pd.read_sql(
            category_query,
            connection
        )

        print("\n========================================")
        print("CATEGORIES DATAFRAME")
        print("========================================")

        print(
            categories_df.to_string(
                index=False
            )
        )

        # ====================================================
        # PART 4 - SQL JOIN
        # ====================================================

        sql_join_query = """
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
        """

        sql_join_df = pd.read_sql(
            sql_join_query,
            connection
        )

        print("\n========================================")
        print("SQL INNER JOIN RESULT")
        print("========================================")

        print(
            sql_join_df.head(10).to_string(
                index=False
            )
        )

        # ====================================================
        # PART 5 - REPRODUCE JOIN USING pd.merge()
        # ====================================================

        pandas_merge_df = pd.merge(
            books_df,
            categories_df,
            on="category_id",
            how="inner"
        )

        # Select the same columns as the SQL JOIN
        pandas_merge_df = pandas_merge_df[
            [
                "book_id",
                "title",
                "price_gbp",
                "price_inr",
                "rating",
                "in_stock",
                "category_name"
            ]
        ]

        # Sort so both outputs are in the same order
        pandas_merge_df = (
            pandas_merge_df
            .sort_values("book_id")
            .reset_index(drop=True)
        )

        sql_join_df = (
            sql_join_df
            .sort_values("book_id")
            .reset_index(drop=True)
        )

        print("\n========================================")
        print("PANDAS pd.merge() RESULT")
        print("========================================")

        print(
            pandas_merge_df.head(10).to_string(
                index=False
            )
        )

        # ====================================================
        # PART 6 - COMPARE SQL JOIN AND PANDAS MERGE
        # ====================================================

        print("\n========================================")
        print("JOIN EQUIVALENCE CHECK")
        print("========================================")

        # SQLite may return in_stock as integer 0/1.
        # Ensure both DataFrames have matching data types.
        sql_join_df["in_stock"] = (
            sql_join_df["in_stock"].astype(int)
        )

        pandas_merge_df["in_stock"] = (
            pandas_merge_df["in_stock"].astype(int)
        )

        # Compare both DataFrames
        are_equal = sql_join_df.equals(
            pandas_merge_df
        )

        print(
            "SQL JOIN and Pandas merge are equivalent:",
            are_equal
        )

        # ----------------------------------------------------
        # Strong validation
        # ----------------------------------------------------

        assert are_equal, (
            "SQL JOIN and Pandas merge results "
            "do not match."
        )

        print(
            "\nSUCCESS: SQL JOIN and Pandas "
            "pd.merge() produced equivalent results."
        )

        # ====================================================
        # PART 7 - SAVE RESULTS
        # ====================================================

        five_star_books.to_csv(
            "data_pipeline/query_five_star_books.csv",
            index=False
        )

        sql_join_df.to_csv(
            "data_pipeline/query_sql_join.csv",
            index=False
        )

        pandas_merge_df.to_csv(
            "data_pipeline/query_pandas_merge.csv",
            index=False
        )

        print("\nQuery results saved successfully.")

    finally:

        connection.close()

        print("\nDatabase connection closed.")


    print("\n========================================")
    print("PANDAS + SQL STAGE COMPLETED")
    print("========================================")