"""Fail early on incompatible, incomplete, or internally inconsistent summaries."""
import re
import numpy as np
import pandas as pd


def parse_period(value: str) -> pd.Period:
    if not re.fullmatch(r"\d{4}-\d{2}", value):
        raise ValueError(f"Expected YYYY-MM period, received {value!r}")
    try:
        return pd.Period(value, freq="M")
    except ValueError as exc:
        raise ValueError(f"Invalid monthly period: {value}") from exc


def summary_periods(df: pd.DataFrame) -> pd.PeriodIndex:
    if df.empty:
        raise ValueError("Monthly summary is empty")
    for column in ["year", "month"]:
        if column not in df or df[column].isna().any() or not df[column].mod(1).eq(0).all():
            raise ValueError(f"Invalid or missing {column}")
    if not df["month"].between(1, 12).all():
        raise ValueError("Months must be 1..12")
    periods = pd.PeriodIndex(pd.to_datetime(dict(year=df.year, month=df.month, day=1)), freq="M")
    if periods.has_duplicates:
        raise ValueError("Duplicate year-month in summary")
    return periods


def validate_monthly_summary(df: pd.DataFrame, start_period: str | None = None,
                             end_period: str | None = None) -> None:
    periods = summary_periods(df)
    if not periods.is_monotonic_increasing:
        raise ValueError("Summary must be sorted by year and month")
    expected = pd.period_range(parse_period(start_period) if start_period else periods.min(),
                               parse_period(end_period) if end_period else periods.max(), freq="M")
    if not periods.equals(expected):
        raise ValueError(f"Unexpected monthly coverage; missing={list(expected.difference(periods))}, extra={list(periods.difference(expected))}")
    required = {"raw_record_count", "trip_count", "outside_period_count", "pickup_zone_known_count",
                "pickup_zone_unknown_count", "airport_pickup_count", "credit_card_count", "flex_fare_count",
                "nonflex_payment_count", "valid_monetary_total_amount_sum", "finite_signed_total_amount_sum",
                "excluded_monetary_total_amount_sum", "processing_fingerprint", "source_signature", "zone_signature"}
    required.update(f"{name}_valid_count" for name in ["duration", "distance", "speed", "monetary", "passenger", "ratecode"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing summary columns: {sorted(missing)}; rebuild legacy summaries")
    for column in [c for c in df if c.endswith("_count")]:
        values = df[column]
        if values.isna().any() or not np.isfinite(values).all() or not values.ge(0).all() or not values.mod(1).eq(0).all():
            raise ValueError(f"Invalid counts: {column}")
    if not (df.raw_record_count == df.trip_count + df.outside_period_count).all():
        raise ValueError("Raw/period count mismatch")
    if not (df.trip_count == df.pickup_zone_known_count + df.pickup_zone_unknown_count).all():
        raise ValueError("Pickup zone denominator mismatch")
    bounds = {"airport_pickup_count": "pickup_zone_known_count", "credit_card_count": "nonflex_payment_count"}
    for column in [c for c in df if c.endswith("_valid_count")]:
        bounds[column] = "trip_count"
    for column, denominator in bounds.items():
        if not df[column].le(df[denominator]).all():
            raise ValueError(f"Count exceeds denominator: {column}")
    for column in [c for c in df if c.endswith("_share") or c.endswith("_coverage_pct")]:
        if not df[column].dropna().between(0, 100).all():
            raise ValueError(f"Percentage outside 0..100: {column}")
    shares = {
        "airport_pickup_share": ("airport_pickup_count", "pickup_zone_known_count"),
        "credit_card_share": ("credit_card_count", "trip_count"),
        "nonflex_credit_card_share": ("credit_card_count", "nonflex_payment_count"),
    }
    for name in ["duration", "distance", "speed", "monetary", "passenger", "ratecode"]:
        shares[f"{name}_coverage_pct"] = (f"{name}_valid_count", "trip_count")
    for metric, (numerator, denominator) in shares.items():
        if metric not in df:
            raise ValueError(f"Missing summary column: {metric}")
        expected_share = 100 * df[numerator] / df[denominator].replace(0, np.nan)
        if not np.allclose(df[metric], expected_share, equal_nan=True):
            raise ValueError(f"Percentage does not match its denominator: {metric}")
    for column in ["processing_fingerprint", "source_signature", "zone_signature"]:
        if df[column].isna().any():
            raise ValueError(f"Missing checkpoint identity: {column}")
    if df.processing_fingerprint.nunique() != 1 or df.zone_signature.nunique() != 1:
        raise ValueError("Mixed processing rules or zone lookup versions")
    for metric, count in [("median_duration_min", "duration_valid_count"), ("median_distance_mi", "distance_valid_count"),
                          ("median_speed_mph", "speed_valid_count"), ("median_total_amount", "monetary_valid_count"),
                          ("valid_monetary_total_amount_sum", "monetary_valid_count")]:
        if metric not in df:
            raise ValueError(f"Missing summary column: {metric}")
        available = df[count].gt(0)
        if not np.isfinite(df.loc[available, metric]).all() or df.loc[~available, metric].notna().any():
            raise ValueError(f"Metric availability does not match count: {metric}")
    reconciled = df.valid_monetary_total_amount_sum.fillna(0) + df.excluded_monetary_total_amount_sum.fillna(0)
    if not np.allclose(reconciled, df.finite_signed_total_amount_sum.fillna(0), atol=0.01, rtol=1e-12):
        raise ValueError("Monetary sums do not reconcile")
