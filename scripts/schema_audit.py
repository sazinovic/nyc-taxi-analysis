"""Audit required columns across every selected monthly source file."""
import argparse
from collections import defaultdict
from pathlib import Path
import pyarrow.parquet as pq
from nyc_taxi.pipeline import REQUIRED_COLUMNS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path.home() / "Data/raw/nyc-taxi/yellow")
    args = parser.parse_args()
    files = sorted(args.data_dir.glob("*/yellow_tripdata_*.parquet"))
    if not files:
        raise ValueError("No monthly Parquet files found")
    schemas = defaultdict(list)
    rows = 0
    for path in files:
        parquet = pq.ParquetFile(path)
        schema = parquet.schema_arrow
        missing = set(REQUIRED_COLUMNS) - set(schema.names)
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        schemas[tuple((column, str(schema.field(column).type)) for column in REQUIRED_COLUMNS)].append(path.name)
        rows += parquet.metadata.num_rows
    print(f"{len(files)} files; {rows:,} raw records; {len(schemas)} required-column schemas")
    for schema, names in schemas.items():
        print(names[0], "to", names[-1], f"({len(names)} files)", schema)


if __name__ == "__main__":
    main()
