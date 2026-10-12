import numpy as np
import pandas as pd
import pytest
from nyc_taxi.pipeline import prepare_trips
from nyc_taxi.config import AnalysisConfig


@pytest.mark.parametrize("column,value,flag", [
    ("total_amount", np.inf, "analysis_monetary"), ("fare_amount", np.inf, "analysis_monetary"),
    ("tip_amount", np.inf, "analysis_monetary"), ("tip_amount", 30, "analysis_monetary"),
    ("trip_distance", np.inf, "analysis_distance"), ("passenger_count", 1.5, "analysis_passenger"),
    ("passenger_count", -1, "analysis_passenger"),
])
def test_invalid_values_do_not_enter_analysis(trips, zones, column, value, flag):
    trips.loc[0, column] = value
    result = prepare_trips(trips, zones, 2026, 1)
    assert not result.loc[0, flag]


@pytest.mark.parametrize("zone", [264, 265, 999, None])
def test_unknown_locations_are_not_nonairports(trips, zones, zone):
    trips["PULocationID"] = zone
    trips["DOLocationID"] = zone
    result = prepare_trips(trips, zones, 2026, 1)
    assert pd.isna(result.loc[0, "same_zone"])
    assert pd.isna(result.loc[0, "airport_pickup"])
    assert pd.isna(result.loc[0, "pickup_airport"])


def test_pipeline_does_not_mutate_inputs(trips, zones):
    original = trips.copy(deep=True)
    result = prepare_trips(trips, zones, 2026, 1)
    result.loc[0, "total_amount"] = 99
    pd.testing.assert_frame_equal(trips, original)


def test_speed_window_applies_to_long_but_slow_trip(trips, zones):
    trips.loc[0, "tpep_dropoff_datetime"] = pd.Timestamp("2026-01-15 13:00:00")
    result = prepare_trips(trips, zones, 2026, 1)
    assert result.loc[0, "valid_speed"]
    assert not result.loc[0, "analysis_speed"]
    relaxed = prepare_trips(trips, zones, 2026, 1, AnalysisConfig(max_duration_min=180))
    assert relaxed.loc[0, "analysis_speed"]


def test_duplicate_lookup_fails(trips, zones):
    with pytest.raises(pd.errors.MergeError):
        prepare_trips(trips, pd.concat([zones, zones.iloc[:1]]), 2026, 1)


def test_missing_columns_fail_with_context(trips, zones):
    with pytest.raises(ValueError, match="trip_distance"):
        prepare_trips(trips.drop(columns="trip_distance"), zones, 2026, 1)


def test_missing_time_is_not_weekday(trips, zones):
    trips.loc[0, "tpep_pickup_datetime"] = pd.NaT
    result = prepare_trips(trips, zones, 2026, 1)
    assert pd.isna(result.loc[0, "is_weekend"])
    assert not result.loc[0, "analysis_time_zone_payment"]


@pytest.mark.parametrize("value", [0, -1, np.inf, np.nan])
def test_config_rejects_invalid_threshold(value):
    with pytest.raises(ValueError):
        AnalysisConfig(max_duration_min=value)
