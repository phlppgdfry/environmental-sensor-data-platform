from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class SensorType(StrEnum):
    AIR_QUALITY = "air_quality"
    WATER_QUALITY = "water_quality"
    NOISE = "noise"
    WEATHER = "weather"


class Device(BaseModel):
    """A provisioned environmental sensor, mapped 1:1 to a ThingsBoard device."""

    sensor_id: str = Field(..., min_length=1, max_length=64)
    project_id: str = Field(..., min_length=1, max_length=64)
    type: SensorType
    location: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    serial_number: str

    @field_validator("sensor_id", "project_id", "serial_number")
    @classmethod
    def strip_and_upper(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value

    @property
    def thingsboard_name(self) -> str:
        return f"{self.project_id}:{self.sensor_id}"
