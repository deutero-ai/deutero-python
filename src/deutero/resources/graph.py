"""Interview flow (graph) resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Union
from uuid import UUID

from deutero._http import compact
from deutero.models import FlowDocument, FlowSignalsOut, GraphCheckOut, GraphModeOut, GraphOut, PatchOp

if TYPE_CHECKING:
    from deutero._http import AsyncHTTPClient, SyncHTTPClient

FlowInput = Union[FlowDocument, Dict[str, Any]]
PatchOpInput = Union[PatchOp, Dict[str, Any]]


class Graph:
    """Synchronous interface for a study's interview flow — the branching alternative to the question list.

    Flows can be passed as :class:`~deutero.models.FlowDocument` models or as plain dicts in
    the API's JSON shape. Call :meth:`describe_node_types` for each step type's config fields.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get(self, study_id: Union[str, UUID]) -> GraphOut:
        """Get the study's interview flow, its ``graph_version`` and whether it is the active script.

        ``flow`` is ``None`` when the study has no flow yet.
        """
        data = self._client.get(f"/api/v1/studies/{study_id}/graph")
        return GraphOut.model_validate(data)

    def set(
        self,
        study_id: Union[str, UUID],
        *,
        flow: FlowInput,
        expected_graph_version: Optional[int] = None,
    ) -> GraphCheckOut:
        """Replace the study's whole interview flow.

        Nothing is saved unless the flow is valid: on any problem the API returns 422
        (raised as :class:`~deutero.exceptions.ValidationError`) and the stored flow is untouched.

        Args:
            study_id: The study.
            flow: The complete flow.
            expected_graph_version: The ``graph_version`` you last read. The write is refused
                with 409 (:class:`~deutero.exceptions.ConflictError`) if the flow has since been
                edited. Omit to overwrite unconditionally.
        """
        data = self._client.put(
            f"/api/v1/studies/{study_id}/graph",
            json=compact(flow=flow, expected_graph_version=expected_graph_version),
        )
        return GraphCheckOut.model_validate(data)

    def patch(
        self,
        study_id: Union[str, UUID],
        *,
        ops: Sequence[PatchOpInput],
        expected_graph_version: Optional[int] = None,
    ) -> GraphCheckOut:
        """Apply targeted edits to the stored flow instead of rewriting it.

        Operations are applied in order and the result is validated as a whole; nothing is
        saved unless the end state is valid. Example ops::

            {"op": "add_node", "node": {...}}
            {"op": "update_node", "id": "q_pets", "config": {"text": "New wording?"}}
            {"op": "remove_node", "id": "q_pets"}
            {"op": "add_edge", "edge": {"from": "q1", "to": "end"}}

        Args:
            study_id: The study.
            ops: Edits to apply, in order.
            expected_graph_version: Optimistic concurrency; see :meth:`set`.
        """
        data = self._client.patch(
            f"/api/v1/studies/{study_id}/graph",
            json=compact(ops=list(ops), expected_graph_version=expected_graph_version),
        )
        return GraphCheckOut.model_validate(data)

    def check(self, study_id: Union[str, UUID], *, flow: Optional[FlowInput] = None) -> GraphCheckOut:
        """Validate a flow and report every problem, changing nothing.

        Args:
            study_id: The study.
            flow: The flow to check. Omit to re-check the study's stored flow.
        """
        data = self._client.post(f"/api/v1/studies/{study_id}/graph/check", json=compact(flow=flow))
        return GraphCheckOut.model_validate(data)

    def get_signals(self, study_id: Union[str, UUID]) -> FlowSignalsOut:
        """Get the delivery config, including signing secrets, of every "Send a signal" step in the saved flow.

        A receiver verifies each signal with its step's secret via :func:`deutero.webhooks.unwrap`.
        """
        data = self._client.get(f"/api/v1/studies/{study_id}/graph/signals")
        return FlowSignalsOut.model_validate(data)

    def import_questions(self, study_id: Union[str, UUID]) -> GraphCheckOut:
        """Build and save a straight-line flow from the study's linear questions.

        **Replaces any flow the study already has.** Each question captures its answer as
        ``q1``, ``q2``, … Does not change the interview mode; call :meth:`activate` when ready.
        """
        data = self._client.post(f"/api/v1/studies/{study_id}/graph/import-questions")
        return GraphCheckOut.model_validate(data)

    def activate(self, study_id: Union[str, UUID]) -> GraphModeOut:
        """Switch the study to ``graph`` mode so interviews follow the stored flow."""
        data = self._client.post(f"/api/v1/studies/{study_id}/graph/activate")
        return GraphModeOut.model_validate(data)

    def deactivate(self, study_id: Union[str, UUID]) -> GraphModeOut:
        """Switch the study back to ``linear`` mode. The stored flow is kept."""
        data = self._client.post(f"/api/v1/studies/{study_id}/graph/deactivate")
        return GraphModeOut.model_validate(data)

    def describe_node_types(self) -> Dict[str, Any]:
        """Get the configuration schema for every flow step type. Read this before authoring a flow."""
        data: Dict[str, Any] = self._client.get("/api/v1/graph/node-types")
        return data


