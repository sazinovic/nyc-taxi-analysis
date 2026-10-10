from pathlib import Path

import pyarrow.parquet as pq


data_dir = (
    Path.home()
    / "Data/raw/nyc-taxi/yellow"
)

old_file = (
    data_dir
    / "2015/yellow_tripdata_2015-01.parquet"
)

new_file = (
    data_dir
    / "2023/yellow_tripdata_2023-02.parquet"
)

old_schema = pq.ParquetFile(old_file).schema_arrow
new_schema = pq.ParquetFile(new_file).schema_arrow

required_columns = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "RatecodeID",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "tip_amount",
    "total_amount",
]

for column in required_columns:
    old_type = old_schema.field(column).type
    new_type = new_schema.field(column).type

    if old_type != new_type:
        print(
            f"{column}: "
            f"2015-01 = {old_type}, "
            f"2023-02 = {new_type}"
        )