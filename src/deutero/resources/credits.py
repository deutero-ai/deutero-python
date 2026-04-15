"""Credits resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union
from uuid import UUID

from deutero.models import CreditBalance, CreditEstimate

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Credits:
    """Synchronous interface for credit operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get_balance(self) -> CreditBalance:
        """Get current credit balance and pending reservations.

        Returns:
            Credit balance including available, used, reserved, and net available.
        """
        data = self._client.get("/api/v1/credits/balance")
        return CreditBalance.model_validate(data)

    def estimate_simulation(
        self,
        *,
        survey_id: Union[str, UUID],
        model_tier: str = "open_weights",
        num_participants: int = 1,
        include_analysis: bool = False,
    ) -> CreditEstimate:
        """Estimate credits for a simulation run.

        Args:
            survey_id: UUID of the survey.
            model_tier: ``"open_weights"``, ``"premium"``, or ``"frontier"``.
            num_participants: Number of participants to simulate.
            include_analysis: Whether to include analysis credits.

        Returns:
            Credit estimation with per-interview and total costs.
        """
        data = self._client.post(
            "/api/v1/credits/estimate/simulation",
            json={
                "survey_id": str(survey_id),
                "model_tier": model_tier,
                "num_participants": num_participants,
                "include_analysis": include_analysis,
            },
        )
        return CreditEstimate.model_validate(data)

    def estimate_analysis(
        self,
        *,
        survey_id: Union[str, UUID],
        model_tier: str = "open_weights",
        num_participants: int = 1,
    ) -> CreditEstimate:
        """Estimate credits for thematic analysis.

        Args:
            survey_id: UUID of the survey.
            model_tier: ``"open_weights"``, ``"premium"``, or ``"frontier"``.
            num_participants: Number of interviews to analyze.

        Returns:
            Credit estimation for analysis.
        """
        data = self._client.post(
            "/api/v1/credits/estimate/analysis",
            json={
                "survey_id": str(survey_id),
                "model_tier": model_tier,
                "num_participants": num_participants,
                "include_analysis": False,
            },
        )
        return CreditEstimate.model_validate(data)

    def estimate_survey(
        self,
        *,
        survey_id: Union[str, UUID],
        model_tier: str = "open_weights",
        num_participants: int = 1,
        include_analysis: bool = False,
    ) -> CreditEstimate:
        """Estimate credits for a full survey (interviews + optional analysis).

        Args:
            survey_id: UUID of the survey.
            model_tier: ``"open_weights"``, ``"premium"``, or ``"frontier"``.
            num_participants: Number of participants.
            include_analysis: Whether to include analysis credits.

        Returns:
            Total credit estimation.
        """
        data = self._client.post(
            "/api/v1/credits/estimate/survey",
            json={
                "survey_id": str(survey_id),
                "model_tier": model_tier,
                "num_participants": num_participants,
                "include_analysis": include_analysis,
            },
        )
        return CreditEstimate.model_validate(data)


class AsyncCredits:
    """Asynchronous interface for credit operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get_balance(self) -> CreditBalance:
        """Get current credit balance. See :meth:`Credits.get_balance`."""
        data = await self._client.get("/api/v1/credits/balance")
        return CreditBalance.model_validate(data)

    async def estimate_simulation(
        self,
        *,
        survey_id: Union[str, UUID],
        model_tier: str = "open_weights",
        num_participants: int = 1,
        include_analysis: bool = False,
    ) -> CreditEstimate:
        """Estimate simulation credits. See :meth:`Credits.estimate_simulation`."""
        data = await self._client.post(
            "/api/v1/credits/estimate/simulation",
            json={
                "survey_id": str(survey_id),
                "model_tier": model_tier,
                "num_participants": num_participants,
                "include_analysis": include_analysis,
            },
        )
        return CreditEstimate.model_validate(data)

    async def estimate_analysis(
        self,
        *,
        survey_id: Union[str, UUID],
        model_tier: str = "open_weights",
        num_participants: int = 1,
    ) -> CreditEstimate:
        """Estimate analysis credits. See :meth:`Credits.estimate_analysis`."""
        data = await self._client.post(
            "/api/v1/credits/estimate/analysis",
            json={
                "survey_id": str(survey_id),
                "model_tier": model_tier,
                "num_participants": num_participants,
                "include_analysis": False,
            },
        )
        return CreditEstimate.model_validate(data)

    async def estimate_survey(
        self,
        *,
        survey_id: Union[str, UUID],
        model_tier: str = "open_weights",
        num_participants: int = 1,
        include_analysis: bool = False,
    ) -> CreditEstimate:
        """Estimate full survey credits. See :meth:`Credits.estimate_survey`."""
        data = await self._client.post(
            "/api/v1/credits/estimate/survey",
            json={
                "survey_id": str(survey_id),
                "model_tier": model_tier,
                "num_participants": num_participants,
                "include_analysis": include_analysis,
            },
        )
        return CreditEstimate.model_validate(data)
