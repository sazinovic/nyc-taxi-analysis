import pandas as pd
import pytest
from nyc_taxi.pipeline import prepare_trips


@pytest.fixture
def zones():
    return pd.DataFrame({"LocationID": [132, 161, 264, 265], "Borough": ["Queens", "Manhattan", "Unknown", "Unknown"],
                         "Zone": ["JFK Airport", "Midtown Center", None, None], "service_zone": ["Airports", "Yellow Zone", None, None]})


@pytest.fixture
def trips():
    return pd.DataFrame({"tpep_pickup_datetime": pd.to_datetime(["2026-01-15 10:00:00"]),
                         "tpep_dropoff_datetime": pd.to_datetime(["2026-01-15 10:30:00"]),
                         "trip_distance": [10.], "fare_amount": [20.], "total_amount": [24.], "tip_amount": [4.],
                         "passenger_count": [1.], "payment_type": [1], "RatecodeID": [1.],
                         "PULocationID": [132], "DOLocationID": [161]})


@pytest.fixture
def prepared(trips, zones):
    return prepare_trips(trips, zones, 2026, 1)
