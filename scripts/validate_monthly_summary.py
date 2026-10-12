"""Validate monthly coverage and metric/count consistency."""
import argparse
from pathlib import Path
import pandas as pd
from nyc_taxi.validation import validate_monthly_summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path.home() / "Data/processed/nyc-taxi/monthly_summary.parquet")
    parser.add_argument("--start", default="2015-01")
    parser.add_argument("--end", default="2026-08")
    args = parser.parse_args()
    df = pd.read_parquet(args.summary)
    validate_monthly_summary(df, args.start, args.end)
    print(f"Validated {len(df)} months, {int(df.trip_count.sum()):,} in-period records")
    print(df.filter(regex="coverage_pct$").describe().round(2))


if __name__ == "__main__":
    main()
