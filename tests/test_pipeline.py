import pandas as pd
from sqlalchemy import select

from sensor_platform.db.schema import TelemetryRecord
from sensor_platform.db.session import init_db, make_engine, session_scope
from sensor_platform.ingestion.pipeline import write_telemetry
from sensor_platform.ingestion.processor import process_telemetry


def test_write_telemetry_is_idempotent():
    engine = make_engine("sqlite:///:memory:")
    init_db(engine)

    raw = pd.DataFrame(
        [
            {"sensor_id": "AIR-001", "timestamp": "2026-08-18T12:00:00Z", "pm25": 18.2},
            {"sensor_id": "AIR-001", "timestamp": "2026-08-18T12:15:00Z", "pm25": 19.1},
        ]
    )
    long_df = process_telemetry(raw)

    write_telemetry(long_df, engine)
    write_telemetry(long_df, engine)  # re-ingest same data

    with session_scope(engine) as session:
        rows = session.execute(select(TelemetryRecord)).scalars().all()

    assert len(rows) == 2  # merge() upserts, no duplicates
