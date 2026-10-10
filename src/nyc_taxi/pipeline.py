from pathlib import Path

import pandas as pd

from nyc_taxi.cleaning import add_analysis_masks, add_cleaning_flags
from nyc_taxi.features import (
    add_core_features,
    add_location_features,
    add_zone_lookup,
)

def run_pipeline(
    trip_file: Path,
    zone_file: Path,
    analysis_year: int,
    analysis_month: int,
) -> pd.DataFrame:
    df = pd.read_parquet(trip_file)

    zones = pd.read_csv(zone_file)

    df = add_core_features(df)

    df = add_zone_lookup(
        df,
        zones,
    )

    df = add_location_features(df)

    df = add_cleaning_flags(
        df,
        analysis_year=analysis_year,
        analysis_month=analysis_month,
    )

    df = add_analysis_masks(df)

    return df