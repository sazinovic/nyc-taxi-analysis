import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["pickup_hour"] = result["tpep_pickup_datetime"].dt.hour
    result["pickup_day_of_week"] = result["tpep_pickup_datetime"].dt.dayofweek
    result["pickup_day_name"] = result["tpep_pickup_datetime"].dt.day_name()
    result["is_weekend"] = result["pickup_day_of_week"] >= 5
    result["pickup_year"] = result["tpep_pickup_datetime"].dt.year
    result["pickup_month"] = result["tpep_pickup_datetime"].dt.month

    return result

def add_trip_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["trip_duration_min"] = (
        result["tpep_dropoff_datetime"]
        - result["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    valid_speed = (
        (result["trip_duration_min"] > 0)
        & (result["trip_distance"] > 0)
    )

    result["speed_mph"] = (
        result["trip_distance"]
        / (result["trip_duration_min"] / 60)
    ).where(valid_speed)

    return result

def add_monetary_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["pre_tip_amount"] = (
        result["total_amount"] - result["tip_amount"]
    )

    valid_tip_rate = (
        (result["payment_type"] == 1)
        & (result["pre_tip_amount"] > 0)
        & (result["tip_amount"] >= 0)
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
    result = df.copy()

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

    return result

def add_location_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["same_zone"] = (
        result["PULocationID"] == result["DOLocationID"]
    )

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
        result["PULocationID"].isin(airport_zone_ids)
    )

    result["airport_dropoff"] = (
        result["DOLocationID"].isin(airport_zone_ids)
    )

    result["pickup_airport"] = (
        result["PULocationID"]
        .map(airport_map)
        .fillna("None")
    )

    result["dropoff_airport"] = (
        result["DOLocationID"]
        .map(airport_map)
        .fillna("None")
    )

    return result