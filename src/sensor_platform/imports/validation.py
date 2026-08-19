from dataclasses import dataclass

import pandas as pd

REQUIRED_COLUMNS = {
    "sensor_id",
    "project_id",
    "type",
    "location",
    "latitude",
    "longitude",
    "serial_number",
}

VALID_TYPES = {"air_quality", "water_quality", "noise", "weather"}


@dataclass
class ValidationResult:
    valid_rows: pd.DataFrame
    invalid_rows: pd.DataFrame
    errors: list[str]

    @property
    def is_clean(self) -> bool:
        return self.invalid_rows.empty


def validate_asset_frame(df: pd.DataFrame) -> ValidationResult:
    """Validate a raw asset-management CSV before it is imported.

    Checks: required columns present, no blank identifiers, lat/lon within
    range, sensor type in the known set, and no duplicate sensor_id rows.
    """
    errors: list[str] = []
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        errors.append(f"missing required columns: {sorted(missing_columns)}")
        return ValidationResult(valid_rows=df.iloc[0:0], invalid_rows=df, errors=errors)

    df = df.copy()
    df["_row_errors"] = [[] for _ in range(len(df))]

    for col in ("sensor_id", "project_id", "serial_number"):
        blank = df[col].astype(str).str.strip().eq("")
        df.loc[blank, "_row_errors"] = df.loc[blank, "_row_errors"].apply(
            lambda errs, c=col: errs + [f"{c} is blank"]
        )

    bad_type = ~df["type"].isin(VALID_TYPES)
    df.loc[bad_type, "_row_errors"] = df.loc[bad_type, "_row_errors"].apply(
        lambda errs: errs + ["unknown sensor type"]
    )

    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    bad_coords = lat.isna() | lon.isna() | ~lat.between(-90, 90) | ~lon.between(-180, 180)
    df.loc[bad_coords, "_row_errors"] = df.loc[bad_coords, "_row_errors"].apply(
        lambda errs: errs + ["invalid latitude/longitude"]
    )

    duplicated = df["sensor_id"].duplicated(keep=False)
    df.loc[duplicated, "_row_errors"] = df.loc[duplicated, "_row_errors"].apply(
        lambda errs: errs + ["duplicate sensor_id in file"]
    )

    has_errors = df["_row_errors"].apply(len).gt(0)
    invalid_rows = df.loc[has_errors].drop(columns=[])
    valid_rows = df.loc[~has_errors].drop(columns=["_row_errors"])

    if not invalid_rows.empty:
        errors.append(f"{len(invalid_rows)} row(s) failed validation")

    return ValidationResult(valid_rows=valid_rows, invalid_rows=invalid_rows, errors=errors)
