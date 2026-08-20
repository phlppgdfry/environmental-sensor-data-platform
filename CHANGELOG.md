# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-20

### Added
- FastAPI read layer (`api/app.py`) exposing projects, per-project report
  summaries and z-score anomalies over HTTP, on top of the existing
  analytics functions.
- MQTT telemetry publisher (`integrations/thingsboard/telemetry_mqtt.py`)
  mirroring the HTTP publisher's interface, for fleets/gateways that speak
  MQTT instead of one-off HTTP POSTs.
- Streamed CSV import (`imports/csv_importer.py`): `import_assets_csv` now
  reads and provisions in configurable chunks instead of loading the whole
  file into memory, while still catching duplicate `sensor_id`s across
  chunk boundaries.
- Live integration tests (`tests/integration/`) against real PostgreSQL and
  ThingsBoard service containers in GitLab CI, marked `@pytest.mark.integration`
  and excluded from the default local `pytest` run.
- ThingsBoard tenant wired up beyond telemetry: a comprehensive ops
  dashboard (map, per-domain trend charts, range charts, KPI tiles, active
  alarms table), a standalone anomaly-routing rule chain with a webhook
  node, a native Calculated Field (`Air Quality Index`), a Notification
  Center rule on the `High PM2.5` alarm, and Entity Groups replacing direct
  "Change owner" customer sharing — all provisioned via the `thingsboard-cli`
  rather than the web UI.

### Fixed
- GitHub Actions CI never ran on pushes to `main` because the repo's
  default branch was still `master`; renamed the default branch and fixed
  the mismatch.
- `docker-compose.yml` mapped ThingsBoard's port incorrectly
  (`8080:9090` instead of `8080:8080`), silently broken because local
  testing always used ThingsBoard Cloud instead of the compose stack.
- A `DetachedInstanceError` in the live PostgreSQL integration test caused
  by asserting on a mapped attribute after the owning session had already
  committed and closed.

## [0.2.0] - 2026-08-19

### Added
- Retry with exponential backoff in `ThingsBoardClient` for transient
  connection errors and 5xx/429 responses (4xx client errors are not
  retried).
- GitLab Pages deployment (`pages` job) that publishes the generated
  environmental report to a permanent URL instead of a 7-day-expiring job
  artifact.
- Pre-commit hooks (`ruff`, `mypy`) via `.pre-commit-config.yaml`.
- Test coverage for `reporting/charts.py` (Plotly and Matplotlib chart
  builders), forcing the headless `Agg` Matplotlib backend for CI.

### Verified
- ThingsBoard integration validated against a live ThingsBoard Cloud
  instance: device provisioning, telemetry publishing, an alarm rule that
  fires from real telemetry, and dashboard sharing with a customer.
- GitLab CI pipeline (lint, test, build, sample report) passes end-to-end
  on a verified account.

## [0.1.0] - 2026-08-19

### Added
- Initial release: CSV asset import with idempotent ThingsBoard device
  provisioning, JWT + device-token ThingsBoard client, telemetry ingestion
  pipeline (PostgreSQL), Pandas/NumPy analytics (aggregation, data quality,
  anomaly detection), Plotly/Matplotlib reporting, Streamlit dashboard, and
  a sensor simulator for load testing.
- GitLab CI and GitHub Actions pipelines.
