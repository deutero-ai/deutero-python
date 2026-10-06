"""Characteristics resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import CharacteristicQuestionOut, CharacteristicsOut, CharacteristicsSettingsOut, SuccessResponse

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Characteristics:
    """Synchronous interface for participant characteristics (segmentation questions)."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get(self, study_id: Union[str, UUID]) -> CharacteristicsOut:
        """Get characteristics settings plus the ordered characteristic question list."""
        data = self._client.get(f"/api/v1/studies/{study_id}/characteristics")
        return CharacteristicsOut.model_validate(data)

    def set_settings(
        self,
        study_id: Union[str, UUID],
        *,
        enabled: bool,
        anonymous: Optional[bool] = None,
    ) -> CharacteristicsSettingsOut:
        """Enable or disable characteristic collection. Disabling preserves the question list.

        Args:
            study_id: The study.
            enabled: Whether participant characteristics are collected before the interview.
            anonymous: Whether the study skips collecting participant first names.
        """
        data = self._client.put(
            f"/api/v1/studies/{study_id}/characteristics/settings",
            json=compact(enabled=enabled, anonymous=anonymous),
        )
        return CharacteristicsSettingsOut.model_validate(data)

    def create_question(
        self,
        study_id: Union[str, UUID],
        *,
        question: str,
        variable: str,
        question_type: Optional[str] = None,
        options: Optional[List[str]] = None,
        slot_description: Optional[str] = None,
    ) -> CharacteristicQuestionOut:
        """Add a characteristic question.

        Args:
            study_id: The study.
            question: Question text.
            variable: Variable name the answer is stored under.
            question_type: ``"multiple"`` (server default; choose from ``options``) or
                ``"slot"`` (free-form value described by ``slot_description``).
            options: Answer options (multiple-choice questions).
            slot_description: What value to elicit (slot questions).
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/characteristics/questions",
            json=compact(
                question=question,
                variable=variable,
                question_type=question_type,
                options=options,
                slot_description=slot_description,
            ),
        )
        return CharacteristicQuestionOut.model_validate(data)

    def update_question(
        self,
        study_id: Union[str, UUID],
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        variable: Optional[str] = None,
        question_type: Optional[str] = None,
        options: Optional[List[str]] = None,
        slot_description: Optional[str] = None,
    ) -> CharacteristicQuestionOut:
        """Update a characteristic question. Only the arguments you pass are changed."""
        data = self._client.patch(
            f"/api/v1/studies/{study_id}/characteristics/questions/{question_id}",
            json=compact(
                question=question,
                variable=variable,
                question_type=question_type,
                options=options,
                slot_description=slot_description,
            ),
        )
        return CharacteristicQuestionOut.model_validate(data)

    def delete_question(self, study_id: Union[str, UUID], question_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a characteristic question."""
        data = self._client.delete(f"/api/v1/studies/{study_id}/characteristics/questions/{question_id}")
        return SuccessResponse.model_validate(data)

    def reorder_questions(
        self,
        study_id: Union[str, UUID],
        *,
        question_ids: Sequence[Union[str, UUID]],
    ) -> CharacteristicsOut:
        """Reorder characteristic questions. Supply every characteristic question ID in the desired order."""
        data = self._client.put(
            f"/api/v1/studies/{study_id}/characteristics/questions/order",
            json={"question_ids": [str(q) for q in question_ids]},
        )
        return CharacteristicsOut.model_validate(data)


class AsyncCharacteristics:
    """Asynchronous interface for participant characteristics (segmentation questions)."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get(self, study_id: Union[str, UUID]) -> CharacteristicsOut:
        """Get characteristics configuration. See :meth:`Characteristics.get`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/characteristics")
        return CharacteristicsOut.model_validate(data)

    async def set_settings(
        self,
        study_id: Union[str, UUID],
        *,
        enabled: bool,
        anonymous: Optional[bool] = None,
    ) -> CharacteristicsSettingsOut:
        """Update characteristics settings. See :meth:`Characteristics.set_settings`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/characteristics/settings",
            json=compact(enabled=enabled, anonymous=anonymous),
        )
        return CharacteristicsSettingsOut.model_validate(data)

    async def create_question(
        self,
        study_id: Union[str, UUID],
        *,
        question: str,
        variable: str,
        question_type: Optional[str] = None,
        options: Optional[List[str]] = None,
        slot_description: Optional[str] = None,
    ) -> CharacteristicQuestionOut:
        """Add a characteristic question. See :meth:`Characteristics.create_question`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/characteristics/questions",
            json=compact(
                question=question,
                variable=variable,
                question_type=question_type,
                options=options,
                slot_description=slot_description,
            ),
        )
        return CharacteristicQuestionOut.model_validate(data)

    async def update_question(
        self,
        study_id: Union[str, UUID],
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        variable: Optional[str] = None,
        question_type: Optional[str] = None,
        options: Optional[List[str]] = None,
        slot_description: Optional[str] = None,
    ) -> CharacteristicQuestionOut:
        """Update a characteristic question. See :meth:`Characteristics.update_question`."""
        data = await self._client.patch(
            f"/api/v1/studies/{study_id}/characteristics/questions/{question_id}",
            json=compact(
                question=question,
                variable=variable,
                question_type=question_type,
                options=options,
                slot_description=slot_description,
            ),
        )
        return CharacteristicQuestionOut.model_validate(data)

    async def delete_question(self, study_id: Union[str, UUID], question_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a characteristic question. See :meth:`Characteristics.delete_question`."""
        data = await self._client.delete(f"/api/v1/studies/{study_id}/characteristics/questions/{question_id}")
        return SuccessResponse.model_validate(data)

    async def reorder_questions(
        self,
        study_id: Union[str, UUID],
        *,
        question_ids: Sequence[Union[str, UUID]],
    ) -> CharacteristicsOut:
        """Reorder characteristic questions. See :meth:`Characteristics.reorder_questions`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/characteristics/questions/order",
            json={"question_ids": [str(q) for q in question_ids]},
        )
        return CharacteristicsOut.model_validate(data)
