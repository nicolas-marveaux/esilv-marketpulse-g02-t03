"""Bloomberg market data provider for MarketPulse.

Two modes:
- APPROVED_SAMPLE (default): reads the instructor-approved JSON fixture
  data/sample/bloomberg_reference_sample.json. Works without a Bloomberg Terminal.
- LIVE: entry point for a real Bloomberg connection. Not implemented here;
  no live connection is ever simulated.

All functions return canonical MarketPulse observations:
date (str), ticker (str), open/high/low/close (float), volume (int).
"""

import json
from pathlib import Path

CANDIDATE_PATHS = [
    Path("data/sample/bloomberg_reference_sample.json"),
    Path("../data/sample/bloomberg_reference_sample.json"),
    Path("../../data/sample/bloomberg_reference_sample.json"),
]

BLOOMBERG_IDENTIFIERS = {
    "AAPL": "AAPL US Equity",
    "SP500": "SPX Index",
}

REQUIRED_OBSERVATION_FIELDS = {
    "observation_date",
    "open_value",
    "high_value",
    "low_value",
    "close_value",
    "volume_value",
}


def get_reference_sample_path():
    """Return the first existing path to the approved sample JSON."""
    for path in CANDIDATE_PATHS:
        if path.exists():
            return path
    return CANDIDATE_PATHS[0]


def load_bloomberg_reference_sample(path=None):
    """Load the approved sample JSON payload."""
    target_path = Path(path) if path else get_reference_sample_path()
    with open(target_path, encoding="utf-8") as file:
        return json.load(file)


def find_reference_series(payload, provider_identifier):
    """Return the series whose provider_identifier matches, else raise ValueError."""
    for series in payload.get("series", []):
        if series.get("provider_identifier") == provider_identifier:
            return series

    raise ValueError(
        f"Approved Bloomberg series not found for identifier: {provider_identifier}"
    )


def validate_reference_series(series):
    """Check a Bloomberg series before normalization.

    Raises ValueError with an explicit message if:
    - canonical_ticker is missing or empty;
    - observations is missing, not a list, or empty;
    - an observation misses one of the six required fields;
    - two observations share the same observation_date.
    """
    if not isinstance(series, dict):
        raise ValueError("Bloomberg series must be a dictionary.")

    ticker = series.get("canonical_ticker")
    if not ticker:
        raise ValueError("Bloomberg series has no canonical_ticker.")

    observations = series.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError(f"Bloomberg series {ticker} has no observations.")

    seen_dates = set()
    for index, obs in enumerate(observations):
        if not isinstance(obs, dict):
            raise ValueError(
                f"Bloomberg series {ticker}: observation #{index} is not a dictionary."
            )

        missing = REQUIRED_OBSERVATION_FIELDS - set(obs)
        if missing:
            raise ValueError(
                f"Bloomberg series {ticker}: observation #{index} "
                f"is missing field(s): {', '.join(sorted(missing))}"
            )

        date = obs["observation_date"]
        if date in seen_dates:
            raise ValueError(
                f"Bloomberg series {ticker}: duplicate observation_date {date}"
            )
        seen_dates.add(date)


def normalize_reference_series(series):
    """Validate, then convert a Bloomberg series into canonical MarketPulse rows."""
    validate_reference_series(series)

    canonical_ticker = series["canonical_ticker"]
    rows = []
    for obs in series["observations"]:
        rows.append({
            "date": obs["observation_date"],
            "ticker": canonical_ticker,
            "open": float(obs["open_value"]),
            "high": float(obs["high_value"]),
            "low": float(obs["low_value"]),
            "close": float(obs["close_value"]),
            "volume": int(obs["volume_value"]),
        })
    return rows


def fetch_approved_sample_prices(provider_identifier, sample_path=None):
    """Load, select and normalize one series in APPROVED_SAMPLE mode."""
    payload = load_bloomberg_reference_sample(sample_path)
    series = find_reference_series(payload, provider_identifier)
    return normalize_reference_series(series)


def fetch_raw_bloomberg_history(identifier, start_date=None, end_date=None):
    """Hook for a live Bloomberg Terminal connection (not implemented)."""
    raise NotImplementedError(
        "Live Bloomberg connection requires the physical trading room terminal environment."
    )


def fetch_bloomberg_prices(ticker, mode="APPROVED_SAMPLE"):
    """Main entry point: return canonical observations for a MarketPulse ticker."""
    if ticker not in BLOOMBERG_IDENTIFIERS:
        raise KeyError(f"Unknown canonical ticker for Bloomberg provider: {ticker}")

    provider_id = BLOOMBERG_IDENTIFIERS[ticker]

    if mode == "APPROVED_SAMPLE":
        return fetch_approved_sample_prices(provider_id)
    if mode == "LIVE":
        fetch_raw_bloomberg_history(provider_id)
        raise NotImplementedError("Live mode not currently active.")
    raise ValueError(f"Unrecognized Bloomberg mode: {mode}")