class AsyncGraph:
    """Asynchronous interface for a study's interview flow. See :class:`Graph`."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get(self, study_id: Union[str, UUID]) -> GraphOut:
        """Get the interview flow. See :meth:`Graph.get`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/graph")
        return GraphOut.model_validate(data)

    async def set(
        self,
        study_id: Union[str, UUID],
        *,
        flow: FlowInput,
        expected_graph_version: Optional[int] = None,
    ) -> GraphCheckOut:
        """Replace the interview flow. See :meth:`Graph.set`."""
        data = await self._client.put(
            f"/api/v1/studies/{study_id}/graph",
            json=compact(flow=flow, expected_graph_version=expected_graph_version),
        )
        return GraphCheckOut.model_validate(data)

    async def patch(
        self,
        study_id: Union[str, UUID],
        *,
        ops: Sequence[PatchOpInput],
        expected_graph_version: Optional[int] = None,
    ) -> GraphCheckOut:
        """Edit parts of the interview flow. See :meth:`Graph.patch`."""
        data = await self._client.patch(
            f"/api/v1/studies/{study_id}/graph",
            json=compact(ops=list(ops), expected_graph_version=expected_graph_version),
        )
        return GraphCheckOut.model_validate(data)

    async def check(self, study_id: Union[str, UUID], *, flow: Optional[FlowInput] = None) -> GraphCheckOut:
        """Check a flow without saving it. See :meth:`Graph.check`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/graph/check", json=compact(flow=flow))
        return GraphCheckOut.model_validate(data)

    async def get_signals(self, study_id: Union[str, UUID]) -> FlowSignalsOut:
        """Get signal delivery settings. See :meth:`Graph.get_signals`."""
        data = await self._client.get(f"/api/v1/studies/{study_id}/graph/signals")
        return FlowSignalsOut.model_validate(data)

    async def import_questions(self, study_id: Union[str, UUID]) -> GraphCheckOut:
        """Seed a flow from the question list. See :meth:`Graph.import_questions`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/graph/import-questions")
        return GraphCheckOut.model_validate(data)

    async def activate(self, study_id: Union[str, UUID]) -> GraphModeOut:
        """Run interviews from the flow. See :meth:`Graph.activate`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/graph/activate")
        return GraphModeOut.model_validate(data)

    async def deactivate(self, study_id: Union[str, UUID]) -> GraphModeOut:
        """Run interviews from the question list. See :meth:`Graph.deactivate`."""
        data = await self._client.post(f"/api/v1/studies/{study_id}/graph/deactivate")
        return GraphModeOut.model_validate(data)

    async def describe_node_types(self) -> Dict[str, Any]:
        """Describe every flow step type. See :meth:`Graph.describe_node_types`."""
        data: Dict[str, Any] = await self._client.get("/api/v1/graph/node-types")
        return data
