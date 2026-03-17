"""Reusable HTTP client with retries and timeout controls."""

from __future__ import annotations

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


LOGGER = logging.getLogger(__name__)


class HTTPClientError(RuntimeError):
    """Raised when provider requests fail."""


class BaseHTTPClient:
    """Common HTTP behavior for external providers."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int,
        max_retries: int,
        backoff_seconds: float,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(default_headers or {})
        self._configure_retries(max_retries=max_retries, backoff_seconds=backoff_seconds)

    def _configure_retries(self, max_retries: int, backoff_seconds: float) -> None:
        retry = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            backoff_factor=backoff_seconds,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "POST"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request_json(
        self,
        method: str,
        path: str = "",
        *,
        params: dict[str, Any] | None = None,
        json_payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Send HTTP request and parse JSON body."""
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            msg = f"Request failed for {url}: {exc}"
            raise HTTPClientError(msg) from exc

        if response.status_code >= 400:
            LOGGER.warning("HTTP error %s for %s: %s", response.status_code, url, response.text[:256])
            msg = f"HTTP {response.status_code} for {url}"
            raise HTTPClientError(msg)

        try:
            return response.json()
        except ValueError as exc:
            msg = f"Invalid JSON response for {url}"
            raise HTTPClientError(msg) from exc
