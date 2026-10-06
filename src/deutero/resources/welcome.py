"""Welcome & consent resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import (
    SuccessResponse,
    WelcomeDraftOut,
    WelcomeOut,
    WelcomeTranslationListOut,
    WelcomeTranslationOut,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Welcome:
    """Synchronous interface for a study's welcome/consent message and its translations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get(self, study_id: Union[str, UUID]) -> WelcomeOut:
        """Get the welcome message participants see first."""
        data = self._client.get(f"/api/v1/studies/{study_id}/welcome")
        return WelcomeOut.model_validate(data)

    def set(self, study_id: Union[str, UUID], *, message: str, consent: Optional[bool] = None) -> WelcomeOut:
        """Create or replace the welcome/consent message.

        Args:
            study_id: The study.
            message: Welcome/consent message shown before the interview.
            consent: Require participants to explicitly agree before the interview begins.
        """
        data = self._client.put(
            f"/api/v1/studies/{study_id}/welcome",
            json=compact(message=message, consent=consent),
        )
        return WelcomeOut.model_validate(data)

    def generate(self, study_id: Union[str, UUID]) -> WelcomeDraftOut:
        """Draft the welcome/consent message with AI. Nothing is saved.

        The draft draws on the study's name, description, research question, target
        population, benefits, risks, support contact, question count, survey type and
        language, and on your profile. Anything missing becomes a placeholder such as
        ``[Insert researcher name]``, listed in ``placeholders``: fill those in, then call
        :meth:`set`. A model call that typically takes 10-30 seconds.
        """
        data = self._client.post(f"/api/v1/studies/{study_id}/welcome/generate")
        return WelcomeDraftOut.model_validate(data)

    def list_translations(self, study_id: Union[str, UUID]) -> WelcomeTranslationListOut:
        """List the welcome message's translations."""
        data = self._client.get(f"/api/v1/studies/{study_id}/welcome/translations")
        return WelcomeTranslationListOut.model_validate(data)

    def upsert_translation(
        self,
        study_id: Union[str, UUID],
        *,
        target_language: str,
        translation_text: str,
        source_language: Optional[str] = None,
    ) -> WelcomeTranslationOut:
        """Add or replace the translation for ``target_language``. The welcome message must be set first.

        Args:
            study_id: The study.
            target_language: Language name or ISO code, e.g. ``"Spanish"`` or ``"es"``.
            translation_text: Translated welcome message.
            source_language: Source language name or ISO code (server default ``"English"``).
        """
        data = self._client.put(
            f"/api/v1/studies/{study_id}/welcome/translations",
            json=compact(
                target_language=target_language,
                translation_text=translation_text,
                source_language=source_language,
            ),
        )
        return WelcomeTranslationOut.model_validate(data)

    def delete_translation(
        self,
        study_id: Union[str, UUID],
        translation_id: Union[str, UUID],
    ) -> SuccessResponse:
        """Delete a welcome-message translation."""
        data = self._client.delete(f"/api/v1/studies/{study_id}/welcome/translations/{translation_id}")
        return SuccessResponse.model_validate(data)


class AsyncWelcome:
    """Asynchronous interface for a study's welcome/consent message and its translations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get(self, study_id: Union[str, UUID]) -> WelcomeOut:
        """Get the welcome message. See :meth:`Welcome.get`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/welcome")
        return WelcomeOut.model_validate(data)

    async def set(self, study_id: Union[str, UUID], *, message: str, consent: Optional[bool] = None) -> WelcomeOut:
        """Set the welcome message. See :meth:`Welcome.set`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/welcome",
            json=compact(message=message, consent=consent),
        )
        return WelcomeOut.model_validate(data)

    async def generate(self, study_id: Union[str, UUID]) -> WelcomeDraftOut:
        """Draft the welcome message with AI. See :meth:`Welcome.generate`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/welcome/generate")
        return WelcomeDraftOut.model_validate(data)

    async def list_translations(self, study_id: Union[str, UUID]) -> WelcomeTranslationListOut:
        """List translations. See :meth:`Welcome.list_translations`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/welcome/translations")
        return WelcomeTranslationListOut.model_validate(data)

    async def upsert_translation(
        self,
        study_id: Union[str, UUID],
        *,
        target_language: str,
        translation_text: str,
        source_language: Optional[str] = None,
    ) -> WelcomeTranslationOut:
        """Add or replace a translation. See :meth:`Welcome.upsert_translation`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/welcome/translations",
            json=compact(
                target_language=target_language,
                translation_text=translation_text,
                source_language=source_language,
            ),
        )
        return WelcomeTranslationOut.model_validate(data)

    async def delete_translation(
        self,
        study_id: Union[str, UUID],
        translation_id: Union[str, UUID],
    ) -> SuccessResponse:
        """Delete a translation. See :meth:`Welcome.delete_translation`."""
        data = await self._client.delete(f"/api/v1/studies/{study_id}/welcome/translations/{translation_id}")
        return SuccessResponse.model_validate(data)
