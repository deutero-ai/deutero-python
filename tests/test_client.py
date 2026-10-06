"""Tests for the Deutero client initialization, lifecycle and error handling."""

from __future__ import annotations

import os

import httpx
import pytest

from deutero import AsyncDeutero, Deutero
from deutero.exceptions import (
    AuthenticationError,
    ConflictError,
    InsufficientCreditsError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

STUDY_ID = "00000000-0000-0000-0000-000000000001"

RESOURCES = [
    "projects",
    "studies",
    "welcome",
    "screening",
    "characteristics",
    "questions",
    "graph",
    "recruitment",
    "embed",
    "personas",
    "simulations",
    "interviews",
    "transcripts",
    "analysis",
    "webhooks",
    "credits",
]


def _client_returning(status: int, body: object) -> Deutero:
    transport = httpx.MockTransport(lambda r: httpx.Response(status, json=body))
    http_client = httpx.Client(transport=transport, base_url="https://x.test")
    return Deutero(api_key="k", base_url="https://x.test", http_client=http_client)


class TestClientInit:
    def test_requires_api_key(self) -> None:
        env = os.environ.copy()
        os.environ.pop("DEUTERO_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="No API key"):
                Deutero()
        finally:
            os.environ.update(env)

    def test_accepts_api_key_kwarg(self) -> None:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(api_key="key123", base_url="https://x.test", http_client=http_client)
        assert repr(c) == "Deutero(base_url='https://x.test')"
        c.close()

    def test_reads_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEUTERO_API_KEY", "env-key")
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(base_url="https://x.test", http_client=http_client)
        c.close()

    def test_default_base_url(self) -> None:
        c = Deutero(api_key="k")
        assert repr(c) == "Deutero(base_url='https://dashboard.deutero.ai/study-api')"
        c.close()

    def test_default_client_sends_key_and_keeps_base_path(self) -> None:
        c = Deutero(api_key="secret")
        request = c._http._client.build_request("GET", "/api/v1/projects")
        assert str(request.url) == "https://dashboard.deutero.ai/study-api/api/v1/projects"
        assert request.headers["X-API-Key"] == "secret"
        c.close()

    def test_context_manager(self) -> None:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        with Deutero(api_key="k", base_url="https://x.test", http_client=http_client) as c:
            assert c.studies is not None

    def test_resource_namespaces_exist(self) -> None:
        c = _client_returning(200, {})
        for name in RESOURCES:
            assert hasattr(c, name), name
        c.close()

    def test_health(self) -> None:
        c = _client_returning(200, {"status": "ok"})
        assert c.health() == {"status": "ok"}
        c.close()


class TestAsyncClientInit:
    def test_requires_api_key(self) -> None:
        env = os.environ.copy()
        os.environ.pop("DEUTERO_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="No API key"):
                AsyncDeutero()
        finally:
            os.environ.update(env)

    async def test_resource_namespaces_exist(self) -> None:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        http_client = httpx.AsyncClient(transport=transport, base_url="https://x.test")
        async with AsyncDeutero(api_key="k", base_url="https://x.test", http_client=http_client) as c:
            for name in RESOURCES:
                assert hasattr(c, name), name


class TestErrorHandling:
    def test_401_raises_authentication_error(self) -> None:
        c = _client_returning(401, {"detail": "Invalid API key"})
        with pytest.raises(AuthenticationError) as exc_info:
            c.credits.get_balance()
        assert exc_info.value.status_code == 401
        c.close()

    def test_403_raises_permission_denied(self) -> None:
        c = _client_returning(403, {"detail": "image_upload needs the standard or premium tier"})
        with pytest.raises(PermissionDeniedError) as exc_info:
            c.questions.create(STUDY_ID, question="Upload a photo", qtype="image_upload")
        assert isinstance(exc_info.value, AuthenticationError)
        c.close()

    def test_404_raises_not_found_error(self) -> None:
        c = _client_returning(404, {"detail": "Study not found"})
        with pytest.raises(NotFoundError):
            c.studies.get(STUDY_ID)
        c.close()

    def test_409_raises_conflict(self) -> None:
        c = _client_returning(409, {"detail": "graph_version is 4, expected 3"})
        with pytest.raises(ConflictError):
            c.graph.set(STUDY_ID, flow={"nodes": []}, expected_graph_version=3)
        c.close()

    def test_422_formats_detail_list(self) -> None:
        body = {"detail": [{"loc": ["body", "name"], "msg": "Field required", "type": "missing"}]}
        c = _client_returning(422, body)
        with pytest.raises(ValidationError) as exc_info:
            c.projects.create(name="")
        assert exc_info.value.message == "HTTP 422: name: Field required"
        assert exc_info.value.body == body
        c.close()

    def test_402_raises_insufficient_credits(self) -> None:
        c = _client_returning(402, {"detail": "Insufficient credits"})
        with pytest.raises(InsufficientCreditsError):
            c.simulations.run(STUDY_ID, persona_id="00000000-0000-0000-0000-000000000002")
        c.close()


class TestCustomHttpClient:
    def test_without_base_url_uses_sdk_base_url_and_key(self) -> None:
        seen = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={"projects": []})

        c = Deutero(api_key="k", http_client=httpx.Client(transport=httpx.MockTransport(handler)))
        c.projects.list()
        assert str(seen[0].url) == "https://dashboard.deutero.ai/study-api/api/v1/projects"
        assert seen[0].headers["X-API-Key"] == "k"
        c.close()
