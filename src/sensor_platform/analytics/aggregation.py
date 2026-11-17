import pandas as pd


def hourly_aggregates(long_df: pd.DataFrame) -> pd.DataFrame:
    """Per sensor, per metric, per hour: mean/min/max/count."""
    df = long_df.copy()
    df["hour"] = df["timestamp"].dt.floor("h")
    grouped = df.groupby(["sensor_id", "metric", "hour"])["value"]
    agg = grouped.agg(mean="mean", min="min", max="max", count="count").reset_index()
    return agg.sort_values(["sensor_id", "metric", "hour"]).reset_index(drop=True)


def project_summary(
    long_df: pd.DataFrame, devices: pd.DataFrame, valid_only: bool = False
) -> pd.DataFrame:
    """Per project, per metric: overall mean/min/max across all its sensors.

    With ``valid_only=True`` physically impossible readings (outside METRIC_BOUNDS) are left
    out of the statistics and counted in an ``excluded`` column instead, so one broken sensor
    cannot turn a pH mean or a humidity maximum into nonsense.
    """
    from sensor_platform.analytics.quality import within_bounds

    merged = long_df.merge(devices[["sensor_id", "project_id"]], on="sensor_id", how="left")
    if not valid_only:
        grouped = merged.groupby(["project_id", "metric"])["value"]
        summary = grouped.agg(mean="mean", min="min", max="max", count="count").reset_index()
        return summary.sort_values(["project_id", "metric"]).reset_index(drop=True)
    merged = merged.assign(_valid=within_bounds(merged))
    keys = ["project_id", "metric"]
    stats = (
        merged[merged["_valid"]]
        .groupby(keys)["value"]
        .agg(mean="mean", min="min", max="max", count="count")
    )
    excluded = (~merged["_valid"]).groupby([merged[k] for k in keys]).sum().rename("excluded")
    summary = stats.join(excluded, how="outer").reset_index()
    summary["count"] = summary["count"].fillna(0).astype(int)
    summary["excluded"] = summary["excluded"].fillna(0).astype(int)
    return summary.sort_values(keys).reset_index(drop=True)


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
