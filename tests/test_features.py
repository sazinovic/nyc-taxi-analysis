import pandas as pd
import pytest

from nyc_taxi.features import (
    add_core_features,
    add_location_features,
    add_monetary_features,
    add_time_features,
    add_trip_features,
    add_zone_lookup,
)


def test_add_time_features():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-03 18:30:00"]
            )
        }
    )

    result = add_time_features(df)

    assert result.loc[0, "pickup_hour"] == 18
    assert result.loc[0, "pickup_day_of_week"] == 5
    assert result.loc[0, "pickup_day_name"] == "Saturday"
    assert result.loc[0, "is_weekend"]
    assert result.loc[0, "pickup_year"] == 2026
    assert result.loc[0, "pickup_month"] == 1


def test_add_trip_features():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-01 10:00:00"]
            ),
            "tpep_dropoff_datetime": pd.to_datetime(
                ["2026-01-01 10:30:00"]
            ),
            "trip_distance": [10.0],
        }
    )

    result = add_trip_features(df)

    assert result.loc[0, "trip_duration_min"] == 30
    assert result.loc[0, "speed_mph"] == pytest.approx(20.0)


def test_add_trip_features_invalid_speed():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-01 10:00:00"]
            ),
            "tpep_dropoff_datetime": pd.to_datetime(
                ["2026-01-01 10:00:00"]
            ),
            "trip_distance": [5.0],
        }
    )

    result = add_trip_features(df)

    assert result.loc[0, "trip_duration_min"] == 0
    assert pd.isna(result.loc[0, "speed_mph"])


def test_add_monetary_features():
    df = pd.DataFrame(
        {
            "total_amount": [24.0],
            "tip_amount": [4.0],
            "payment_type": [1],
        }
    )

    result = add_monetary_features(df)

    assert result.loc[0, "pre_tip_amount"] == 20
    assert result.loc[0, "effective_tip_rate"] == pytest.approx(20.0)


def test_add_monetary_features_non_card_tip_rate_is_missing():
    df = pd.DataFrame(
        {
            "total_amount": [24.0],
            "tip_amount": [4.0],
            "payment_type": [2],
        }
    )

    result = add_monetary_features(df)

    assert result.loc[0, "pre_tip_amount"] == 20
    assert pd.isna(result.loc[0, "effective_tip_rate"])


def test_add_zone_lookup():
    df = pd.DataFrame(
        {
            "PULocationID": [132],
            "DOLocationID": [161],
        }
    )

    zones = pd.DataFrame(
        {
            "LocationID": [132, 161],
            "Borough": ["Queens", "Manhattan"],
            "Zone": ["JFK Airport", "Midtown Center"],
            "service_zone": ["Airports", "Yellow Zone"],
        }
    )

    result = add_zone_lookup(df, zones)

    assert result.loc[0, "PU_Borough"] == "Queens"
    assert result.loc[0, "PU_Zone"] == "JFK Airport"
    assert result.loc[0, "DO_Borough"] == "Manhattan"
    assert result.loc[0, "DO_Zone"] == "Midtown Center"


def test_add_location_features():
    df = pd.DataFrame(
        {
            "PULocationID": [132, 161],
            "DOLocationID": [161, 161],
            "PU_Borough": ["Queens", "Manhattan"],
            "DO_Borough": ["Manhattan", "Manhattan"],
        }
    )

    result = add_location_features(df)

    assert not result.loc[0, "same_zone"]
    assert not result.loc[0, "same_borough"]
    assert result.loc[0, "airport_pickup"]
    assert not result.loc[0, "airport_dropoff"]
    assert result.loc[0, "pickup_airport"] == "JFK"
    assert result.loc[0, "dropoff_airport"] == "None"

    assert result.loc[1, "same_zone"]
    assert result.loc[1, "same_borough"]
    assert not result.loc[1, "airport_pickup"]
    assert result.loc[1, "pickup_airport"] == "None"


def test_add_location_features_unknown_borough():
    df = pd.DataFrame(
        {
            "PULocationID": [1],
            "DOLocationID": [161],
            "PU_Borough": ["Unknown"],
            "DO_Borough": ["Manhattan"],
        }
    )

    result = add_location_features(df)

    assert pd.isna(result.loc[0, "same_borough"])


def test_add_core_features():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-03 18:00:00"]
            ),
            "tpep_dropoff_datetime": pd.to_datetime(
                ["2026-01-03 18:30:00"]
            ),
            "trip_distance": [10.0],
            "total_amount": [24.0],
            "tip_amount": [4.0],
            "payment_type": [1],
        }
    )

    result = add_core_features(df)

    assert result.loc[0, "pickup_hour"] == 18
    assert result.loc[0, "trip_duration_min"] == 30
    assert result.loc[0, "speed_mph"] == pytest.approx(20.0)
    assert result.loc[0, "pre_tip_amount"] == 20
    assert result.loc[0, "effective_tip_rate"] == pytest.approx(20.0)