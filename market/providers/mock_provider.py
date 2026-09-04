# Mock market data provider
import random
import time
from datetime import datetime


class MockMarketProvider:

    def __init__(self):

        self.prices = {
            "RELIANCE": 1450.00,
            "TCS": 3200.00,
            "INFY": 1580.00,
            "HDFCBANK": 1700.00,
            "ICICIBANK": 1200.00
        }

    def get_ticks(self):

        ticks = []

        for symbol in self.prices:

            change = random.uniform(-2, 2)

            self.prices[symbol] += change

            tick = {
                "symbol": symbol,
                "price": round(
                    self.prices[symbol],
                    2
                ),
                "volume": random.randint(
                    1000,
                    10000
                ),
                "timestamp":
                    datetime.now().isoformat()
            }

            ticks.append(tick)

        return ticks