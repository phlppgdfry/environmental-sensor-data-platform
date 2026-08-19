import pandas as pd
import plotly.graph_objects as go

from sensor_platform.analytics.aggregation import hourly_aggregates
from sensor_platform.reporting.charts import (
    matplotlib_daily_summary,
    plotly_metric_timeseries,
    plotly_sensor_map,
    plotly_uptime_bar,
)


def _long_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-08-18T00:00:00Z", periods=10, freq="15min")
    return pd.DataFrame(
        {
            "sensor_id": ["AIR-001"] * 10,
            "timestamp": timestamps,
            "metric": ["pm25"] * 10,
            "value": [10.0 + i for i in range(10)],
        }
    )


def test_plotly_metric_timeseries_returns_figure_with_data():
    fig = plotly_metric_timeseries(_long_df(), "pm25")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [10.0 + i for i in range(10)]


def test_plotly_sensor_map_returns_figure():
    devices = pd.DataFrame(
        [
            {
                "sensor_id": "AIR-001",
                "type": "air_quality",
                "location": "Brugge",
                "project_id": "BRUGGE-01",
                "latitude": 51.2093,
                "longitude": 3.2247,
            }
        ]
    )
    fig = plotly_sensor_map(devices)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_plotly_uptime_bar_respects_top_n():
    uptime_df = pd.DataFrame(
        {
            "sensor_id": [f"S-{i}" for i in range(30)],
            "uptime_pct": list(range(30)),
        }
    )
    fig = plotly_uptime_bar(uptime_df, top_n=5)
    assert isinstance(fig, go.Figure)
    assert len(fig.data[0].y) == 5


def test_matplotlib_daily_summary_writes_png(tmp_path):
    long_df = _long_df()
    agg = hourly_aggregates(long_df)
    output_path = tmp_path / "daily_pm25.png"

    result = matplotlib_daily_summary(agg, "pm25", str(output_path))

    assert result == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
