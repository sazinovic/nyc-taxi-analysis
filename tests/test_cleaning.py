import pandas as pd

from nyc_taxi.cleaning import add_analysis_masks, add_cleaning_flags


def test_add_cleaning_flags():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                [
                    "2026-01-15 10:00:00",
                    "2026-02-01 10:00:00",
                ]
            ),
            "trip_duration_min": [30.0, 0.0],
            "trip_distance": [5.0, 0.0],
            "speed_mph": [10.0, pd.NA],
            "fare_amount": [20.0, -5.0],
            "total_amount": [25.0, -3.0],
            "tip_amount": [5.0, 2.0],
            "passenger_count": [2.0, pd.NA],
            "payment_type": [1, 0],
            "RatecodeID": [1.0, pd.NA],
        }
    )

    result = add_cleaning_flags(
        df,
        analysis_year=2026,
        analysis_month=1,
    )

    assert result.loc[0, "valid_analysis_period"]
    assert not result.loc[1, "valid_analysis_period"]

    assert result.loc[0, "valid_duration"]
    assert not result.loc[1, "valid_duration"]

    assert result.loc[0, "valid_distance"]
    assert not result.loc[1, "valid_distance"]

    assert result.loc[0, "valid_speed"]
    assert not result.loc[1, "valid_speed"]

    assert result.loc[0, "valid_monetary"]
    assert not result.loc[1, "valid_monetary"]

    assert result.loc[0, "valid_passenger_count"]
    assert pd.isna(result.loc[1, "valid_passenger_count"])

    assert result.loc[0, "valid_payment_type"]
    assert result.loc[1, "valid_payment_type"]

    assert result.loc[0, "valid_ratecode"]
    assert pd.isna(result.loc[1, "valid_ratecode"])


def test_invalid_passenger_count():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-15 10:00:00"]
            ),
            "trip_duration_min": [10.0],
            "trip_distance": [2.0],
            "speed_mph": [12.0],
            "fare_amount": [10.0],
            "total_amount": [12.0],
            "tip_amount": [2.0],
            "passenger_count": [9.0],
            "payment_type": [1],
            "RatecodeID": [1.0],
        }
    )

    result = add_cleaning_flags(
        df,
        analysis_year=2026,
        analysis_month=1,
    )

    assert not result.loc[0, "valid_passenger_count"]


def test_invalid_ratecode():
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-15 10:00:00"]
            ),
            "trip_duration_min": [10.0],
            "trip_distance": [2.0],
            "speed_mph": [12.0],
            "fare_amount": [10.0],
            "total_amount": [12.0],
            "tip_amount": [2.0],
            "passenger_count": [1.0],
            "payment_type": [1],
            "RatecodeID": [99.0],
        }
    )

    result = add_cleaning_flags(
        df,
        analysis_year=2026,
        analysis_month=1,
    )

    assert pd.isna(result.loc[0, "valid_ratecode"])


def test_add_analysis_masks():
    df = pd.DataFrame(
        {
            "valid_analysis_period": [True, True, True],
            "trip_duration_min": [30.0, 150.0, 20.0],
            "trip_distance": [5.0, 10.0, 70.0],
            "valid_speed": [True, False, True],
            "valid_monetary": [True, True, False],
            "valid_passenger_count": pd.Series(
                [True, False, pd.NA],
                dtype="boolean",
            ),
            "valid_ratecode": pd.Series(
                [True, False, pd.NA],
                dtype="boolean",
            ),
        }
    )

    result = add_analysis_masks(df)

    assert result["analysis_duration"].tolist() == [
        True,
        False,
        True,
    ]

    assert result["analysis_distance"].tolist() == [
        True,
        True,
        False,
    ]

    assert result["analysis_speed"].tolist() == [
        True,
        False,
        False,
    ]

    assert result["analysis_monetary"].tolist() == [
        True,
        True,
        False,
    ]

    assert result["analysis_passenger"].tolist() == [
        True,
        False,
        False,
    ]

    assert result["analysis_ratecode"].tolist() == [
        True,
        False,
        False,
    ]