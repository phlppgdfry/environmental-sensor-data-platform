"""Runs against a real PostgreSQL instance, not the sqlite-in-memory used
by the unit test suite. Skips locally unless DATABASE_URL is set; wired up
in CI against a `postgres:16-alpine` service container.
"""

import os

import pandas as pd
import pytest
from sqlalchemy import select

from sensor_platform.db.schema import TelemetryRecord
from sensor_platform.db.session import init_db, make_engine, session_scope
from sensor_platform.ingestion.pipeline import write_telemetry
from sensor_platform.ingestion.processor import process_telemetry

pytestmark = pytest.mark.integration


@pytest.fixture
def live_engine():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping live PostgreSQL integration test")
    engine = make_engine(database_url)
    init_db(engine)
    yield engine
    with session_scope(engine) as session:
        session.query(TelemetryRecord).filter(
            TelemetryRecord.sensor_id == "CI-INTEGRATION-PG"
        ).delete()


def test_write_and_read_telemetry_against_real_postgres(live_engine):
    raw = pd.DataFrame(
        [{"sensor_id": "CI-INTEGRATION-PG", "timestamp": "2026-08-19T12:00:00Z", "pm25": 12.3}]
    )
    long_df = process_telemetry(raw)

    write_telemetry(long_df, live_engine)

    with session_scope(live_engine) as session:
        rows = (
            session.execute(
                select(TelemetryRecord).where(TelemetryRecord.sensor_id == "CI-INTEGRATION-PG")
            )
            .scalars()
            .all()
        )
    assert len(rows) == 1
    assert rows[0].value == 12.3


def test_write_telemetry_upserts_on_conflict(live_engine):
    raw = pd.DataFrame(
        [{"sensor_id": "CI-INTEGRATION-PG", "timestamp": "2026-08-19T12:15:00Z", "pm25": 10.0}]
    )
    long_df = process_telemetry(raw)

    write_telemetry(long_df, live_engine)
    write_telemetry(long_df, live_engine)  # re-ingest same data

    with session_scope(live_engine) as session:
        rows = (
            session.execute(
                select(TelemetryRecord).where(
                    TelemetryRecord.sensor_id == "CI-INTEGRATION-PG",
                    TelemetryRecord.timestamp == long_df.iloc[0]["timestamp"].to_pydatetime(),
                )
            )
            .scalars()
            .all()
        )
    assert len(rows) == 1
