"""Interviews (response monitoring) resource."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero.models import (
    InterviewDetailListOut,
    InterviewDetailOut,
    InterviewEffectsOut,
    InterviewListOut,
    TranscriptOut,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Interviews:
    """Synchronous interface for monitoring a study's interviews."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list(
        self,
        study_id: Union[str, UUID],
        *,
        completed: Optional[bool] = None,
        simulated: Optional[bool] = None,
        test_runs: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        started_after: Union[str, datetime, None] = None,
        started_before: Union[str, datetime, None] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> InterviewListOut:
        """List a study's interviews, newest first.

        Args:
            study_id: The study.
            completed: Filter by completion status.
            simulated: ``True`` for only simulated, ``False`` for only real. The server
                returns only real interviews when this is omitted.
            test_runs: ``True`` for only test runs (your own interviews through the dashboard's
                Try Interview / Preview), ``False`` to leave them out. The server leaves them
                out when this is omitted.
            external_participant_id: Only interviews that arrived with this id of yours.
            started_after: Only interviews started after this time.
            started_before: Only interviews started before this time.
            limit: Page size (server default 50).
            offset: Page offset.
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/interviews",
            params={
                "completed": completed,
                "simulated": simulated,
                "test_runs": test_runs,
                "external_participant_id": external_participant_id,
                "started_after": started_after,
                "started_before": started_before,
                "limit": limit,
                "offset": offset,
            },
        )
        return InterviewListOut.model_validate(data)

    def find_by_external_id(
        self,
        study_id: Union[str, UUID],
        *,
        external_participant_id: str,
        include_simulated: Optional[bool] = None,
        include_test_runs: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> InterviewDetailListOut:
        """Look up every interview that arrived carrying your own participant id, in full detail.

        Args:
            study_id: The study.
            external_participant_id: Your id for the participant, exactly as the entry link
                (``?participant_id=``) or embed metadata carried it.
            include_simulated: Include simulated interviews (server default ``False``).
            include_test_runs: Include test runs — your own interviews through the dashboard's
                Try Interview / Preview (server default ``False``).
            limit: Most recent N attempts (server default 20).
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/interviews/by-external-id",
            params={
                "external_participant_id": external_participant_id,
                "include_simulated": include_simulated,
                "include_test_runs": include_test_runs,
                "limit": limit,
            },
        )
        return InterviewDetailListOut.model_validate(data)

    def get(self, interview_id: Union[str, UUID]) -> InterviewDetailOut:
        """Get one interview with its screening answers, characteristics, metadata and captured variables."""
        data = self._client.get(f"/api/v1/interviews/{interview_id}")
        return InterviewDetailOut.model_validate(data)

    def get_transcript(self, interview_id: Union[str, UUID]) -> TranscriptOut:
        """Get an interview's messages in order, plus captured variables and branch decisions."""
        data = self._client.get(f"/api/v1/interviews/{interview_id}/transcript")
        return TranscriptOut.model_validate(data)

    def get_fetches_and_signals(self, interview_id: Union[str, UUID]) -> InterviewEffectsOut:
        """Get what an interview flow's data fetches and signals did. Empty for linear studies."""
        data = self._client.get(f"/api/v1/interviews/{interview_id}/fetches-and-signals")
        return InterviewEffectsOut.model_validate(data)


class AsyncInterviews:
    """Asynchronous interface for monitoring a study's interviews."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        study_id: Union[str, UUID],
        *,
        completed: Optional[bool] = None,
        simulated: Optional[bool] = None,
        test_runs: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        started_after: Union[str, datetime, None] = None,
        started_before: Union[str, datetime, None] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> InterviewListOut:
        """List interviews. See :meth:`Interviews.list`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/interviews",
            params={
                "completed": completed,
                "simulated": simulated,
                "test_runs": test_runs,
                "external_participant_id": external_participant_id,
                "started_after": started_after,
                "started_before": started_before,
                "limit": limit,
                "offset": offset,
            },
        )
        return InterviewListOut.model_validate(data)

    async def find_by_external_id(
        self,
        study_id: Union[str, UUID],
        *,
        external_participant_id: str,
        include_simulated: Optional[bool] = None,
        include_test_runs: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> InterviewDetailListOut:
        """Look up interviews by your participant id. See :meth:`Interviews.find_by_external_id`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/interviews/by-external-id",
            params={
                "external_participant_id": external_participant_id,
                "include_simulated": include_simulated,
                "include_test_runs": include_test_runs,
                "limit": limit,
            },
        )
        return InterviewDetailListOut.model_validate(data)

    async def get(self, interview_id: Union[str, UUID]) -> InterviewDetailOut:
        """Get interview detail. See :meth:`Interviews.get`."""
        data = await self._client.get(f"/api/v1/interviews/{interview_id}")
        return InterviewDetailOut.model_validate(data)

    async def get_transcript(self, interview_id: Union[str, UUID]) -> TranscriptOut:
        """Get an interview transcript. See :meth:`Interviews.get_transcript`."""
        data = await self._client.get(f"/api/v1/interviews/{interview_id}/transcript")
        return TranscriptOut.model_validate(data)

    async def get_fetches_and_signals(self, interview_id: Union[str, UUID]) -> InterviewEffectsOut:
        """Get data fetches and signals. See :meth:`Interviews.get_fetches_and_signals`."""
        data = await self._client.get(f"/api/v1/interviews/{interview_id}/fetches-and-signals")
        return InterviewEffectsOut.model_validate(data)
