"""Simulations resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import ModelTier, SimulationListOut, SimulationOut, SimulationStartOut

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Simulations:
    """Synchronous interface for simulated interview runs."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def run(
        self,
        study_id: Union[str, UUID],
        *,
        persona_id: Union[str, UUID, None] = None,
        persona: Optional[str] = None,
        model_tier: Union[str, ModelTier, None] = None,
        deliver_signals: Optional[bool] = None,
    ) -> SimulationStartOut:
        """Start one simulated interview and return immediately.

        The run continues in the background; poll :meth:`get` until ``status`` is
        ``"completed"`` or ``"failed"``. Credits are reserved up front; a run that would exceed
        the balance raises :class:`~deutero.exceptions.InsufficientCreditsError`.

        Args:
            study_id: The study.
            persona_id: Stored persona to play the participant. Omit for a generic participant.
            persona: Ad-hoc persona text, used when no ``persona_id`` is given.
            model_tier: ``"open_weights"`` (server default), ``"standard"`` or ``"premium"``.
            deliver_signals: Let the run's "Send a signal" steps reach their real endpoints.
        """
        data = self._client.post(
            f"/api/v1/studies/{study_id}/simulations",
            json=compact(
                persona_id=persona_id,
                persona=persona,
                model_tier=model_tier,
                deliver_signals=deliver_signals,
            ),
        )
        return SimulationStartOut.model_validate(data)

    def list(
        self,
        study_id: Union[str, UUID],
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SimulationListOut:
        """List the study's simulation runs, newest first.

        Args:
            study_id: The study.
            status: Filter by ``"running"``, ``"completed"`` or ``"failed"``.
            limit: Page size (server default 50).
            offset: Page offset.
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/simulations",
            params={"status": status, "limit": limit, "offset": offset},
        )
        return SimulationListOut.model_validate(data)

    def get(self, simulation_id: Union[str, UUID]) -> SimulationOut:
        """Get one simulation run's current state."""
        data = self._client.get(f"/api/v1/simulations/{simulation_id}")
        return SimulationOut.model_validate(data)

    def delete(self, simulation_id: Union[str, UUID]) -> None:
        """Delete a finished run's record. The interview it produced is kept."""
        self._client.delete(f"/api/v1/simulations/{simulation_id}")


class AsyncSimulations:
    """Asynchronous interface for simulated interview runs."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def run(
        self,
        study_id: Union[str, UUID],
        *,
        persona_id: Union[str, UUID, None] = None,
        persona: Optional[str] = None,
        model_tier: Union[str, ModelTier, None] = None,
        deliver_signals: Optional[bool] = None,
    ) -> SimulationStartOut:
        """Start a simulated interview. See :meth:`Simulations.run`."""
        data = await self._client.post(
            f"/api/v1/studies/{study_id}/simulations",
            json=compact(
                persona_id=persona_id,
                persona=persona,
                model_tier=model_tier,
                deliver_signals=deliver_signals,
            ),
        )
        return SimulationStartOut.model_validate(data)

    async def list(
        self,
        study_id: Union[str, UUID],
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SimulationListOut:
        """List simulation runs. See :meth:`Simulations.list`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/simulations",
            params={"status": status, "limit": limit, "offset": offset},
        )
        return SimulationListOut.model_validate(data)

    async def get(self, simulation_id: Union[str, UUID]) -> SimulationOut:
        """Get a simulation run. See :meth:`Simulations.get`."""
        data = await self._client.get(f"/api/v1/simulations/{simulation_id}")
        return SimulationOut.model_validate(data)

    async def delete(self, simulation_id: Union[str, UUID]) -> None:
        """Delete a simulation run record. See :meth:`Simulations.delete`."""
        await self._client.delete(f"/api/v1/simulations/{simulation_id}")
