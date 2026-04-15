"""Studies (surveys) resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero.models import (
    AgentRequirementsResponse,
    ModelTierInfo,
    ParticipationStats,
    StudyGenerateParams,
    StudyGenerateResponse,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Studies:
    """Synchronous interface for study operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def generate(
        self,
        *,
        study_type: str = "user_experience",
        language: Optional[str] = "English",
        business_context: Optional[str] = None,
        research_need: Optional[str] = None,
        target_users: Optional[str] = None,
        constraints: Optional[str] = None,
        research_question: Optional[str] = None,
        population_of_interest: Optional[str] = None,
        context_or_setting: Optional[str] = None,
        key_concepts: Optional[str] = None,
        scope_and_boundaries: Optional[str] = None,
        problem_hypothesis: Optional[str] = None,
        customer_segment: Optional[str] = None,
        solution_concept: Optional[str] = None,
        key_assumptions: Optional[str] = None,
        success_criteria: Optional[str] = None,
        population_segment: Optional[str] = None,
        geographic_scope: Optional[str] = None,
        survey_context: Optional[str] = None,
        data_quality_requirements: Optional[str] = None,
        model_tier: Optional[str] = None,
    ) -> StudyGenerateResponse:
        """Generate a new research study.

        Args:
            study_type: Type of study — ``"user_experience"``, ``"sociology"``,
                ``"customer_development"``, or ``"polling"``.
            language: Language for the study (default ``"English"``).
            business_context: Business/product context (UX research).
            research_need: Why the research is needed (UX research).
            target_users: Primary audience (UX research).
            constraints: Constraints or considerations (UX research).
            research_question: The research question (sociology / polling).
            population_of_interest: Population of interest (sociology).
            context_or_setting: Context or setting (sociology).
            key_concepts: Key concepts (sociology).
            scope_and_boundaries: Scope and boundaries (sociology).
            problem_hypothesis: Problem hypothesis (customer development).
            customer_segment: Customer segment (customer development).
            solution_concept: Solution concept (customer development).
            key_assumptions: Key assumptions (customer development).
            success_criteria: Success criteria (customer development).
            population_segment: Population segment (polling).
            geographic_scope: Geographic scope (polling).
            survey_context: Survey context (polling).
            data_quality_requirements: Data quality requirements (polling).
            model_tier: Model tier — ``"open_weights"``, ``"premium"``, or ``"frontier"``.

        Returns:
            The generated study with its ID, name, description, and XML specification.
        """
        params = StudyGenerateParams(
            study_type=study_type,
            language=language,
            business_context=business_context,
            research_need=research_need,
            target_users=target_users,
            constraints=constraints,
            research_question=research_question,
            population_of_interest=population_of_interest,
            context_or_setting=context_or_setting,
            key_concepts=key_concepts,
            scope_and_boundaries=scope_and_boundaries,
            problem_hypothesis=problem_hypothesis,
            customer_segment=customer_segment,
            solution_concept=solution_concept,
            key_assumptions=key_assumptions,
            success_criteria=success_criteria,
            population_segment=population_segment,
            geographic_scope=geographic_scope,
            survey_context=survey_context,
            data_quality_requirements=data_quality_requirements,
            model_tier=model_tier,
        )
        data = self._client.post(
            "/api/v1/surveys/generate",
            json=params.model_dump(exclude_none=True),
        )
        return StudyGenerateResponse.model_validate(data)

    def get_participation(self, study_id: Union[str, UUID]) -> ParticipationStats:
        """Get participation statistics for a study.

        Args:
            study_id: UUID of the study.

        Returns:
            Participation and completion statistics.
        """
        data = self._client.get(f"/api/v1/surveys/{study_id}/participation")
        return ParticipationStats.model_validate(data)

    def get_agent_requirements(self, study_id: Union[str, UUID]) -> AgentRequirementsResponse:
        """Get or generate agent requirements markdown for a study.

        Args:
            study_id: UUID of the study.

        Returns:
            Markdown document with user requirements derived from analysis.
        """
        data = self._client.post(f"/api/v1/surveys/{study_id}/agent-requirements")
        return AgentRequirementsResponse.model_validate(data)

    def get_model_tier(self, study_id: Union[str, UUID]) -> ModelTierInfo:
        """Get the current model tier of a study.

        Args:
            study_id: UUID of the study.

        Returns:
            Current model tier configuration.
        """
        data = self._client.get(f"/api/v1/surveys/{study_id}/model-tier")
        return ModelTierInfo.model_validate(data)

    def set_model_tier(self, study_id: Union[str, UUID], *, model_tier: str) -> ModelTierInfo:
        """Set the model tier of a study.

        Args:
            study_id: UUID of the study.
            model_tier: One of ``"open_weights"``, ``"premium"``, or ``"frontier"``.

        Returns:
            Updated model tier configuration.
        """
        data = self._client.put(
            f"/api/v1/surveys/{study_id}/model-tier",
            json={"model_tier": model_tier},
        )
        return ModelTierInfo.model_validate(data)


