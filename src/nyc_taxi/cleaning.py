import pandas as pd


def add_cleaning_flags(
    df: pd.DataFrame,
    analysis_year: int,
    analysis_month: int,
) -> pd.DataFrame:
    result = df.copy()

    result["valid_analysis_period"] = (
        (result["tpep_pickup_datetime"].dt.year == analysis_year)
        & (result["tpep_pickup_datetime"].dt.month == analysis_month)
    )

    result["valid_duration"] = (
        result["trip_duration_min"] > 0
    )

    result["valid_distance"] = (
        result["trip_distance"] > 0
    )

    result["valid_speed"] = (
        result["valid_duration"]
        & result["valid_distance"]
        & (result["speed_mph"] <= 60)
    )

    result["valid_fare_amount"] = (
        result["fare_amount"] >= 0
    )

    result["valid_total_amount"] = (
        result["total_amount"] >= 0
    )

    result["valid_tip_amount"] = (
        result["tip_amount"] >= 0
    )

    result["valid_monetary"] = (
        result["valid_fare_amount"]
        & result["valid_total_amount"]
        & result["valid_tip_amount"]
    )

    result["valid_passenger_count"] = pd.Series(
        pd.NA,
        index=result.index,
        dtype="boolean",
    )

    known_passenger_count = result["passenger_count"].notna()

    result.loc[
        known_passenger_count,
        "valid_passenger_count",
    ] = result.loc[
        known_passenger_count,
        "passenger_count",
    ].between(0, 6)

    result["valid_payment_type"] = (
        result["payment_type"].isin([0, 1, 2, 3, 4, 5, 6])
    )

    result["valid_ratecode"] = pd.Series(
        pd.NA,
        index=result.index,
        dtype="boolean",
    )

    known_ratecode = result["RatecodeID"].notna()

    result.loc[
        known_ratecode,
        "valid_ratecode",
    ] = result.loc[
        known_ratecode,
        "RatecodeID",
    ].isin([1, 2, 3, 4, 5, 6])

    return result


def add_analysis_masks(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["analysis_time_zone_payment"] = (
        result["valid_analysis_period"]
    )

    result["analysis_duration"] = (
        result["valid_analysis_period"]
        & (result["trip_duration_min"] > 0)
        & (result["trip_duration_min"] <= 120)
    )

    result["analysis_distance"] = (
        result["valid_analysis_period"]
        & (result["trip_distance"] > 0)
        & (result["trip_distance"] <= 60)
    )

    result["analysis_speed"] = (
        result["valid_analysis_period"]
        & result["valid_speed"]
    )

    result["analysis_monetary"] = (
        result["valid_analysis_period"]
        & result["valid_monetary"]
    )

    result["analysis_passenger"] = (
        result["valid_analysis_period"]
        & result["valid_passenger_count"].fillna(False)
    )

    result["analysis_ratecode"] = (
        result["valid_analysis_period"]
        & result["valid_ratecode"].fillna(False)
    )

    return result