from sensor_platform.imports.validation import validate_asset_frame
from sensor_platform.simulator.sensor_simulator import (
    SimulationConfig,
    generate_asset_frame,
    generate_telemetry_frame,
)


def test_generated_assets_pass_validation():
    config = SimulationConfig(sensor_count=25, seed=1)
    assets = generate_asset_frame(config)
    result = validate_asset_frame(assets)
    assert result.is_clean
    assert len(assets) == 25
    assert assets["sensor_id"].is_unique


def test_generated_telemetry_has_gaps_duplicates_and_outliers():
    config = SimulationConfig(sensor_count=10, hours=6, interval_minutes=15, seed=1)
    assets = generate_asset_frame(config)
    telemetry = generate_telemetry_frame(assets, config)

    expected_max_rows = len(assets) * (6 * 60 // 15)
    assert 0 < len(telemetry) <= expected_max_rows * 1.1
    assert set(telemetry["sensor_id"]) <= set(assets["sensor_id"])


def test_simulation_is_reproducible_with_same_seed():
    config = SimulationConfig(sensor_count=15, hours=3, seed=7)
    assets_a = generate_asset_frame(config)
    assets_b = generate_asset_frame(config)
    assert assets_a.equals(assets_b)
