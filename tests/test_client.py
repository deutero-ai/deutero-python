"""Tests for the Deutero client initialization and lifecycle."""

from __future__ import annotations

import os

import httpx
import pytest

from deutero import AsyncDeutero, Deutero
from deutero.exceptions import AuthenticationError, NotFoundError, ValidationError, InsufficientCreditsError


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

    def test_context_manager(self) -> None:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        with Deutero(api_key="k", base_url="https://x.test", http_client=http_client) as c:
            assert c.studies is not None

    def test_resource_namespaces_exist(self) -> None:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(api_key="k", base_url="https://x.test", http_client=http_client)
        assert hasattr(c, "studies")
        assert hasattr(c, "questions")
        assert hasattr(c, "personas")
        assert hasattr(c, "interviews")
        assert hasattr(c, "analysis")
        assert hasattr(c, "credits")
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


class TestErrorHandling:
    def test_403_raises_authentication_error(self) -> None:
        transport = httpx.MockTransport(
            lambda r: httpx.Response(403, json={"detail": "Invalid API key"})
        )
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(api_key="bad", base_url="https://x.test", http_client=http_client)
        with pytest.raises(AuthenticationError) as exc_info:
            c.credits.get_balance()
        assert exc_info.value.status_code == 403
        c.close()

    def test_404_raises_not_found_error(self) -> None:
        transport = httpx.MockTransport(
            lambda r: httpx.Response(404, json={"detail": "Survey not found"})
        )
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(api_key="k", base_url="https://x.test", http_client=http_client)
        with pytest.raises(NotFoundError):
            c.studies.get_participation("00000000-0000-0000-0000-000000000001")
        c.close()

    def test_400_raises_validation_error(self) -> None:
        transport = httpx.MockTransport(
            lambda r: httpx.Response(400, json={"detail": "Invalid study_type"})
        )
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(api_key="k", base_url="https://x.test", http_client=http_client)
        with pytest.raises(ValidationError):
            c.studies.generate(study_type="invalid")
        c.close()

    def test_402_raises_insufficient_credits(self) -> None:
        transport = httpx.MockTransport(
            lambda r: httpx.Response(402, json={"detail": "Insufficient credits"})
        )
        http_client = httpx.Client(transport=transport, base_url="https://x.test")
        c = Deutero(api_key="k", base_url="https://x.test", http_client=http_client)
        with pytest.raises(InsufficientCreditsError):
            c.interviews.simulate(
                study_id="00000000-0000-0000-0000-000000000001",
                persona_id="p1",
            )
        c.close()
