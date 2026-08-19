from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TelemetryRecord(Base):
    __tablename__ = "telemetry"

    id = Column(String, primary_key=True)  # f"{sensor_id}:{timestamp.isoformat()}:{metric}"
    sensor_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)


class DeviceRecord(Base):
    __tablename__ = "devices"

    sensor_id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    serial_number = Column(String, nullable=False)
