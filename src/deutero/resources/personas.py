"""Personas resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import PersonaGenerateOut, PersonaListOut, PersonaOut, SuccessResponse

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Personas:
    """Synchronous interface for personas: AI participants used in simulated interviews."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list(self, study_id: Union[str, UUID]) -> PersonaListOut:
        """List every persona defined for the study, newest first."""
        data = self._client.get(f"/api/v1/studies/{study_id}/personas")
        return PersonaListOut.model_validate(data)

    def create(self, study_id: Union[str, UUID], *, content: str, source: Optional[str] = None) -> PersonaOut:
        """Write a persona by hand.

        Args:
            study_id: The study.
            content: Who this simulated participant is — background, situation, attitudes —
                written as prose in the third person, as if briefing an actor.
            source: ``"manual"`` (server default) or ``"generated"``.
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/personas",
            json=compact(content=content, source=source),
        )
        return PersonaOut.model_validate(data)

    def update(self, study_id: Union[str, UUID], persona_id: Union[str, UUID], *, content: str) -> PersonaOut:
        """Replace a persona's description. Only affects future simulation runs."""
        data = self._client.patch(
            f"/api/v1/studies/{study_id}/personas/{persona_id}",
            json={"content": content},
        )
        return PersonaOut.model_validate(data)

    def delete(self, study_id: Union[str, UUID], persona_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a persona. Interviews already simulated with it are kept."""
        data = self._client.delete(f"/api/v1/studies/{study_id}/personas/{persona_id}")
        return SuccessResponse.model_validate(data)

    def generate(
        self,
        study_id: Union[str, UUID],
        *,
        count: Optional[int] = None,
        save: Optional[bool] = None,
    ) -> PersonaGenerateOut:
        """Draft personas with AI from the study's own context.

        Args:
            study_id: The study.
            count: How many personas to generate (1-10; server default 1).
            save: Persist them to the study (server default ``True``). Pass ``False`` to
                preview without storing; previewed personas have no IDs.
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/personas/generate",
            json=compact(count=count, save=save),
        )
        return PersonaGenerateOut.model_validate(data)


class AsyncPersonas:
    """Asynchronous interface for personas: AI participants used in simulated interviews."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(self, study_id: Union[str, UUID]) -> PersonaListOut:
        """List personas. See :meth:`Personas.list`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/personas")
        return PersonaListOut.model_validate(data)

    async def create(self, study_id: Union[str, UUID], *, content: str, source: Optional[str] = None) -> PersonaOut:
        """Create a persona. See :meth:`Personas.create`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/personas",
            json=compact(content=content, source=source),
        )
        return PersonaOut.model_validate(data)

    async def update(self, study_id: Union[str, UUID], persona_id: Union[str, UUID], *, content: str) -> PersonaOut:
        """Update a persona. See :meth:`Personas.update`."""
        data = await self._client.patch(
            f"/api/v1/studies/{study_id}/personas/{persona_id}",
            json={"content": content},
        )
        return PersonaOut.model_validate(data)

    async def delete(self, study_id: Union[str, UUID], persona_id: Union[str, UUID]) -> SuccessResponse:
        """Delete a persona. See :meth:`Personas.delete`."""
        data = await self._client.delete(f"/api/v1/studies/{study_id}/personas/{persona_id}")
        return SuccessResponse.model_validate(data)

    async def generate(
        self,
        study_id: Union[str, UUID],
        *,
        count: Optional[int] = None,
        save: Optional[bool] = None,
    ) -> PersonaGenerateOut:
        """Generate personas with AI. See :meth:`Personas.generate`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/personas/generate",
            json=compact(count=count, save=save),
        )
        return PersonaGenerateOut.model_validate(data)
