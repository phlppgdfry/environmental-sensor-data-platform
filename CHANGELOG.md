# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
