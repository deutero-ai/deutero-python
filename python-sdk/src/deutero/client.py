"""Deutero API client — synchronous and asynchronous."""

from __future__ import annotations

import os
from typing import Optional

import httpx

from deutero._http import AsyncHTTPClient, SyncHTTPClient, _DEFAULT_BASE_URL, _DEFAULT_TIMEOUT
from deutero.resources.analysis import Analysis, AsyncAnalysis
from deutero.resources.credits import AsyncCredits, Credits
from deutero.resources.interviews import AsyncInterviews, Interviews
from deutero.resources.personas import AsyncPersonas, Personas
from deutero.resources.questions import AsyncQuestions, Questions
from deutero.resources.studies import AsyncStudies, Studies


class Deutero:
    """Synchronous client for the Deutero API.

    Usage::

        from deutero import Deutero

        client = Deutero(api_key="your-api-key")

        study = client.studies.generate(
            study_type="user_experience",
            business_context="...",
            research_need="...",
        )

    The API key can also be set via the ``DEUTERO_API_KEY`` environment variable.

    Args:
        api_key: Your Deutero API key. Falls back to ``DEUTERO_API_KEY`` env var.
        base_url: Override the base URL (default: ``https://app.deutero.ai``).
        timeout: Request timeout in seconds (default: 120).
        http_client: Optional pre-configured :class:`httpx.Client`.
    """

    studies: Studies
    questions: Questions
    personas: Personas
    interviews: Interviews
    analysis: Analysis
    credits: Credits

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("DEUTERO_API_KEY", "")
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key= or set the DEUTERO_API_KEY environment variable."
            )

        self._http = SyncHTTPClient(
            api_key=resolved_key,
            base_url=base_url or _DEFAULT_BASE_URL,
            timeout=timeout or _DEFAULT_TIMEOUT,
            http_client=http_client,
        )

        self.studies = Studies(self._http)
        self.questions = Questions(self._http)
        self.personas = Personas(self._http)
        self.interviews = Interviews(self._http)
        self.analysis = Analysis(self._http)
        self.credits = Credits(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> Deutero:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Deutero(base_url={self._http._base_url!r})"


class AsyncDeutero:
    """Asynchronous client for the Deutero API.

    Usage::

        import asyncio
        from deutero import AsyncDeutero

        async def main():
            client = AsyncDeutero(api_key="your-api-key")

            study = await client.studies.generate(
                study_type="user_experience",
                business_context="...",
                research_need="...",
            )

            await client.close()

        asyncio.run(main())

    The API key can also be set via the ``DEUTERO_API_KEY`` environment variable.

    Args:
        api_key: Your Deutero API key. Falls back to ``DEUTERO_API_KEY`` env var.
        base_url: Override the base URL (default: ``https://app.deutero.ai``).
        timeout: Request timeout in seconds (default: 120).
        http_client: Optional pre-configured :class:`httpx.AsyncClient`.
    """

    studies: AsyncStudies
    questions: AsyncQuestions
    personas: AsyncPersonas
    interviews: AsyncInterviews
    analysis: AsyncAnalysis
    credits: AsyncCredits

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("DEUTERO_API_KEY", "")
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key= or set the DEUTERO_API_KEY environment variable."
            )

        self._http = AsyncHTTPClient(
            api_key=resolved_key,
            base_url=base_url or _DEFAULT_BASE_URL,
            timeout=timeout or _DEFAULT_TIMEOUT,
            http_client=http_client,
        )

        self.studies = AsyncStudies(self._http)
        self.questions = AsyncQuestions(self._http)
        self.personas = AsyncPersonas(self._http)
        self.interviews = AsyncInterviews(self._http)
        self.analysis = AsyncAnalysis(self._http)
        self.credits = AsyncCredits(self._http)

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.close()

    async def __aenter__(self) -> AsyncDeutero:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncDeutero(base_url={self._http._base_url!r})"
