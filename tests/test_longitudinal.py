import pandas as pd
import pytest
from nyc_taxi.config import AnalysisConfig
from nyc_taxi.longitudinal import build_monthly_summary, save_checkpoint


def write_inputs(tmp_path, trips, zones, months=(1, 2)):
    data = tmp_path / "raw"
    zone_file = tmp_path / "zones.csv"
    zones.to_csv(zone_file, index=False)
    for month in months:
        folder = data / "2026"
        folder.mkdir(parents=True, exist_ok=True)
        rows = trips.copy()
        rows["tpep_pickup_datetime"] += pd.DateOffset(months=month - 1)
        rows["tpep_dropoff_datetime"] += pd.DateOffset(months=month - 1)
        rows.to_parquet(folder / f"yellow_tripdata_2026-{month:02d}.parquet", index=False)
    return data, zone_file, tmp_path / "summary.parquet"


def test_resume_skips_and_returns_requested_range(tmp_path, trips, zones, monkeypatch):
    data, zone_file, output = write_inputs(tmp_path, trips, zones)
    full = build_monthly_summary(data, zone_file, "2026-01", "2026-02", output)
    def must_not_run(*args, **kwargs):
        raise AssertionError("Checkpoint should skip completed inputs")
    monkeypatch.setattr("nyc_taxi.longitudinal.run_pipeline", must_not_run)
    selected = build_monthly_summary(data, zone_file, "2026-02", "2026-02", output)
    assert selected.month.tolist() == [2]
    pd.testing.assert_frame_equal(full, pd.read_parquet(output))


def test_duplicate_inputs_fail_before_writing(tmp_path, trips, zones):
    data, zone_file, output = write_inputs(tmp_path, trips, zones, (1,))
    other = data / "duplicate"
    other.mkdir()
    (other / "yellow_tripdata_2026-01.parquet").write_bytes((data / "2026/yellow_tripdata_2026-01.parquet").read_bytes())
    with pytest.raises(ValueError, match="Duplicate input"):
        build_monthly_summary(data, zone_file, output_file=output)
    assert not output.exists()


@pytest.mark.parametrize("change", ["config", "source", "zones", "legacy", "duplicate"])
def test_checkpoint_changes_are_rejected(tmp_path, trips, zones, change):
    data, zone_file, output = write_inputs(tmp_path, trips, zones, (1,))
    build_monthly_summary(data, zone_file, output_file=output)
    config = AnalysisConfig()
    if change == "config":
        config = AnalysisConfig(max_duration_min=180)
    elif change == "source":
        path = data / "2026/yellow_tripdata_2026-01.parquet"
        df = pd.read_parquet(path); df.loc[0, "total_amount"] = 25; df.to_parquet(path)
    elif change == "zones":
        zone_file.write_text(zone_file.read_text() + "162,Manhattan,Other,Yellow Zone\n")
    else:
        df = pd.read_parquet(output)
        if change == "legacy":
            df = df.drop(columns="processing_fingerprint")
        else:
            df = pd.concat([df, df], ignore_index=True)
        df.to_parquet(output)
    with pytest.raises(ValueError):
        build_monthly_summary(data, zone_file, output_file=output, config=config)
    rebuilt = build_monthly_summary(data, zone_file, output_file=output, config=config, rebuild=True)
    assert len(rebuilt) == 1


def test_atomic_save_preserves_existing_file_on_failure(tmp_path, prepared, monkeypatch):
    output = tmp_path / "summary.parquet"
    output.write_bytes(b"existing checkpoint")
    def fail(self, path, **kwargs):
        path.write_bytes(b"partial write")
        raise OSError("interrupted")
    monkeypatch.setattr(pd.DataFrame, "to_parquet", fail)
    with pytest.raises(OSError):
        save_checkpoint(prepared, output)
    assert output.read_bytes() == b"existing checkpoint"
    assert list(tmp_path.iterdir()) == [output]


def test_missing_month_fails(tmp_path, trips, zones):
    data, zone_file, _ = write_inputs(tmp_path, trips, zones, (1, 3))
    with pytest.raises(ValueError, match="Missing monthly"):
        build_monthly_summary(data, zone_file)


@pytest.mark.parametrize("start,end", [("2026-1", "2026-02"), ("2026-13", "2026-14"), ("2026-02", "2026-01")])
def test_bad_range_fails(tmp_path, start, end):
    with pytest.raises(ValueError):
        build_monthly_summary(tmp_path, tmp_path / "zones.csv", start, end)


def test_disjoint_range_does_not_corrupt_checkpoint(tmp_path, trips, zones):
    data, zone_file, output = write_inputs(tmp_path, trips, zones, (1, 3))
    build_monthly_summary(data, zone_file, '2026-01', '2026-01', output)
    original = output.read_bytes()
    with pytest.raises(ValueError, match='gaps'):
        build_monthly_summary(data, zone_file, '2026-03', '2026-03', output)
    assert output.read_bytes() == original
