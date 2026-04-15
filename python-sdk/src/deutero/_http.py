"""Low-level HTTP transport for the Deutero SDK.

Provides both synchronous and asynchronous HTTP clients backed by httpx.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from deutero.exceptions import ConnectionError, TimeoutError, raise_for_status

_DEFAULT_TIMEOUT = 120.0
_DEFAULT_BASE_URL = "https://app.deutero.ai"
_USER_AGENT = "deutero-python/0.1.0"


def _build_headers(api_key: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {
        "X-API-Key": api_key,
        "User-Agent": _USER_AGENT,
        "Accept": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def _parse_response(response: httpx.Response) -> Any:
    request_id = response.headers.get("x-request-id")
    try:
        body = response.json()
    except Exception:
        body = response.text

    raise_for_status(response.status_code, body, request_id=request_id)
    return body


class SyncHTTPClient:
    """Synchronous HTTP client."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            response = self._client.request(
                method,
                path,
                json=json,
                params=_clean_params(params),
            )
        except httpx.ConnectError as exc:
            raise ConnectionError(f"Failed to connect to {self._base_url}: {exc}") from exc
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {path} timed out after {self._timeout}s") from exc

        return _parse_response(response)

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def put(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", path, json=json, params=params)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()


class AsyncHTTPClient:
    """Asynchronous HTTP client."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            response = await self._client.request(
                method,
                path,
                json=json,
                params=_clean_params(params),
            )
        except httpx.ConnectError as exc:
            raise ConnectionError(f"Failed to connect to {self._base_url}: {exc}") from exc
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {path} timed out after {self._timeout}s") from exc

        return _parse_response(response)

    async def get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("POST", path, json=json, params=params)

    async def put(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("PUT", path, json=json, params=params)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()


def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Remove None values from query parameters."""
    if params is None:
        return None
    return {k: str(v) if not isinstance(v, str) else v for k, v in params.items() if v is not None}
