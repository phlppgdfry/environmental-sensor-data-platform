import json

import httpx
import pandas as pd

from sensor_platform.imports.csv_importer import import_assets_csv
from tests.conftest import make_mock_thingsboard_client


def _write_assets_csv(tmp_path, rows: list[dict]) -> str:
    path = tmp_path / "assets.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return str(path)


def _handler(created_devices: list[str]):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/auth/login":
            return httpx.Response(200, json={"token": "fake-jwt"})
        if request.url.path == "/api/tenant/devices":
            return httpx.Response(404)
        if request.url.path == "/api/device" and request.method == "POST":
            name = json.loads(request.read())["name"]
            created_devices.append(name)
            return httpx.Response(200, json={"id": {"id": f"uuid-{len(created_devices)}"}})
        if "attributes/SERVER_SCOPE" in request.url.path:
            return httpx.Response(200, json={})
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    return handler


def _asset_row(i: int) -> dict:
    return {
        "sensor_id": f"AIR-{i:04d}",
        "project_id": "BRUGGE-01",
        "type": "air_quality",
        "location": "Brugge",
        "latitude": 51.2093,
        "longitude": 3.2247,
        "serial_number": f"SN{i:05d}",
    }


def test_import_processes_multiple_chunks(tmp_path):
    rows = [_asset_row(i) for i in range(25)]
    path = _write_assets_csv(tmp_path, rows)
    created: list[str] = []
    client = make_mock_thingsboard_client(_handler(created))

    report = import_assets_csv(path, client, chunk_size=10)

    assert report.total_rows == 25
    assert report.chunks_processed == 3  # 10 + 10 + 5
    assert report.created == 25
    assert report.rejected == 0


def test_import_detects_duplicate_across_chunk_boundary(tmp_path):
    rows = [_asset_row(0), _asset_row(1), _asset_row(0)]  # AIR-0000 duplicated across chunks
    path = _write_assets_csv(tmp_path, rows)
    created: list[str] = []
    client = make_mock_thingsboard_client(_handler(created))

    report = import_assets_csv(path, client, chunk_size=1)

    assert report.total_rows == 3
    assert report.chunks_processed == 3
    assert report.created == 2
    assert report.rejected == 1
    assert any("duplicate a sensor_id from an earlier chunk" in e for e in report.errors)


def test_import_reports_invalid_rows(tmp_path):
    rows = [_asset_row(0), {**_asset_row(1), "latitude": 999}]
    path = _write_assets_csv(tmp_path, rows)
    created: list[str] = []
    client = make_mock_thingsboard_client(_handler(created))

    report = import_assets_csv(path, client, chunk_size=10)

    assert report.total_rows == 2
    assert report.created == 1
    assert report.rejected == 1
    assert report.success_rate == 0.5
