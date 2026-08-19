import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

from sensor_platform.ingestion.processor import process_telemetry


def get_data_dir() -> Path:
    """Directory holding assets.csv / telemetry.csv, e.g. from simulate_sensors.py.

    Overridable via SENSOR_DATA_DIR so tests (and alternate deployments)
    don't have to share the default `data/generated` directory.
    """
    return Path(os.environ.get("SENSOR_DATA_DIR", "data/generated"))


@lru_cache
def _cached_load(assets_path: str, telemetry_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    devices = pd.read_csv(assets_path)
    raw_telemetry = pd.read_csv(telemetry_path)
    long_df = process_telemetry(raw_telemetry)
    return devices, long_df


def load_data(data_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load (devices, long_format_telemetry) from CSVs in `data_dir`.

    Cached per (assets_path, telemetry_path) pair so repeated API requests
    don't re-read and re-melt the CSVs on every call.
    """
    data_dir = data_dir or get_data_dir()
    assets_path = str(data_dir / "assets.csv")
    telemetry_path = str(data_dir / "telemetry.csv")
    return _cached_load(assets_path, telemetry_path)


def clear_cache() -> None:
    _cached_load.cache_clear()
