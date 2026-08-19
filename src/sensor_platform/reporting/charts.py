import matplotlib

matplotlib.use("Agg")  # headless: no display available in tests or CI runners

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plotly_metric_timeseries(long_df: pd.DataFrame, metric: str) -> go.Figure:
    subset = long_df[long_df["metric"] == metric]
    fig = px.line(
        subset,
        x="timestamp",
        y="value",
        color="sensor_id",
        title=f"{metric} over time",
        labels={"value": metric, "timestamp": "Time"},
    )
    fig.update_layout(template="plotly_white", legend_title_text="Sensor")
    return fig


def plotly_sensor_map(devices: pd.DataFrame) -> go.Figure:
    fig = px.scatter_mapbox(
        devices,
        lat="latitude",
        lon="longitude",
        color="type",
        hover_name="sensor_id",
        hover_data=["location", "project_id"],
        zoom=7,
        title="Sensor locations",
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig


def plotly_uptime_bar(uptime_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    subset = uptime_df.sort_values("uptime_pct").head(top_n)
    fig = px.bar(
        subset,
        x="uptime_pct",
        y="sensor_id",
        orientation="h",
        title=f"Lowest uptime ({top_n} sensors)",
        labels={"uptime_pct": "Uptime %"},
    )
    fig.update_layout(template="plotly_white")
    return fig


def matplotlib_daily_summary(agg_df: pd.DataFrame, metric: str, output_path: str) -> str:
    subset = agg_df[agg_df["metric"] == metric]
    daily = subset.groupby(subset["hour"].dt.date)["mean"].mean()

    fig, ax = plt.subplots(figsize=(8, 4))
    daily.plot(ax=ax, marker="o")
    ax.set_title(f"Daily average {metric}")
    ax.set_ylabel(metric)
    ax.set_xlabel("Date")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
