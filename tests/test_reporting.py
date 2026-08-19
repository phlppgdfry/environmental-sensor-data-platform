import pandas as pd

from sensor_platform.reporting.reports import generate_project_report


def test_generate_project_report_writes_expected_files(tmp_path):
    devices = pd.DataFrame(
        [
            {"sensor_id": "AIR-001", "project_id": "BRUGGE-01"},
            {"sensor_id": "AIR-002", "project_id": "BRUGGE-01"},
        ]
    )
    timestamps = pd.date_range("2026-08-18T00:00:00Z", periods=10, freq="15min")
    long_df = pd.DataFrame(
        {
            "sensor_id": ["AIR-001"] * 10,
            "timestamp": timestamps,
            "metric": ["pm25"] * 10,
            "value": [18.0] * 9 + [900.0],
        }
    )

    paths = generate_project_report(long_df, devices, "BRUGGE-01", tmp_path)

    assert paths.html_path.exists()
    assert paths.summary_csv_path.exists()
    assert paths.anomalies_csv_path.exists()
    assert "BRUGGE-01" in paths.html_path.read_text(encoding="utf-8")
