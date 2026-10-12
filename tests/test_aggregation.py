import pandas as pd
import pytest
from nyc_taxi.aggregation import aggregate_monthly_summary
from nyc_taxi.pipeline import prepare_trips


def test_subsets_and_signed_amounts(trips, zones):
    rows = pd.concat([trips] * 3, ignore_index=True)
    rows.loc[1, ["fare_amount", "total_amount", "tip_amount"]] = [-20, -24, -4]
    rows.loc[2, "tpep_pickup_datetime"] = pd.Timestamp("2026-02-15")
    result = aggregate_monthly_summary(prepare_trips(rows, zones, 2026, 1), 2026, 1).iloc[0]
    assert result.trip_count == 2
    assert result.monetary_valid_count == 1
    assert result.valid_monetary_total_amount_sum == 24
    assert result.finite_signed_total_amount_sum == 0
    assert result.excluded_monetary_total_amount_sum == -24
    assert result.monetary_coverage_pct == 50


def test_unknown_location_has_explicit_denominator(trips, zones):
    rows = pd.concat([trips] * 2, ignore_index=True)
    rows.loc[1, "PULocationID"] = 264
    result = aggregate_monthly_summary(prepare_trips(rows, zones, 2026, 1), 2026, 1).iloc[0]
    assert result.trip_count == 2
    assert result.pickup_zone_known_count == 1
    assert result.pickup_zone_unknown_count == 1
    assert result.airport_pickup_share == 100


def test_empty_subset_is_missing_not_zero(prepared):
    result = aggregate_monthly_summary(prepared.iloc[:0], 2026, 1).iloc[0]
    assert result.trip_count == 0
    assert pd.isna(result.valid_monetary_total_amount_sum)
    assert pd.isna(result.median_speed_mph)
    assert pd.isna(result.airport_pickup_share)


def test_payment_denominators(trips, zones):
    rows = pd.concat([trips] * 5, ignore_index=True)
    rows["payment_type"] = [1, 2, 0, 5, 99]
    result = aggregate_monthly_summary(prepare_trips(rows, zones, 2026, 1), 2026, 1).iloc[0]
    assert result.credit_card_share == 20
    assert result.nonflex_credit_card_share == 50
    assert result.payment_unclassified_count == 1
    assert result.flex_fare_count == 1


def test_monetary_outlier_is_reported_not_silently_deleted(trips, zones):
    trips.loc[0, "total_amount"] = 1000
    result = aggregate_monthly_summary(prepare_trips(trips, zones, 2026, 1), 2026, 1).iloc[0]
    assert result.monetary_outlier_count == 1
    assert result.monetary_outlier_amount_sum == 1000
    assert result.valid_monetary_total_amount_sum == 1000
