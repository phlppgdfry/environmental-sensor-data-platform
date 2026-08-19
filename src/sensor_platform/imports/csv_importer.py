import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from sensor_platform.imports.mapping import frame_to_devices
from sensor_platform.imports.validation import ValidationResult, validate_asset_frame
from sensor_platform.integrations.thingsboard.client import ThingsBoardClient
from sensor_platform.integrations.thingsboard.devices import DeviceProvisioner

logger = logging.getLogger(__name__)


@dataclass
class ImportReport:
    total_rows: int
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    rejected: int = 0
    validation: ValidationResult | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_rows == 0:
            return 1.0
        return (self.total_rows - self.rejected) / self.total_rows


def import_assets_csv(path: str | Path, client: ThingsBoardClient) -> ImportReport:
    """Import a materiaalbeheer-style CSV and provision devices in ThingsBoard.

    The import is idempotent: re-running it against the same CSV does not
    create duplicate devices — existing devices are matched on
    `Device.thingsboard_name` and updated in place.
    """
    df = pd.read_csv(path, dtype=str)
    result = validate_asset_frame(df)
    devices = frame_to_devices(result.valid_rows) if not result.valid_rows.empty else []

    provisioner = DeviceProvisioner(client)
    report = ImportReport(total_rows=len(df), validation=result, rejected=len(result.invalid_rows))

    for device in devices:
        outcome = provisioner.provision(device)
        if outcome == "created":
            report.created += 1
        elif outcome == "updated":
            report.updated += 1
        else:
            report.unchanged += 1

    report.errors.extend(result.errors)
    logger.info(
        "import complete: total=%s created=%s updated=%s unchanged=%s rejected=%s",
        report.total_rows,
        report.created,
        report.updated,
        report.unchanged,
        report.rejected,
    )
    return report
