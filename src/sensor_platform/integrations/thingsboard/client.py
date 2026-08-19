"""Thin REST client for ThingsBoard.

ThingsBoard exposes two distinct authentication planes:

* Management plane (devices, attributes, server-side telemetry queries):
  authenticated with a JWT bearer token obtained via ``/api/auth/login``.
* Device plane (a sensor publishing its own telemetry): authenticated with a
  per-device access token, no user JWT involved.

This client wraps the management plane. ``TelemetryPublisher`` (telemetry.py)
wraps the device plane.
"""

import time
from typing import Any

import httpx


class ThingsBoardAuthError(RuntimeError):
    pass


class ThingsBoardClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "ThingsBoardClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- auth -----------------------------------------------------------

    def _login(self) -> None:
        response = self._http.post(
            "/api/auth/login",
            json={"username": self._username, "password": self._password},
        )
        if response.status_code != 200:
            raise ThingsBoardAuthError(
                f"ThingsBoard login failed: {response.status_code} {response.text}"
            )
        payload = response.json()
        self._token = payload["token"]
        # ThingsBoard JWTs are short-lived; refresh proactively before expiry.
        self._token_expires_at = time.monotonic() + 60 * 15

    def _auth_headers(self) -> dict[str, str]:
        if self._token is None or time.monotonic() >= self._token_expires_at:
            self._login()
        return {"X-Authorization": f"Bearer {self._token}"}

    # -- generic request helpers ----------------------------------------

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("DELETE", path, **kwargs)

    def _request(
        self, method: str, path: str, retry_on_401: bool = True, **kwargs: Any
    ) -> httpx.Response:
        headers = self._auth_headers()
        response = self._http.request(method, path, headers=headers, **kwargs)
        if response.status_code == 401 and retry_on_401:
            self._token = None
            return self._request(method, path, retry_on_401=False, **kwargs)
        return response
