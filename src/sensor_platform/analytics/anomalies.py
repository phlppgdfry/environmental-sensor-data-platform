import numpy as np
import pandas as pd


def zscore_anomalies(long_df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Flag readings whose per-(sensor, metric) z-score exceeds the threshold."""
    df = long_df.copy()
    grouped = df.groupby(["sensor_id", "metric"])["value"]
    df["mean"] = grouped.transform("mean")
    df["std"] = grouped.transform("std").replace(0, np.nan)
    df["zscore"] = (df["value"] - df["mean"]) / df["std"]
    anomalies = df.loc[df["zscore"].abs() > threshold].copy()
    anomalies["zscore"] = anomalies["zscore"].round(2)
    return anomalies.drop(columns=["mean", "std"]).sort_values("zscore", key=abs, ascending=False)


def iqr_anomalies(long_df: pd.DataFrame, k: float = 1.5) -> pd.DataFrame:
    """Flag readings outside [Q1 - k*IQR, Q3 + k*IQR] per (sensor, metric)."""
    rows = []
    for _, group in long_df.groupby(["sensor_id", "metric"]):
        q1, q3 = group["value"].quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - k * iqr, q3 + k * iqr
        outliers = group[(group["value"] < low) | (group["value"] > high)]
        rows.append(outliers)
    if not rows:
        return long_df.iloc[0:0]
    return pd.concat(rows).sort_values("timestamp").reset_index(drop=True)


def threshold_violations(long_df: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    """Flag readings above a fixed regulatory/operational threshold per metric.

    E.g. thresholds={"pm25": 35.0} for a WHO daily PM2.5 guideline check.
    """
    frames = []
    for metric, limit in thresholds.items():
        subset = long_df[(long_df["metric"] == metric) & (long_df["value"] > limit)].copy()
        subset["limit"] = limit
        frames.append(subset)
    if not frames:
        return long_df.iloc[0:0]
    return pd.concat(frames).sort_values("timestamp").reset_index(drop=True)
