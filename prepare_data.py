import os
import json
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

FEATURE_FOLDER = "data/features"

OUTPUT_FOLDER = "data/processed"

STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK"
]


TRAIN_RATIO = 0.70

VALIDATION_RATIO = 0.15

TEST_RATIO = 0.15


# ============================================================
# FEATURES USED BY THE AI
# ============================================================

FEATURE_COLUMNS = [

    "return_1d",

    "return_5d",

    "return_20d",

    "sma_20",

    "sma_50",

    "sma_200",

    "price_sma20",

    "price_sma50",

    "price_sma200",

    "ema_12",

    "ema_26",

    "macd",

    "macd_signal",

    "macd_histogram",

    "rsi_14",

    "volatility_20",

    "volume_ratio",

    "daily_range",

    "close_position",

    "sma20_sma50",

    "sma50_sma200"

]


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_train_data(
    train_df,
    validation_df,
    test_df
):

    scaler = {}


    for column in FEATURE_COLUMNS:

        mean = train_df[column].mean()

        std = train_df[column].std()


        # Avoid division by zero

        if std == 0 or np.isnan(std):

            std = 1.0


        scaler[column] = {

            "mean": float(mean),

            "std": float(std)

        }


        train_df[column] = (
            train_df[column] - mean
        ) / std


        validation_df[column] = (
            validation_df[column] - mean
        ) / std


        test_df[column] = (
            test_df[column] - mean
        ) / std


    return (
        train_df,
        validation_df,
        test_df,
        scaler
    )


# ============================================================
# PROCESS ONE STOCK
# ============================================================

def process_stock(
    symbol
):

    input_file = os.path.join(
        FEATURE_FOLDER,
        f"{symbol}.csv"
    )


    print()

    print("=" * 70)

    print(
        f"PROCESSING {symbol}"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not os.path.exists(
        input_file
    ):

        print(
            "ERROR: File not found:"
        )

        print(
            input_file
        )

        return


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = pd.read_csv(
        input_file
    )


    print(
        "Total rows:",
        len(df)
    )


    # --------------------------------------------------------
    # SORT BY DATE
    # --------------------------------------------------------

    df["trade_date"] = pd.to_datetime(
        df["trade_date"]
    )


    df = df.sort_values(
        "trade_date"
    ).reset_index(
        drop=True
    )


    # --------------------------------------------------------
    # CHECK FEATURES
    # --------------------------------------------------------

    missing_columns = [

        column

        for column in FEATURE_COLUMNS

        if column not in df.columns

    ]


    if missing_columns:

        print(
            "ERROR: Missing feature columns:"
        )

        print(
            missing_columns
        )

        return


    # --------------------------------------------------------
    # REMOVE REMAINING INVALID VALUES
    # --------------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )


    df = df.dropna(
        subset=FEATURE_COLUMNS
    ).reset_index(
        drop=True
    )


    print(
        "Rows after cleaning:",
        len(df)
    )


    # --------------------------------------------------------
    # CALCULATE SPLIT POINTS
    # --------------------------------------------------------

    total_rows = len(df)


    train_end = int(
        total_rows *
        TRAIN_RATIO
    )


    validation_end = int(
        total_rows *
        (
            TRAIN_RATIO +
            VALIDATION_RATIO
        )
    )


    # --------------------------------------------------------
    # SPLIT CHRONOLOGICALLY
    # --------------------------------------------------------

    train_df = df[
        :train_end
    ].copy()


    validation_df = df[
        train_end:validation_end
    ].copy()


    test_df = df[
        validation_end:
    ].copy()


    print()

    print(
        "TRAIN rows:",
        len(train_df)
    )


    print(
        "VALIDATION rows:",
        len(validation_df)
    )


    print(
        "TEST rows:",
        len(test_df)
    )


    # --------------------------------------------------------
    # SHOW DATES
    # --------------------------------------------------------

    print()

    print(
        "TRAIN:"
    )

    print(
        train_df["trade_date"].min(),
        "→",
        train_df["trade_date"].max()
    )


    print()

    print(
        "VALIDATION:"
    )

    print(
        validation_df["trade_date"].min(),
        "→",
        validation_df["trade_date"].max()
    )


    print()

    print(
        "TEST:"
    )

    print(
        test_df["trade_date"].min(),
        "→",
        test_df["trade_date"].max()
    )


    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------
    #
    # VERY IMPORTANT:
    #
    # Mean and standard deviation are calculated
    # ONLY from TRAINING DATA.
    #
    # Validation and test data use the same
    # training statistics.
    #
    # --------------------------------------------------------

    (
        train_df,
        validation_df,
        test_df,
        scaler
    ) = normalize_train_data(
        train_df,
        validation_df,
        test_df
    )


    # --------------------------------------------------------
    # CREATE OUTPUT FOLDERS
    # --------------------------------------------------------

    stock_folder = os.path.join(
        OUTPUT_FOLDER,
        symbol
    )


    os.makedirs(
        stock_folder,
        exist_ok=True
    )


    # --------------------------------------------------------
    # SAVE TRAINING DATA
    # --------------------------------------------------------

    train_file = os.path.join(
        stock_folder,
        "train.csv"
    )


    train_df.to_csv(
        train_file,
        index=False
    )


    # --------------------------------------------------------
    # SAVE VALIDATION DATA
    # --------------------------------------------------------

    validation_file = os.path.join(
        stock_folder,
        "validation.csv"
    )


    validation_df.to_csv(
        validation_file,
        index=False
    )


    # --------------------------------------------------------
    # SAVE TEST DATA
    # --------------------------------------------------------

    test_file = os.path.join(
        stock_folder,
        "test.csv"
    )


    test_df.to_csv(
        test_file,
        index=False
    )


    # --------------------------------------------------------
    # SAVE SCALER
    # --------------------------------------------------------

    scaler_file = os.path.join(
        stock_folder,
        "scaler.json"
    )


    with open(
        scaler_file,
        "w"
    ) as file:

        json.dump(
            scaler,
            file,
            indent=4
        )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print(
        "Saved:"
    )

    print(
        train_file
    )

    print(
        validation_file
    )

    print(
        test_file
    )

    print(
        scaler_file
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print("=" * 70)

    print(
        "       NEUROTRADE DATA PREPARATION"
    )

    print("=" * 70)


    print()

    print(
        "Train ratio:",
        TRAIN_RATIO
    )


    print(
        "Validation ratio:",
        VALIDATION_RATIO
    )


    print(
        "Test ratio:",
        TEST_RATIO
    )


    for stock in STOCKS:

        process_stock(
            stock
        )


    print()

    print("=" * 70)

    print(
        "DATA PREPARATION COMPLETE"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()