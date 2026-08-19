import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from sensor_platform.imports.mapping import frame_to_devices
from sensor_platform.imports.validation import validate_asset_frame
from sensor_platform.integrations.thingsboard.client import ThingsBoardClient
from sensor_platform.integrations.thingsboard.devices import DeviceProvisioner

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 5_000


@dataclass
class ImportReport:
    total_rows: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    rejected: int = 0
    chunks_processed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_rows == 0:
            return 1.0
        return (self.total_rows - self.rejected) / self.total_rows


def import_assets_csv(
    path: str | Path, client: ThingsBoardClient, chunk_size: int = DEFAULT_CHUNK_SIZE
) -> ImportReport:
    """Import a materiaalbeheer-style CSV and provision devices in ThingsBoard.

    Reads and provisions the CSV in chunks of `chunk_size` rows rather than
    loading the whole file into memory — needed once an asset export runs
    into the hundreds of thousands of rows. Duplicate sensor_ids are still
    caught even when the two copies land in different chunks.

    The import is idempotent: re-running it against the same CSV does not
    create duplicate devices — existing devices are matched on
    `Device.thingsboard_name` and updated in place.
    """
    provisioner = DeviceProvisioner(client)
    report = ImportReport()
    seen_sensor_ids: set[str] = set()

    for chunk in pd.read_csv(path, dtype=str, chunksize=chunk_size):
        report.total_rows += len(chunk)
        report.chunks_processed += 1

        result = validate_asset_frame(chunk)
        report.errors.extend(result.errors)
        report.rejected += len(result.invalid_rows)

        valid_rows = result.valid_rows
        if valid_rows.empty:
            continue

        cross_chunk_dup = valid_rows["sensor_id"].isin(seen_sensor_ids)
        if cross_chunk_dup.any():
            report.rejected += int(cross_chunk_dup.sum())
            report.errors.append(
                f"{int(cross_chunk_dup.sum())} row(s) duplicate a sensor_id from an earlier chunk"
            )
            valid_rows = valid_rows.loc[~cross_chunk_dup]

        seen_sensor_ids.update(valid_rows["sensor_id"])

        for device in frame_to_devices(valid_rows):
            outcome = provisioner.provision(device)
            if outcome == "created":
                report.created += 1
            elif outcome == "updated":
                report.updated += 1
            else:
                report.unchanged += 1

    logger.info(
        "import complete: total=%s chunks=%s created=%s updated=%s unchanged=%s rejected=%s",
        report.total_rows,
        report.chunks_processed,
        report.created,
        report.updated,
        report.unchanged,
        report.rejected,
    )
    return report
