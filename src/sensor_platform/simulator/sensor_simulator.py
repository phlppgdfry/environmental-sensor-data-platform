"""Generates synthetic asset and telemetry data for load-testing and demos.

Deliberately injects realistic messiness (missing intervals, duplicates,
out-of-range outliers, "stuck" offline sensors) so the analytics/quality
layer has something real to detect.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

LOCATIONS = [
    ("Brugge", 51.2093, 3.2247),
    ("Zeebrugge", 51.3310, 3.2070),
    ("Knokke", 51.3500, 3.2667),
    ("Oostende", 51.2154, 2.9286),
    ("Gent", 51.0543, 3.7174),
    ("Antwerpen", 51.2194, 4.4025),
]

SENSOR_TYPES = ["air_quality", "water_quality", "noise", "weather"]

METRICS_BY_TYPE: dict[str, dict[str, tuple[float, float]]] = {
    "air_quality": {"pm25": (12, 6), "pm10": (20, 9), "no2": (15, 5), "co2": (420, 30)},
    "water_quality": {"ph": (7.2, 0.3), "turbidity": (3, 1.5), "water_temperature": (14, 3)},
    "noise": {"decibel": (55, 8)},
    "weather": {"temperature": (16, 5), "humidity": (65, 12), "wind_speed": (14, 6)},
}


@dataclass
class SimulationConfig:
    sensor_count: int = 100
    project_id: str = "BRUGGE-01"
    hours: int = 24
    interval_minutes: int = 15
    missing_rate: float = 0.03
    duplicate_rate: float = 0.01
    outlier_rate: float = 0.01
    offline_sensor_rate: float = 0.02
    seed: int = 42


def generate_asset_frame(config: SimulationConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)
    rows = []
    for i in range(config.sensor_count):
        sensor_type = SENSOR_TYPES[i % len(SENSOR_TYPES)]
        location_name, base_lat, base_lon = LOCATIONS[i % len(LOCATIONS)]
        jitter = rng.normal(0, 0.01, size=2)
        rows.append(
            {
                "sensor_id": f"{sensor_type.upper()[:3]}-{i:04d}",
                "project_id": config.project_id,
                "type": sensor_type,
                "location": location_name,
                "latitude": round(base_lat + jitter[0], 6),
                "longitude": round(base_lon + jitter[1], 6),
                "serial_number": f"SN{rng.integers(10_000, 99_999)}",
            }
        )
    return pd.DataFrame(rows)


def generate_telemetry_frame(assets: pd.DataFrame, config: SimulationConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed + 1)
    start = datetime.now(UTC).replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=config.hours
    )
    timestamps = [
        start + timedelta(minutes=i * config.interval_minutes)
        for i in range(int(config.hours * 60 / config.interval_minutes))
    ]

    offline_sensors = set(
        assets["sensor_id"].sample(frac=config.offline_sensor_rate, random_state=config.seed)
    )

    records = []
    for _, asset in assets.iterrows():
        metrics_spec = METRICS_BY_TYPE[asset["type"]]
        is_offline = asset["sensor_id"] in offline_sensors
        offline_from = timestamps[rng.integers(len(timestamps))] if is_offline else None

        for ts in timestamps:
            if is_offline and offline_from is not None and ts >= offline_from:
                continue  # sensor stopped reporting -> gap in the series
            if rng.random() < config.missing_rate:
                continue  # transient dropped reading

            metrics = {
                name: round(float(rng.normal(mean, std)), 2)
                for name, (mean, std) in metrics_spec.items()
            }

            if rng.random() < config.outlier_rate:
                keys = list(metrics)
                key = keys[rng.integers(len(keys))]
                multiplier = [-1, 8, 15][rng.integers(3)]
                metrics[key] = round(metrics[key] * multiplier, 2)

            record = {"sensor_id": asset["sensor_id"], "timestamp": ts, **metrics}
            records.append(record)
            if rng.random() < config.duplicate_rate:
                records.append(dict(record))  # duplicate telemetry, same ts

    return pd.DataFrame(records).sort_values(["sensor_id", "timestamp"]).reset_index(drop=True)
