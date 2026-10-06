"""Projects resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import ProjectListOut, ProjectOut

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient


class Projects:
    """Synchronous interface for project operations."""

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def list(self) -> ProjectListOut:
        """List every project in the caller's organization."""
        data = self._client.get("/api/v1/projects")
        return ProjectListOut.model_validate(data)

    def create(self, *, name: str, description: Optional[str] = None) -> ProjectOut:
        """Create a new project owned by the caller's organization.

        Args:
            name: Project name.
            description: Project description.
        """
        data = self._client.post("/api/v1/projects", json=compact(name=name, description=description))
        return ProjectOut.model_validate(data)

    def get(self, project_id: Union[str, UUID]) -> ProjectOut:
        """Get a project by ID."""
        data = self._client.get(f"/api/v1/projects/{project_id}")
        return ProjectOut.model_validate(data)

    def update(
        self,
        project_id: Union[str, UUID],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ProjectOut:
        """Update a project's name and/or description. Omitted fields are untouched."""
        data = self._client.patch(
            f"/api/v1/projects/{project_id}",
            json=compact(name=name, description=description),
        )
        return ProjectOut.model_validate(data)


class AsyncProjects:
    """Asynchronous interface for project operations."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(self) -> ProjectListOut:
        """List projects. See :meth:`Projects.list`."""
        data = await self._client.get("/api/v1/projects")
        return ProjectListOut.model_validate(data)

    async def create(self, *, name: str, description: Optional[str] = None) -> ProjectOut:
        """Create a project. See :meth:`Projects.create`."""
        data = await self._client.post("/api/v1/projects", json=compact(name=name, description=description))
        return ProjectOut.model_validate(data)

    async def get(self, project_id: Union[str, UUID]) -> ProjectOut:
        """Get a project. See :meth:`Projects.get`."""
        data = await self._client.get(f"/api/v1/projects/{project_id}")
        return ProjectOut.model_validate(data)

    async def update(
        self,
        project_id: Union[str, UUID],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ProjectOut:
        """Update a project. See :meth:`Projects.update`."""
        data = await self._client.patch(
            f"/api/v1/projects/{project_id}",
            json=compact(name=name, description=description),
        )
        return ProjectOut.model_validate(data)