class AsyncStudies:
    """Asynchronous interface for study operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def generate(
        self,
        *,
        study_type: str = "user_experience",
        language: Optional[str] = "English",
        business_context: Optional[str] = None,
        research_need: Optional[str] = None,
        target_users: Optional[str] = None,
        constraints: Optional[str] = None,
        research_question: Optional[str] = None,
        population_of_interest: Optional[str] = None,
        context_or_setting: Optional[str] = None,
        key_concepts: Optional[str] = None,
        scope_and_boundaries: Optional[str] = None,
        problem_hypothesis: Optional[str] = None,
        customer_segment: Optional[str] = None,
        solution_concept: Optional[str] = None,
        key_assumptions: Optional[str] = None,
        success_criteria: Optional[str] = None,
        population_segment: Optional[str] = None,
        geographic_scope: Optional[str] = None,
        survey_context: Optional[str] = None,
        data_quality_requirements: Optional[str] = None,
        model_tier: Optional[str] = None,
    ) -> StudyGenerateResponse:
        """Generate a new research study. See :meth:`Studies.generate` for parameter docs."""
        params = StudyGenerateParams(
            study_type=study_type,
            language=language,
            business_context=business_context,
            research_need=research_need,
            target_users=target_users,
            constraints=constraints,
            research_question=research_question,
            population_of_interest=population_of_interest,
            context_or_setting=context_or_setting,
            key_concepts=key_concepts,
            scope_and_boundaries=scope_and_boundaries,
            problem_hypothesis=problem_hypothesis,
            customer_segment=customer_segment,
            solution_concept=solution_concept,
            key_assumptions=key_assumptions,
            success_criteria=success_criteria,
            population_segment=population_segment,
            geographic_scope=geographic_scope,
            survey_context=survey_context,
            data_quality_requirements=data_quality_requirements,
            model_tier=model_tier,
        )
        data = await self._client.post(
            "/api/v1/surveys/generate",
            json=params.model_dump(exclude_none=True),
        )
        return StudyGenerateResponse.model_validate(data)

    async def get_participation(self, study_id: Union[str, UUID]) -> ParticipationStats:
        """Get participation statistics for a study."""
        data = await self._client.get(f"/api/v1/surveys/{study_id}/participation")
        return ParticipationStats.model_validate(data)

    async def get_agent_requirements(self, study_id: Union[str, UUID]) -> AgentRequirementsResponse:
        """Get or generate agent requirements markdown for a study."""
        data = await self._client.post(f"/api/v1/surveys/{study_id}/agent-requirements")
        return AgentRequirementsResponse.model_validate(data)

    async def get_model_tier(self, study_id: Union[str, UUID]) -> ModelTierInfo:
        """Get the current model tier of a study."""
        data = await self._client.get(f"/api/v1/surveys/{study_id}/model-tier")
        return ModelTierInfo.model_validate(data)

    async def set_model_tier(self, study_id: Union[str, UUID], *, model_tier: str) -> ModelTierInfo:
        """Set the model tier of a study."""
        data = await self._client.put(
            f"/api/v1/surveys/{study_id}/model-tier",
            json={"model_tier": model_tier},
        )
        return ModelTierInfo.model_validate(data)
