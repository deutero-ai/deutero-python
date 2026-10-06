"""Studies resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import (
    ModelTier,
    PauseOut,
    PublicationStatusOut,
    PublishOut,
    StudyDraft,
    StudyDraftFromSiteOut,
    StudyListOut,
    StudyOut,
    StudyStatsOut,
    StudyType,
    ValidationRunOut,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Studies:
    """Synchronous interface for study operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        project_id: Union[str, UUID],
        name: str,
        description: Optional[str] = None,
        survey_type: Union[str, StudyType, None] = None,
        research_question: Optional[str] = None,
        objectives: Optional[str] = None,
        target_population: Optional[str] = None,
        methodology: Optional[str] = None,
        benefits: Optional[str] = None,
        risks: Optional[str] = None,
        support_contact: Optional[str] = None,
        institution: Optional[str] = None,
        language: Optional[str] = None,
        anonymous: Optional[bool] = None,
        model_tier: Union[str, ModelTier, None] = None,
        redirect_url: Optional[str] = None,
        max_responses: Optional[int] = None,
        voice_enabled: Optional[bool] = None,
        video_enabled: Optional[bool] = None,
    ) -> StudyOut:
        """Create a new study inside a project.

        The study starts with an empty question list in linear interview mode. Configure
        the rest with the welcome, screening, characteristics, questions, recruitment and
        embed resources.

        Args:
            project_id: Project to create the study in.
            name: Study name shown to participants.
            description: Study description.
            survey_type: ``"sociology"`` (server default), ``"user_experience"``,
                ``"customer_development"`` or ``"polling"``.
            research_question: The research question(s).
            objectives: Research objectives.
            target_population: Target participant population.
            methodology: Methodology notes.
            benefits: Participation benefits (used in consent).
            risks: Participation risks (used in consent).
            support_contact: Researcher/support contact.
            institution: Institutional affiliation.
            language: Primary interview language (server default ``"English"``).
            anonymous: Skip collecting participant first names.
            model_tier: ``"open_weights"`` (server default), ``"standard"`` or ``"premium"``.
            redirect_url: URL participants are sent to after completing. May contain
                ``{{external_participant_id}}``.
            max_responses: Response quota (omit for unlimited).
            voice_enabled: Offer a voice-call interview link alongside text chat.
            video_enabled: Offer a video-call interview link alongside text chat.
        """
        payload = compact(
            project_id=project_id,
            name=name,
            description=description,
            survey_type=survey_type,
            research_question=research_question,
            objectives=objectives,
            target_population=target_population,
            methodology=methodology,
            benefits=benefits,
            risks=risks,
            support_contact=support_contact,
            institution=institution,
            language=language,
            anonymous=anonymous,
            model_tier=model_tier,
            redirect_url=redirect_url,
            max_responses=max_responses,
            voice_enabled=voice_enabled,
            video_enabled=video_enabled,
        )
        data = self._client.post("/api/v1/studies", json=payload)
        return StudyOut.model_validate(data)

    def list(self, project_id: Union[str, UUID]) -> StudyListOut:
        """List the studies in a project."""
        data = self._client.get(f"/api/v1/projects/{project_id}/studies")
        return StudyListOut.model_validate(data)

    def get(self, study_id: Union[str, UUID]) -> StudyOut:
        """Get a study's full configuration, lifecycle-stage status and participation links."""
        data = self._client.get(f"/api/v1/studies/{study_id}")
        return StudyOut.model_validate(data)

    def update(
        self,
        study_id: Union[str, UUID],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        survey_type: Union[str, StudyType, None] = None,
        research_question: Optional[str] = None,
        objectives: Optional[str] = None,
        target_population: Optional[str] = None,
        methodology: Optional[str] = None,
        benefits: Optional[str] = None,
        risks: Optional[str] = None,
        support_contact: Optional[str] = None,
        institution: Optional[str] = None,
        language: Optional[str] = None,
        anonymous: Optional[bool] = None,
        model_tier: Union[str, ModelTier, None] = None,
        redirect_url: Optional[str] = None,
        max_responses: Optional[int] = None,
        voice_enabled: Optional[bool] = None,
        video_enabled: Optional[bool] = None,
    ) -> StudyOut:
        """Partially update a study. Only the arguments you pass are changed.

        See :meth:`create` for argument meanings. To remove a response quota use
        :meth:`Recruitment.update` with ``clear_max_responses=True``.
        """
        payload = compact(
            name=name,
            description=description,
            survey_type=survey_type,
            research_question=research_question,
            objectives=objectives,
            target_population=target_population,
            methodology=methodology,
            benefits=benefits,
            risks=risks,
            support_contact=support_contact,
            institution=institution,
            language=language,
            anonymous=anonymous,
            model_tier=model_tier,
            redirect_url=redirect_url,
            max_responses=max_responses,
            voice_enabled=voice_enabled,
            video_enabled=video_enabled,
        )
        data = self._client.patch(f"/api/v1/studies/{study_id}", json=payload)
        return StudyOut.model_validate(data)

    def get_stats(self, study_id: Union[str, UUID]) -> StudyStatsOut:
        """Get participation statistics: interview counts, completion rate and quota fill."""
        data = self._client.get(f"/api/v1/studies/{study_id}/stats")
        return StudyStatsOut.model_validate(data)

    def draft(
        self,
        *,
        survey_type: Union[str, StudyType],
        language: Optional[str] = None,
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
        business_context: Optional[str] = None,
        research_need: Optional[str] = None,
        target_users: Optional[str] = None,
        research_type: Optional[str] = None,
        constraints: Optional[str] = None,
        population_segment: Optional[str] = None,
        geographic_scope: Optional[str] = None,
        survey_context: Optional[str] = None,
        data_quality_requirements: Optional[str] = None,
    ) -> StudyDraft:
        """Turn a short research brief into a study draft with AI. Nothing is stored.

        Review or edit the draft, then pass its fields to :meth:`create` (with a
        ``project_id``). The draft has no interview questions: create the study, then call
        :meth:`Questions.generate`. This is a model call that typically takes 20-40 seconds.

        Only the brief fields for the chosen ``survey_type`` are read:

        * ``"sociology"``: ``research_question`` and ``population_of_interest`` (required),
          ``context_or_setting``, ``key_concepts``, ``scope_and_boundaries``.
        * ``"customer_development"``: ``problem_hypothesis`` and ``customer_segment``
          (required), ``solution_concept``, ``key_assumptions``, ``success_criteria``.
        * ``"user_experience"``: ``business_context`` and ``research_need`` (required),
          ``target_users``, ``research_type`` (discover, test or ideate), ``constraints``.
        * ``"polling"``: ``research_question`` (required), ``population_segment``,
          ``geographic_scope``, ``survey_context``, ``data_quality_requirements``.

        Args:
            survey_type: Study methodology; decides which brief fields are read.
            language: Language to write the draft in, which is also the study's interview
                language (server default ``"English"``).
        """
        payload = compact(
            survey_type=survey_type,
            language=language,
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
            business_context=business_context,
            research_need=research_need,
            target_users=target_users,
            research_type=research_type,
            constraints=constraints,
            population_segment=population_segment,
            geographic_scope=geographic_scope,
            survey_context=survey_context,
            data_quality_requirements=data_quality_requirements,
        )
        data = self._client.post("/api/v1/study-drafts", json=payload)
        return StudyDraft.model_validate(data)

    def draft_from_site(self, *, url: str, language: Optional[str] = None) -> StudyDraftFromSiteOut:
        """Read a product landing page and draft a user research study for it with AI.

        Nothing is stored. When ``is_valid``, pass the ``draft`` fields to :meth:`create`
        (with a ``project_id``); otherwise ``draft`` is ``None`` and ``rationale`` says what
        was missing. Each site allows a limited number of drafts per user (the API answers
        429 past it). This fetches the page and makes a model call that typically takes
        20-40 seconds.

        Args:
            url: Public http(s) URL of the product or startup landing page.
            language: Language to write the draft and rationale in (server default ``"English"``).
        """
        data = self._client.post("/api/v1/study-drafts/from-site", json=compact(url=url, language=language))
        return StudyDraftFromSiteOut.model_validate(data)

    def get_publication(self, study_id: Union[str, UUID]) -> PublicationStatusOut:
        """Get the study's publication status: draft, open, paused or closed.

        Also reports how many studies the plan may have open, the publish-time credit check
        and the latest validation run.
        """
        data = self._client.get(f"/api/v1/studies/{study_id}/publication")
        return PublicationStatusOut.model_validate(data)

    def validate(self, study_id: Union[str, UUID]) -> ValidationRunOut:
        """Validate everything participants will read, without publishing.

        Checks the questions or flow, welcome, screening and characteristics for ethical,
        blocking and methodological issues and records the result; :meth:`publish` reuses it
        while the configuration is unchanged. A model call: allow up to a minute.
        """
        data = self._client.post(f"/api/v1/studies/{study_id}/validate")
        return ValidationRunOut.model_validate(data)

    def publish(
        self,
        study_id: Union[str, UUID],
        *,
        acknowledge_validation_run_id: Union[str, UUID, None] = None,
        acknowledge_credit_shortfall: Optional[bool] = None,
    ) -> PublishOut:
        """Open the study to participants, or resume a paused one.

        Checks the plan's open-study limit, credits and validation first. A refusal raises
        :class:`~deutero.ConflictError`; its ``body`` carries the refusal code, the issues and
        the ``validation_run_id``. Publishing an open study is a no-op (``already_open``).

        Args:
            study_id: The study.
            acknowledge_validation_run_id: To publish despite methodological issues, pass the
                ``validation_run_id`` from the refusal. Ethical and blocking issues cannot be
                acknowledged and must be fixed.
            acknowledge_credit_shortfall: Publish even though the balance covers at least one
                interview but not every remaining response.
        """
        payload = compact(
            acknowledge_validation_run_id=acknowledge_validation_run_id,
            acknowledge_credit_shortfall=acknowledge_credit_shortfall,
        )
        data = self._client.post(f"/api/v1/studies/{study_id}/publish", json=payload)
        return PublishOut.model_validate(data)

    def pause(self, study_id: Union[str, UUID]) -> PauseOut:
        """Stop admitting new participants and unlock editing. Resume with :meth:`publish`.

        Interviews already running finish on the configuration they started with;
        ``in_flight_count`` says how many.
        """
        data = self._client.post(f"/api/v1/studies/{study_id}/pause")
        return PauseOut.model_validate(data)


