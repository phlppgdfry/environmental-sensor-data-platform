from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class TelemetryReading(BaseModel):
    """A single telemetry sample pushed by a sensor."""

    sensor_id: str
    timestamp: datetime
    metrics: dict[str, float] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def to_thingsboard_payload(self) -> dict:
        return {"ts": int(self.timestamp.timestamp() * 1000), "values": self.metrics}
