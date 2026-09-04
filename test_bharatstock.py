import os
import requests

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("BHARATSTOCK_API_KEY")

URL = "https://bharatstockapi.com/v1/stocks/RELIANCE"

headers = {
    "X-API-Key": API_KEY
}

response = requests.get(
    URL,
    headers=headers,
    timeout=10
)

print("Status:", response.status_code)

print()

print(response.json())