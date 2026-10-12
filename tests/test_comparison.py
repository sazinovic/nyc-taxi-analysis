import pandas as pd
import pytest
from nyc_taxi.comparison import compare_periods


def monthly_rows():
    return pd.DataFrame({"year": [2026, 2026], "month": [1, 2], "trip_count": [100, 900],
        "median_duration_min": [1, 100], "median_distance_mi": [1, 2], "median_speed_mph": [10, 20],
        "median_total_amount": [10, 20], "valid_monetary_total_amount_sum": [1000, 18000],
        "airport_pickup_count": [10, 450], "pickup_zone_known_count": [100, 900],
        "credit_card_count": [100, 0], "nonflex_payment_count": [100, 900], "flex_fare_count": [0, 0]})


def test_shares_use_counts_and_medians_have_explicit_names():
    row = compare_periods(monthly_rows(), years=(2026,), end_month=2).loc[2026]
    assert row.credit_card_share == 10
    assert row.airport_pickup_share == 46
    assert row.average_monthly_median_duration_min == 50.5


def test_incomplete_season_fails():
    with pytest.raises(ValueError, match="Incomplete"):
        compare_periods(monthly_rows().iloc[:1], years=(2026,), end_month=2)
