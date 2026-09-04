# Market data engine
import pandas as pd
from datetime import datetime


class MarketDataEngine:

    def __init__(self):

        self.latest_prices = {}

        self.history = []

    def process_tick(self, tick):

        symbol = tick["symbol"]

        price = float(tick["price"])

        volume = int(tick.get("volume", 0))

        timestamp = tick.get(
            "timestamp",
            datetime.now().isoformat()
        )

        self.latest_prices[symbol] = {
            "price": price,
            "volume": volume,
            "timestamp": timestamp
        }

        self.history.append({
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "timestamp": timestamp
        })

    def get_latest_price(self, symbol):

        if symbol not in self.latest_prices:
            return None

        return self.latest_prices[symbol]

    def get_history(self):

        return pd.DataFrame(self.history)