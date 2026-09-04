import os
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

RAW_FOLDER = "data/raw"
FEATURE_FOLDER = "data/features"

STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK"
]


# ============================================================
# MODEL FEATURES
# ============================================================

MODEL_FEATURES = [
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
# RSI
# ============================================================

def calculate_rsi(prices, period=14):

    delta = prices.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(period).mean()

    average_loss = loss.rolling(period).mean()

    rs = (
        average_gain /
        average_loss.replace(0, np.nan)
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df):

    df = df.copy()

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce"
    )

    df = df.sort_values(
        "trade_date"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # VALIDATE REQUIRED RAW COLUMNS
    # --------------------------------------------------------

    required_raw = [
        "trade_date",
        "close",
        "high",
        "low"
    ]

    for column in required_raw:

        if column not in df.columns:

            raise ValueError(
                f"Missing required column: {column}"
            )

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    if "adjusted_close" in df.columns:

        price = pd.to_numeric(
            df["adjusted_close"],
            errors="coerce"
        )

    else:

        price = pd.to_numeric(
            df["close"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # RETURNS
    # --------------------------------------------------------

    df["return_1d"] = price.pct_change()

    df["return_5d"] = price.pct_change(5)

    df["return_20d"] = price.pct_change(20)

    # --------------------------------------------------------
    # SMA
    # --------------------------------------------------------

    df["sma_20"] = price.rolling(20).mean()

    df["sma_50"] = price.rolling(50).mean()

    df["sma_200"] = price.rolling(200).mean()

    # --------------------------------------------------------
    # PRICE / SMA
    # --------------------------------------------------------

    df["price_sma20"] = (
        price / df["sma_20"]
    )

    df["price_sma50"] = (
        price / df["sma_50"]
    )

    df["price_sma200"] = (
        price / df["sma_200"]
    )

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------

    df["ema_12"] = price.ewm(
        span=12,
        adjust=False
    ).mean()

    df["ema_26"] = price.ewm(
        span=26,
        adjust=False
    ).mean()

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    df["macd"] = (
        df["ema_12"] -
        df["ema_26"]
    )

    df["macd_signal"] = (
        df["macd"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    df["macd_histogram"] = (
        df["macd"] -
        df["macd_signal"]
    )

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    df["rsi_14"] = calculate_rsi(
        price,
        14
    )

    # --------------------------------------------------------
    # VOLATILITY
    # --------------------------------------------------------

    df["volatility_20"] = (
        df["return_1d"]
        .rolling(20)
        .std()
    )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    if "volume" in df.columns:

        volume = pd.to_numeric(
            df["volume"],
            errors="coerce"
        )

        df["volume_sma20"] = (
            volume.rolling(20).mean()
        )

        df["volume_ratio"] = (
            volume /
            df["volume_sma20"]
        )

    else:

        df["volume_sma20"] = np.nan

        df["volume_ratio"] = np.nan

    # --------------------------------------------------------
    # DAILY RANGE
    # --------------------------------------------------------

    high = pd.to_numeric(
        df["high"],
        errors="coerce"
    )

    low = pd.to_numeric(
        df["low"],
        errors="coerce"
    )

    df["daily_range"] = (
        (high - low) /
        price
    )

    # --------------------------------------------------------
    # CLOSE POSITION
    # --------------------------------------------------------

    df["close_position"] = (
        (price - low) /
        (high - low).replace(
            0,
            np.nan
        )
    )

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    df["sma20_sma50"] = (
        df["sma_20"] /
        df["sma_50"]
    )

    df["sma50_sma200"] = (
        df["sma_50"] /
        df["sma_200"]
    )

    # --------------------------------------------------------
    # FUTURE RETURN
    #
    # EVALUATION ONLY
    # NEVER USED BY DQN
    # --------------------------------------------------------

    df["future_return_1d"] = (
        price.shift(-1) /
        price -
        1
    )

    # --------------------------------------------------------
    # CLEAN INF
    # --------------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # --------------------------------------------------------
    # REQUIRED FEATURE CHECK
    # --------------------------------------------------------

    df = df.dropna(
        subset=MODEL_FEATURES
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    if len(df) < 250:

        raise ValueError(
            f"Only {len(df)} valid rows remain. "
            "At least 250 rows are recommended."
        )

    return df


# ============================================================
# PROCESS STOCK
# ============================================================

def process_stock(symbol):

    filename = os.path.join(
        RAW_FOLDER,
        f"{symbol}.csv"
    )

    print()
    print("=" * 70)
    print(f"Processing {symbol}.csv")
    print("=" * 70)

    if not os.path.exists(filename):

        print(
            "ERROR: File not found:",
            filename
        )

        return

    df = pd.read_csv(filename)

    print(
        "Original rows:",
        len(df)
    )

    print(
        "Original columns:",
        len(df.columns)
    )

    features = create_features(df)

    print(
        "Feature rows:",
        len(features)
    )

    print(
        "Total output columns:",
        len(features.columns)
    )

    print(
        "DQN input features:",
        len(MODEL_FEATURES)
    )

    os.makedirs(
        FEATURE_FOLDER,
        exist_ok=True
    )

    output_file = os.path.join(
        FEATURE_FOLDER,
        f"{symbol}.csv"
    )

    features.to_csv(
        output_file,
        index=False
    )

    print(
        "Saved:",
        output_file
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("             NEUROTRADE FEATURE ENGINE")
    print("=" * 70)

    for stock in STOCKS:

        process_stock(stock)

    print()
    print("=" * 70)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()