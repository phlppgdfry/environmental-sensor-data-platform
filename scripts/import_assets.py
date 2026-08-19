"""Import a materiaalbeheer-style asset CSV and provision devices in ThingsBoard.

Usage:
    python scripts/import_assets.py data/generated/assets.csv
"""

import typer

from sensor_platform.config.settings import get_settings
from sensor_platform.imports.csv_importer import import_assets_csv
from sensor_platform.integrations.thingsboard.client import ThingsBoardClient

app = typer.Typer(add_completion=False)


@app.command()
def main(csv_path: str) -> None:
    settings = get_settings()
    with ThingsBoardClient(
        base_url=settings.thingsboard_base_url,
        username=settings.thingsboard_username,
        password=settings.thingsboard_password,
    ) as client:
        report = import_assets_csv(csv_path, client)

    typer.echo(f"Total rows:   {report.total_rows}")
    typer.echo(f"Created:      {report.created}")
    typer.echo(f"Updated:      {report.updated}")
    typer.echo(f"Unchanged:    {report.unchanged}")
    typer.echo(f"Rejected:     {report.rejected}")
    typer.echo(f"Success rate: {report.success_rate:.1%}")
    for error in report.errors:
        typer.echo(f"  ! {error}")


if __name__ == "__main__":
    app()
