"""Streamlit dashboard for the Environmental Sensor Data Platform.

Run with:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sensor_platform.analytics.anomalies import zscore_anomalies
from sensor_platform.analytics.quality import build_quality_report
from sensor_platform.ingestion.processor import process_telemetry
from sensor_platform.reporting.charts import (
    plotly_metric_timeseries,
    plotly_sensor_map,
    plotly_uptime_bar,
)

st.set_page_config(page_title="Environmental Sensor Platform", layout="wide")

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "generated"


@st.cache_data
def load_data():
    devices = pd.read_csv(DATA_DIR / "assets.csv")
    raw_telemetry = pd.read_csv(DATA_DIR / "telemetry.csv")
    long_df = process_telemetry(raw_telemetry)
    return devices, long_df


st.title("Environmental Sensor Data Platform")

if not (DATA_DIR / "telemetry.csv").exists():
    st.warning(
        "No generated data found. Run `python scripts/simulate_sensors.py` first "
        "to create `data/generated/assets.csv` and `telemetry.csv`."
    )
    st.stop()

devices, long_df = load_data()
quality = build_quality_report(long_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Sensors", len(devices))
col2.metric("Readings", f"{len(long_df):,}")
col3.metric("Data completeness", f"{quality.completeness_pct}%")
col4.metric("Anomalies (top)", len(zscore_anomalies(long_df)))

st.subheader("Sensor locations")
st.plotly_chart(plotly_sensor_map(devices), use_container_width=True)

metric = st.selectbox("Metric", sorted(long_df["metric"].unique()))
st.subheader(f"{metric} over time")
st.plotly_chart(plotly_metric_timeseries(long_df, metric), use_container_width=True)

st.subheader("Lowest sensor uptime")
st.plotly_chart(plotly_uptime_bar(quality.sensor_uptime), use_container_width=True)

st.subheader("Out-of-range readings")
st.dataframe(quality.out_of_range.head(50))
