import pandas as pd


# ============================================================
# CONSTANTS
# ============================================================

GBP_TO_INR = 105.50

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):
    """
    Clean the raw scraped book dataset.
    """

    df = df.copy()

    print("\nStarting data cleaning...")

    # --------------------------------------------------------
    # 1. CLEAN PRICE
    # --------------------------------------------------------

    print("Cleaning price column...")

    # Show some raw values so we can see what was scraped
    print("\nSample raw price values:")
    print(df["price"].head())

    # Extract only the numeric price.
    #
    # Examples:
    # £51.77   -> 51.77
    # Â£51.77  -> 51.77
    # $51.77   -> 51.77
    #  51.77   -> 51.77
    #
    # This is safer than only removing the £ symbol.
    df["price_gbp"] = (
        df["price"]
        .astype(str)
        .str.extract(r"(\d+(?:\.\d+)?)", expand=False)
    )

    # Convert extracted value to numeric
    df["price_gbp"] = pd.to_numeric(
        df["price_gbp"],
        errors="coerce"
    )

    invalid_prices = df["price_gbp"].isna().sum()

    print("\nInvalid price values found:", invalid_prices)

    # --------------------------------------------------------
    # 2. CONVERT STAR RATING
    # --------------------------------------------------------

    print("Converting star ratings...")

    # Remove accidental spaces before mapping
    df["star_rating"] = (
        df["star_rating"]
        .astype(str)
        .str.strip()
    )

    df["rating"] = df["star_rating"].map(RATING_MAP)

    invalid_ratings = df["rating"].isna().sum()

    print("Invalid rating values found:", invalid_ratings)

    # --------------------------------------------------------
    # 3. CONVERT AVAILABILITY
    # --------------------------------------------------------

    print("Converting availability to boolean...")

    df["in_stock"] = (
        df["availability"]
        .astype(str)
        .str.lower()
        .str.strip()
        .str.contains("in stock", na=False)
    )

    # --------------------------------------------------------
    # 4. HANDLE INVALID PRICE VALUES
    # --------------------------------------------------------

    print("Handling missing/invalid numeric values...")

    if df["price_gbp"].isna().any():

        # Check whether at least one valid price exists
        if df["price_gbp"].notna().any():

            median_price = df["price_gbp"].median()

            print(
                f"Imputing missing price values "
                f"with median: {median_price:.2f}"
            )

            df["price_gbp"] = df["price_gbp"].fillna(
                median_price
            )

        else:

            raise ValueError(
                "All price values failed parsing. "
                "Please check the raw price column."
            )

    # --------------------------------------------------------
    # 5. HANDLE INVALID RATING VALUES
    # --------------------------------------------------------

    if df["rating"].isna().any():

        if df["rating"].notna().any():

            median_rating = df["rating"].median()

            print(
                f"Imputing missing rating values "
                f"with median: {median_rating}"
            )

            df["rating"] = df["rating"].fillna(
                median_rating
            )

        else:

            raise ValueError(
                "All rating values failed parsing."
            )

    # Convert final rating to integer
    df["rating"] = (
        df["rating"]
        .round()
        .astype(int)
    )

    # --------------------------------------------------------
    # 6. GBP TO INR
    # --------------------------------------------------------

    print(
        f"Converting GBP to INR using fixed rate: "
        f"1 GBP = {GBP_TO_INR} INR"
    )

    df["price_inr"] = (
        df["price_gbp"] * GBP_TO_INR
    ).round(2)

    # --------------------------------------------------------
    # 7. CLEAN TEXT COLUMNS
    # --------------------------------------------------------

    df["title"] = (
        df["title"]
        .astype(str)
        .str.strip()
    )

    df["category"] = (
        df["category"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 8. SELECT FINAL COLUMNS
    # --------------------------------------------------------

    cleaned_df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ].copy()

    print("Data cleaning completed.")

    return cleaned_df


# ============================================================
# VALIDATION
# ============================================================

def validate_data(df):
    """
    Validate the cleaned dataset.
    """

    print("\n========================================")
    print("VALIDATING CLEANED DATA")
    print("========================================")

    # At least 60 books
    assert len(df) >= 60, (
        f"Validation failed: only {len(df)} books found. "
        "At least 60 are required."
    )

    print(f"✓ Book count passed: {len(df)}")

    # At least 3 categories
    category_count = df["category"].nunique()

    assert category_count >= 3, (
        f"Validation failed: only {category_count} "
        "categories found."
    )

    print(
        f"✓ Category count passed: {category_count}"
    )

    # No missing GBP prices
    assert df["price_gbp"].notna().all(), (
        "Validation failed: price_gbp contains "
        "missing values."
    )

    print("✓ price_gbp has no missing values")

    # No missing INR prices
    assert df["price_inr"].notna().all(), (
        "Validation failed: price_inr contains "
        "missing values."
    )

    print("✓ price_inr has no missing values")

    # Ratings must be between 1 and 5
    assert df["rating"].between(1, 5).all(), (
        "Validation failed: ratings must be "
        "between 1 and 5."
    )

    print("✓ Ratings are between 1 and 5")

    # in_stock should be boolean
    assert pd.api.types.is_bool_dtype(
        df["in_stock"]
    ), (
        "Validation failed: in_stock must "
        "be boolean."
    )

    print("✓ in_stock is boolean")

    # No missing titles
    assert df["title"].notna().all(), (
        "Validation failed: title contains "
        "missing values."
    )

    print("✓ Titles contain no missing values")

    # No missing categories
    assert df["category"].notna().all(), (
        "Validation failed: category contains "
        "missing values."
    )

    print("✓ Categories contain no missing values")

    print("\nAll validation checks passed!")


# ============================================================
# SHOW SUMMARY
# ============================================================

def show_summary(df):
    """
    Display a summary of the cleaned dataset.
    """

    print("\n========================================")
    print("CLEANED DATASET SUMMARY")
    print("========================================")

    print("\nDataset shape:")
    print(df.shape)

    print("\nTotal books:")
    print(len(df))

    print("\nTotal categories:")
    print(df["category"].nunique())

    print("\nCategory names:")
    print(df["category"].unique())

    print("\nBooks per category:")
    print(df["category"].value_counts())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nPrice statistics:")
    print(
        df[
            [
                "price_gbp",
                "price_inr"
            ]
        ].describe()
    )

    print("\nRating distribution:")
    print(
        df["rating"]
        .value_counts()
        .sort_index()
    )

    print("\nStock distribution:")
    print(
        df["in_stock"].value_counts()
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("ZEPTO DATA PIPELINE - DATA CLEANING")
    print("========================================")

    input_file = "data_pipeline/raw_books.csv"

    output_file = "data_pipeline/cleaned_books.csv"

    # --------------------------------------------------------
    # LOAD RAW DATA
    # --------------------------------------------------------

    print(
        f"\nLoading raw data from: {input_file}"
    )

    try:

        raw_df = pd.read_csv(
            input_file
        )

    except FileNotFoundError:

        print("\nERROR:")
        print(
            "raw_books.csv was not found."
        )

        print(
            "\nRun the scraper first:"
        )

        print(
            "python data_pipeline\\scraper.py"
        )

        raise SystemExit(1)

    print(
        "Raw dataset loaded successfully."
    )

    print(
        "Raw dataset shape:",
        raw_df.shape
    )

    # --------------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------------

    cleaned_df = clean_data(
        raw_df
    )

    # --------------------------------------------------------
    # VALIDATE DATA
    # --------------------------------------------------------

    validate_data(
        cleaned_df
    )

    # --------------------------------------------------------
    # SHOW SUMMARY
    # --------------------------------------------------------

    show_summary(
        cleaned_df
    )

    # --------------------------------------------------------
    # SAVE CLEANED CSV
    # --------------------------------------------------------

    cleaned_df.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    print("\n========================================")
    print("SUCCESS")
    print("========================================")

    print(
        f"Cleaned data saved to: "
        f"{output_file}"
    )

    print(
        f"Books: {len(cleaned_df)}"
    )

    print(
        f"Categories: "
        f"{cleaned_df['category'].nunique()}"
    )

    print(
        f"GBP → INR rate used: "
        f"1 GBP = {GBP_TO_INR} INR"
    )

    print(
        "\nData pipeline cleaning stage "
        "completed successfully!"
    )