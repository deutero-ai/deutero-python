"""Shared fixtures for Deutero SDK tests."""

from __future__ import annotations

import httpx
import pytest

from deutero import AsyncDeutero, Deutero

TEST_API_KEY = "test-api-key-12345678"
TEST_BASE_URL = "https://test.deutero.ai"


@pytest.fixture()
def mock_transport() -> httpx.MockTransport:
    """A no-op mock transport that returns 200 with empty JSON by default."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    return httpx.MockTransport(handler)


@pytest.fixture()
def client(mock_transport: httpx.MockTransport) -> Deutero:
    """A synchronous Deutero client wired to a mock transport."""
    http_client = httpx.Client(
        transport=mock_transport,
        base_url=TEST_BASE_URL,
    )
    c = Deutero(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        http_client=http_client,
    )
    yield c
    c.close()


@pytest.fixture()
def async_client(mock_transport: httpx.MockTransport) -> AsyncDeutero:
    """An async Deutero client wired to a mock transport."""
    http_client = httpx.AsyncClient(
        transport=mock_transport,
        base_url=TEST_BASE_URL,
    )
    c = AsyncDeutero(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        http_client=http_client,
    )
    yield c
