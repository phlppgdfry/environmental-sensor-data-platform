import pandas as pd

from sensor_platform.analytics.aggregation import hourly_aggregates, project_summary
from sensor_platform.analytics.anomalies import (
    iqr_anomalies,
    threshold_violations,
    zscore_anomalies,
)
from sensor_platform.analytics.quality import (
    build_quality_report,
    detect_missing_intervals,
    flag_out_of_range,
)
from sensor_platform.ingestion.processor import deduplicate, process_telemetry, to_long_format


def _long_df() -> pd.DataFrame:
    timestamps = pd.date_range("2026-08-18T00:00:00Z", periods=20, freq="15min")
    values = [18.0] * 19 + [900.0]  # one clear outlier
    return pd.DataFrame(
        {
            "sensor_id": ["AIR-001"] * 20,
            "timestamp": timestamps,
            "metric": ["pm25"] * 20,
            "value": values,
        }
    )


def test_process_telemetry_reshapes_wide_to_long(sample_telemetry_df):
    long_df = process_telemetry(sample_telemetry_df)
    assert set(long_df.columns) == {"sensor_id", "timestamp", "metric", "value"}
    assert (long_df["metric"] == "pm10").any()


def test_deduplicate_drops_exact_duplicate_rows():
    df = pd.DataFrame({"sensor_id": ["A", "A"], "timestamp": ["t1", "t1"], "pm25": [1.0, 1.0]})
    deduped = deduplicate(df)
    assert len(deduped) == 1


def test_to_long_format_drops_nulls():
    df = pd.DataFrame({"sensor_id": ["A"], "timestamp": ["t1"], "pm25": [None]})
    long_df = to_long_format(df)
    assert long_df.empty


def test_hourly_aggregates_groups_by_hour():
    long_df = _long_df()
    agg = hourly_aggregates(long_df)
    assert "mean" in agg.columns
    assert agg["count"].sum() == 20


def test_project_summary_merges_devices():
    long_df = _long_df()
    devices = pd.DataFrame({"sensor_id": ["AIR-001"], "project_id": ["BRUGGE-01"]})
    summary = project_summary(long_df, devices)
    assert summary.loc[0, "project_id"] == "BRUGGE-01"


def test_zscore_anomalies_flags_the_outlier():
    long_df = _long_df()
    anomalies = zscore_anomalies(long_df, threshold=3.0)
    assert len(anomalies) == 1
    assert anomalies.iloc[0]["value"] == 900.0


def test_iqr_anomalies_flags_the_outlier():
    long_df = _long_df()
    anomalies = iqr_anomalies(long_df)
    assert (anomalies["value"] == 900.0).any()


def test_threshold_violations_respects_limit():
    long_df = _long_df()
    violations = threshold_violations(long_df, {"pm25": 35.0})
    assert len(violations) == 1
    assert violations.iloc[0]["limit"] == 35.0


def test_flag_out_of_range_uses_metric_bounds():
    long_df = _long_df()
    flagged = flag_out_of_range(long_df)
    assert len(flagged) == 1  # 900 pm25 exceeds bound of 500


def test_quality_report_completeness():
    long_df = _long_df()
    report = build_quality_report(long_df)
    assert report.total_readings == 20
    assert 0 < report.completeness_pct < 100


def test_detect_missing_intervals_finds_gap():
    timestamps = list(pd.date_range("2026-08-18T00:00:00Z", periods=3, freq="15min")) + [
        pd.Timestamp("2026-08-18T05:00:00Z")
    ]
    long_df = pd.DataFrame(
        {
            "sensor_id": ["AIR-001"] * 4,
            "timestamp": timestamps,
            "metric": ["pm25"] * 4,
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    gaps = detect_missing_intervals(long_df, "AIR-001", "pm25", expected_interval_minutes=15)
    assert len(gaps) == 1
    assert gaps.iloc[0]["gap_minutes"] > 200
