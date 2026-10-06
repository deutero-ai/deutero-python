"""Tests for resource methods — every endpoint in the OpenAPI spec is called through the SDK.

Each case checks the HTTP method, path, JSON body and query string the SDK sends, then
feeds back a minimal response generated from the spec's response schema and checks that it
parses into the matching model. The same cases run against the sync and async clients.
"""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

import httpx
import pytest
from pydantic import BaseModel

import deutero.models
from deutero import AsyncDeutero, Deutero
from deutero.models import FlowDocument, FlowEdge, FlowNode, PatchOp

SPEC = json.loads((Path(__file__).parent / "fixtures" / "openapi.json").read_text())
SCHEMAS: Dict[str, Any] = SPEC["components"]["schemas"]
BASE = "https://t.test/study-api"

STUDY = "00000000-0000-0000-0000-000000000001"
PROJECT = "00000000-0000-0000-0000-000000000002"
QUESTION = "00000000-0000-0000-0000-000000000003"
PERSONA = "00000000-0000-0000-0000-000000000004"
INTERVIEW = "00000000-0000-0000-0000-000000000005"
SIMULATION = "00000000-0000-0000-0000-000000000006"
WEBHOOK = "00000000-0000-0000-0000-000000000007"
KEY = "00000000-0000-0000-0000-000000000008"
TRANSLATION = "00000000-0000-0000-0000-000000000009"
VALIDATION_RUN = "00000000-0000-0000-0000-00000000000a"


# ---------------------------------------------------------------------------
# Spec helpers
# ---------------------------------------------------------------------------

def _sample(schema: Dict[str, Any]) -> Any:
    """Build the smallest value that satisfies ``schema`` (required fields only)."""
    if "$ref" in schema:
        return _sample(SCHEMAS[schema["$ref"].split("/")[-1]])
    if "anyOf" in schema:
        return _sample(next(s for s in schema["anyOf"] if s.get("type") != "null"))
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        return {name: _sample(schema["properties"][name]) for name in schema.get("required", [])}
    if kind == "array":
        return []
    if kind == "string":
        return STUDY if schema.get("format") == "uuid" else "x"
    return {"integer": 1, "number": 1.5, "boolean": True}.get(kind or "")


class Route(NamedTuple):
    method: str
    template: str
    pattern: "re.Pattern[str]"
    status: int
    schema: Optional[Dict[str, Any]]


def _routes() -> List[Route]:
    routes = []
    for template, ops in SPEC["paths"].items():
        pattern = re.compile("^/study-api" + re.sub(r"\{[^}]+\}", "[^/]+", template) + "$")
        for method, op in ops.items():
            status, response = next((c, r) for c, r in op["responses"].items() if c.startswith("2"))
            schema = response.get("content", {}).get("application/json", {}).get("schema")
            routes.append(Route(method.upper(), template, pattern, int(status), schema))
    return routes


ROUTES = _routes()


def _match(request: httpx.Request) -> Route:
    # Literal segments (e.g. ``/interviews/by-external-id``) must win over ``{id}`` placeholders.
    candidates = [r for r in ROUTES if r.method == request.method and r.pattern.match(request.url.path)]
    assert candidates, f"no spec route for {request.method} {request.url.path}"
    return min(candidates, key=lambda r: r.template.count("{"))


class Recorder:
    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []
        self.routes: List[Route] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        route = _match(request)
        self.requests.append(request)
        self.routes.append(route)
        if route.schema is None:
            return httpx.Response(route.status)
        return httpx.Response(route.status, json=_sample(route.schema))


# ---------------------------------------------------------------------------
# Cases: (id, call, method, path, json body, query params)
# ---------------------------------------------------------------------------

FLOW = FlowDocument(
    nodes=[FlowNode(id="start", type="start"), FlowNode(id="end", type="end")],
    edges=[FlowEdge(from_="start", to="end")],
)
FLOW_JSON = {
    "nodes": [{"id": "start", "type": "start"}, {"id": "end", "type": "end"}],
    "edges": [{"from": "start", "to": "end", "default": False, "priority": 0}],
}

Call = Callable[[Any], Any]
Case = Tuple[str, Call, str, str, Optional[Dict[str, Any]], Optional[Dict[str, str]]]

