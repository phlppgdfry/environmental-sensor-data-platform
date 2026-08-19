"""FastAPI service exposing the analytics layer over HTTP.

Run locally with:
    uvicorn sensor_platform.api.app:app --reload

Reads the same generated CSVs the Streamlit dashboard and report scripts
use (see `sensor_platform.api.data.load_data`) — this is a read layer over
the same analytics functions, not a separate system.
"""

from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query

from sensor_platform.analytics.aggregation import project_summary
from sensor_platform.analytics.anomalies import zscore_anomalies
from sensor_platform.analytics.quality import build_quality_report
from sensor_platform.api.data import get_data_dir, load_data

app = FastAPI(
    title="Environmental Sensor Platform API",
    description="Read-only analytics API over sensor telemetry and device data.",
    version="0.2.0",
)


def _load(data_dir: Path = Depends(get_data_dir)) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        return load_data(data_dir)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "No generated data found. Run `python scripts/simulate_sensors.py` "
                "to create assets.csv and telemetry.csv first."
            ),
        ) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/projects")
def list_projects(data: tuple[pd.DataFrame, pd.DataFrame] = Depends(_load)) -> list[str]:
    devices, _ = data
    return sorted(devices["project_id"].unique().tolist())


@app.get("/reports/{project_id}")
def get_report(
    project_id: str, data: tuple[pd.DataFrame, pd.DataFrame] = Depends(_load)
) -> dict:
    devices, long_df = data
    project_devices = devices[devices["project_id"] == project_id]
    if project_devices.empty:
        raise HTTPException(status_code=404, detail=f"unknown project_id: {project_id!r}")

    sensor_ids = set(project_devices["sensor_id"])
    project_readings = long_df[long_df["sensor_id"].isin(sensor_ids)]
    summary = project_summary(project_readings, project_devices)
    quality = build_quality_report(project_readings)

    return {
        "project_id": project_id,
        "sensor_count": len(sensor_ids),
        "reading_count": len(project_readings),
        "completeness_pct": quality.completeness_pct,
        "metric_summary": summary.to_dict(orient="records"),
        "lowest_uptime": quality.sensor_uptime.head(10).to_dict(orient="records"),
    }


@app.get("/anomalies")
def get_anomalies(
    project_id: str | None = Query(None, description="Filter to one project_id"),
    threshold: float = Query(3.0, gt=0, description="Z-score magnitude threshold"),
    limit: int = Query(50, gt=0, le=1000),
    data: tuple[pd.DataFrame, pd.DataFrame] = Depends(_load),
) -> list[dict]:
    devices, long_df = data
    if project_id is not None:
        sensor_ids = set(devices.loc[devices["project_id"] == project_id, "sensor_id"])
        if not sensor_ids:
            raise HTTPException(status_code=404, detail=f"unknown project_id: {project_id!r}")
        long_df = long_df[long_df["sensor_id"].isin(sensor_ids)]

    anomalies = zscore_anomalies(long_df, threshold=threshold).head(limit)
    anomalies = anomalies.copy()
    anomalies["timestamp"] = anomalies["timestamp"].astype(str)
    return anomalies.to_dict(orient="records")
