import pandas as pd


def hourly_aggregates(long_df: pd.DataFrame) -> pd.DataFrame:
    """Per sensor, per metric, per hour: mean/min/max/count."""
    df = long_df.copy()
    df["hour"] = df["timestamp"].dt.floor("h")
    grouped = df.groupby(["sensor_id", "metric", "hour"])["value"]
    agg = grouped.agg(mean="mean", min="min", max="max", count="count").reset_index()
    return agg.sort_values(["sensor_id", "metric", "hour"]).reset_index(drop=True)


def project_summary(long_df: pd.DataFrame, devices: pd.DataFrame) -> pd.DataFrame:
    """Per project, per metric: overall mean/min/max across all its sensors."""
    merged = long_df.merge(devices[["sensor_id", "project_id"]], on="sensor_id", how="left")
    grouped = merged.groupby(["project_id", "metric"])["value"]
    summary = grouped.agg(mean="mean", min="min", max="max", count="count").reset_index()
    return summary.sort_values(["project_id", "metric"]).reset_index(drop=True)


def rolling_average(long_df: pd.DataFrame, window: str = "3h") -> pd.DataFrame:
    """Rolling time-window average per sensor per metric."""
    results = []
    for (sensor_id, metric), group in long_df.groupby(["sensor_id", "metric"]):
        group = group.sort_values("timestamp").set_index("timestamp")
        rolling = group["value"].rolling(window).mean().reset_index()
        rolling["sensor_id"] = sensor_id
        rolling["metric"] = metric
        rolling = rolling.rename(columns={"value": "rolling_mean"})
        results.append(rolling)
    if not results:
        return pd.DataFrame(columns=["timestamp", "sensor_id", "metric", "rolling_mean"])
    return pd.concat(results, ignore_index=True)
