"""Keep source rows; distinguish validity from task-specific selection."""
import numpy as np
import pandas as pd
from nyc_taxi.config import AnalysisConfig, DEFAULT_CONFIG


def finite(values: pd.Series) -> pd.Series:
    return pd.Series(np.isfinite(values.to_numpy(dtype=float, na_value=np.nan)), index=values.index)


def add_cleaning_flags(df: pd.DataFrame, analysis_year: int, analysis_month: int,
                       config: AnalysisConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    pd.Timestamp(year=analysis_year, month=analysis_month, day=1)
    result = df.copy(deep=False)  # pandas 3 Copy-on-Write keeps the caller unchanged.
    pickup = result["tpep_pickup_datetime"]
    result["valid_analysis_period"] = ((pickup.dt.year == analysis_year) & (pickup.dt.month == analysis_month)).fillna(False)
    for name, column in [("duration", "trip_duration_min"), ("distance", "trip_distance")]:
        result[f"valid_{name}"] = (finite(result[column]) & result[column].gt(0)).fillna(False)
    result["valid_speed"] = (result["valid_duration"] & result["valid_distance"]
        & finite(result["speed_mph"]) & result["speed_mph"].gt(0)
        & result["speed_mph"].le(config.max_speed_mph)).fillna(False)
    for column in ["fare_amount", "total_amount", "tip_amount"]:
        result[f"valid_{column}"] = (finite(result[column]) & result[column].ge(0)).fillna(False)
    result["valid_monetary"] = (result["valid_fare_amount"] & result["valid_total_amount"]
        & result["valid_tip_amount"] & result["tip_amount"].le(result["total_amount"])).fillna(False)
    result["monetary_outlier"] = (finite(result["total_amount"])
        & result["total_amount"].gt(config.monetary_alert_usd)).fillna(False)
    passengers = result["passenger_count"]
    result["valid_passenger_count"] = (finite(passengers) & passengers.between(0, 6)
        & passengers.mod(1).eq(0)).where(passengers.notna()).astype("boolean")
    result["valid_payment_type"] = result["payment_type"].isin(range(7))
    rates = result["RatecodeID"]
    result["ratecode_known"] = (rates.notna() & rates.ne(99)).fillna(False)
    result["valid_ratecode"] = rates.isin(range(1, 7)).where(result["ratecode_known"]).astype("boolean")
    return result


def add_analysis_masks(df: pd.DataFrame, config: AnalysisConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    result = df.copy(deep=False)
    period = result["valid_analysis_period"].fillna(False)
    result["analysis_time_zone_payment"] = period
    result["analysis_duration"] = (period & result["trip_duration_min"].gt(0)
        & result["trip_duration_min"].le(config.max_duration_min)).fillna(False)
    result["analysis_distance"] = (period & result["trip_distance"].gt(0)
        & result["trip_distance"].le(config.max_distance_mi)).fillna(False)
    result["analysis_speed"] = (result["analysis_duration"] & result["analysis_distance"]
        & result["valid_speed"]).fillna(False)
    for name, flag in [("monetary", "valid_monetary"), ("passenger", "valid_passenger_count"),
                       ("ratecode", "valid_ratecode")]:
        result[f"analysis_{name}"] = (period & result[flag].fillna(False)).fillna(False)
    return result
