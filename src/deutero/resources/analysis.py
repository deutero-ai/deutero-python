"""Analysis resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero.models import (
    AnalysisRunResponse,
    AnalysisStatusResponse,
    CrossCaseAnalysisResult,
    InterviewAnalysisResult,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Analysis:
    """Synchronous interface for thematic analysis operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def run(
        self,
        *,
        interview_id: Optional[Union[str, UUID]] = None,
        study_id: Optional[Union[str, UUID]] = None,
        model_tier: str = "open_weights",
        cross_case_analysis: bool = False,
    ) -> AnalysisRunResponse:
        """Run thematic analysis on interviews.

        **Individual analysis (phases 1–4):**
        Provide ``interview_id`` for a single interview, or ``study_id`` to
        analyze all completed interviews. Runs in the background.

        **Cross-case analysis (phase 5):**
        Provide ``study_id`` and set ``cross_case_analysis=True``. Requires
        at least 3 interviews with completed phases 1–4. Runs synchronously.

        Args:
            interview_id: UUID of a specific interview.
            study_id: UUID of a study.
            model_tier: ``"open_weights"``, ``"premium"``, or ``"frontier"``.
            cross_case_analysis: Whether to run cross-case analysis.

        Returns:
            Analysis job info with queued interviews and credit usage.
        """
        payload = {
            "model_tier": model_tier,
            "cross_case_analysis": cross_case_analysis,
        }
        if interview_id is not None:
            payload["interview_id"] = str(interview_id)
        if study_id is not None:
            payload["study_id"] = str(study_id)

        data = self._client.post("/api/v1/analysis/run", json=payload)
        return AnalysisRunResponse.model_validate(data)

    def get_status(
        self,
        *,
        interview_id: Optional[Union[str, UUID]] = None,
        study_id: Optional[Union[str, UUID]] = None,
    ) -> AnalysisStatusResponse:
        """Get analysis status for interviews.

        Provide either ``interview_id`` for a single interview or ``study_id``
        for all interviews in a study.

        Args:
            interview_id: UUID of a specific interview.
            study_id: UUID of a study.

        Returns:
            Status and phase completion for each interview.
        """
        params = {}
        if interview_id is not None:
            params["interview_id"] = str(interview_id)
        if study_id is not None:
            params["survey_id"] = str(study_id)

        data = self._client.get("/api/v1/analysis/status", params=params)
        return AnalysisStatusResponse.model_validate(data)

    def get_interview_results(
        self,
        *,
        interview_id: Union[str, UUID],
        phase: str,
    ) -> InterviewAnalysisResult:
        """Get analysis results for a specific phase of an interview.

        Args:
            interview_id: UUID of the interview.
            phase: One of ``"initial_engagement"``, ``"initial_noting"``,
                ``"emergent_themes"``, or ``"connections"``.

        Returns:
            The XML output for the requested phase.
        """
        data = self._client.get(
            "/api/v1/analysis/results/interview",
            params={
                "interview_id": str(interview_id),
                "phase": phase,
            },
        )
        return InterviewAnalysisResult.model_validate(data)

    def get_survey_results(self, *, study_id: Union[str, UUID]) -> CrossCaseAnalysisResult:
        """Get cross-case analysis results for a survey.

        Args:
            study_id: UUID of the survey.

        Returns:
            The cross-case analysis XML output.
        """
        data = self._client.get(
            "/api/v1/analysis/results/survey",
            params={"survey_id": str(study_id)},
        )
        return CrossCaseAnalysisResult.model_validate(data)


class AsyncAnalysis:
    """Asynchronous interface for thematic analysis operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def run(
        self,
        *,
        interview_id: Optional[Union[str, UUID]] = None,
        study_id: Optional[Union[str, UUID]] = None,
        model_tier: str = "open_weights",
        cross_case_analysis: bool = False,
    ) -> AnalysisRunResponse:
        """Run thematic analysis on interviews. See :meth:`Analysis.run`."""
        payload = {
            "model_tier": model_tier,
            "cross_case_analysis": cross_case_analysis,
        }
        if interview_id is not None:
            payload["interview_id"] = str(interview_id)
        if study_id is not None:
            payload["study_id"] = str(study_id)

        data = await self._client.post("/api/v1/analysis/run", json=payload)
        return AnalysisRunResponse.model_validate(data)

    async def get_status(
        self,
        *,
        interview_id: Optional[Union[str, UUID]] = None,
        study_id: Optional[Union[str, UUID]] = None,
    ) -> AnalysisStatusResponse:
        """Get analysis status. See :meth:`Analysis.get_status`."""
        params = {}
        if interview_id is not None:
            params["interview_id"] = str(interview_id)
        if study_id is not None:
            params["survey_id"] = str(study_id)

        data = await self._client.get("/api/v1/analysis/status", params=params)
        return AnalysisStatusResponse.model_validate(data)

    async def get_interview_results(
        self,
        *,
        interview_id: Union[str, UUID],
        phase: str,
    ) -> InterviewAnalysisResult:
        """Get interview analysis results. See :meth:`Analysis.get_interview_results`."""
        data = await self._client.get(
            "/api/v1/analysis/results/interview",
            params={
                "interview_id": str(interview_id),
                "phase": phase,
            },
        )
        return InterviewAnalysisResult.model_validate(data)

    async def get_survey_results(self, *, study_id: Union[str, UUID]) -> CrossCaseAnalysisResult:
        """Get cross-case analysis results. See :meth:`Analysis.get_survey_results`."""
        data = await self._client.get(
            "/api/v1/analysis/results/survey",
            params={"survey_id": str(study_id)},
        )
        return CrossCaseAnalysisResult.model_validate(data)
