"""Monthly medians, explicit denominators, and monetary diagnostics."""
import pandas as pd
from nyc_taxi.cleaning import finite


def aggregate_monthly_summary(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    period = df["analysis_time_zone_payment"].fillna(False)
    monetary = df["analysis_monetary"].fillna(False) & period
    summary = {"year": year, "month": month, "raw_record_count": len(df),
               "trip_count": int(period.sum()), "outside_period_count": int((~period).sum())}
    for name, column, metric in [
        ("duration", "trip_duration_min", "median_duration_min"),
        ("distance", "trip_distance", "median_distance_mi"),
        ("speed", "speed_mph", "median_speed_mph"),
        ("monetary", "total_amount", "median_total_amount"),
    ]:
        mask = df[f"analysis_{name}"].fillna(False) & period
        summary[f"{name}_valid_count"] = int(mask.sum())
        summary[metric] = df.loc[mask, column].median()
    for name in ["passenger", "ratecode"]:
        summary[f"{name}_valid_count"] = int((df[f"analysis_{name}"].fillna(False) & period).sum())
    total = df["total_amount"]
    finite_total = period & finite(total)
    summary.update({
        "valid_monetary_total_amount_sum": total.loc[monetary].sum(min_count=1),
        "finite_signed_total_amount_sum": total.loc[finite_total].sum(min_count=1),
        "excluded_monetary_total_amount_sum": total.loc[finite_total & ~monetary].sum(min_count=1),
        "monetary_excluded_count": int((period & ~monetary).sum()),
        "nonfinite_total_count": int((period & ~finite(total)).sum()),
        "monetary_outlier_count": int((period & df["monetary_outlier"]).sum()),
        "monetary_outlier_amount_sum": total.loc[monetary & df["monetary_outlier"]].sum(min_count=1),
        "max_valid_total_amount": total.loc[monetary].max(),
    })
    airport = df.loc[period, "airport_pickup"]
    airport_count = int(airport.fillna(False).sum())
    airport_known = int(airport.notna().sum())
    payment = df.loc[period, "payment_type"]
    card_count = int(payment.eq(1).sum())
    classified = payment.isin(range(7))
    nonflex = payment.isin(range(1, 5))  # Exclude Flex, unknown, and voided.
    summary.update({
        "airport_pickup_count": airport_count,
        "pickup_zone_known_count": airport_known,
        "pickup_zone_unknown_count": int(airport.isna().sum()),
        "airport_pickup_share": 100 * airport_count / airport_known if airport_known else float("nan"),
        "credit_card_count": card_count,
        "payment_classified_count": int(classified.sum()),
        "payment_unclassified_count": int((~classified).sum()),
        "flex_fare_count": int(payment.eq(0).sum()),
        "nonflex_payment_count": int(nonflex.sum()),
        "credit_card_share": 100 * card_count / summary["trip_count"] if summary["trip_count"] else float("nan"),
        "nonflex_credit_card_share": 100 * card_count / int(nonflex.sum()) if nonflex.any() else float("nan"),
    })
    for name in ["duration", "distance", "speed", "monetary", "passenger", "ratecode"]:
        summary[f"{name}_coverage_pct"] = (100 * summary[f"{name}_valid_count"] / summary["trip_count"]
                                            if summary["trip_count"] else float("nan"))
    return pd.DataFrame([summary])
