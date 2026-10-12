"""Comparable seasonal windows; aggregate counts before calculating shares."""
import pandas as pd
from nyc_taxi.validation import summary_periods


def compare_periods(df: pd.DataFrame, years=(2015, 2019, 2026), end_month: int = 8) -> pd.DataFrame:
    summary_periods(df)
    if not 1 <= end_month <= 12:
        raise ValueError("end_month must be 1..12")
    rows = []
    for year in years:
        subset = df.loc[df.year.eq(year) & df.month.le(end_month)]
        if set(subset.month) != set(range(1, end_month + 1)):
            raise ValueError(f"Incomplete January–{end_month:02d} coverage for {year}")
        row = {"year": year, "end_month": end_month, "average_monthly_trips": subset.trip_count.mean()}
        for column in ["median_duration_min", "median_distance_mi", "median_speed_mph", "median_total_amount"]:
            if subset[column].isna().any():
                raise ValueError(f"Cannot compare missing monthly values: {year}, {column}")
            row[f"average_monthly_{column}"] = subset[column].mean()
        amounts = subset.valid_monetary_total_amount_sum
        row["average_monthly_valid_monetary_total_amount_sum"] = amounts.mean() if amounts.notna().all() else float("nan")
        for metric, numerator, denominator in [
            ("airport_pickup_share", "airport_pickup_count", "pickup_zone_known_count"),
            ("credit_card_share", "credit_card_count", "trip_count"),
            ("nonflex_credit_card_share", "credit_card_count", "nonflex_payment_count"),
            ("flex_fare_share", "flex_fare_count", "trip_count"),
        ]:
            denom = subset[denominator].sum()
            row[metric] = 100 * subset[numerator].sum() / denom if denom else float("nan")
        rows.append(row)
    return pd.DataFrame(rows).set_index("year")
