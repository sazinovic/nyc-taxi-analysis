import pandas as pd

def aggregate_monthly_summary(
    df: pd.DataFrame,
    year: int,
    month: int,
) -> pd.DataFrame:
    period_mask = df["analysis_time_zone_payment"]

    duration_mask = df["analysis_duration"]
    distance_mask = df["analysis_distance"]
    speed_mask = df["analysis_speed"]
    monetary_mask = df["analysis_monetary"]

    period_df = df.loc[period_mask]

    summary = {
        "year": year,
        "month": month,
        "trip_count": int(period_mask.sum()),
        "median_duration_min": df.loc[
            duration_mask,
            "trip_duration_min",
        ].median(),
        "median_distance_mi": df.loc[
            distance_mask,
            "trip_distance",
        ].median(),
        "median_speed_mph": df.loc[
            speed_mask,
            "speed_mph",
        ].median(),
        "median_total_amount": df.loc[
            monetary_mask,
            "total_amount",
        ].median(),
        "total_amount_sum": df.loc[
            monetary_mask,
            "total_amount",
        ].sum(),
        "airport_pickup_share": (
            period_df["airport_pickup"].mean() * 100
        ),
        "credit_card_share": (
            (period_df["payment_type"] == 1).mean() * 100
        ),
    }

    return pd.DataFrame([summary])