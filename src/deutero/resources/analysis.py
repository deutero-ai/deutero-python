"""Analysis & clustering resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import (
    AnalysisCategory,
    AnalyzableQuestionsOut,
    ClusteringOut,
    OptimalClustersOut,
    OptionsResponsesOut,
    ScaleResponsesOut,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Analysis:
    """Synchronous interface for per-question aggregations and response clustering.

    ``question_id`` arguments take a question ID for linear studies, or the graph step ID
    you authored for flow studies.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list_questions(
        self,
        study_id: Union[str, UUID],
        *,
        category: Union[str, AnalysisCategory],
    ) -> AnalyzableQuestionsOut:
        """List the study's questions eligible for an analysis view.

        Args:
            study_id: The study.
            category: ``"text"`` (clusterable free text), ``"scale"`` or ``"options"``.
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/analysis/questions",
            params={"category": category},
        )
        return AnalyzableQuestionsOut.model_validate(data)

    def get_scale_responses(self, study_id: Union[str, UUID], *, question_id: str) -> ScaleResponsesOut:
        """Tally responses per scale value for a scale question."""
        data = self._client.get(
            f"/api/v1/studies/{study_id}/analysis/responses/scale",
            params={"question_id": question_id},
        )
        return ScaleResponsesOut.model_validate(data)

    def get_options_responses(self, study_id: Union[str, UUID], *, question_id: str) -> OptionsResponsesOut:
        """Tally responses per option for a single- or multi-select question."""
        data = self._client.get(
            f"/api/v1/studies/{study_id}/analysis/responses/options",
            params={"question_id": question_id},
        )
        return OptionsResponsesOut.model_validate(data)

    def cluster(
        self,
        study_id: Union[str, UUID],
        *,
        question_id: Optional[str] = None,
        question_number: Optional[int] = None,
        n_clusters: Optional[int] = None,
    ) -> ClusteringOut:
        """Group participants' free-text answers to one question into labeled themes (k-means).

        The result is saved and becomes the study's latest clustering run.

        Args:
            study_id: The study.
            question_id: The question to cluster.
            question_number: Alternative to ``question_id`` for linear studies.
            n_clusters: Number of clusters, 2-20 (server default 3). Too few responses for
                the requested count raises :class:`~deutero.exceptions.ValidationError`.
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/analysis/cluster",
            json=compact(question_id=question_id, question_number=question_number, n_clusters=n_clusters),
        )
        return ClusteringOut.model_validate(data)

    def get_optimal_clusters(
        self,
        study_id: Union[str, UUID],
        *,
        question_id: Optional[str] = None,
        question_number: Optional[int] = None,
    ) -> OptimalClustersOut:
        """Estimate the best cluster count for a question using the elbow method."""
        data = self._client.post(
            f"/api/v1/studies/{study_id}/analysis/optimal-clusters",
            json=compact(question_id=question_id, question_number=question_number),
        )
        return OptimalClustersOut.model_validate(data)

    def get_latest_clustering(self, study_id: Union[str, UUID]) -> ClusteringOut:
        """Get the study's most recent saved clustering run. ``exists`` is ``False`` if there is none."""
        data = self._client.get(f"/api/v1/studies/{study_id}/analysis/clustering/latest")
        return ClusteringOut.model_validate(data)


class AsyncAnalysis:
    """Asynchronous interface for per-question aggregations and response clustering."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_questions(
        self,
        study_id: Union[str, UUID],
        *,
        category: Union[str, AnalysisCategory],
    ) -> AnalyzableQuestionsOut:
        """List analyzable questions. See :meth:`Analysis.list_questions`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/analysis/questions",
            params={"category": category},
        )
        return AnalyzableQuestionsOut.model_validate(data)

    async def get_scale_responses(self, study_id: Union[str, UUID], *, question_id: str) -> ScaleResponsesOut:
        """Tally scale responses. See :meth:`Analysis.get_scale_responses`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/analysis/responses/scale",
            params={"question_id": question_id},
        )
        return ScaleResponsesOut.model_validate(data)

    async def get_options_responses(self, study_id: Union[str, UUID], *, question_id: str) -> OptionsResponsesOut:
        """Tally options responses. See :meth:`Analysis.get_options_responses`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/analysis/responses/options",
            params={"question_id": question_id},
        )
        return OptionsResponsesOut.model_validate(data)

    async def cluster(
        self,
        study_id: Union[str, UUID],
        *,
        question_id: Optional[str] = None,
        question_number: Optional[int] = None,
        n_clusters: Optional[int] = None,
    ) -> ClusteringOut:
        """Cluster responses. See :meth:`Analysis.cluster`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/analysis/cluster",
            json=compact(question_id=question_id, question_number=question_number, n_clusters=n_clusters),
        )
        return ClusteringOut.model_validate(data)

    async def get_optimal_clusters(
        self,
        study_id: Union[str, UUID],
        *,
        question_id: Optional[str] = None,
        question_number: Optional[int] = None,
    ) -> OptimalClustersOut:
        """Estimate the cluster count. See :meth:`Analysis.get_optimal_clusters`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/analysis/optimal-clusters",
            json=compact(question_id=question_id, question_number=question_number),
        )
        return OptimalClustersOut.model_validate(data)

    async def get_latest_clustering(self, study_id: Union[str, UUID]) -> ClusteringOut:
        """Get the latest clustering run. See :meth:`Analysis.get_latest_clustering`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/analysis/clustering/latest")
        return ClusteringOut.model_validate(data)
