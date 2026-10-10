from pathlib import Path

from nyc_taxi.pipeline import run_pipeline


data_file = (
    Path.home()
    / "Data/raw/nyc-taxi/yellow/2026/yellow_tripdata_2026-01.parquet"
)

zone_file = (
    Path.home()
    / "Data/raw/nyc-taxi/taxi_zone_lookup.csv"
)

df = run_pipeline(
    trip_file=data_file,
    zone_file=zone_file,
    analysis_year=2026,
    analysis_month=1,
)

print(
    df[
        [
            "analysis_time_zone_payment",
            "analysis_duration",
            "analysis_distance",
            "analysis_speed",
            "analysis_monetary",
            "analysis_passenger",
            "analysis_ratecode",
        ]
    ].sum()
)