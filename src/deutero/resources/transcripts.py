"""Transcript export and search resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero.models import SearchMode, SearchOut, TranscriptsBulkOut

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Transcripts:
    """Synchronous interface for bulk transcript export and search over participant answers."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list(
        self,
        study_id: Union[str, UUID],
        *,
        completed: Optional[bool] = None,
        include_simulated: Optional[bool] = None,
        include_test_runs: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> TranscriptsBulkOut:
        """Fetch full transcripts in bulk, newest interview first, paginated by interview.

        Args:
            study_id: The study.
            completed: Filter by completion status.
            include_simulated: Include simulated interviews (server default ``False``).
            include_test_runs: Include test runs — your own interviews through the dashboard's
                Try Interview / Preview (server default ``False``).
            external_participant_id: Only interviews that arrived with this id of yours.
            limit: Interviews per page (server default 20).
            offset: Page offset.
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/transcripts",
            params={
                "completed": completed,
                "include_simulated": include_simulated,
                "include_test_runs": include_test_runs,
                "external_participant_id": external_participant_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return TranscriptsBulkOut.model_validate(data)

    def search(
        self,
        study_id: Union[str, UUID],
        *,
        q: str,
        mode: Union[str, SearchMode, None] = None,
        question_id: Optional[str] = None,
        completed_only: Optional[bool] = None,
        include_simulated: Optional[bool] = None,
        include_test_runs: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        strict: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> SearchOut:
        """Search participant answers.

        Args:
            study_id: The study.
            q: Search query.
            mode: ``"string"`` (full-text + fuzzy), ``"semantic"`` (embedding similarity) or
                ``"hybrid"`` (server default; rank fusion of both).
            question_id: Restrict to one question — a question ID for linear studies, or the
                graph step ID for flow studies.
            completed_only: Only completed interviews.
            include_simulated: Include simulated interviews.
            include_test_runs: Include test runs — your own interviews through the dashboard's
                Try Interview / Preview (server default ``False``).
            external_participant_id: Restrict to one person's interviews, by your id for them.
            strict: In hybrid mode, fail with 503 instead of silently falling back to string
                search when semantic search is unavailable.
            limit: Maximum hits (server default 20).
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/search",
            params={
                "q": q,
                "mode": mode,
                "question_id": question_id,
                "completed_only": completed_only,
                "include_simulated": include_simulated,
                "include_test_runs": include_test_runs,
                "external_participant_id": external_participant_id,
                "strict": strict,
                "limit": limit,
            },
        )
        return SearchOut.model_validate(data)


class AsyncTranscripts:
    """Asynchronous interface for bulk transcript export and search over participant answers."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        study_id: Union[str, UUID],
        *,
        completed: Optional[bool] = None,
        include_simulated: Optional[bool] = None,
        include_test_runs: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> TranscriptsBulkOut:
        """Fetch transcripts in bulk. See :meth:`Transcripts.list`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/transcripts",
            params={
                "completed": completed,
                "include_simulated": include_simulated,
                "include_test_runs": include_test_runs,
                "external_participant_id": external_participant_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return TranscriptsBulkOut.model_validate(data)

    async def search(
        self,
        study_id: Union[str, UUID],
        *,
        q: str,
        mode: Union[str, SearchMode, None] = None,
        question_id: Optional[str] = None,
        completed_only: Optional[bool] = None,
        include_simulated: Optional[bool] = None,
        include_test_runs: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        strict: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> SearchOut:
        """Search participant answers. See :meth:`Transcripts.search`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/search",
            params={
                "q": q,
                "mode": mode,
                "question_id": question_id,
                "completed_only": completed_only,
                "include_simulated": include_simulated,
                "include_test_runs": include_test_runs,
                "external_participant_id": external_participant_id,
                "strict": strict,
                "limit": limit,
            },
        )
        return SearchOut.model_validate(data)
