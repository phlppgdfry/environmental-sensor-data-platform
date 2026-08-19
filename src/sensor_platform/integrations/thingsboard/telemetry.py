"""Device-plane telemetry publishing.

Unlike the management API, publishing telemetry as a device uses a
per-device access token, not a user JWT — this mirrors how a real sensor
(or gateway) would authenticate.
"""

import httpx

from sensor_platform.models.telemetry import TelemetryReading


class TelemetryPublisher:
    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)

    def close(self) -> None:
        self._http.close()

    def publish(self, device_access_token: str, reading: TelemetryReading) -> httpx.Response:
        return self._http.post(
            f"/api/v1/{device_access_token}/telemetry",
            json=reading.to_thingsboard_payload(),
        )

    def publish_batch(
        self, device_access_token: str, readings: list[TelemetryReading]
    ) -> list[httpx.Response]:
        return [self.publish(device_access_token, reading) for reading in readings]
