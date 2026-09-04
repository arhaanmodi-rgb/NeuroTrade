import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FOLDER = "data/raw"


STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK"
]


# ============================================================
# VALIDATE ONE STOCK
# ============================================================

def validate_stock(symbol):

    filename = os.path.join(
        DATA_FOLDER,
        f"{symbol}.csv"
    )


    print()
    print("=" * 60)
    print(f"VALIDATING {symbol}")
    print("=" * 60)


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not os.path.exists(filename):

        print("ERROR: File does not exist.")

        return False


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = pd.read_csv(
        filename
    )


    print(
        "Rows:",
        len(df)
    )


    print(
        "Columns:",
        list(df.columns)
    )


    # --------------------------------------------------------
    # CHECK EMPTY DATA
    # --------------------------------------------------------

    if len(df) == 0:

        print(
            "ERROR: Dataset is empty."
        )

        return False


    # --------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [

        "trade_date",
        "open",
        "high",
        "low",
        "close"

    ]


    missing = [

        column

        for column in required_columns

        if column not in df.columns

    ]


    if missing:

        print(
            "ERROR: Missing columns:",
            missing
        )

        return False


    # --------------------------------------------------------
    # DATE CONVERSION
    # --------------------------------------------------------

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce"
    )


    invalid_dates = df[
        "trade_date"
    ].isna().sum()


    print(
        "Invalid dates:",
        invalid_dates
    )


    # --------------------------------------------------------
    # CHECK NULL VALUES
    # --------------------------------------------------------

    print()
    print("Missing values:")


    print(
        df[
            required_columns
        ].isna().sum()
    )


    # --------------------------------------------------------
    # CHECK DUPLICATES
    # --------------------------------------------------------

    duplicates = df[
        "trade_date"
    ].duplicated().sum()


    print()
    print(
        "Duplicate dates:",
        duplicates
    )


    # --------------------------------------------------------
    # CHECK PRICE VALUES
    # --------------------------------------------------------

    price_columns = [

        "open",
        "high",
        "low",
        "close"

    ]


    for column in price_columns:

        if column in df.columns:

            negative = (
                df[column] <= 0
            ).sum()


            print(
                f"{column} <= 0:",
                negative
            )


    # --------------------------------------------------------
    # HIGH / LOW LOGIC
    # --------------------------------------------------------

    bad_high_low = (

        (df["high"] < df["low"])

    ).sum()


    print()
    print(
        "High < Low:",
        bad_high_low
    )


    # --------------------------------------------------------
    # DATE RANGE
    # --------------------------------------------------------

    valid_dates = df[
        "trade_date"
    ].dropna()


    if len(valid_dates) > 0:

        print()

        print(
            "First date:",
            valid_dates.min()
        )

        print(
            "Last date:",
            valid_dates.max()
        )


    # --------------------------------------------------------
    # PRICE RANGE
    # --------------------------------------------------------

    print()

    print(
        "Minimum close:",
        df["close"].min()
    )


    print(
        "Maximum close:",
        df["close"].max()
    )


    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    problems = (

        invalid_dates

        + duplicates

        + bad_high_low

    )


    if problems == 0:

        print()

        print(
            "STATUS: DATA LOOKS GOOD"
        )

        return True


    else:

        print()

        print(
            "STATUS: CHECK DATA"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)

    print(
        "       NEUROTRADE DATA VALIDATOR"
    )

    print("=" * 60)


    successful = 0


    for stock in STOCKS:

        if validate_stock(stock):

            successful += 1


    print()
    print("=" * 60)

    print(
        f"VALIDATION RESULT: "
        f"{successful}/{len(STOCKS)} stocks passed"
    )

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()