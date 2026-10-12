"""Command-line entry point for monthly processing."""
import argparse
from pathlib import Path
from nyc_taxi.longitudinal import build_monthly_summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path.home() / "Data/raw/nyc-taxi/yellow")
    parser.add_argument("--zone-file", type=Path, default=Path.home() / "Data/raw/nyc-taxi/taxi_zone_lookup.csv")
    parser.add_argument("--output", type=Path, default=Path.home() / "Data/processed/nyc-taxi/monthly_summary.parquet")
    parser.add_argument("--start", default="2015-01")
    parser.add_argument("--end", default="2026-08")
    parser.add_argument("--rebuild", action="store_true", help="Replace the checkpoint by processing the requested range afresh")
    args = parser.parse_args()
    result = build_monthly_summary(args.data_dir, args.zone_file, args.start, args.end, args.output, rebuild=args.rebuild)
    print(f"Validated {len(result)} months; {int(result.trip_count.sum()):,} in-period records; {args.output}")


if __name__ == "__main__":
    main()
