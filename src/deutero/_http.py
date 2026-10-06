"""Low-level HTTP transport for the Deutero SDK.

Provides both synchronous and asynchronous HTTP clients backed by httpx.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
from pydantic import BaseModel

from deutero.exceptions import ConnectionError, TimeoutError, raise_for_status

_DEFAULT_TIMEOUT = 120.0
_DEFAULT_BASE_URL = "https://dashboard.deutero.ai/study-api"
_USER_AGENT = "deutero-python/0.2.0"


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
    if response.status_code == 204 or not response.content:
        raise_for_status(response.status_code, None, request_id=request_id)
        return None
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
        self._headers = _build_headers(api_key)
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=self._base_url,
            headers=self._headers,
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
                self._url(path),
                json=json,
                params=_clean_params(params),
                headers=self._headers,
            )
        except httpx.ConnectError as exc:
            raise ConnectionError(f"Failed to connect to {self._base_url}: {exc}") from exc
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {path} timed out after {self._timeout}s") from exc

        return _parse_response(response)

    def _url(self, path: str) -> str:
        # A caller-supplied httpx client may not carry our base URL.
        return path if str(self._client.base_url) else self._base_url + path

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def put(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", path, json=json, params=params)

    def patch(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PATCH", path, json=json, params=params)

    def delete(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("DELETE", path, params=params)

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
        self._headers = _build_headers(api_key)
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
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
                self._url(path),
                json=json,
                params=_clean_params(params),
                headers=self._headers,
            )
        except httpx.ConnectError as exc:
            raise ConnectionError(f"Failed to connect to {self._base_url}: {exc}") from exc
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {path} timed out after {self._timeout}s") from exc

        return _parse_response(response)

    def _url(self, path: str) -> str:
        # A caller-supplied httpx client may not carry our base URL.
        return path if str(self._client.base_url) else self._base_url + path

    async def get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("POST", path, json=json, params=params)

    async def put(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("PUT", path, json=json, params=params)

    async def patch(self, path: str, *, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("PATCH", path, json=json, params=params)

    async def delete(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("DELETE", path, params=params)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()


def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Remove None values from query parameters and stringify the rest."""
    if params is None:
        return None
    return {k: _param_value(v) for k, v in params.items() if v is not None}


def _param_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, enum.Enum):
        return str(value.value)
    return value if isinstance(value, str) else str(value)


def compact(**fields: Any) -> Dict[str, Any]:
    """Build a JSON body from keyword arguments, dropping those left as ``None``."""
    return {k: _jsonable(v) for k, v in fields.items() if v is not None}


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value
