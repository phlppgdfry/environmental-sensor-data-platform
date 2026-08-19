import pandas as pd
import pytest
from fastapi.testclient import TestClient

from sensor_platform.api import data as data_module
from sensor_platform.api.app import app, get_data_dir


@pytest.fixture
def api_client(tmp_path):
    devices = pd.DataFrame(
        [
            {
                "sensor_id": "AIR-001",
                "project_id": "BRUGGE-01",
                "type": "air_quality",
                "location": "Brugge",
                "latitude": 51.2093,
                "longitude": 3.2247,
                "serial_number": "SN1",
            },
            {
                "sensor_id": "AIR-002",
                "project_id": "BRUGGE-01",
                "type": "air_quality",
                "location": "Brugge",
                "latitude": 51.21,
                "longitude": 3.22,
                "serial_number": "SN2",
            },
        ]
    )
    timestamps = pd.date_range("2026-08-18T00:00:00Z", periods=20, freq="15min")
    telemetry = pd.DataFrame(
        {
            "sensor_id": ["AIR-001"] * 20,
            "timestamp": timestamps,
            "pm25": [18.0] * 19 + [900.0],
        }
    )
    devices.to_csv(tmp_path / "assets.csv", index=False)
    telemetry.to_csv(tmp_path / "telemetry.csv", index=False)

    data_module.clear_cache()
    app.dependency_overrides[get_data_dir] = lambda: tmp_path
    yield TestClient(app)
    app.dependency_overrides.clear()
    data_module.clear_cache()


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_projects(api_client):
    response = api_client.get("/projects")
    assert response.status_code == 200
    assert response.json() == ["BRUGGE-01"]


def test_get_report_for_known_project(api_client):
    response = api_client.get("/reports/BRUGGE-01")
    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "BRUGGE-01"
    assert body["sensor_count"] == 2
    assert body["reading_count"] == 20
    assert "metric_summary" in body
    assert "lowest_uptime" in body


def test_get_report_for_unknown_project_is_404(api_client):
    response = api_client.get("/reports/NOPE")
    assert response.status_code == 404


def test_get_anomalies_flags_the_outlier(api_client):
    response = api_client.get("/anomalies")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["value"] == 900.0


def test_get_anomalies_filtered_by_unknown_project_is_404(api_client):
    response = api_client.get("/anomalies", params={"project_id": "NOPE"})
    assert response.status_code == 404


def test_get_anomalies_respects_limit(api_client):
    response = api_client.get("/anomalies", params={"threshold": 0.0001, "limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1
