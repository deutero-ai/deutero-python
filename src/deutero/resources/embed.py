"""Embed resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import EmbedKeyListOut, EmbedSnippetOut

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Embed:
    """Synchronous interface for embed keys and widget install snippets."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list_keys(self) -> EmbedKeyListOut:
        """List every embed key owned by the caller's organization (secrets omitted)."""
        data = self._client.get("/api/v1/embed/keys")
        return EmbedKeyListOut.model_validate(data)

    def create_key(
        self,
        *,
        allowed_origins: List[str],
        study_id: Union[str, UUID, None] = None,
        metadata_max_bytes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a publishable embed key.

        **The response includes ``publishable_key`` and ``signing_secret`` — this is the only
        time they are returned. Store them immediately.**

        Args:
            allowed_origins: Exact origins (scheme + host + port) the widget may load on.
                The ``"*"`` wildcard is not allowed.
            study_id: Pin the key to one study (omit for any study in the organization).
            metadata_max_bytes: Maximum serialized size of the metadata a bootstrap may carry
                (at least 256).
        """
        data: Dict[str, Any] = self._client.post(
            "/api/v1/embed/keys",
            json=compact(
                allowed_origins=allowed_origins,
                study_id=study_id,
                metadata_max_bytes=metadata_max_bytes,
            ),
        )
        return data

    def update_key(
        self,
        key_id: Union[str, UUID],
        *,
        allowed_origins: Optional[List[str]] = None,
        status: Optional[str] = None,
        metadata_max_bytes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Change allowed origins, revoke/reactivate, or adjust the metadata size limit.

        Args:
            key_id: The embed key.
            allowed_origins: Replacement list of allowed origins.
            status: ``"active"`` or ``"revoked"``.
            metadata_max_bytes: Maximum serialized metadata size (at least 256).
        """
        data: Dict[str, Any] = self._client.patch(
            f"/api/v1/embed/keys/{key_id}",
            json=compact(
                allowed_origins=allowed_origins,
                status=status,
                metadata_max_bytes=metadata_max_bytes,
            ),
        )
        return data

    def get_snippet(
        self,
        study_id: Union[str, UUID],
        *,
        publishable_key: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> EmbedSnippetOut:
        """Generate the HTML install snippet for embedding this study's interview widget.

        Args:
            study_id: The study.
            publishable_key: Key to fill into the snippet; a placeholder is emitted otherwise.
            mode: Widget presentation (``data-mode``); server default ``"chat"``.
        """
        data = self._client.get(
            f"/api/v1/studies/{study_id}/embed/snippet",
            params={"publishable_key": publishable_key, "mode": mode},
        )
        return EmbedSnippetOut.model_validate(data)


class AsyncEmbed:
    """Asynchronous interface for embed keys and widget install snippets."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_keys(self) -> EmbedKeyListOut:
        """List embed keys. See :meth:`Embed.list_keys`."""
        data = await self._client.get("/api/v1/embed/keys")
        return EmbedKeyListOut.model_validate(data)

    async def create_key(
        self,
        *,
        allowed_origins: List[str],
        study_id: Union[str, UUID, None] = None,
        metadata_max_bytes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create an embed key. See :meth:`Embed.create_key`."""
        data: Dict[str, Any] = await self._client.post(
            "/api/v1/embed/keys",
            json=compact(
                allowed_origins=allowed_origins,
                study_id=study_id,
                metadata_max_bytes=metadata_max_bytes,
            ),
        )
        return data

    async def update_key(
        self,
        key_id: Union[str, UUID],
        *,
        allowed_origins: Optional[List[str]] = None,
        status: Optional[str] = None,
        metadata_max_bytes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an embed key. See :meth:`Embed.update_key`."""
        data: Dict[str, Any] = await self._client.patch(
            f"/api/v1/embed/keys/{key_id}",
            json=compact(
                allowed_origins=allowed_origins,
                status=status,
                metadata_max_bytes=metadata_max_bytes,
            ),
        )
        return data

    async def get_snippet(
        self,
        study_id: Union[str, UUID],
        *,
        publishable_key: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> EmbedSnippetOut:
        """Get the embed install snippet. See :meth:`Embed.get_snippet`."""
        data = await self._client.get(
            f"/api/v1/studies/{study_id}/embed/snippet",
            params={"publishable_key": publishable_key, "mode": mode},
        )
        return EmbedSnippetOut.model_validate(data)