CASES: List[Case] = [
    # Projects
    ("projects.list", lambda c: c.projects.list(), "GET", "/api/v1/projects", None, None),
    ("projects.create", lambda c: c.projects.create(name="P", description="D"),
     "POST", "/api/v1/projects", {"name": "P", "description": "D"}, None),
    ("projects.get", lambda c: c.projects.get(PROJECT), "GET", f"/api/v1/projects/{PROJECT}", None, None),
    ("projects.update", lambda c: c.projects.update(PROJECT, name="Renamed"),
     "PATCH", f"/api/v1/projects/{PROJECT}", {"name": "Renamed"}, None),
    # Studies
    ("studies.create",
     lambda c: c.studies.create(project_id=PROJECT, name="S", survey_type=deutero.models.StudyType.POLLING,
                                max_responses=10, anonymous=False),
     "POST", "/api/v1/studies",
     {"project_id": PROJECT, "name": "S", "survey_type": "polling", "max_responses": 10, "anonymous": False}, None),
    ("studies.list", lambda c: c.studies.list(PROJECT), "GET", f"/api/v1/projects/{PROJECT}/studies", None, None),
    ("studies.get", lambda c: c.studies.get(STUDY), "GET", f"/api/v1/studies/{STUDY}", None, None),
    ("studies.update", lambda c: c.studies.update(STUDY, model_tier="premium", voice_enabled=True),
     "PATCH", f"/api/v1/studies/{STUDY}", {"model_tier": "premium", "voice_enabled": True}, None),
    ("studies.get_stats", lambda c: c.studies.get_stats(STUDY), "GET", f"/api/v1/studies/{STUDY}/stats", None, None),
    ("studies.draft",
     lambda c: c.studies.draft(survey_type=deutero.models.StudyType.SOCIOLOGY, research_question="How?",
                               population_of_interest="Remote workers", language="French"),
     "POST", "/api/v1/study-drafts",
     {"survey_type": "sociology", "research_question": "How?", "population_of_interest": "Remote workers",
      "language": "French"}, None),
    ("studies.draft_from_site", lambda c: c.studies.draft_from_site(url="https://acme.test"),
     "POST", "/api/v1/study-drafts/from-site", {"url": "https://acme.test"}, None),
    # Publication
    ("studies.get_publication", lambda c: c.studies.get_publication(STUDY),
     "GET", f"/api/v1/studies/{STUDY}/publication", None, None),
    ("studies.validate", lambda c: c.studies.validate(STUDY), "POST", f"/api/v1/studies/{STUDY}/validate", None, None),
    ("studies.publish",
     lambda c: c.studies.publish(STUDY, acknowledge_validation_run_id=VALIDATION_RUN,
                                 acknowledge_credit_shortfall=True),
     "POST", f"/api/v1/studies/{STUDY}/publish",
     {"acknowledge_validation_run_id": VALIDATION_RUN, "acknowledge_credit_shortfall": True}, None),
    ("studies.publish_plain", lambda c: c.studies.publish(STUDY),
     "POST", f"/api/v1/studies/{STUDY}/publish", {}, None),
    ("studies.pause", lambda c: c.studies.pause(STUDY), "POST", f"/api/v1/studies/{STUDY}/pause", None, None),
    # Welcome
    ("welcome.get", lambda c: c.welcome.get(STUDY), "GET", f"/api/v1/studies/{STUDY}/welcome", None, None),
    ("welcome.set", lambda c: c.welcome.set(STUDY, message="Hi", consent=True),
     "PUT", f"/api/v1/studies/{STUDY}/welcome", {"message": "Hi", "consent": True}, None),
    ("welcome.generate", lambda c: c.welcome.generate(STUDY),
     "POST", f"/api/v1/studies/{STUDY}/welcome/generate", None, None),
    ("welcome.list_translations", lambda c: c.welcome.list_translations(STUDY),
     "GET", f"/api/v1/studies/{STUDY}/welcome/translations", None, None),
    ("welcome.upsert_translation",
     lambda c: c.welcome.upsert_translation(STUDY, target_language="es", translation_text="Hola"),
     "PUT", f"/api/v1/studies/{STUDY}/welcome/translations", {"target_language": "es", "translation_text": "Hola"},
     None),
    ("welcome.delete_translation", lambda c: c.welcome.delete_translation(STUDY, TRANSLATION),
     "DELETE", f"/api/v1/studies/{STUDY}/welcome/translations/{TRANSLATION}", None, None),
    # Screening
    ("screening.get", lambda c: c.screening.get(STUDY), "GET", f"/api/v1/studies/{STUDY}/screening", None, None),
    ("screening.set_settings", lambda c: c.screening.set_settings(STUDY, enabled=True, redirect_url="https://r"),
     "PUT", f"/api/v1/studies/{STUDY}/screening/settings", {"enabled": True, "redirect_url": "https://r"}, None),
    ("screening.create_question",
     lambda c: c.screening.create_question(STUDY, question="Q?", options=["a", "b"], acceptable_options=["a"]),
     "POST", f"/api/v1/studies/{STUDY}/screening/questions",
     {"question": "Q?", "options": ["a", "b"], "acceptable_options": ["a"]}, None),
    ("screening.update_question", lambda c: c.screening.update_question(STUDY, QUESTION, acceptable_options=["b"]),
     "PATCH", f"/api/v1/studies/{STUDY}/screening/questions/{QUESTION}", {"acceptable_options": ["b"]}, None),
    ("screening.delete_question", lambda c: c.screening.delete_question(STUDY, QUESTION),
     "DELETE", f"/api/v1/studies/{STUDY}/screening/questions/{QUESTION}", None, None),
    ("screening.reorder_questions", lambda c: c.screening.reorder_questions(STUDY, question_ids=[QUESTION]),
     "PUT", f"/api/v1/studies/{STUDY}/screening/questions/order", {"question_ids": [QUESTION]}, None),
    # Characteristics
    ("characteristics.get", lambda c: c.characteristics.get(STUDY),
     "GET", f"/api/v1/studies/{STUDY}/characteristics", None, None),
    ("characteristics.set_settings", lambda c: c.characteristics.set_settings(STUDY, enabled=True, anonymous=True),
     "PUT", f"/api/v1/studies/{STUDY}/characteristics/settings", {"enabled": True, "anonymous": True}, None),
    ("characteristics.create_question",
     lambda c: c.characteristics.create_question(STUDY, question="Age?", variable="age", question_type="slot",
                                                 slot_description="Age in years"),
     "POST", f"/api/v1/studies/{STUDY}/characteristics/questions",
     {"question": "Age?", "variable": "age", "question_type": "slot", "slot_description": "Age in years"}, None),
    ("characteristics.update_question",
     lambda c: c.characteristics.update_question(STUDY, QUESTION, options=["18-24", "25+"]),
     "PATCH", f"/api/v1/studies/{STUDY}/characteristics/questions/{QUESTION}", {"options": ["18-24", "25+"]}, None),
    ("characteristics.delete_question", lambda c: c.characteristics.delete_question(STUDY, QUESTION),
     "DELETE", f"/api/v1/studies/{STUDY}/characteristics/questions/{QUESTION}", None, None),
    ("characteristics.reorder_questions",
     lambda c: c.characteristics.reorder_questions(STUDY, question_ids=[QUESTION]),
     "PUT", f"/api/v1/studies/{STUDY}/characteristics/questions/order", {"question_ids": [QUESTION]}, None),
    # Credits
    ("credits.get_balance", lambda c: c.credits.get_balance(), "GET", "/api/v1/credits/balance", None, None),
    # Questions
    ("questions.list", lambda c: c.questions.list(STUDY), "GET", f"/api/v1/studies/{STUDY}/questions", None, None),
    ("questions.create",
     lambda c: c.questions.create(STUDY, question="How satisfied?", qtype="scale",
                                  scale=deutero.models.ScaleConfig(maxScale=5), follow_up=False),
     "POST", f"/api/v1/studies/{STUDY}/questions",
     {"question": "How satisfied?", "qtype": "scale", "follow_up": False,
      "scale": {"minScale": 1, "maxScale": 5, "minLabel": "Least", "maxLabel": "Most"}}, None),
    ("questions.generate",
     lambda c: c.questions.generate(STUDY, n_questions=5, additional_instructions="Start with a warm-up"),
     "POST", f"/api/v1/studies/{STUDY}/questions/generate",
     {"n_questions": 5, "additional_instructions": "Start with a warm-up"}, None),
    ("questions.update", lambda c: c.questions.update(STUDY, QUESTION, options=[], max_turns=4),
     "PATCH", f"/api/v1/studies/{STUDY}/questions/{QUESTION}", {"options": [], "max_turns": 4}, None),
    ("questions.delete", lambda c: c.questions.delete(STUDY, QUESTION),
     "DELETE", f"/api/v1/studies/{STUDY}/questions/{QUESTION}", None, None),
    ("questions.reorder", lambda c: c.questions.reorder(STUDY, question_ids=[QUESTION]),
     "PUT", f"/api/v1/studies/{STUDY}/questions/order", {"question_ids": [QUESTION]}, None),
    ("questions.validate", lambda c: c.questions.validate(STUDY),
     "POST", f"/api/v1/studies/{STUDY}/questions/validate", None, None),
    # Interview flow
    ("graph.get", lambda c: c.graph.get(STUDY), "GET", f"/api/v1/studies/{STUDY}/graph", None, None),
    ("graph.set", lambda c: c.graph.set(STUDY, flow=FLOW, expected_graph_version=2),
     "PUT", f"/api/v1/studies/{STUDY}/graph", {"flow": FLOW_JSON, "expected_graph_version": 2}, None),
    ("graph.patch",
     lambda c: c.graph.patch(STUDY, ops=[PatchOp(op="remove_node", id="q1"), {"op": "remove_edge", "from": "a",
                                                                               "to": "b"}]),
     "PATCH", f"/api/v1/studies/{STUDY}/graph",
     {"ops": [{"op": "remove_node", "id": "q1"}, {"op": "remove_edge", "from": "a", "to": "b"}]}, None),
    ("graph.get_signals", lambda c: c.graph.get_signals(STUDY),
     "GET", f"/api/v1/studies/{STUDY}/graph/signals", None, None),
    ("graph.check", lambda c: c.graph.check(STUDY, flow=FLOW_JSON),
     "POST", f"/api/v1/studies/{STUDY}/graph/check", {"flow": FLOW_JSON}, None),
    ("graph.import_questions", lambda c: c.graph.import_questions(STUDY),
     "POST", f"/api/v1/studies/{STUDY}/graph/import-questions", None, None),
    ("graph.activate", lambda c: c.graph.activate(STUDY),
     "POST", f"/api/v1/studies/{STUDY}/graph/activate", None, None),
    ("graph.deactivate", lambda c: c.graph.deactivate(STUDY),
     "POST", f"/api/v1/studies/{STUDY}/graph/deactivate", None, None),
    ("graph.describe_node_types", lambda c: c.graph.describe_node_types(),
     "GET", "/api/v1/graph/node-types", None, None),
    # Recruitment
    ("recruitment.get", lambda c: c.recruitment.get(STUDY),
     "GET", f"/api/v1/studies/{STUDY}/recruitment", None, None),
    ("recruitment.update", lambda c: c.recruitment.update(STUDY, short_url_slug="my-study", clear_max_responses=True),
     "PUT", f"/api/v1/studies/{STUDY}/recruitment", {"short_url_slug": "my-study", "clear_max_responses": True},
     None),
    # Embed
    ("embed.list_keys", lambda c: c.embed.list_keys(), "GET", "/api/v1/embed/keys", None, None),
    ("embed.create_key", lambda c: c.embed.create_key(allowed_origins=["https://a.test"], study_id=STUDY),
     "POST", "/api/v1/embed/keys", {"allowed_origins": ["https://a.test"], "study_id": STUDY}, None),
    ("embed.update_key", lambda c: c.embed.update_key(KEY, status="revoked"),
     "PATCH", f"/api/v1/embed/keys/{KEY}", {"status": "revoked"}, None),
    ("embed.get_snippet", lambda c: c.embed.get_snippet(STUDY, publishable_key="pk_1"),
     "GET", f"/api/v1/studies/{STUDY}/embed/snippet", None, {"publishable_key": "pk_1"}),
    # Personas
    ("personas.list", lambda c: c.personas.list(STUDY), "GET", f"/api/v1/studies/{STUDY}/personas", None, None),
    ("personas.create", lambda c: c.personas.create(STUDY, content="A nurse"),
     "POST", f"/api/v1/studies/{STUDY}/personas", {"content": "A nurse"}, None),
    ("personas.update", lambda c: c.personas.update(STUDY, PERSONA, content="A doctor"),
     "PATCH", f"/api/v1/studies/{STUDY}/personas/{PERSONA}", {"content": "A doctor"}, None),
    ("personas.delete", lambda c: c.personas.delete(STUDY, PERSONA),
     "DELETE", f"/api/v1/studies/{STUDY}/personas/{PERSONA}", None, None),
    ("personas.generate", lambda c: c.personas.generate(STUDY, count=3, save=False),
     "POST", f"/api/v1/studies/{STUDY}/personas/generate", {"count": 3, "save": False}, None),
    # Simulations
    ("simulations.run", lambda c: c.simulations.run(STUDY, persona_id=PERSONA, model_tier="standard"),
     "POST", f"/api/v1/studies/{STUDY}/simulations", {"persona_id": PERSONA, "model_tier": "standard"}, None),
    ("simulations.list", lambda c: c.simulations.list(STUDY, status="running", limit=10),
     "GET", f"/api/v1/studies/{STUDY}/simulations", None, {"status": "running", "limit": "10"}),
    ("simulations.get", lambda c: c.simulations.get(SIMULATION),
     "GET", f"/api/v1/simulations/{SIMULATION}", None, None),
    ("simulations.delete", lambda c: c.simulations.delete(SIMULATION),
     "DELETE", f"/api/v1/simulations/{SIMULATION}", None, None),
    # Interviews
    ("interviews.list",
     lambda c: c.interviews.list(STUDY, completed=True, simulated=False, test_runs=True,
                                 started_after="2026-01-01T00:00:00"),
     "GET", f"/api/v1/studies/{STUDY}/interviews", None,
     {"completed": "true", "simulated": "false", "test_runs": "true", "started_after": "2026-01-01T00:00:00"}),
    ("interviews.find_by_external_id",
     lambda c: c.interviews.find_by_external_id(STUDY, external_participant_id="crm-42", include_test_runs=True),
     "GET", f"/api/v1/studies/{STUDY}/interviews/by-external-id", None,
     {"external_participant_id": "crm-42", "include_test_runs": "true"}),
    ("interviews.get", lambda c: c.interviews.get(INTERVIEW), "GET", f"/api/v1/interviews/{INTERVIEW}", None, None),
    ("interviews.get_transcript", lambda c: c.interviews.get_transcript(INTERVIEW),
     "GET", f"/api/v1/interviews/{INTERVIEW}/transcript", None, None),
    ("interviews.get_fetches_and_signals", lambda c: c.interviews.get_fetches_and_signals(INTERVIEW),
     "GET", f"/api/v1/interviews/{INTERVIEW}/fetches-and-signals", None, None),
    # Transcripts & search
    ("transcripts.list",
     lambda c: c.transcripts.list(STUDY, include_simulated=True, include_test_runs=False, offset=20),
     "GET", f"/api/v1/studies/{STUDY}/transcripts", None,
     {"include_simulated": "true", "include_test_runs": "false", "offset": "20"}),
    ("transcripts.search",
     lambda c: c.transcripts.search(STUDY, q="pricing", mode=deutero.models.SearchMode.SEMANTIC, strict=True,
                                    include_test_runs=True),
     "GET", f"/api/v1/studies/{STUDY}/search", None,
     {"q": "pricing", "mode": "semantic", "strict": "true", "include_test_runs": "true"}),
    # Analysis
    ("analysis.list_questions", lambda c: c.analysis.list_questions(STUDY, category="scale"),
     "GET", f"/api/v1/studies/{STUDY}/analysis/questions", None, {"category": "scale"}),
    ("analysis.get_scale_responses", lambda c: c.analysis.get_scale_responses(STUDY, question_id="q1"),
     "GET", f"/api/v1/studies/{STUDY}/analysis/responses/scale", None, {"question_id": "q1"}),
    ("analysis.get_options_responses", lambda c: c.analysis.get_options_responses(STUDY, question_id="q1"),
     "GET", f"/api/v1/studies/{STUDY}/analysis/responses/options", None, {"question_id": "q1"}),
    ("analysis.cluster", lambda c: c.analysis.cluster(STUDY, question_id="q1", n_clusters=4),
     "POST", f"/api/v1/studies/{STUDY}/analysis/cluster", {"question_id": "q1", "n_clusters": 4}, None),
    ("analysis.get_optimal_clusters", lambda c: c.analysis.get_optimal_clusters(STUDY, question_number=2),
     "POST", f"/api/v1/studies/{STUDY}/analysis/optimal-clusters", {"question_number": 2}, None),
    ("analysis.get_latest_clustering", lambda c: c.analysis.get_latest_clustering(STUDY),
     "GET", f"/api/v1/studies/{STUDY}/analysis/clustering/latest", None, None),
    # Webhooks
    ("webhooks.list_event_types", lambda c: c.webhooks.list_event_types(),
     "GET", "/api/v1/webhooks/event-types", None, None),
    ("webhooks.list", lambda c: c.webhooks.list(), "GET", "/api/v1/webhooks", None, None),
    ("webhooks.create",
     lambda c: c.webhooks.create(label="CRM", url="https://h.test", events=["interview.completed"]),
     "POST", "/api/v1/webhooks", {"label": "CRM", "url": "https://h.test", "events": ["interview.completed"]}, None),
    ("webhooks.update", lambda c: c.webhooks.update(WEBHOOK, enabled=False),
     "PATCH", f"/api/v1/webhooks/{WEBHOOK}", {"enabled": False}, None),
    ("webhooks.delete", lambda c: c.webhooks.delete(WEBHOOK), "DELETE", f"/api/v1/webhooks/{WEBHOOK}", None, None),
    ("webhooks.rotate_secret", lambda c: c.webhooks.rotate_secret(WEBHOOK),
     "POST", f"/api/v1/webhooks/{WEBHOOK}/rotate-secret", None, None),
    ("webhooks.list_deliveries", lambda c: c.webhooks.list_deliveries(WEBHOOK, success=False),
     "GET", f"/api/v1/webhooks/{WEBHOOK}/deliveries", None, {"success": "false"}),
    # Health
    ("health", lambda c: c.health(), "GET", "/health", None, None),
]


