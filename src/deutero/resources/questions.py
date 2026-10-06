"""Interview questions resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import (
    GeneratedQuestionsOut,
    QuestionListOut,
    QuestionOut,
    ScaleConfig,
    SuccessResponse,
    ValidationOut,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Questions:
    """Synchronous interface for a study's linear interview question list."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list(self, study_id: Union[str, UUID]) -> QuestionListOut:
        """List the study's main questions, in interview order."""
        data = self._client.get(f"/api/v1/studies/{study_id}/questions")
        return QuestionListOut.model_validate(data)

    def create(
        self,
        study_id: Union[str, UUID],
        *,
        question: str,
        qtype: Optional[str] = None,
        explanation: Optional[str] = None,
        scale: Union[ScaleConfig, Dict[str, Any], None] = None,
        options: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        min_select: Optional[int] = None,
        max_select: Optional[int] = None,
        follow_up: Optional[bool] = None,
        min_turns: Optional[int] = None,
        max_turns: Optional[int] = None,
        expected_image: Optional[str] = None,
    ) -> QuestionOut:
        """Create a question and append it to the end of the study's question list.

        If ``qtype`` is omitted the type is inferred from the config you pass: ``scale`` →
        scale, ``options`` → choices, ``slots`` → slots, ``expected_image`` → image_upload,
        otherwise text.

        Args:
            study_id: The study.
            question: Question text.
            qtype: Explicit question type, e.g. ``"text"``, ``"scale"``, ``"choices"``,
                ``"multi_select"``, ``"ranking"``, ``"slots"``, ``"card_sort"`` or
                ``"image_upload"``. ``image_upload`` needs the standard or premium model tier.
            explanation: Interviewer guidance for probing this question.
            scale: Scale config (scale questions), e.g.
                ``{"minScale": 1, "maxScale": 5, "minLabel": "Not at all", "maxLabel": "Very"}``.
            options: Answer options (choices / multi_select / ranking questions).
            slots: Named slots to fill (slots questions).
            groups: Bucket names (card_sort questions).
            min_select: Minimum selections (multi_select).
            max_select: Maximum selections (multi_select).
            follow_up: Whether the interviewer asks follow-ups (server default ``True``).
            min_turns: Minimum conversation turns.
            max_turns: Maximum conversation turns.
            expected_image: Description of the expected upload (image_upload questions).
        """
        payload = compact(
            question=question,
            qtype=qtype,
            explanation=explanation,
            scale=scale,
            options=options,
            slots=slots,
            groups=groups,
            min_select=min_select,
            max_select=max_select,
            follow_up=follow_up,
            min_turns=min_turns,
            max_turns=max_turns,
            expected_image=expected_image,
        )
        data = self._client.post(f"/api/v1/studies/{study_id}/questions", json=payload)
        return QuestionOut.model_validate(data)

    def generate(
        self,
        study_id: Union[str, UUID],
        *,
        n_questions: Optional[int] = None,
        additional_instructions: Optional[str] = None,
    ) -> GeneratedQuestionsOut:
        """Write interview questions with AI and append them to the study's question list.

        The generator works from the study's research question, objectives, methodology and
        target population, and picks a mix of question types in the study's language. New
        questions extend any existing list rather than repeating it; nothing is replaced.
        A model call that typically takes 30 seconds to two minutes.

        Args:
            study_id: The study.
            n_questions: How many questions to generate, 3-20 (server default 10).
            additional_instructions: Extra guidance, e.g. ``"start with two warm-up questions"``.
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/questions/generate",
            json=compact(n_questions=n_questions, additional_instructions=additional_instructions),
        )
        return GeneratedQuestionsOut.model_validate(data)

    def update(
        self,
        study_id: Union[str, UUID],
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        qtype: Optional[str] = None,
        explanation: Optional[str] = None,
        scale: Union[ScaleConfig, Dict[str, Any], None] = None,
        options: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        min_select: Optional[int] = None,
        max_select: Optional[int] = None,
        follow_up: Optional[bool] = None,
        min_turns: Optional[int] = None,
        max_turns: Optional[int] = None,
        expected_image: Optional[str] = None,
    ) -> QuestionOut:
        """Partially update a question. Only the arguments you pass are changed.

        Pass an empty list to clear ``options``, ``slots`` or ``groups``. See :meth:`create`
        for argument meanings.
        """
        payload = compact(
            question=question,
            qtype=qtype,
            explanation=explanation,
            scale=scale,
            options=options,
            slots=slots,
            groups=groups,
            min_select=min_select,
            max_select=max_select,
            follow_up=follow_up,
            min_turns=min_turns,
            max_turns=max_turns,
            expected_image=expected_image,
        )
        data = self._client.patch(f"/api/v1/studies/{study_id}/questions/{question_id}", json=payload)
        return QuestionOut.model_validate(data)

    def delete(self, study_id: Union[str, UUID], question_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a question and its attached images; remaining questions are renumbered."""
        data = self._client.delete(f"/api/v1/studies/{study_id}/questions/{question_id}")
        return SuccessResponse.model_validate(data)

    def reorder(
        self,
        study_id: Union[str, UUID],
        *,
        question_ids: Sequence[Union[str, UUID]],
    ) -> QuestionListOut:
        """Reorder the question list. Supply every question ID in the desired interview order."""
        data = self._client.put(
            f"/api/v1/studies/{study_id}/questions/order",
            json={"question_ids": [str(q) for q in question_ids]},
        )
        return QuestionListOut.model_validate(data)

    def validate(self, study_id: Union[str, UUID]) -> ValidationOut:
        """Review the questions before the study goes live.

        Returns an overall ethics pass/fail plus per-question language-quality and
        redundancy findings — the same check the dashboard's **Validate** button runs.
        """
        data = self._client.post(f"/api/v1/studies/{study_id}/questions/validate")
        return ValidationOut.model_validate(data)


