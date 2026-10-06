"""Recruitment resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import RecruitmentOut

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Recruitment:
    """Synchronous interface for participation links, short URLs and response quotas."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get(self, study_id: Union[str, UUID]) -> RecruitmentOut:
        """Get participation links, quota status and pre-interview gate flags.

        Append ``&source=<campaign tag>`` and/or ``&participant_id=<your id>`` to a link to
        attribute arrivals; they are recorded on the interview as ``web_source`` and
        ``external_participant_id``.
        """
        data = self._client.get(f"/api/v1/studies/{study_id}/recruitment")
        return RecruitmentOut.model_validate(data)

    def update(
        self,
        study_id: Union[str, UUID],
        *,
        short_url_slug: Optional[str] = None,
        max_responses: Optional[int] = None,
        clear_max_responses: Optional[bool] = None,
        redirect_url: Optional[str] = None,
    ) -> RecruitmentOut:
        """Set the short-link slug, response quota and/or post-completion redirect. Omitted fields are untouched.

        Args:
            study_id: The study.
            short_url_slug: Custom short-link slug (lowercase letters, digits, hyphens), unique
                across all studies.
            max_responses: Response quota.
            clear_max_responses: Set ``True`` to remove the response quota.
            redirect_url: Post-completion redirect. May contain ``{{external_participant_id}}``.
        """
        data = self._client.put(
            f"/api/v1/studies/{study_id}/recruitment",
            json=compact(
                short_url_slug=short_url_slug,
                max_responses=max_responses,
                clear_max_responses=clear_max_responses,
                redirect_url=redirect_url,
            ),
        )
        return RecruitmentOut.model_validate(data)


class AsyncRecruitment:
    """Asynchronous interface for participation links, short URLs and response quotas."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get(self, study_id: Union[str, UUID]) -> RecruitmentOut:
        """Get recruitment configuration. See :meth:`Recruitment.get`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/recruitment")
        return RecruitmentOut.model_validate(data)

    async def update(
        self,
        study_id: Union[str, UUID],
        *,
        short_url_slug: Optional[str] = None,
        max_responses: Optional[int] = None,
        clear_max_responses: Optional[bool] = None,
        redirect_url: Optional[str] = None,
    ) -> RecruitmentOut:
        """Update recruitment configuration. See :meth:`Recruitment.update`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/recruitment",
            json=compact(
                short_url_slug=short_url_slug,
                max_responses=max_responses,
                clear_max_responses=clear_max_responses,
                redirect_url=redirect_url,
            ),
        )
        return RecruitmentOut.model_validate(data)
