"""DataFrame transformation shared by notebooks and monthly processing."""
from pathlib import Path
import pandas as pd
from nyc_taxi.cleaning import add_analysis_masks, add_cleaning_flags
from nyc_taxi.config import AnalysisConfig, DEFAULT_CONFIG
from nyc_taxi.features import add_core_features, add_location_features, add_zone_lookup

REQUIRED_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "fare_amount",
                    "total_amount", "tip_amount", "passenger_count", "payment_type", "RatecodeID",
                    "PULocationID", "DOLocationID"]


def prepare_trips(df: pd.DataFrame, zones: pd.DataFrame, analysis_year: int, analysis_month: int,
                  config: AnalysisConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required trip columns: {sorted(missing)}")
    missing_zones = {"LocationID", "Borough", "Zone", "service_zone"} - set(zones.columns)
    if missing_zones:
        raise ValueError(f"Missing zone lookup columns: {sorted(missing_zones)}")
    for column in ["tpep_pickup_datetime", "tpep_dropoff_datetime"]:
        if not pd.api.types.is_datetime64_any_dtype(df[column]):
            raise ValueError(f"{column} must have a datetime dtype")
    result = add_core_features(df)
    result = add_zone_lookup(result, zones)
    result = add_location_features(result)
    result = add_cleaning_flags(result, analysis_year, analysis_month, config)
    return add_analysis_masks(result, config)


def run_pipeline(trip_file: Path, zone_file: Path, analysis_year: int, analysis_month: int,
                 config: AnalysisConfig = DEFAULT_CONFIG, *, required_only: bool = False) -> pd.DataFrame:
    df = pd.read_parquet(trip_file, columns=REQUIRED_COLUMNS if required_only else None)
    return prepare_trips(df, pd.read_csv(zone_file), analysis_year, analysis_month, config)
