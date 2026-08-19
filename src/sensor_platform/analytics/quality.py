from dataclasses import dataclass

import pandas as pd

# Physically plausible ranges used to flag clearly broken readings.
METRIC_BOUNDS = {
    "pm25": (0, 500),
    "pm10": (0, 600),
    "no2": (0, 400),
    "co2": (300, 5000),
    "ph": (0, 14),
    "turbidity": (0, 1000),
    "water_temperature": (-2, 40),
    "decibel": (0, 140),
    "temperature": (-30, 50),
    "humidity": (0, 100),
    "wind_speed": (0, 60),
}


@dataclass
class QualityReport:
    total_readings: int
    out_of_range: pd.DataFrame
    sensor_uptime: pd.DataFrame
    completeness_pct: float


def flag_out_of_range(long_df: pd.DataFrame) -> pd.DataFrame:
    def is_invalid(row: pd.Series) -> bool:
        bounds = METRIC_BOUNDS.get(row["metric"])
        if bounds is None:
            return False
        low, high = bounds
        return not (low <= row["value"] <= high)

    mask = long_df.apply(is_invalid, axis=1)
    return long_df.loc[mask].reset_index(drop=True)


def sensor_uptime(long_df: pd.DataFrame, expected_interval_minutes: int = 15) -> pd.DataFrame:
    """Estimate uptime % per sensor from the density of its timestamps."""
    rows = []
    for sensor_id, group in long_df.groupby("sensor_id"):
        timestamps = group["timestamp"].drop_duplicates().sort_values()
        if len(timestamps) < 2:
            rows.append(
                {"sensor_id": sensor_id, "uptime_pct": 0.0, "reading_count": len(timestamps)}
            )
            continue
        span_minutes = (timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds() / 60
        expected = max(span_minutes / expected_interval_minutes, 1)
        uptime_pct = min(len(timestamps) / expected, 1.0) * 100
        rows.append(
            {
                "sensor_id": sensor_id,
                "uptime_pct": round(uptime_pct, 1),
                "reading_count": len(timestamps),
            }
        )
    return pd.DataFrame(rows).sort_values("uptime_pct").reset_index(drop=True)


def build_quality_report(
    long_df: pd.DataFrame, expected_interval_minutes: int = 15
) -> QualityReport:
    out_of_range = flag_out_of_range(long_df)
    uptime = sensor_uptime(long_df, expected_interval_minutes)
    completeness = 100.0 * (1 - len(out_of_range) / len(long_df)) if len(long_df) else 100.0
    return QualityReport(
        total_readings=len(long_df),
        out_of_range=out_of_range,
        sensor_uptime=uptime,
        completeness_pct=round(completeness, 2),
    )


def detect_missing_intervals(
    long_df: pd.DataFrame, sensor_id: str, metric: str, expected_interval_minutes: int = 15
) -> pd.DataFrame:
    """Gaps larger than 2x the expected interval for one sensor/metric series."""
    series = long_df[(long_df["sensor_id"] == sensor_id) & (long_df["metric"] == metric)]
    timestamps = series["timestamp"].sort_values().reset_index(drop=True)
    if len(timestamps) < 2:
        return pd.DataFrame(columns=["gap_start", "gap_end", "gap_minutes"])

    diffs = timestamps.diff().dt.total_seconds() / 60
    threshold = expected_interval_minutes * 2
    gap_mask = diffs > threshold
    gaps = pd.DataFrame(
        {
            "gap_start": timestamps.shift(1)[gap_mask],
            "gap_end": timestamps[gap_mask],
            "gap_minutes": diffs[gap_mask],
        }
    ).reset_index(drop=True)
    return gaps
