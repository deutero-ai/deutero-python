"""Interviews resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union
from uuid import UUID

from deutero.models import InterviewSimulateResponse

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Interviews:
    """Synchronous interface for interview operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def simulate(
        self,
        *,
        study_id: Union[str, UUID],
        persona_id: str,
    ) -> InterviewSimulateResponse:
        """Simulate a full interview for a study persona.

        The interview simulation runs in the background on the server. This
        method returns immediately with the transcript URL and credit usage
        information.

        Args:
            study_id: UUID of the study.
            persona_id: ID of the persona to simulate.

        Returns:
            Simulation result with transcript URL and credit info.
        """
        data = self._client.post(
            "/api/v1/interviews/simulate",
            json={
                "survey_id": str(study_id),
                "persona_id": persona_id,
            },
        )
        return InterviewSimulateResponse.model_validate(data)


class AsyncInterviews:
    """Asynchronous interface for interview operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def simulate(
        self,
        *,
        study_id: Union[str, UUID],
        persona_id: str,
    ) -> InterviewSimulateResponse:
        """Simulate a full interview for a study persona. See :meth:`Interviews.simulate`."""
        data = await self._client.post(
            "/api/v1/interviews/simulate",
            json={
                "survey_id": str(study_id),
                "persona_id": persona_id,
            },
        )
        return InterviewSimulateResponse.model_validate(data)
