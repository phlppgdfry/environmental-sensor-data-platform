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
    summary = pd.read_csv(paths.summary_csv_path)
    assert summary.loc[0, "max"] == 18.0  # the 900 µg/m³ reading is outside METRIC_BOUNDS
    assert summary.loc[0, "excluded"] == 1
    assert "within plausible range" in paths.html_path.read_text(encoding="utf-8")


def test_report_counts_all_anomalies_not_just_the_table(tmp_path):
    devices = pd.DataFrame([{"sensor_id": f"S{i}", "project_id": "P"} for i in range(40)])
    rows = []
    for i in range(40):
        for t, v in enumerate([10.0] * 30 + [500.0]):
            rows.append(
                {
                    "sensor_id": f"S{i}",
                    "timestamp": pd.Timestamp("2026-01-01T00:00Z") + pd.Timedelta(minutes=15 * t),
                    "metric": "pm25",
                    "value": v,
                }
            )
    long_df = pd.DataFrame(rows)

    paths = generate_project_report(long_df, devices, "P", tmp_path)

    anomalies = pd.read_csv(paths.anomalies_csv_path)
    assert len(anomalies) > 25
    assert f"of {len(anomalies)} flagged" in paths.html_path.read_text(encoding="utf-8")
