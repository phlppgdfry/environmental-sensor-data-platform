"""Generate an environmental report for one project from generated CSV data.

Usage:
    python scripts/generate_report.py --project BRUGGE-01
"""

import pandas as pd
import typer

from sensor_platform.ingestion.processor import process_telemetry
from sensor_platform.reporting.reports import generate_project_report

app = typer.Typer(add_completion=False)


@app.command()
def main(
    project: str = typer.Option("BRUGGE-01", "--project"),
    assets_csv: str = typer.Option("data/generated/assets.csv"),
    telemetry_csv: str = typer.Option("data/generated/telemetry.csv"),
    output_dir: str = typer.Option("reports/generated"),
) -> None:
    devices = pd.read_csv(assets_csv)
    raw_telemetry = pd.read_csv(telemetry_csv)
    long_df = process_telemetry(raw_telemetry)

    paths = generate_project_report(long_df, devices, project, output_dir)

    typer.echo(f"HTML report:    {paths.html_path}")
    typer.echo(f"Summary CSV:    {paths.summary_csv_path}")
    typer.echo(f"Anomalies CSV:  {paths.anomalies_csv_path}")


if __name__ == "__main__":
    app()
