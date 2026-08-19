from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = (
        "postgresql+psycopg2://sensor_platform:sensor_platform@localhost:5432/sensor_platform"
    )

    thingsboard_base_url: str = "http://localhost:8080"
    thingsboard_username: str = "tenant@thingsboard.org"
    thingsboard_password: str = "tenant"
    thingsboard_device_profile: str = "default"

    simulator_sensor_count: int = 100
    simulator_interval_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
