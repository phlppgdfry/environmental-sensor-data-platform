import logging

import pandas as pd

from sensor_platform.db.schema import TelemetryRecord
from sensor_platform.db.session import session_scope
from sensor_platform.ingestion.processor import process_telemetry

logger = logging.getLogger(__name__)


def ingest_telemetry_csv(path: str, engine) -> pd.DataFrame:
    """Read raw wide-format telemetry CSV, normalize it, and upsert into PostgreSQL.

    Returns the normalized long-format DataFrame for downstream analytics.
    """
    raw = pd.read_csv(path)
    long_df = process_telemetry(raw)
    write_telemetry(long_df, engine)
    logger.info("ingested %s telemetry rows from %s", len(long_df), path)
    return long_df


def write_telemetry(long_df: pd.DataFrame, engine) -> int:
    if long_df.empty:
        return 0

    records = [
        TelemetryRecord(
            id=f"{row.sensor_id}:{row.timestamp.isoformat()}:{row.metric}",
            sensor_id=row.sensor_id,
            timestamp=row.timestamp.to_pydatetime(),
            metric=row.metric,
            value=float(row.value),
        )
        for row in long_df.itertuples(index=False)
    ]

    with session_scope(engine) as session:
        # merge() makes the write idempotent: re-ingesting the same file
        # updates existing rows instead of raising a primary-key conflict.
        for record in records:
            session.merge(record)

    return len(records)
