from pathlib import Path
import csv
import json


DATA_DIR = Path("data/sample")

# These starter values mirror config/settings.yml.
# settings.yml is a human-readable configuration contract in the CORE.
# Parsing YAML is optional and is not required by the 18-hour lab sequence.
LOOKBACK_LABEL = "1 month"
INTERVAL_LABEL = "Daily"


def load_instruments():
    with open(DATA_DIR / "instruments.json", encoding="utf-8") as file:
        return json.load(file)


def load_prices():
    with open(DATA_DIR / "prices.csv", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def filter_prices(prices, ticker):
    return [row for row in prices if row["ticker"] == ticker]

def get_first_close(prices):
    return prices[0]['close']


def get_last_close(prices):
    return prices[-1]['close']

def display_market_summary(asset, prices,show_currency=True):
    
    prices = filter_prices(prices, asset["ticker"])

    print(f"{asset['ticker']} - {asset['name']}")
    print(f"Observations : {len(prices)}")
    if show_currency:
        print(f"First price: {get_first_close(prices)} {asset['currency']}")
        print(f"Last price: {get_last_close(prices)} {asset['currency']}")
    else:
        print(f"First price: {get_first_close(prices)}")
        print(f"Last price: {get_last_close(prices)}")
    print()

def main():
    instruments = load_instruments()
    prices = load_prices()

    instrument = instruments["instrument"]
    benchmark = instruments["benchmark"]

    print("=== MarketPulse ===")
    print()
    print("Market Configuration")
    print(f"Period: {LOOKBACK_LABEL}")
    print(f"Interval: {INTERVAL_LABEL}")
    print()
    print("Instrument")
    display_market_summary(instrument, prices)
    print("Benchmark")
    display_market_summary(benchmark, prices, False)

if __name__ == "__main__":
    main()
