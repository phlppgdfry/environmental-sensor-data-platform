import logging
from typing import Literal

from sensor_platform.integrations.thingsboard.client import ThingsBoardClient
from sensor_platform.models.device import Device

logger = logging.getLogger(__name__)

ProvisionOutcome = Literal["created", "updated", "unchanged"]


class DeviceProvisioner:
    """Idempotent device provisioning: create-or-update by unique name."""

    def __init__(self, client: ThingsBoardClient, device_profile: str = "default") -> None:
        self._client = client
        self._device_profile = device_profile

    def find_by_name(self, name: str) -> dict | None:
        response = self._client.get(f"/api/tenant/devices?deviceName={name}")
        if response.status_code == 200:
            return response.json()
        return None

    def provision(self, device: Device) -> ProvisionOutcome:
        name = device.thingsboard_name
        existing = self.find_by_name(name)

        attributes = {
            "sensorId": device.sensor_id,
            "projectId": device.project_id,
            "sensorType": device.type.value,
            "location": device.location,
            "latitude": device.latitude,
            "longitude": device.longitude,
            "serialNumber": device.serial_number,
        }

        if existing is not None:
            if _attributes_match(existing.get("additionalInfo") or {}, attributes):
                logger.debug("device %s unchanged", name)
                return "unchanged"
            existing["additionalInfo"] = {**(existing.get("additionalInfo") or {}), **attributes}
            self._client.post("/api/device", json=existing)
            self._push_server_attributes(existing["id"]["id"], attributes)
            logger.info("device %s updated", name)
            return "updated"

        payload = {
            "name": name,
            "type": self._device_profile,
            "additionalInfo": attributes,
        }
        response = self._client.post("/api/device", json=payload)
        response.raise_for_status()
        created = response.json()
        self._push_server_attributes(created["id"]["id"], attributes)
        logger.info("device %s created", name)
        return "created"

    def _push_server_attributes(self, device_id: str, attributes: dict) -> None:
        self._client.post(
            f"/api/plugins/telemetry/DEVICE/{device_id}/attributes/SERVER_SCOPE",
            json=attributes,
        )

    def get_device_credentials(self, device_id: str) -> str | None:
        response = self._client.get(f"/api/device/{device_id}/credentials")
        if response.status_code != 200:
            return None
        return response.json().get("credentialsId")


def _attributes_match(existing: dict, incoming: dict) -> bool:
    return all(existing.get(key) == value for key, value in incoming.items())
