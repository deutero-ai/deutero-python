"""Webhooks resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import (
    WebhookCreatedOut,
    WebhookDeleteOut,
    WebhookDeliveryListOut,
    WebhookEventTypeListOut,
    WebhookListOut,
    WebhookOut,
    WebhookSecretOut,
)

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Webhooks:
    """Synchronous interface for organization-level webhook endpoints.

    To verify and parse the deliveries these endpoints receive, see :mod:`deutero.webhooks`.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list_event_types(self) -> WebhookEventTypeListOut:
        """List every subscribable event type and the fields its payload carries."""
        data = self._client.get("/api/v1/webhooks/event-types")
        return WebhookEventTypeListOut.model_validate(data)

    def list(self) -> WebhookListOut:
        """List every webhook endpoint in the organization, newest first (secrets omitted)."""
        data = self._client.get("/api/v1/webhooks")
        return WebhookListOut.model_validate(data)

    def create(
        self,
        *,
        label: str,
        url: str,
        events: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
    ) -> WebhookCreatedOut:
        """Subscribe a URL to organization events.

        **The response carries the signing secret — the only time it is shown.** Store it
        before doing anything else; your receiver passes it to :func:`deutero.webhooks.unwrap`.

        Args:
            label: How you will recognize this endpoint in the list.
            url: Publicly reachable http(s) URL that receives the POSTs.
            events: Event types to subscribe to. Omitted or empty subscribes to every event.
            enabled: Whether deliveries start immediately (server default ``True``).
        """
        data = self._client.post(
            "/api/v1/webhooks",
            json=compact(label=label, url=url, events=events, enabled=enabled),
        )
        return WebhookCreatedOut.model_validate(data)

    def update(
        self,
        webhook_id: Union[str, UUID],
        *,
        label: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
    ) -> WebhookOut:
        """Update an endpoint. Only the arguments you pass change; ``events`` replaces the list."""
        data = self._client.patch(
            f"/api/v1/webhooks/{webhook_id}",
            json=compact(label=label, url=url, events=events, enabled=enabled),
        )
        return WebhookOut.model_validate(data)

    def delete(self, webhook_id: Union[str, UUID]) -> WebhookDeleteOut:
        """Permanently delete an endpoint, its secret and its delivery log.

        To pause deliveries instead, call :meth:`update` with ``enabled=False``.
        """
        data = self._client.delete(f"/api/v1/webhooks/{webhook_id}")
        return WebhookDeleteOut.model_validate(data)

    def rotate_secret(self, webhook_id: Union[str, UUID]) -> WebhookSecretOut:
        """Mint a new signing secret. **The previous secret stops verifying immediately.**"""
        data = self._client.post(f"/api/v1/webhooks/{webhook_id}/rotate-secret")
        return WebhookSecretOut.model_validate(data)

    def list_deliveries(
        self,
        webhook_id: Union[str, UUID],
        *,
        event_type: Optional[str] = None,
        success: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> WebhookDeliveryListOut:
        """List an endpoint's delivery log, newest first.

        Args:
            webhook_id: The endpoint.
            event_type: Only deliveries of this event type.
            success: ``True`` for only successes, ``False`` for only failures.
            external_participant_id: Only deliveries about this participant id of yours.
            limit: Page size (server default 50).
            offset: Page offset.
        """
        data = self._client.get(
            f"/api/v1/webhooks/{webhook_id}/deliveries",
            params={
                "event_type": event_type,
                "success": success,
                "external_participant_id": external_participant_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return WebhookDeliveryListOut.model_validate(data)


class AsyncWebhooks:
    """Asynchronous interface for organization-level webhook endpoints."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_event_types(self) -> WebhookEventTypeListOut:
        """List event types. See :meth:`Webhooks.list_event_types`."""
        data = await self._client.get("/api/v1/webhooks/event-types")
        return WebhookEventTypeListOut.model_validate(data)

    async def list(self) -> WebhookListOut:
        """List endpoints. See :meth:`Webhooks.list`."""
        data = await self._client.get("/api/v1/webhooks")
        return WebhookListOut.model_validate(data)

    async def create(
        self,
        *,
        label: str,
        url: str,
        events: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
    ) -> WebhookCreatedOut:
        """Create an endpoint. See :meth:`Webhooks.create`."""
        data = await self._client.post(
            "/api/v1/webhooks",
            json=compact(label=label, url=url, events=events, enabled=enabled),
        )
        return WebhookCreatedOut.model_validate(data)

    async def update(
        self,
        webhook_id: Union[str, UUID],
        *,
        label: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
    ) -> WebhookOut:
        """Update an endpoint. See :meth:`Webhooks.update`."""
        data = await self._client.patch(
            f"/api/v1/webhooks/{webhook_id}",
            json=compact(label=label, url=url, events=events, enabled=enabled),
        )
        return WebhookOut.model_validate(data)

    async def delete(self, webhook_id: Union[str, UUID]) -> WebhookDeleteOut:
        """Delete an endpoint. See :meth:`Webhooks.delete`."""
        data = await self._client.delete(f"/api/v1/webhooks/{webhook_id}")
        return WebhookDeleteOut.model_validate(data)

    async def rotate_secret(self, webhook_id: Union[str, UUID]) -> WebhookSecretOut:
        """Rotate the signing secret. See :meth:`Webhooks.rotate_secret`."""
        data = await self._client.post(f"/api/v1/webhooks/{webhook_id}/rotate-secret")
        return WebhookSecretOut.model_validate(data)

    async def list_deliveries(
        self,
        webhook_id: Union[str, UUID],
        *,
        event_type: Optional[str] = None,
        success: Optional[bool] = None,
        external_participant_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> WebhookDeliveryListOut:
        """List deliveries. See :meth:`Webhooks.list_deliveries`."""
        data = await self._client.get(
            f"/api/v1/webhooks/{webhook_id}/deliveries",
            params={
                "event_type": event_type,
                "success": success,
                "external_participant_id": external_participant_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return WebhookDeliveryListOut.model_validate(data)
