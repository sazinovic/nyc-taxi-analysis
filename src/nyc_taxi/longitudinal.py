"""Sequential monthly processing with validated, atomic checkpoints."""
import hashlib
import os
from pathlib import Path
import tempfile
import pandas as pd
from nyc_taxi.aggregation import aggregate_monthly_summary
from nyc_taxi.config import AnalysisConfig, DEFAULT_CONFIG
from nyc_taxi.pipeline import run_pipeline
from nyc_taxi.validation import parse_period, summary_periods, validate_monthly_summary


def source_signature(path: Path) -> str:
    stat = path.stat()
    # Fast change detector, not a cryptographic checksum of a multi-GB file.
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def save_checkpoint(df: pd.DataFrame, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{output_file.name}.", suffix=".parquet", dir=output_file.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        df.to_parquet(temporary, index=False)
        os.replace(temporary, output_file)
    finally:
        temporary.unlink(missing_ok=True)


def build_monthly_summary(data_dir: Path, zone_file: Path, start_period: str | None = None,
                          end_period: str | None = None, output_file: Path | None = None,
                          config: AnalysisConfig = DEFAULT_CONFIG, *, rebuild: bool = False) -> pd.DataFrame:
    start = parse_period(start_period) if start_period else None
    end = parse_period(end_period) if end_period else None
    if start is not None and end is not None and start > end:
        raise ValueError("start_period must not follow end_period")
    files = {}
    for path in sorted(data_dir.glob("*/yellow_tripdata_*.parquet")):
        period = parse_period(path.stem.removeprefix("yellow_tripdata_"))
        if (start is not None and period < start) or (end is not None and period > end):
            continue
        if period in files:
            raise ValueError(f"Duplicate input month {period}: {files[period]} and {path}")
        files[period] = path
    if not files:
        raise ValueError("No monthly input files match the requested period")
    expected = pd.period_range(start if start is not None else min(files), end if end is not None else max(files), freq="M")
    missing = expected.difference(pd.PeriodIndex(list(files), freq="M"))
    if len(missing):
        raise ValueError(f"Missing monthly input files: {list(missing)}")
    zone_signature = hashlib.sha256(zone_file.read_bytes()).hexdigest()
    result = pd.DataFrame()
    processed = set()
    if output_file is not None and output_file.exists() and not rebuild:
        result = pd.read_parquet(output_file)
        validate_monthly_summary(result)
        if not result.processing_fingerprint.eq(config.fingerprint).all() or not result.zone_signature.eq(zone_signature).all():
            raise ValueError("Checkpoint rules or zone lookup changed; use rebuild=True / --rebuild")
        periods = summary_periods(result)
        identities = dict(zip(periods, result.source_signature))
        for period, path in files.items():
            if period in identities and identities[period] != source_signature(path):
                raise ValueError(f"Input changed for {period}; rebuild the checkpoint")
        processed = set(periods)
        combined = periods.union(pd.PeriodIndex(list(files), freq="M"))
        if len(pd.period_range(combined.min(), combined.max(), freq="M")) != len(combined):
            raise ValueError("Requested range would create gaps in the checkpoint; use a separate output file")
    for index, (period, path) in enumerate(sorted(files.items()), start=1):
        if period in processed:
            print(f"[{index}/{len(files)}] Skipping {period}", flush=True)
            continue
        print(f"[{index}/{len(files)}] Processing {period}", flush=True)
        signature = source_signature(path)
        df = run_pipeline(path, zone_file, period.year, period.month, config, required_only=True)
        if source_signature(path) != signature:
            raise ValueError(f"Input changed while processing {period}; checkpoint was not updated")
        summary = aggregate_monthly_summary(df, period.year, period.month)
        summary["processing_fingerprint"] = config.fingerprint
        summary["source_signature"] = signature
        summary["zone_signature"] = zone_signature
        result = summary if result.empty else pd.concat([result, summary], ignore_index=True)
        result = result.sort_values(["year", "month"]).reset_index(drop=True)
        processed.add(period)
        if output_file is not None:
            save_checkpoint(result, output_file)
        del df
    periods = summary_periods(result)
    selected = result.loc[periods.isin(expected)].reset_index(drop=True)
    validate_monthly_summary(selected, str(expected.min()), str(expected.max()))
    return selected
