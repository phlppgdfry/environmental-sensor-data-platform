"""Runs against a real ThingsBoard instance (device provisioning, server
attributes, credential lookup and telemetry publish), not the mocked
httpx transport used by the unit test suite. Skips locally unless
THINGSBOARD_BASE_URL is set; wired up in CI against a
`thingsboard/tb-postgres` service container.
"""

import os
from datetime import UTC, datetime

import pytest

from sensor_platform.integrations.thingsboard.client import ThingsBoardClient
from sensor_platform.integrations.thingsboard.devices import DeviceProvisioner
from sensor_platform.integrations.thingsboard.telemetry import TelemetryPublisher
from sensor_platform.models.device import Device
from sensor_platform.models.telemetry import TelemetryReading

pytestmark = pytest.mark.integration


@pytest.fixture
def live_client():
    base_url = os.environ.get("THINGSBOARD_BASE_URL")
    if not base_url:
        pytest.skip("THINGSBOARD_BASE_URL not set; skipping live ThingsBoard integration test")
    username = os.environ.get("THINGSBOARD_USERNAME", "tenant@thingsboard.org")
    password = os.environ.get("THINGSBOARD_PASSWORD", "tenant")
    with ThingsBoardClient(
        base_url=base_url, username=username, password=password, timeout=15.0
    ) as client:
        yield client


def _device(sensor_id: str) -> Device:
    return Device(
        sensor_id=sensor_id,
        project_id="CI-INTEGRATION",
        type="air_quality",
        location="CI runner",
        latitude=51.0,
        longitude=3.0,
        serial_number=f"SN-{sensor_id}",
    )


def test_provision_device_is_idempotent_against_real_thingsboard(live_client):
    provisioner = DeviceProvisioner(live_client)
    device = _device("CI-TB-001")

    first_outcome = provisioner.provision(device)
    second_outcome = provisioner.provision(device)

    assert first_outcome in ("created", "unchanged")
    assert second_outcome == "unchanged"

    found = provisioner.find_by_name(device.thingsboard_name)
    assert found is not None
    assert found["additionalInfo"]["sensorId"] == "CI-TB-001"


def test_publish_telemetry_against_real_thingsboard(live_client):
    provisioner = DeviceProvisioner(live_client)
    device = _device("CI-TB-002")
    provisioner.provision(device)

    found = provisioner.find_by_name(device.thingsboard_name)
    device_id = found["id"]["id"]
    access_token = provisioner.get_device_credentials(device_id)
    assert access_token

    reading = TelemetryReading(
        sensor_id=device.sensor_id, timestamp=datetime.now(UTC), metrics={"pm25": 21.4}
    )
    with TelemetryPublisher(base_url=os.environ["THINGSBOARD_BASE_URL"]) as publisher:
        response = publisher.publish(access_token, reading)

    assert response.status_code == 200
