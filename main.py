import time

from market.data_engine import MarketDataEngine
from market.providers.mock_provider import MockMarketProvider


def main():

    print("=" * 60)
    print("             NEUROTRADE AI")
    print("          MARKET DATA ENGINE")
    print("=" * 60)

    engine = MarketDataEngine()

    provider = MockMarketProvider()

    print("\nStarting market data stream...\n")

    for _ in range(20):

        ticks = provider.get_ticks()

        for tick in ticks:

            engine.process_tick(tick)

            print(
                f"{tick['timestamp']} | "
                f"{tick['symbol']:10} | "
                f"₹{tick['price']:10.2f} | "
                f"Volume: {tick['volume']}"
            )

        time.sleep(1)

    print("\n" + "=" * 60)

    print("LATEST PRICES")

    print("=" * 60)

    for symbol, data in engine.latest_prices.items():

        print(
            f"{symbol:10} "
            f"₹{data['price']:10.2f}"
        )

    print("\nTotal ticks received:")

    print(len(engine.history))


if __name__ == "__main__":
    main()