class AsyncQuestions:
    """Asynchronous interface for a study's linear interview question list."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(self, study_id: Union[str, UUID]) -> QuestionListOut:
        """List questions. See :meth:`Questions.list`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/questions")
        return QuestionListOut.model_validate(data)

    async def create(
        self,
        study_id: Union[str, UUID],
        *,
        question: str,
        qtype: Optional[str] = None,
        explanation: Optional[str] = None,
        scale: Union[ScaleConfig, Dict[str, Any], None] = None,
        options: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        min_select: Optional[int] = None,
        max_select: Optional[int] = None,
        follow_up: Optional[bool] = None,
        min_turns: Optional[int] = None,
        max_turns: Optional[int] = None,
        expected_image: Optional[str] = None,
    ) -> QuestionOut:
        """Create a question. See :meth:`Questions.create`."""
        payload = compact(
            question=question,
            qtype=qtype,
            explanation=explanation,
            scale=scale,
            options=options,
            slots=slots,
            groups=groups,
            min_select=min_select,
            max_select=max_select,
            follow_up=follow_up,
            min_turns=min_turns,
            max_turns=max_turns,
            expected_image=expected_image,
        )
        data = await self._client.post(f"/api/v1/studies/{study_id}/questions", json=payload)
        return QuestionOut.model_validate(data)

    async def generate(
        self,
        study_id: Union[str, UUID],
        *,
        n_questions: Optional[int] = None,
        additional_instructions: Optional[str] = None,
    ) -> GeneratedQuestionsOut:
        """Generate questions with AI. See :meth:`Questions.generate`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/questions/generate",
            json=compact(n_questions=n_questions, additional_instructions=additional_instructions),
        )
        return GeneratedQuestionsOut.model_validate(data)

    async def update(
        self,
        study_id: Union[str, UUID],
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        qtype: Optional[str] = None,
        explanation: Optional[str] = None,
        scale: Union[ScaleConfig, Dict[str, Any], None] = None,
        options: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        min_select: Optional[int] = None,
        max_select: Optional[int] = None,
        follow_up: Optional[bool] = None,
        min_turns: Optional[int] = None,
        max_turns: Optional[int] = None,
        expected_image: Optional[str] = None,
    ) -> QuestionOut:
        """Update a question. See :meth:`Questions.update`."""
        payload = compact(
            question=question,
            qtype=qtype,
            explanation=explanation,
            scale=scale,
            options=options,
            slots=slots,
            groups=groups,
            min_select=min_select,
            max_select=max_select,
            follow_up=follow_up,
            min_turns=min_turns,
            max_turns=max_turns,
            expected_image=expected_image,
        )
        data = await self._client.patch(f"/api/v1/studies/{study_id}/questions/{question_id}", json=payload)
        return QuestionOut.model_validate(data)

    async def delete(self, study_id: Union[str, UUID], question_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a question. See :meth:`Questions.delete`."""
        data = await self._client.delete(f"/api/v1/studies/{study_id}/questions/{question_id}")
        return SuccessResponse.model_validate(data)

    async def reorder(
        self,
        study_id: Union[str, UUID],
        *,
        question_ids: Sequence[Union[str, UUID]],
    ) -> QuestionListOut:
        """Reorder questions. See :meth:`Questions.reorder`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/questions/order",
            json={"question_ids": [str(q) for q in question_ids]},
        )
        return QuestionListOut.model_validate(data)

    async def validate(self, study_id: Union[str, UUID]) -> ValidationOut:
        """Validate questions. See :meth:`Questions.validate`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/questions/validate")
        return ValidationOut.model_validate(data)
