import httpx

from sensor_platform.integrations.thingsboard.devices import DeviceProvisioner
from sensor_platform.integrations.thingsboard.telemetry import TelemetryPublisher
from sensor_platform.models.device import Device
from sensor_platform.models.telemetry import TelemetryReading
from tests.conftest import make_mock_thingsboard_client


def _device() -> Device:
    return Device(
        sensor_id="AIR-001",
        project_id="BRUGGE-01",
        type="air_quality",
        location="Brugge",
        latitude=51.2093,
        longitude=3.2247,
        serial_number="SN93821",
    )


def test_login_then_create_device_when_not_found():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.url.path == "/api/auth/login":
            return httpx.Response(200, json={"token": "fake-jwt"})
        if request.url.path == "/api/tenant/devices":
            return httpx.Response(404)
        if request.url.path == "/api/device" and request.method == "POST":
            return httpx.Response(
                200, json={"id": {"id": "device-uuid-1"}, "name": "BRUGGE-01:AIR-001"}
            )
        if "attributes/SERVER_SCOPE" in request.url.path:
            return httpx.Response(200, json={})
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = make_mock_thingsboard_client(handler)
    provisioner = DeviceProvisioner(client)

    outcome = provisioner.provision(_device())

    assert outcome == "created"
    assert ("POST", "/api/auth/login") in calls
    assert any(method == "POST" and path == "/api/device" for method, path in calls)


def test_provision_is_idempotent_when_unchanged():
    existing_device = {
        "id": {"id": "device-uuid-1"},
        "name": "BRUGGE-01:AIR-001",
        "additionalInfo": {
            "sensorId": "AIR-001",
            "projectId": "BRUGGE-01",
            "sensorType": "air_quality",
            "location": "Brugge",
            "latitude": 51.2093,
            "longitude": 3.2247,
            "serialNumber": "SN93821",
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/auth/login":
            return httpx.Response(200, json={"token": "fake-jwt"})
        if request.url.path == "/api/tenant/devices":
            return httpx.Response(200, json=existing_device)
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = make_mock_thingsboard_client(handler)
    provisioner = DeviceProvisioner(client)

    outcome = provisioner.provision(_device())

    assert outcome == "unchanged"


def test_expired_token_triggers_relogin():
    login_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal login_calls
        if request.url.path == "/api/auth/login":
            login_calls += 1
            return httpx.Response(200, json={"token": f"jwt-{login_calls}"})
        if request.url.path == "/api/tenant/devices":
            if request.headers.get("X-Authorization") == "Bearer jwt-1":
                return httpx.Response(401)
            return httpx.Response(404)
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = make_mock_thingsboard_client(handler)
    provisioner = DeviceProvisioner(client)

    result = provisioner.find_by_name("BRUGGE-01:AIR-001")

    assert result is None
    assert login_calls == 2


def test_telemetry_publish_uses_device_token_not_jwt():
    seen_paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        assert "X-Authorization" not in request.headers
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    publisher = TelemetryPublisher(base_url="http://tb.test", transport=transport)

    reading = TelemetryReading(
        sensor_id="AIR-001", timestamp="2026-08-18T12:00:00Z", metrics={"pm25": 18.2}
    )
    response = publisher.publish("device-access-token-123", reading)

    assert response.status_code == 200
    assert seen_paths == ["/api/v1/device-access-token-123/telemetry"]
