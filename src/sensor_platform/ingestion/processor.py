"""Wide -> long telemetry normalization and deduplication.

Raw telemetry arrives as one row per (sensor_id, timestamp) with one column
per metric. Processing normalizes it into a long/tidy frame
(sensor_id, timestamp, metric, value), which is what the analytics layer
and the database schema both expect.
"""

import pandas as pd

METADATA_COLUMNS = {"sensor_id", "timestamp"}


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate telemetry rows (same sensor, timestamp, values)."""
    return df.drop_duplicates(subset=[c for c in df.columns], keep="first").reset_index(drop=True)


def to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [c for c in df.columns if c not in METADATA_COLUMNS]
    long_df = df.melt(
        id_vars=["sensor_id", "timestamp"],
        value_vars=metric_columns,
        var_name="metric",
        value_name="value",
    )
    return long_df.dropna(subset=["value"]).reset_index(drop=True)


def process_telemetry(raw: pd.DataFrame) -> pd.DataFrame:
    """Full ingestion transform: dedup wide rows, then reshape to long."""
    raw = raw.copy()
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], utc=True)
    deduped = deduplicate(raw)
    return to_long_format(deduped)
