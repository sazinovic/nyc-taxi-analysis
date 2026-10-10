from pathlib import Path

import pandas as pd

from nyc_taxi.aggregation import aggregate_monthly_summary
from nyc_taxi.pipeline import run_pipeline


def build_monthly_summary(
    data_dir: Path,
    zone_file: Path,
    start_period: str | None = None,
    end_period: str | None = None,
    output_file: Path | None = None,
) -> pd.DataFrame:
    files = sorted(
        data_dir.glob("*/yellow_tripdata_*.parquet")
    )

    if start_period is not None:
        files = [
            file
            for file in files
            if file.stem.replace("yellow_tripdata_", "")
            >= start_period
        ]

    if end_period is not None:
        files = [
            file
            for file in files
            if file.stem.replace("yellow_tripdata_", "")
            <= end_period
        ]

    result = pd.DataFrame()
    processed_periods = set()

    if output_file is not None and output_file.exists():
        result = pd.read_parquet(output_file)

        processed_periods = {
            f"{int(year):04d}-{int(month):02d}"
            for year, month in zip(
                result["year"],
                result["month"],
            )
        }

        print(
            f"Resuming from checkpoint: "
            f"{len(processed_periods)} months already processed"
        )

    for index, trip_file in enumerate(files, start=1):
        period = trip_file.stem.replace(
            "yellow_tripdata_",
            "",
        )

        if period in processed_periods:
            print(
                f"[{index}/{len(files)}] "
                f"Skipping {period} "
                f"(already processed)"
            )
            continue

        year_text, month_text = period.split("-")

        year = int(year_text)
        month = int(month_text)

        print(
            f"[{index}/{len(files)}] "
            f"Processing {year}-{month:02d}"
        )

        df = run_pipeline(
            trip_file=trip_file,
            zone_file=zone_file,
            analysis_year=year,
            analysis_month=month,
        )

        summary = aggregate_monthly_summary(
            df,
            year=year,
            month=month,
        )

        result = pd.concat(
            [result, summary],
            ignore_index=True,
        )

        result = (
            result
            .sort_values(["year", "month"])
            .reset_index(drop=True)
        )

        if output_file is not None:
            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            result.to_parquet(
                output_file,
                index=False,
            )

            print(
                f"Saved checkpoint: {output_file}"
            )

        del df

    return result