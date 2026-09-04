import os
import requests
import pandas as pd

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)


API_KEY = os.getenv(
    "BHARATSTOCK_API_KEY"
)


if not API_KEY:

    print("=" * 60)
    print("ERROR: BHARATSTOCK_API_KEY NOT FOUND")
    print("=" * 60)
    print()
    print("Make sure your .env contains:")
    print()
    print("BHARATSTOCK_API_KEY=YOUR_API_KEY")
    print()

    raise SystemExit(1)


print("BharatStock API key loaded successfully.")


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://bharatstockapi.com"

DATA_FOLDER = os.path.join(
    BASE_DIR,
    "data",
    "raw"
)


# ============================================================
# DOWNLOAD STOCK HISTORY
# ============================================================

def get_stock_history(
    symbol,
    start_date,
    end_date
):

    url = (
        f"{BASE_URL}"
        f"/v1/stocks/{symbol}/prices"
    )


    headers = {
        "X-API-Key": API_KEY
    }


    all_data = []


    page = 1

    page_size = 200


    while True:

        print(
            f"  Downloading page {page}..."
        )


        params = {

            "from": start_date,

            "to": end_date,

            "page": page,

            "page_size": page_size

        }


        response = requests.get(

            url,

            headers=headers,

            params=params,

            timeout=20

        )


        # ====================================================
        # ERROR HANDLING
        # ====================================================

        if response.status_code != 200:

            print()

            print(
                f"ERROR {symbol}: "
                f"{response.status_code}"
            )

            print(
                response.text
            )

            return None


        result = response.json()


        # ====================================================
        # GET DATA
        # ====================================================

        data = result.get(
            "data",
            []
        )


        if not data:

            break


        all_data.extend(
            data
        )


        print(
            f"  Received "
            f"{len(data)} rows"
        )


        # ====================================================
        # PAGINATION
        # ====================================================

        pagination = result.get(
            "pagination",
            {}
        )


        total_pages = pagination.get(
            "total_pages"
        )


        if total_pages is not None:

            if page >= total_pages:

                break

        else:

            if len(data) < page_size:

                break


        page += 1


    # ========================================================
    # NO DATA
    # ========================================================

    if not all_data:

        print(
            f"No data returned "
            f"for {symbol}"
        )

        return None


    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        all_data
    )


    # ========================================================
    # ADD SYMBOL
    # ========================================================

    df["symbol"] = symbol


    # ========================================================
    # CONVERT DATE
    # ========================================================

    df["trade_date"] = pd.to_datetime(
        df["trade_date"]
    )


    # ========================================================
    # SORT
    # ========================================================

    df = df.sort_values(
        "trade_date"
    )


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    df = df.drop_duplicates(
        subset=[
            "trade_date"
        ]
    )


    return df


# ============================================================
# SAVE DATA
# ============================================================

def save_stock(
    df,
    symbol
):

    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )


    filename = os.path.join(
        DATA_FOLDER,
        f"{symbol}.csv"
    )


    df.to_csv(
        filename,
        index=False
    )


    print()

    print(
        f"Saved {symbol}: "
        f"{len(df)} rows"
    )

    print(
        f"File: {filename}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print("=" * 60)

    print(
        "       NEUROTRADE HISTORICAL DATA"
    )

    print("=" * 60)


    stocks = [

        "RELIANCE",

        "TCS",

        "INFY",

        "HDFCBANK",

        "ICICIBANK"

    ]


    start_date = "2020-01-01"

    end_date = "2026-08-28"


    for symbol in stocks:

        print()

        print(
            f"Downloading {symbol}..."
        )


        df = get_stock_history(

            symbol,

            start_date,

            end_date

        )


        if df is not None:

            save_stock(
                df,
                symbol
            )


    print()

    print("=" * 60)

    print(
        "DOWNLOAD COMPLETE"
    )

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()