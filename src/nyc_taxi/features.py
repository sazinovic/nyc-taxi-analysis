import pandas as pd

from nyc_taxi.cleaning import finite


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=False)

    result["pickup_hour"] = result["tpep_pickup_datetime"].dt.hour
    result["pickup_day_of_week"] = result["tpep_pickup_datetime"].dt.dayofweek
    result["pickup_day_name"] = result["tpep_pickup_datetime"].dt.day_name()
    result["is_weekend"] = (result["pickup_day_of_week"] >= 5).where(result["tpep_pickup_datetime"].notna()).astype("boolean")
    result["pickup_year"] = result["tpep_pickup_datetime"].dt.year
    result["pickup_month"] = result["tpep_pickup_datetime"].dt.month

    return result

def add_trip_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=False)

    result["trip_duration_min"] = (
        result["tpep_dropoff_datetime"]
        - result["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    valid_speed = (
        (finite(result["trip_duration_min"]) & (result["trip_duration_min"] > 0))
        & (finite(result["trip_distance"]) & (result["trip_distance"] > 0))
    )

    result["speed_mph"] = (
        result["trip_distance"]
        / (result["trip_duration_min"] / 60)
    ).where(valid_speed)

    return result

def add_monetary_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=False)

    result["pre_tip_amount"] = (
        result["total_amount"] - result["tip_amount"]
    )

    valid_tip_rate = (
        (result["payment_type"] == 1)
        & (result["pre_tip_amount"] > 0)
        & (result["tip_amount"] >= 0)
        & finite(result["tip_amount"])
        & finite(result["total_amount"])
    )

    result["effective_tip_rate"] = (
        result["tip_amount"]
        / result["pre_tip_amount"]
        * 100
    ).where(valid_tip_rate)

    return result

def add_core_features(df: pd.DataFrame) -> pd.DataFrame:
    result = add_time_features(df)
    result = add_trip_features(result)
    result = add_monetary_features(result)

    return result

def add_zone_lookup(
    df: pd.DataFrame,
    zones: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy(deep=False)

    for column in ["PULocationID", "DOLocationID"]:
        if not pd.api.types.is_numeric_dtype(result[column]):
            result[column] = pd.to_numeric(result[column], errors="raise")

    pickup_zones = zones.rename(
        columns={
            "LocationID": "PULocationID",
            "Borough": "PU_Borough",
            "Zone": "PU_Zone",
            "service_zone": "PU_service_zone",
        }
    )

    dropoff_zones = zones.rename(
        columns={
            "LocationID": "DOLocationID",
            "Borough": "DO_Borough",
            "Zone": "DO_Zone",
            "service_zone": "DO_service_zone",
        }
    )

    result = result.merge(
        pickup_zones[
            [
                "PULocationID",
                "PU_Borough",
                "PU_Zone",
                "PU_service_zone",
            ]
        ],
        on="PULocationID",
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        dropoff_zones[
            [
                "DOLocationID",
                "DO_Borough",
                "DO_Zone",
                "DO_service_zone",
            ]
        ],
        on="DOLocationID",
        how="left",
        validate="many_to_one",
    )

    result["pickup_zone_known"] = result["PU_Zone"].notna() & ~result["PULocationID"].isin([264, 265])
    result["dropoff_zone_known"] = result["DO_Zone"].notna() & ~result["DOLocationID"].isin([264, 265])
    return result

def add_location_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=False)

    # Direct callers may omit lookup flags; standard TLC IDs are 1..263.
    for prefix, column in [("pickup", "PULocationID"), ("dropoff", "DOLocationID")]:
        flag = f"{prefix}_zone_known"
        if flag not in result:
            result[flag] = result[column].isin(range(1, 264))
    result["same_zone"] = (result["PULocationID"] == result["DOLocationID"]).where(
        result["pickup_zone_known"] & result["dropoff_zone_known"]
    ).astype("boolean")

    valid_borough = (
        result["PU_Borough"].notna()
        & result["DO_Borough"].notna()
        & (result["PU_Borough"] != "Unknown")
        & (result["DO_Borough"] != "Unknown")
    )

    result["same_borough"] = (
        (result["PU_Borough"] == result["DO_Borough"])
        .where(valid_borough)
        .astype("boolean")
    )

    airport_map = {
        1: "EWR",
        132: "JFK",
        138: "LGA",
    }

    airport_zone_ids = list(airport_map)

    result["airport_pickup"] = (
        result["PULocationID"].isin(airport_zone_ids).where(result["pickup_zone_known"]).astype("boolean")
    )

    result["airport_dropoff"] = (
        result["DOLocationID"].isin(airport_zone_ids).where(result["dropoff_zone_known"]).astype("boolean")
    )

    result["pickup_airport"] = (
        result["PULocationID"]
        .map(airport_map)
        .fillna("None")
        .where(result["pickup_zone_known"])
    )

    result["dropoff_airport"] = (
        result["DOLocationID"]
        .map(airport_map)
        .fillna("None")
        .where(result["dropoff_zone_known"])
    )

    return result