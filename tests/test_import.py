import pandas as pd

from sensor_platform.imports.mapping import frame_to_devices
from sensor_platform.imports.validation import validate_asset_frame


def test_valid_frame_passes_cleanly(sample_assets_df):
    result = validate_asset_frame(sample_assets_df)
    assert result.is_clean
    assert len(result.valid_rows) == 2
    assert result.invalid_rows.empty


def test_missing_required_column_is_rejected():
    df = pd.DataFrame([{"sensor_id": "AIR-001"}])
    result = validate_asset_frame(df)
    assert not result.is_clean
    assert "missing required columns" in result.errors[0]


def test_duplicate_sensor_id_flagged(sample_assets_df):
    df = pd.concat([sample_assets_df, sample_assets_df.iloc[[0]]], ignore_index=True)
    result = validate_asset_frame(df)
    assert len(result.invalid_rows) == 2  # both copies of the duplicate row
    assert len(result.valid_rows) == 1


def test_invalid_coordinates_flagged(sample_assets_df):
    df = sample_assets_df.copy()
    df.loc[0, "latitude"] = 999
    result = validate_asset_frame(df)
    assert len(result.invalid_rows) == 1
    assert len(result.valid_rows) == 1


def test_blank_sensor_id_flagged(sample_assets_df):
    df = sample_assets_df.copy()
    df.loc[0, "sensor_id"] = "  "
    result = validate_asset_frame(df)
    assert len(result.invalid_rows) == 1


def test_unknown_type_flagged(sample_assets_df):
    df = sample_assets_df.copy()
    df.loc[0, "type"] = "lava_temperature"
    result = validate_asset_frame(df)
    assert len(result.invalid_rows) == 1


def test_frame_to_devices_maps_types(sample_assets_df):
    devices = frame_to_devices(sample_assets_df)
    assert len(devices) == 2
    assert devices[0].thingsboard_name == "BRUGGE-01:AIR-001"
    assert devices[0].type.value == "air_quality"
