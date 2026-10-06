"""Deutero API client — synchronous and asynchronous."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

from deutero._http import _DEFAULT_BASE_URL, _DEFAULT_TIMEOUT, AsyncHTTPClient, SyncHTTPClient
from deutero.resources.analysis import Analysis, AsyncAnalysis
from deutero.resources.characteristics import AsyncCharacteristics, Characteristics
from deutero.resources.credits import AsyncCredits, Credits
from deutero.resources.embed import AsyncEmbed, Embed
from deutero.resources.graph import AsyncGraph, Graph
from deutero.resources.interviews import AsyncInterviews, Interviews
from deutero.resources.personas import AsyncPersonas, Personas
from deutero.resources.projects import AsyncProjects, Projects
from deutero.resources.questions import AsyncQuestions, Questions
from deutero.resources.recruitment import AsyncRecruitment, Recruitment
from deutero.resources.screening import AsyncScreening, Screening
from deutero.resources.simulations import AsyncSimulations, Simulations
from deutero.resources.studies import AsyncStudies, Studies
from deutero.resources.transcripts import AsyncTranscripts, Transcripts
from deutero.resources.webhooks import AsyncWebhooks, Webhooks
from deutero.resources.welcome import AsyncWelcome, Welcome


def _resolve_api_key(api_key: Optional[str]) -> str:
    resolved_key = api_key or os.environ.get("DEUTERO_API_KEY", "")
    if not resolved_key:
        raise ValueError(
            "No API key provided. Pass api_key= or set the DEUTERO_API_KEY environment variable."
        )
    return resolved_key


class Deutero:
    """Synchronous client for the Deutero Study Management API.

    Usage::

        from deutero import Deutero

        client = Deutero(api_key="your-api-key")

        project = client.projects.create(name="Onboarding research")
        study = client.studies.create(project_id=project.id, name="Why new users drop off")

    The API key can also be set via the ``DEUTERO_API_KEY`` environment variable.

    Args:
        api_key: Your Deutero API key. Falls back to ``DEUTERO_API_KEY`` env var.
        base_url: Override the base URL (default: ``https://dashboard.deutero.ai/study-api``).
        timeout: Request timeout in seconds (default: 120).
        http_client: Optional pre-configured :class:`httpx.Client`.
    """

    projects: Projects
    studies: Studies
    welcome: Welcome
    screening: Screening
    characteristics: Characteristics
    questions: Questions
    graph: Graph
    recruitment: Recruitment
    embed: Embed
    personas: Personas
    simulations: Simulations
    interviews: Interviews
    transcripts: Transcripts
    analysis: Analysis
    webhooks: Webhooks
    credits: Credits

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._http = SyncHTTPClient(
            api_key=_resolve_api_key(api_key),
            base_url=base_url or _DEFAULT_BASE_URL,
            timeout=timeout or _DEFAULT_TIMEOUT,
            http_client=http_client,
        )

        self.projects = Projects(self._http)
        self.studies = Studies(self._http)
        self.welcome = Welcome(self._http)
        self.screening = Screening(self._http)
        self.characteristics = Characteristics(self._http)
        self.questions = Questions(self._http)
        self.graph = Graph(self._http)
        self.recruitment = Recruitment(self._http)
        self.embed = Embed(self._http)
        self.personas = Personas(self._http)
        self.simulations = Simulations(self._http)
        self.interviews = Interviews(self._http)
        self.transcripts = Transcripts(self._http)
        self.analysis = Analysis(self._http)
        self.webhooks = Webhooks(self._http)
        self.credits = Credits(self._http)

    def health(self) -> Dict[str, Any]:
        """Liveness check. Does not require a valid API key."""
        data: Dict[str, Any] = self._http.get("/health")
        return data

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
    """Asynchronous client for the Deutero Study Management API.

    Usage::

        import asyncio
        from deutero import AsyncDeutero

        async def main():
            async with AsyncDeutero(api_key="your-api-key") as client:
                projects = await client.projects.list()

        asyncio.run(main())

    The API key can also be set via the ``DEUTERO_API_KEY`` environment variable.

    Args:
        api_key: Your Deutero API key. Falls back to ``DEUTERO_API_KEY`` env var.
        base_url: Override the base URL (default: ``https://dashboard.deutero.ai/study-api``).
        timeout: Request timeout in seconds (default: 120).
        http_client: Optional pre-configured :class:`httpx.AsyncClient`.
    """

    projects: AsyncProjects
    studies: AsyncStudies
    welcome: AsyncWelcome
    screening: AsyncScreening
    characteristics: AsyncCharacteristics
    questions: AsyncQuestions
    graph: AsyncGraph
    recruitment: AsyncRecruitment
    embed: AsyncEmbed
    personas: AsyncPersonas
    simulations: AsyncSimulations
    interviews: AsyncInterviews
    transcripts: AsyncTranscripts
    analysis: AsyncAnalysis
    webhooks: AsyncWebhooks
    credits: AsyncCredits

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._http = AsyncHTTPClient(
            api_key=_resolve_api_key(api_key),
            base_url=base_url or _DEFAULT_BASE_URL,
            timeout=timeout or _DEFAULT_TIMEOUT,
            http_client=http_client,
        )

        self.projects = AsyncProjects(self._http)
        self.studies = AsyncStudies(self._http)
        self.welcome = AsyncWelcome(self._http)
        self.screening = AsyncScreening(self._http)
        self.characteristics = AsyncCharacteristics(self._http)
        self.questions = AsyncQuestions(self._http)
        self.graph = AsyncGraph(self._http)
        self.recruitment = AsyncRecruitment(self._http)
        self.embed = AsyncEmbed(self._http)
        self.personas = AsyncPersonas(self._http)
        self.simulations = AsyncSimulations(self._http)
        self.interviews = AsyncInterviews(self._http)
        self.transcripts = AsyncTranscripts(self._http)
        self.analysis = AsyncAnalysis(self._http)
        self.webhooks = AsyncWebhooks(self._http)
        self.credits = AsyncCredits(self._http)

    async def health(self) -> Dict[str, Any]:
        """Liveness check. See :meth:`Deutero.health`."""
        data: Dict[str, Any] = await self._http.get("/health")
        return data

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.close()

    async def __aenter__(self) -> AsyncDeutero:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncDeutero(base_url={self._http._base_url!r})"
