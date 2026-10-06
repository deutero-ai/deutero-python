"""Screening resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import ScreeningOut, ScreeningQuestionOut, ScreeningSettingsOut, SuccessResponse

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Screening:
    """Synchronous interface for screening: qualifying questions that gate participation."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get(self, study_id: Union[str, UUID]) -> ScreeningOut:
        """Get screening settings plus the ordered screening question list."""
        data = self._client.get(f"/api/v1/studies/{study_id}/screening")
        return ScreeningOut.model_validate(data)

    def set_settings(
        self,
        study_id: Union[str, UUID],
        *,
        enabled: bool,
        disqualification_message: Optional[str] = None,
        redirect_url: Optional[str] = None,
    ) -> ScreeningSettingsOut:
        """Enable or disable screening. Disabling preserves questions and settings.

        Args:
            study_id: The study.
            enabled: Whether screening runs before the interview.
            disqualification_message: Message shown to participants who do not qualify.
            redirect_url: URL disqualified participants are sent to. May contain
                ``{{external_participant_id}}``.
        """
        data = self._client.put(
            f"/api/v1/studies/{study_id}/screening/settings",
            json=compact(
                enabled=enabled,
                disqualification_message=disqualification_message,
                redirect_url=redirect_url,
            ),
        )
        return ScreeningSettingsOut.model_validate(data)

    def create_question(
        self,
        study_id: Union[str, UUID],
        *,
        question: str,
        options: List[str],
        acceptable_options: List[str],
    ) -> ScreeningQuestionOut:
        """Append a multiple-choice qualifying question.

        Args:
            study_id: The study.
            question: Screening question text.
            options: Answer options.
            acceptable_options: Subset of ``options`` that qualify the participant.
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/screening/questions",
            json=compact(question=question, options=options, acceptable_options=acceptable_options),
        )
        return ScreeningQuestionOut.model_validate(data)

    def update_question(
        self,
        study_id: Union[str, UUID],
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        options: Optional[List[str]] = None,
        acceptable_options: Optional[List[str]] = None,
    ) -> ScreeningQuestionOut:
        """Update a screening question. Only the arguments you pass are changed."""
        data = self._client.patch(
            f"/api/v1/studies/{study_id}/screening/questions/{question_id}",
            json=compact(question=question, options=options, acceptable_options=acceptable_options),
        )
        return ScreeningQuestionOut.model_validate(data)

    def delete_question(self, study_id: Union[str, UUID], question_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a screening question, along with any recorded answers to it."""
        data = self._client.delete(f"/api/v1/studies/{study_id}/screening/questions/{question_id}")
        return SuccessResponse.model_validate(data)

    def reorder_questions(
        self,
        study_id: Union[str, UUID],
        *,
        question_ids: Sequence[Union[str, UUID]],
    ) -> ScreeningOut:
        """Reorder screening questions. Supply every screening question ID in the desired order."""
        data = self._client.put(
            f"/api/v1/studies/{study_id}/screening/questions/order",
            json={"question_ids": [str(q) for q in question_ids]},
        )
        return ScreeningOut.model_validate(data)


class AsyncScreening:
    """Asynchronous interface for screening: qualifying questions that gate participation."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get(self, study_id: Union[str, UUID]) -> ScreeningOut:
        """Get screening configuration. See :meth:`Screening.get`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/screening")
        return ScreeningOut.model_validate(data)

    async def set_settings(
        self,
        study_id: Union[str, UUID],
        *,
        enabled: bool,
        disqualification_message: Optional[str] = None,
        redirect_url: Optional[str] = None,
    ) -> ScreeningSettingsOut:
        """Update screening settings. See :meth:`Screening.set_settings`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/screening/settings",
            json=compact(
                enabled=enabled,
                disqualification_message=disqualification_message,
                redirect_url=redirect_url,
            ),
        )
        return ScreeningSettingsOut.model_validate(data)

    async def create_question(
        self,
        study_id: Union[str, UUID],
        *,
        question: str,
        options: List[str],
        acceptable_options: List[str],
    ) -> ScreeningQuestionOut:
        """Add a screening question. See :meth:`Screening.create_question`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/screening/questions",
            json=compact(question=question, options=options, acceptable_options=acceptable_options),
        )
        return ScreeningQuestionOut.model_validate(data)

    async def update_question(
        self,
        study_id: Union[str, UUID],
        question_id: Union[str, UUID],
        *,
        question: Optional[str] = None,
        options: Optional[List[str]] = None,
        acceptable_options: Optional[List[str]] = None,
    ) -> ScreeningQuestionOut:
        """Update a screening question. See :meth:`Screening.update_question`."""
        data = await self._client.patch(
            f"/api/v1/studies/{study_id}/screening/questions/{question_id}",
            json=compact(question=question, options=options, acceptable_options=acceptable_options),
        )
        return ScreeningQuestionOut.model_validate(data)

    async def delete_question(self, study_id: Union[str, UUID], question_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a screening question. See :meth:`Screening.delete_question`."""
        data = await self._client.delete(f"/api/v1/studies/{study_id}/screening/questions/{question_id}")
        return SuccessResponse.model_validate(data)

    async def reorder_questions(
        self,
        study_id: Union[str, UUID],
        *,
        question_ids: Sequence[Union[str, UUID]],
    ) -> ScreeningOut:
        """Reorder screening questions. See :meth:`Screening.reorder_questions`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/screening/questions/order",
            json={"question_ids": [str(q) for q in question_ids]},
        )
        return ScreeningOut.model_validate(data)
