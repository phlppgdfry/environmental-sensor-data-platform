"""Device-plane telemetry publishing over MQTT.

HTTP (`telemetry.py`) is fine for occasional or batch publishing. Real
sensor fleets and gateways more commonly speak MQTT: a persistent
connection, lower per-message overhead, and QoS delivery guarantees matter
once you're pushing from hundreds of devices continuously rather than
posting one-off HTTP requests.

Auth mirrors the HTTP device plane: the device access token is used as the
MQTT username (no password), never a user JWT.
"""

import json
from collections.abc import Callable

import paho.mqtt.client as mqtt

from sensor_platform.models.telemetry import TelemetryReading

TELEMETRY_TOPIC = "v1/devices/me/telemetry"


class MQTTPublishError(RuntimeError):
    pass


class MQTTTelemetryPublisher:
    def __init__(
        self,
        host: str,
        port: int = 1883,
        device_access_token: str | None = None,
        connect_timeout: float = 5.0,
        publish_timeout: float = 5.0,
        client_factory: Callable[[mqtt.CallbackAPIVersion], mqtt.Client] = mqtt.Client,
    ) -> None:
        self.host = host
        self.port = port
        self._publish_timeout = publish_timeout
        self._client = client_factory(mqtt.CallbackAPIVersion.VERSION2)
        if device_access_token:
            self._client.username_pw_set(device_access_token)
        self._client.connect(host, port, keepalive=int(connect_timeout) or 60)
        self._client.loop_start()

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def __enter__(self) -> "MQTTTelemetryPublisher":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def publish(self, reading: TelemetryReading, qos: int = 1) -> None:
        payload = json.dumps(reading.to_thingsboard_payload())
        result = self._client.publish(TELEMETRY_TOPIC, payload, qos=qos)
        result.wait_for_publish(timeout=self._publish_timeout)
        if not result.is_published():
            raise MQTTPublishError(f"telemetry publish did not complete: rc={result.rc}")

    def publish_batch(self, readings: list[TelemetryReading], qos: int = 1) -> None:
        for reading in readings:
            self.publish(reading, qos=qos)


def connect_device(
    host: str, device_access_token: str, port: int = 1883
) -> MQTTTelemetryPublisher:
    """Convenience constructor matching the naming used elsewhere in the repo."""
    return MQTTTelemetryPublisher(host=host, port=port, device_access_token=device_access_token)
