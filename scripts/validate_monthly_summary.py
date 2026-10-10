from pathlib import Path

import pandas as pd


summary_file = (
    Path.home()
    / "Data/processed/nyc-taxi/monthly_summary.parquet"
)

df = pd.read_parquet(summary_file)

print("Shape:", df.shape)

print(
    "First period:",
    df.iloc[0]["year"],
    df.iloc[0]["month"],
)

print(
    "Last period:",
    df.iloc[-1]["year"],
    df.iloc[-1]["month"],
)

print(
    "Duplicate year-month:",
    df.duplicated(["year", "month"]).sum(),
)

print("\nMissing values:")
print(df.isna().sum())