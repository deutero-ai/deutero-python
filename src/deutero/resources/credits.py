"""Credits resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from deutero.models import CreditBalanceOut

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Credits:
    """Synchronous interface for credit operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get_balance(self) -> CreditBalanceOut:
        """Get the organization's current credit balance."""
        data = self._client.get("/api/v1/credits/balance")
        return CreditBalanceOut.model_validate(data)


class AsyncCredits:
    """Asynchronous interface for credit operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get_balance(self) -> CreditBalanceOut:
        """Get the credit balance. See :meth:`Credits.get_balance`."""
        data = await self._client.get("/api/v1/credits/balance")
        return CreditBalanceOut.model_validate(data)
