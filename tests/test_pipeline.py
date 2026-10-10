import pandas as pd

from nyc_taxi.pipeline import run_pipeline


def test_run_pipeline(tmp_path):
    trips = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                ["2026-01-15 10:00:00"]
            ),
            "tpep_dropoff_datetime": pd.to_datetime(
                ["2026-01-15 10:30:00"]
            ),
            "trip_distance": [10.0],
            "fare_amount": [20.0],
            "total_amount": [24.0],
            "tip_amount": [4.0],
            "passenger_count": [1.0],
            "payment_type": [1],
            "RatecodeID": [1.0],
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

    trip_file = tmp_path / "trips.parquet"
    zone_file = tmp_path / "zones.csv"

    trips.to_parquet(trip_file)
    zones.to_csv(zone_file, index=False)

    result = run_pipeline(
        trip_file=trip_file,
        zone_file=zone_file,
        analysis_year=2026,
        analysis_month=1,
    )

    assert len(result) == 1

    assert result.loc[0, "pickup_hour"] == 10
    assert result.loc[0, "trip_duration_min"] == 30
    assert result.loc[0, "speed_mph"] == 20

    assert result.loc[0, "PU_Zone"] == "JFK Airport"
    assert result.loc[0, "DO_Zone"] == "Midtown Center"

    assert result.loc[0, "airport_pickup"]
    assert result.loc[0, "pickup_airport"] == "JFK"

    assert result.loc[0, "valid_analysis_period"]
    assert result.loc[0, "valid_monetary"]

    assert result.loc[0, "analysis_duration"]
    assert result.loc[0, "analysis_distance"]
    assert result.loc[0, "analysis_speed"]
    assert result.loc[0, "analysis_monetary"]