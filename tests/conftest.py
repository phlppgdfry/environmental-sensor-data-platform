import httpx
import pandas as pd
import pytest

from sensor_platform.integrations.thingsboard.client import ThingsBoardClient


@pytest.fixture
def sample_assets_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sensor_id": "AIR-001",
                "project_id": "BRUGGE-01",
                "type": "air_quality",
                "location": "Brugge",
                "latitude": 51.2093,
                "longitude": 3.2247,
                "serial_number": "SN93821",
            },
            {
                "sensor_id": "WATER-001",
                "project_id": "COAST-02",
                "type": "water_quality",
                "location": "Knokke",
                "latitude": 51.3500,
                "longitude": 3.2667,
                "serial_number": "SN88291",
            },
        ]
    )


@pytest.fixture
def sample_telemetry_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sensor_id": "AIR-001",
                "timestamp": "2026-08-18T12:00:00Z",
                "pm25": 18.2,
                "pm10": 31.4,
            },
            {
                "sensor_id": "AIR-001",
                "timestamp": "2026-08-18T12:15:00Z",
                "pm25": 19.1,
                "pm10": 30.9,
            },
            {
                "sensor_id": "AIR-001",
                "timestamp": "2026-08-18T12:30:00Z",
                "pm25": 550.0,
                "pm10": 32.1,
            },
            {
                "sensor_id": "WATER-001",
                "timestamp": "2026-08-18T12:00:00Z",
                "ph": 7.1,
                "pm25": None,
            },
        ]
    )


def make_mock_thingsboard_client(handler, **kwargs) -> ThingsBoardClient:
    transport = httpx.MockTransport(handler)
    return ThingsBoardClient(
        base_url="http://tb.test",
        username="tenant@thingsboard.org",
        password="tenant",
        transport=transport,
        backoff_base_seconds=0,
        **kwargs,
    )
