"""Questions resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

from deutero.models import (
    Question,
    QuestionGenerateResponse,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient

_SENTINEL = object()


def _build_question_update_payload(**kwargs: Any) -> Dict[str, Any]:
    """Build a payload dict containing only explicitly provided (non-sentinel) values."""
    return {k: v for k, v in kwargs.items() if v is not None}


class Questions:
    """Synchronous interface for question operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def generate(
        self,
        *,
        study_id: Union[str, UUID],
        number_of_questions: int,
        additional_instructions: Optional[str] = None,
    ) -> QuestionGenerateResponse:
        """Generate interview questions for a study.

        Args:
            study_id: UUID of the study to generate questions for.
            number_of_questions: Number of questions to generate (1–25).
            additional_instructions: Optional extra instructions for the AI.

        Returns:
            Generated questions with edit and interview URLs.
        """
        payload: Dict[str, Any] = {
            "survey_id": str(study_id),
            "number_of_questions": number_of_questions,
        }
        if additional_instructions is not None:
            payload["additional_instructions"] = additional_instructions

        data = self._client.post("/api/v1/questions/generate", json=payload)
        return QuestionGenerateResponse.model_validate(data)

    def get(self, question_id: Union[str, UUID]) -> Question:
        """Get properties of a question by ID.

        Args:
            question_id: UUID of the question.

        Returns:
            The question with all its properties.
        """
        data = self._client.get(f"/api/v1/questions/{question_id}")
        return Question.model_validate(data)

    def update(
        self,
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        explanation: Optional[str] = None,
        scale: Optional[Dict[str, Any]] = None,
        options: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        follow_up: Optional[bool] = None,
        min_turns: Optional[int] = None,
        max_turns: Optional[int] = None,
        expected_image: Optional[str] = None,
    ) -> Question:
        """Update one or more properties of a question.

        Only the fields provided will be updated; others remain unchanged.

        Args:
            question_id: UUID of the question to update.
            question: New question text.
            explanation: Interviewer guidance/explanation.
            scale: Scale configuration dict (minScale, maxScale, minLabel, maxLabel).
            options: Fixed choice options list.
            slots: Slot names list.
            follow_up: Whether follow-up is enabled.
            min_turns: Minimum conversation turns.
            max_turns: Maximum conversation turns.
            expected_image: Expected image description.

        Returns:
            The updated question.
        """
        payload = _build_question_update_payload(
            question=question,
            explanation=explanation,
            scale=scale,
            options=options,
            slots=slots,
            follow_up=follow_up,
            min_turns=min_turns,
            max_turns=max_turns,
            expected_image=expected_image,
        )
        data = self._client.put(
            f"/api/v1/questions/{question_id}",
            json=payload,
        )
        return Question.model_validate(data)


class AsyncQuestions:
    """Asynchronous interface for question operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def generate(
        self,
        *,
        study_id: Union[str, UUID],
        number_of_questions: int,
        additional_instructions: Optional[str] = None,
    ) -> QuestionGenerateResponse:
        """Generate interview questions for a study. See :meth:`Questions.generate`."""
        payload: Dict[str, Any] = {
            "survey_id": str(study_id),
            "number_of_questions": number_of_questions,
        }
        if additional_instructions is not None:
            payload["additional_instructions"] = additional_instructions

        data = await self._client.post("/api/v1/questions/generate", json=payload)
        return QuestionGenerateResponse.model_validate(data)

    async def get(self, question_id: Union[str, UUID]) -> Question:
        """Get properties of a question by ID."""
        data = await self._client.get(f"/api/v1/questions/{question_id}")
        return Question.model_validate(data)

    async def update(
        self,
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        explanation: Optional[str] = None,
        scale: Optional[Dict[str, Any]] = None,
        options: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        follow_up: Optional[bool] = None,
        min_turns: Optional[int] = None,
        max_turns: Optional[int] = None,
        expected_image: Optional[str] = None,
    ) -> Question:
        """Update one or more properties of a question. See :meth:`Questions.update`."""
        payload = _build_question_update_payload(
            question=question,
            explanation=explanation,
            scale=scale,
            options=options,
            slots=slots,
            follow_up=follow_up,
            min_turns=min_turns,
            max_turns=max_turns,
            expected_image=expected_image,
        )
        data = await self._client.put(
            f"/api/v1/questions/{question_id}",
            json=payload,
        )
        return Question.model_validate(data)
