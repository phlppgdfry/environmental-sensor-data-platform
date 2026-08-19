import pandas as pd

from sensor_platform.models.device import Device


def row_to_device(row: pd.Series) -> Device:
    return Device(
        sensor_id=str(row["sensor_id"]),
        project_id=str(row["project_id"]),
        type=row["type"],
        location=str(row["location"]),
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        serial_number=str(row["serial_number"]),
    )


def frame_to_devices(df: pd.DataFrame) -> list[Device]:
    return [row_to_device(row) for _, row in df.iterrows()]
