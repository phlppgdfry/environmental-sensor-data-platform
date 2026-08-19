"""Generate synthetic asset + telemetry CSVs for demos and load tests.

Usage:
    python scripts/simulate_sensors.py --sensors 1000 --hours 24
"""

import time
from pathlib import Path

import typer

from sensor_platform.simulator.sensor_simulator import (
    SimulationConfig,
    generate_asset_frame,
    generate_telemetry_frame,
)

app = typer.Typer(add_completion=False)


@app.command()
def main(
    sensors: int = typer.Option(100, help="Number of sensors to simulate"),
    hours: int = typer.Option(24, help="Hours of telemetry history to generate"),
    interval_minutes: int = typer.Option(15, help="Minutes between telemetry samples"),
    project_id: str = typer.Option("BRUGGE-01", help="Project to assign sensors to"),
    output_dir: str = typer.Option("data/generated", help="Where to write CSV output"),
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    config = SimulationConfig(
        sensor_count=sensors,
        project_id=project_id,
        hours=hours,
        interval_minutes=interval_minutes,
    )

    start = time.perf_counter()
    assets = generate_asset_frame(config)
    telemetry = generate_telemetry_frame(assets, config)
    elapsed = time.perf_counter() - start

    assets_path = output_path / "assets.csv"
    telemetry_path = output_path / "telemetry.csv"
    assets.to_csv(assets_path, index=False)
    telemetry.to_csv(telemetry_path, index=False)

    typer.echo(f"Sensors:            {sensors}")
    typer.echo(f"Telemetry records:  {len(telemetry)}")
    typer.echo(f"Generation time:    {elapsed:.2f}s")
    typer.echo(f"Assets written to:  {assets_path}")
    typer.echo(f"Telemetry written:  {telemetry_path}")


if __name__ == "__main__":
    app()