class AsyncStudies:
    """Asynchronous interface for study operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        project_id: Union[str, UUID],
        name: str,
        description: Optional[str] = None,
        survey_type: Union[str, StudyType, None] = None,
        research_question: Optional[str] = None,
        objectives: Optional[str] = None,
        target_population: Optional[str] = None,
        methodology: Optional[str] = None,
        benefits: Optional[str] = None,
        risks: Optional[str] = None,
        support_contact: Optional[str] = None,
        institution: Optional[str] = None,
        language: Optional[str] = None,
        anonymous: Optional[bool] = None,
        model_tier: Union[str, ModelTier, None] = None,
        redirect_url: Optional[str] = None,
        max_responses: Optional[int] = None,
        voice_enabled: Optional[bool] = None,
        video_enabled: Optional[bool] = None,
    ) -> StudyOut:
        """Create a study. See :meth:`Studies.create`."""
        payload = compact(
            project_id=project_id,
            name=name,
            description=description,
            survey_type=survey_type,
            research_question=research_question,
            objectives=objectives,
            target_population=target_population,
            methodology=methodology,
            benefits=benefits,
            risks=risks,
            support_contact=support_contact,
            institution=institution,
            language=language,
            anonymous=anonymous,
            model_tier=model_tier,
            redirect_url=redirect_url,
            max_responses=max_responses,
            voice_enabled=voice_enabled,
            video_enabled=video_enabled,
        )
        data = await self._client.post("/api/v1/studies", json=payload)
        return StudyOut.model_validate(data)

    async def list(self, project_id: Union[str, UUID]) -> StudyListOut:
        """List studies in a project. See :meth:`Studies.list`."""
        data = await self._client.get(f"/api/v1/projects/{project_id}/studies")
        return StudyListOut.model_validate(data)

    async def get(self, study_id: Union[str, UUID]) -> StudyOut:
        """Get a study. See :meth:`Studies.get`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}")
        return StudyOut.model_validate(data)

    async def update(
        self,
        study_id: Union[str, UUID],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        survey_type: Union[str, StudyType, None] = None,
        research_question: Optional[str] = None,
        objectives: Optional[str] = None,
        target_population: Optional[str] = None,
        methodology: Optional[str] = None,
        benefits: Optional[str] = None,
        risks: Optional[str] = None,
        support_contact: Optional[str] = None,
        institution: Optional[str] = None,
        language: Optional[str] = None,
        anonymous: Optional[bool] = None,
        model_tier: Union[str, ModelTier, None] = None,
        redirect_url: Optional[str] = None,
        max_responses: Optional[int] = None,
        voice_enabled: Optional[bool] = None,
        video_enabled: Optional[bool] = None,
    ) -> StudyOut:
        """Update a study. See :meth:`Studies.update`."""
        payload = compact(
            name=name,
            description=description,
            survey_type=survey_type,
            research_question=research_question,
            objectives=objectives,
            target_population=target_population,
            methodology=methodology,
            benefits=benefits,
            risks=risks,
            support_contact=support_contact,
            institution=institution,
            language=language,
            anonymous=anonymous,
            model_tier=model_tier,
            redirect_url=redirect_url,
            max_responses=max_responses,
            voice_enabled=voice_enabled,
            video_enabled=video_enabled,
        )
        data = await self._client.patch(f"/api/v1/studies/{study_id}", json=payload)
        return StudyOut.model_validate(data)

    async def get_stats(self, study_id: Union[str, UUID]) -> StudyStatsOut:
        """Get participation statistics. See :meth:`Studies.get_stats`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/stats")
        return StudyStatsOut.model_validate(data)

    async def draft(
        self,
        *,
        survey_type: Union[str, StudyType],
        language: Optional[str] = None,
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
        business_context: Optional[str] = None,
        research_need: Optional[str] = None,
        target_users: Optional[str] = None,
        research_type: Optional[str] = None,
        constraints: Optional[str] = None,
        population_segment: Optional[str] = None,
        geographic_scope: Optional[str] = None,
        survey_context: Optional[str] = None,
        data_quality_requirements: Optional[str] = None,
    ) -> StudyDraft:
        """Draft a study from a research brief. See :meth:`Studies.draft`."""
        payload = compact(
            survey_type=survey_type,
            language=language,
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
            business_context=business_context,
            research_need=research_need,
            target_users=target_users,
            research_type=research_type,
            constraints=constraints,
            population_segment=population_segment,
            geographic_scope=geographic_scope,
            survey_context=survey_context,
            data_quality_requirements=data_quality_requirements,
        )
        data = await self._client.post("/api/v1/study-drafts", json=payload)
        return StudyDraft.model_validate(data)

    async def draft_from_site(self, *, url: str, language: Optional[str] = None) -> StudyDraftFromSiteOut:
        """Draft a study from a landing page. See :meth:`Studies.draft_from_site`."""
        data = await self._client.post("/api/v1/study-drafts/from-site", json=compact(url=url, language=language))
        return StudyDraftFromSiteOut.model_validate(data)

    async def get_publication(self, study_id: Union[str, UUID]) -> PublicationStatusOut:
        """Get publication status. See :meth:`Studies.get_publication`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/publication")
        return PublicationStatusOut.model_validate(data)

    async def validate(self, study_id: Union[str, UUID]) -> ValidationRunOut:
        """Validate a study without publishing. See :meth:`Studies.validate`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/validate")
        return ValidationRunOut.model_validate(data)

    async def publish(
        self,
        study_id: Union[str, UUID],
        *,
        acknowledge_validation_run_id: Union[str, UUID, None] = None,
        acknowledge_credit_shortfall: Optional[bool] = None,
    ) -> PublishOut:
        """Publish a study. See :meth:`Studies.publish`."""
        payload = compact(
            acknowledge_validation_run_id=acknowledge_validation_run_id,
            acknowledge_credit_shortfall=acknowledge_credit_shortfall,
        )
        data = await self._client.post(f"/api/v1/studies/{study_id}/publish", json=payload)
        return PublishOut.model_validate(data)

    async def pause(self, study_id: Union[str, UUID]) -> PauseOut:
        """Pause a study. See :meth:`Studies.pause`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/pause")
        return PauseOut.model_validate(data)