def _check(case: Case, recorder: Recorder, result: Any) -> None:
    _, _, method, path, body, params = case
    assert len(recorder.requests) == 1
    request, route = recorder.requests[0], recorder.routes[0]
    assert request.method == method
    assert request.url.path == "/study-api" + path
    assert request.headers["X-API-Key"] == "k"

    sent = json.loads(request.content) if request.content else None
    if body is None:
        assert not sent, f"unexpected body {sent}"
    else:
        assert sent == body

    assert dict(request.url.params) == (params or {})

    if route.schema is None:
        assert result is None
    elif "$ref" in route.schema:
        model = getattr(deutero.models, route.schema["$ref"].split("/")[-1])
        assert isinstance(result, model)
    else:
        assert isinstance(result, dict) and not isinstance(result, BaseModel)


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_sync(case: Case) -> None:
    recorder = Recorder()
    http_client = httpx.Client(transport=httpx.MockTransport(recorder), base_url=BASE)
    with Deutero(api_key="k", base_url=BASE, http_client=http_client) as client:
        result = case[1](client)
    _check(case, recorder, result)


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
async def test_async(case: Case) -> None:
    recorder = Recorder()
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(recorder), base_url=BASE)
    async with AsyncDeutero(api_key="k", base_url=BASE, http_client=http_client) as client:
        pending = case[1](client)
        assert inspect.isawaitable(pending)
        result = await pending
    _check(case, recorder, result)


def test_every_spec_endpoint_is_covered() -> None:
    covered = set()
    for case in CASES:
        recorder = Recorder()
        http_client = httpx.Client(transport=httpx.MockTransport(recorder), base_url=BASE)
        with Deutero(api_key="k", base_url=BASE, http_client=http_client) as client:
            case[1](client)
        covered.add((recorder.routes[0].method, recorder.routes[0].template))
    expected = {(r.method, r.template) for r in ROUTES}
    assert expected - covered == set()


def test_sync_and_async_resources_match() -> None:
    sync, async_ = Deutero(api_key="k"), AsyncDeutero(api_key="k")
    for name, resource in vars(sync).items():
        if name.startswith("_"):
            continue
        async_resource = getattr(async_, name)
        public = {m for m in dir(resource) if not m.startswith("_")}
        assert public == {m for m in dir(async_resource) if not m.startswith("_")}, name
        for method in public:
            assert inspect.signature(getattr(resource, method)) == inspect.signature(getattr(async_resource, method))
            assert inspect.iscoroutinefunction(getattr(async_resource, method)), f"{name}.{method}"
    sync.close()
