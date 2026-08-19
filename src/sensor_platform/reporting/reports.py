from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, select_autoescape

from sensor_platform.analytics.aggregation import project_summary
from sensor_platform.analytics.anomalies import zscore_anomalies
from sensor_platform.analytics.quality import build_quality_report

REPORT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Environmental report — {{ project_id }}</title>
<style>
  body { font-family: -apple-system, Arial, sans-serif; margin: 2rem; color: #1a1a1a; }
  h1 { margin-bottom: 0; }
  .meta { color: #666; margin-bottom: 2rem; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; }
  th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: right; font-size: 0.9rem; }
  th { background: #f4f4f4; text-align: left; }
  td:first-child, th:first-child { text-align: left; }
  .stat-row { display: flex; gap: 2rem; margin-bottom: 2rem; }
  .stat { background: #f8f8f8; padding: 1rem 1.5rem; border-radius: 8px; }
  .stat .value { font-size: 1.6rem; font-weight: 700; }
  .stat .label { color: #666; font-size: 0.85rem; }
</style>
</head>
<body>
  <h1>Environmental Sensor Report</h1>
  <div class="meta">Project {{ project_id }} — generated {{ generated_at }}</div>

  <div class="stat-row">
    <div class="stat">
      <div class="value">{{ sensor_count }}</div>
      <div class="label">Sensors</div>
    </div>
    <div class="stat">
      <div class="value">{{ total_readings }}</div>
      <div class="label">Readings</div>
    </div>
    <div class="stat">
      <div class="value">{{ completeness_pct }}%</div>
      <div class="label">Data completeness</div>
    </div>
    <div class="stat">
      <div class="value">{{ anomaly_count }}</div>
      <div class="label">Anomalies flagged</div>
    </div>
  </div>

  <h2>Metric summary</h2>
  {{ summary_table | safe }}

  <h2>Lowest sensor uptime</h2>
  {{ uptime_table | safe }}

  <h2>Top anomalies</h2>
  {{ anomalies_table | safe }}
</body>
</html>
"""


@dataclass
class ReportPaths:
    html_path: Path
    summary_csv_path: Path
    anomalies_csv_path: Path


def generate_project_report(
    long_df: pd.DataFrame,
    devices: pd.DataFrame,
    project_id: str,
    output_dir: str | Path,
) -> ReportPaths:
    output_dir = Path(output_dir) / project_id
    output_dir.mkdir(parents=True, exist_ok=True)

    project_devices = devices[devices["project_id"] == project_id]
    sensor_ids = set(project_devices["sensor_id"])
    project_readings = long_df[long_df["sensor_id"].isin(sensor_ids)]

    summary = project_summary(project_readings, project_devices)
    quality = build_quality_report(project_readings)
    anomalies = zscore_anomalies(project_readings).head(25)
    anomalies["value"] = anomalies["value"].round(2)
    anomalies["zscore"] = anomalies["zscore"].round(2)

    env = Environment(autoescape=select_autoescape(["html"]))
    template = env.from_string(REPORT_TEMPLATE)
    html = template.render(
        project_id=project_id,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        sensor_count=len(sensor_ids),
        total_readings=len(project_readings),
        completeness_pct=quality.completeness_pct,
        anomaly_count=len(anomalies),
        summary_table=summary.round(2).to_html(index=False, classes="summary"),
        uptime_table=quality.sensor_uptime.head(10).to_html(index=False, classes="uptime"),
        anomalies_table=anomalies.to_html(index=False, classes="anomalies"),
    )

    html_path = output_dir / "report.html"
    summary_csv_path = output_dir / "sensor-summary.csv"
    anomalies_csv_path = output_dir / "anomalies.csv"

    html_path.write_text(html, encoding="utf-8")
    summary.to_csv(summary_csv_path, index=False)
    anomalies.to_csv(anomalies_csv_path, index=False)

    return ReportPaths(html_path, summary_csv_path, anomalies_csv_path)
