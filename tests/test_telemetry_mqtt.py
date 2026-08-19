import json
from unittest.mock import MagicMock

import pytest

from sensor_platform.integrations.thingsboard.telemetry_mqtt import (
    TELEMETRY_TOPIC,
    MQTTPublishError,
    MQTTTelemetryPublisher,
)
from sensor_platform.models.telemetry import TelemetryReading


def _fake_client_factory(publish_rc: int = 0, is_published: bool = True):
    def factory(callback_api_version):
        client = MagicMock()
        publish_result = MagicMock()
        publish_result.rc = publish_rc
        publish_result.is_published.return_value = is_published
        client.publish.return_value = publish_result
        return client

    return factory


def _reading() -> TelemetryReading:
    return TelemetryReading(
        sensor_id="AIR-001", timestamp="2026-08-18T12:00:00Z", metrics={"pm25": 18.2}
    )


def test_connect_uses_device_token_as_username_no_password():
    factory = _fake_client_factory()
    publisher = MQTTTelemetryPublisher(
        host="tb.test", device_access_token="device-token-123", client_factory=factory
    )

    publisher._client.username_pw_set.assert_called_once_with("device-token-123")
    publisher._client.connect.assert_called_once()
    publisher._client.loop_start.assert_called_once()


def test_publish_sends_telemetry_payload_to_correct_topic():
    factory = _fake_client_factory()
    publisher = MQTTTelemetryPublisher(
        host="tb.test", device_access_token="device-token-123", client_factory=factory
    )

    publisher.publish(_reading())

    topic, payload = publisher._client.publish.call_args.args[:2]
    assert topic == TELEMETRY_TOPIC
    body = json.loads(payload)
    assert body["values"] == {"pm25": 18.2}


def test_publish_raises_when_broker_does_not_confirm():
    factory = _fake_client_factory(is_published=False)
    publisher = MQTTTelemetryPublisher(
        host="tb.test", device_access_token="device-token-123", client_factory=factory
    )

    with pytest.raises(MQTTPublishError):
        publisher.publish(_reading())


def test_publish_batch_publishes_each_reading():
    factory = _fake_client_factory()
    publisher = MQTTTelemetryPublisher(
        host="tb.test", device_access_token="device-token-123", client_factory=factory
    )

    publisher.publish_batch([_reading(), _reading(), _reading()])

    assert publisher._client.publish.call_count == 3


def test_close_stops_loop_and_disconnects():
    factory = _fake_client_factory()
    publisher = MQTTTelemetryPublisher(
        host="tb.test", device_access_token="device-token-123", client_factory=factory
    )

    publisher.close()

    publisher._client.loop_stop.assert_called_once()
    publisher._client.disconnect.assert_called_once()


def test_context_manager_closes_on_exit():
    factory = _fake_client_factory()
    with MQTTTelemetryPublisher(
        host="tb.test", device_access_token="device-token-123", client_factory=factory
    ) as publisher:
        pass

    publisher._client.disconnect.assert_called_once()
