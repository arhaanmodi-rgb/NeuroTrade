import os
import requests

from dotenv import load_dotenv


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv(".env")


API_KEY = os.getenv(
    "BHARATSTOCK_API_KEY"
)


print("=" * 60)

print(
    "NEUROTRADE - HISTORY API TEST"
)

print("=" * 60)


print()

print(
    "API key loaded:",
    bool(API_KEY)
)


print(
    "API key length:",
    len(API_KEY)
    if API_KEY
    else 0
)


# ============================================================
# STOP IF KEY IS MISSING
# ============================================================

if not API_KEY:

    print()

    print(
        "ERROR: API key not found."
    )

    raise SystemExit(1)


# ============================================================
# API URL
# ============================================================

url = (
    "https://bharatstockapi.com"
    "/v1/stocks/RELIANCE/prices"
)


# ============================================================
# HEADERS
# ============================================================

headers = {

    "X-API-Key": API_KEY

}


# ============================================================
# PARAMETERS
# ============================================================

params = {

    "from": "2025-01-01",

    "to": "2025-03-01",

    "page": 1,

    "page_size": 10

}


# ============================================================
# SEND REQUEST
# ============================================================

print()

print(
    "Sending request..."
)


response = requests.get(

    url,

    headers=headers,

    params=params,

    timeout=20

)


# ============================================================
# RESPONSE
# ============================================================

print()

print(
    "HTTP STATUS:",
    response.status_code
)


print()


if response.status_code == 200:

    print(
        "SUCCESS!"
    )

    print()

    result = response.json()


    data = result.get(
        "data",
        []
    )


    pagination = result.get(
        "pagination",
        {}
    )


    print(
        "Rows received:",
        len(data)
    )


    print(
        "Pagination:",
        pagination
    )


    print()

    print(
        "First row:"
    )


    if data:

        print(
            data[0]
        )

    else:

        print(
            "No data returned."
        )


else:

    print(
        "REQUEST FAILED"
    )

    print()

    print(
        response.text
    )