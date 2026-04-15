"""Personas resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union
from uuid import UUID

from deutero.models import PersonaGenerateResponse

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Personas:
    """Synchronous interface for persona operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def generate(
        self,
        *,
        study_id: Union[str, UUID],
        number_of_personas: int,
        additional_instructions: Optional[str] = None,
    ) -> PersonaGenerateResponse:
        """Generate interviewee personas for a study.

        Args:
            study_id: UUID of the study.
            number_of_personas: Number of personas to generate (1–25).
            additional_instructions: Optional extra instructions for persona generation.

        Returns:
            The generated personas with their IDs.
        """
        payload: Dict[str, Any] = {
            "survey_id": str(study_id),
            "number_of_personas": number_of_personas,
        }
        if additional_instructions is not None:
            payload["additional_instructions"] = additional_instructions

        data = self._client.post("/api/v1/personas/generate", json=payload)
        return PersonaGenerateResponse.model_validate(data)


class AsyncPersonas:
    """Asynchronous interface for persona operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def generate(
        self,
        *,
        study_id: Union[str, UUID],
        number_of_personas: int,
        additional_instructions: Optional[str] = None,
    ) -> PersonaGenerateResponse:
        """Generate interviewee personas for a study. See :meth:`Personas.generate`."""
        payload: Dict[str, Any] = {
            "survey_id": str(study_id),
            "number_of_personas": number_of_personas,
        }
        if additional_instructions is not None:
            payload["additional_instructions"] = additional_instructions

        data = await self._client.post("/api/v1/personas/generate", json=payload)
        return PersonaGenerateResponse.model_validate(data)
