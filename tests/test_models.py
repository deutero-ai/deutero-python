"""Tests for Pydantic models."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import BaseModel

import deutero.models
from deutero._http import compact
from deutero.models import (
    AnalysisCategory,
    ClusteringOut,
    CreditBalanceOut,
    FlowDocument,
    FlowEdge,
    FlowNode,
    ModelTier,
    PatchOp,
    ScaleConfig,
    SearchMode,
    StudyOut,
    StudyType,
    TranscriptOut,
)

STUDY_ID = "12345678-1234-1234-1234-123456789abc"


class TestEnums:
    def test_study_type_values(self) -> None:
        assert StudyType.SOCIOLOGY == "sociology"
        assert StudyType.USER_EXPERIENCE == "user_experience"
        assert StudyType.CUSTOMER_DEVELOPMENT == "customer_development"
        assert StudyType.POLLING == "polling"

    def test_model_tier_values(self) -> None:
        assert ModelTier.OPEN_WEIGHTS == "open_weights"
        assert ModelTier.STANDARD == "standard"
        assert ModelTier.PREMIUM == "premium"

    def test_search_and_analysis_values(self) -> None:
        assert SearchMode.HYBRID == "hybrid"
        assert AnalysisCategory.OPTIONS == "options"


class TestStudyOut:
    def test_parse_minimal_applies_defaults(self) -> None:
        study = StudyOut.model_validate({
            "id": STUDY_ID,
            "project_id": None,
            "name": "Onboarding",
            "dashboard_url": "https://dashboard.deutero.ai/x",
            "participation_url": "https://app.deutero.ai/chat?survey_id=x",
        })
        assert study.id == UUID(STUDY_ID)
        assert study.interview_mode == "linear"
        assert study.question_count == 0
        assert study.short_participation_url is None

    def test_ignores_unknown_fields(self) -> None:
        study = StudyOut.model_validate({
            "id": STUDY_ID,
            "project_id": STUDY_ID,
            "name": "Onboarding",
            "dashboard_url": "d",
            "participation_url": "p",
            "some_future_field": 1,
        })
        assert study.name == "Onboarding"


class TestCreditBalanceOut:
    def test_parse(self) -> None:
        balance = CreditBalanceOut.model_validate({
            "available_credits": 100.0,
            "credits_used": 20.0,
            "credits_reserved": 5.0,
            "base_limit": 80.0,
            "purchased_credits": 20.0,
            "rollover_credits": 5.0,
            "is_trial_active": False,
            "trial_credits_used": 0,
            "net_available": 75.0,
        })
        assert balance.net_available == 75.0


class TestTranscriptOut:
    def test_parse_nested(self) -> None:
        transcript = TranscriptOut.model_validate({
            "interview_id": STUDY_ID,
            "messages": [{"id": STUDY_ID, "type": "question", "content": "Hi?"}],
            "variables": [{"name": "q1", "value": ["a", "b"], "value_type": "list[string]"}],
            "decisions": [{"node_id": "branch", "matched_class": "yes", "chosen_node_id": "q2"}],
        })
        assert transcript.messages[0].content == "Hi?"
        assert transcript.variables[0].value == ["a", "b"]
        assert transcript.decisions[0].used_default is False


class TestClusteringOut:
    def test_defaults_when_no_run(self) -> None:
        result = ClusteringOut.model_validate({"exists": False})
        assert result.exists is False
        assert result.data_points == []


class TestFlowModels:
    def test_edge_uses_from_alias(self) -> None:
        edge = FlowEdge.model_validate({"from": "start", "to": "q1", "class": "yes"})
        assert edge.from_ == "start"
        assert edge.class_ == "yes"
        assert FlowEdge(from_="a", to="b").from_ == "a"

    def test_flow_serializes_with_api_field_names(self) -> None:
        flow = FlowDocument(
            nodes=[
                FlowNode(id="start", type="start"),
                FlowNode(id="q1", type="question", config={"qtype": "text", "text": "Hi?"}),
                FlowNode(id="end", type="end"),
            ],
            edges=[FlowEdge(from_="start", to="q1"), FlowEdge(from_="q1", to="end")],
        )
        body = compact(flow=flow)
        assert body["flow"]["edges"][0] == {"from": "start", "to": "q1", "default": False, "priority": 0}
        assert body["flow"]["nodes"][0] == {"id": "start", "type": "start"}

    def test_patch_op_keeps_nulls_inside_config(self) -> None:
        op = PatchOp(op="update_node", id="q1", config={"text": "New?", "hint": None})
        assert compact(ops=[op])["ops"] == [{"op": "update_node", "id": "q1", "config": {"text": "New?", "hint": None}}]

    def test_scale_config_defaults(self) -> None:
        scale = ScaleConfig()
        assert (scale.minScale, scale.maxScale) == (1, 10)


SCHEMAS = json.loads((Path(__file__).parent / "fixtures" / "openapi.json").read_text())["components"]["schemas"]
SHARED = sorted(
    name
    for name, obj in vars(deutero.models).items()
    if isinstance(obj, type) and issubclass(obj, BaseModel) and "properties" in SCHEMAS.get(name, {})
)


@pytest.mark.parametrize("name", SHARED)
def test_model_fields_match_spec(name: str) -> None:
    model = getattr(deutero.models, name)
    fields = {f.alias or key for key, f in model.model_fields.items()}
    assert fields == set(SCHEMAS[name]["properties"])
