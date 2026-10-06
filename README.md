# Deutero Python SDK

Official Python bindings for the [Deutero](https://deutero.ai) Study Management API.

Run the full study lifecycle from Python: create and configure studies, gate them with screening and consent, author linear or branching interview flows, recruit and embed, rehearse with AI personas, then monitor, search and cluster the responses.

[![PyPI version](https://img.shields.io/pypi/v/deutero.svg)](https://pypi.org/project/deutero/)
[![Python](https://img.shields.io/pypi/pyversions/deutero.svg)](https://pypi.org/project/deutero/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Installation

```bash
pip install deutero
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add deutero
```

**Requirements:** Python 3.9+

## Quick start

```python
from deutero import Deutero

client = Deutero(api_key="your-api-key")

# 1. Create a project and a study
project = client.projects.create(name="Onboarding research")
study = client.studies.create(
    project_id=project.id,
    name="Why new users drop off",
    survey_type="user_experience",
    research_question="Where does onboarding lose people?",
    target_population="Product managers at 50-500 person companies",
)

# 2. Welcome message, then the interview questions
client.welcome.set(study.id, message="Thanks for joining! This takes about 10 minutes.", consent=True)
client.questions.create(study.id, question="Walk me through your first day with the product.", max_turns=6)
client.questions.create(
    study.id,
    question="How easy was setup?",
    qtype="scale",
    scale={"minScale": 1, "maxScale": 5, "minLabel": "Very hard", "maxLabel": "Very easy"},
)
report = client.questions.validate(study.id)
print("Ethics check passed:", report.ethics_check.passed)

# 3. Rehearse with an AI participant before recruiting
personas = client.personas.generate(study.id, count=1)
run = client.simulations.run(study.id, persona_id=personas.personas[0].id)
print("Simulation started:", run.id, run.status)

# 4. Publish (studies start as drafts), then share the participation link
client.studies.publish(study.id)
recruitment = client.recruitment.get(study.id)
print("Share this link:", recruitment.participation_url)

# 5. Monitor responses
stats = client.studies.get_stats(study.id)
print(f"{stats.completed_interviews}/{stats.total_interviews} completed")
```

## Authentication

Get your API key from the dashboard settings page. You can provide it in two ways:

**Option 1 — Constructor argument:**

```python
client = Deutero(api_key="dtro_...")
```

**Option 2 — Environment variable:**

```bash
export DEUTERO_API_KEY="dtro_..."
```

```python
client = Deutero()  # reads from DEUTERO_API_KEY
```

The key is sent in the `X-API-Key` header.

## Async support

Every method is available in an async variant via `AsyncDeutero`, with identical signatures:

```python
import asyncio
from deutero import AsyncDeutero

async def main():
    async with AsyncDeutero(api_key="your-api-key") as client:
        projects = await client.projects.list()
        for project in projects.projects:
            print(project.name, project.study_count)

asyncio.run(main())
```

## API Reference

All IDs accept either a `str` or a `uuid.UUID`. Optional arguments left as `None` are not sent, so the server default applies (and, for updates, the field is left unchanged). Responses are typed Pydantic models from `deutero.models`.

### `client.projects`

| Method | Endpoint |
|--------|----------|
| `list()` | `GET /projects` |
| `create(name=, description=)` | `POST /projects` |
| `get(project_id)` | `GET /projects/{id}` |
| `update(project_id, name=, description=)` | `PATCH /projects/{id}` |

### `client.studies`

| Method | Endpoint |
|--------|----------|
| `create(project_id=, name=, ...)` | `POST /studies` |
| `list(project_id)` | `GET /projects/{id}/studies` |
| `get(study_id)` | `GET /studies/{id}` |
| `update(study_id, ...)` | `PATCH /studies/{id}` |
| `get_stats(study_id)` | `GET /studies/{id}/stats` |
| `draft(survey_type=, language=, ...brief fields)` | `POST /study-drafts` |
| `draft_from_site(url=, language=)` | `POST /study-drafts/from-site` |
| `get_publication(study_id)` | `GET /studies/{id}/publication` |
| `validate(study_id)` | `POST /studies/{id}/validate` |
| `publish(study_id, acknowledge_validation_run_id=, acknowledge_credit_shortfall=)` | `POST /studies/{id}/publish` |
| `pause(study_id)` | `POST /studies/{id}/pause` |

`survey_type` is one of `sociology`, `user_experience`, `customer_development`, `polling` (see `StudyType`). `model_tier` is one of `open_weights`, `standard`, `premium` (see `ModelTier`; `frontier` is accepted as a deprecated alias for `premium`).

**Drafting with AI.** `draft()` turns a short research brief into study fields and `draft_from_site()` does the same from a product landing page. Neither stores anything: pass the draft's fields to `create()`, then fill in the questions with `client.questions.generate()`.

```python
draft = client.studies.draft(
    survey_type="customer_development",
    problem_hypothesis="Small agencies lose hours every week reconciling invoices",
    customer_segment="Owners of 5-20 person design agencies",
)
study = client.studies.create(project_id=project.id, **draft.model_dump(exclude_none=True))
client.questions.generate(study.id, n_questions=8)
```

**Publication.** A study's `status` is `draft`, `open`, `paused` or `closed`; only an open study admits participants, and an open study's interview configuration is locked. `publish()` checks the plan's open-study limit, credits and a validation of everything participants will read. Ethical and blocking issues must be fixed; methodological issues can be acknowledged. A refused publish raises `ConflictError`, with the details in `e.body`.

```python
run = client.studies.validate(study.id)
for issue in run.issues:
    print(issue.severity, issue.code, issue.message)

if run.outcome in ("passed", "methodological_issues"):
    client.studies.publish(study.id, acknowledge_validation_run_id=run.run_id)

client.studies.pause(study.id)   # stop admitting participants and unlock editing
client.studies.publish(study.id) # reopen
```

### `client.welcome`

| Method | Endpoint |
|--------|----------|
| `get(study_id)` | `GET /studies/{id}/welcome` |
| `set(study_id, message=, consent=)` | `PUT /studies/{id}/welcome` |
| `generate(study_id)` | `POST /studies/{id}/welcome/generate` |
| `list_translations(study_id)` | `GET /studies/{id}/welcome/translations` |
| `upsert_translation(study_id, target_language=, translation_text=)` | `PUT /studies/{id}/welcome/translations` |
| `delete_translation(study_id, translation_id)` | `DELETE /studies/{id}/welcome/translations/{tid}` |

### `client.screening` and `client.characteristics`

Both have the same shape: screening gates participation with qualifying questions, and characteristics collect participant attributes for segmentation.

| Method | Endpoint |
|--------|----------|
| `get(study_id)` | `GET /studies/{id}/screening` |
| `set_settings(study_id, enabled=, ...)` | `PUT /studies/{id}/screening/settings` |
| `create_question(study_id, ...)` | `POST /studies/{id}/screening/questions` |
| `update_question(study_id, question_id, ...)` | `PATCH /studies/{id}/screening/questions/{qid}` |
| `delete_question(study_id, question_id)` | `DELETE /studies/{id}/screening/questions/{qid}` |
| `reorder_questions(study_id, question_ids=)` | `PUT /studies/{id}/screening/questions/order` |

```python
client.screening.create_question(
    study.id,
    question="Do you use the product at work?",
    options=["Yes", "No"],
    acceptable_options=["Yes"],
)
client.screening.set_settings(study.id, enabled=True, disqualification_message="Thanks anyway!")

client.characteristics.create_question(study.id, question="What is your role?", variable="role",
                                       options=["Engineer", "PM", "Designer"])
client.characteristics.set_settings(study.id, enabled=True)
```

### `client.questions`

The linear interview question list.

| Method | Endpoint |
|--------|----------|
| `list(study_id)` | `GET /studies/{id}/questions` |
| `create(study_id, question=, qtype=, ...)` | `POST /studies/{id}/questions` |
| `generate(study_id, n_questions=, additional_instructions=)` | `POST /studies/{id}/questions/generate` |
| `update(study_id, question_id, ...)` | `PATCH /studies/{id}/questions/{qid}` |
| `delete(study_id, question_id)` | `DELETE /studies/{id}/questions/{qid}` |
| `reorder(study_id, question_ids=)` | `PUT /studies/{id}/questions/order` |
| `validate(study_id)` | `POST /studies/{id}/questions/validate` |

If `qtype` is omitted it is inferred: `scale` → scale, `options` → choices, `slots` → slots, `expected_image` → image_upload, otherwise text.

### `client.graph`

The branching alternative to the linear list: an interview flow of steps, conditional paths, captured answers, data fetches and signals.

| Method | Endpoint |
|--------|----------|
| `get(study_id)` | `GET /studies/{id}/graph` |
| `set(study_id, flow=, expected_graph_version=)` | `PUT /studies/{id}/graph` |
| `patch(study_id, ops=, expected_graph_version=)` | `PATCH /studies/{id}/graph` |
| `check(study_id, flow=)` | `POST /studies/{id}/graph/check` |
| `get_signals(study_id)` | `GET /studies/{id}/graph/signals` |
| `import_questions(study_id)` | `POST /studies/{id}/graph/import-questions` |
| `activate(study_id)` / `deactivate(study_id)` | `POST /studies/{id}/graph/activate` / `deactivate` |
| `describe_node_types()` | `GET /graph/node-types` |

Flows and patch operations can be plain dicts in the API's JSON shape, or the typed `FlowDocument`, `FlowNode`, `FlowEdge` and `PatchOp` models. `from` and `class` are Python keywords, so on the models they are `from_` and `class_`:

```python
from deutero import FlowDocument, FlowEdge, FlowNode, PatchOp

# Start from the existing question list, then add a branch
client.graph.import_questions(study.id)
graph = client.graph.get(study.id)

result = client.graph.patch(
    study.id,
    expected_graph_version=graph.graph_version,
    ops=[
        PatchOp(op="update_node", id="q1", config={"text": "Walk me through your first week."}),
    ],
)
if result.valid:
    client.graph.activate(study.id)
else:
    for error in result.errors:
        print(error.node_id, error.code, error.message)
```

`set` and `patch` save nothing unless the resulting flow is valid; invalid flows raise `ValidationError` (with the problems in `e.body`), and a stale `expected_graph_version` raises `ConflictError`.

### `client.recruitment`

| Method | Endpoint |
|--------|----------|
| `get(study_id)` | `GET /studies/{id}/recruitment` |
| `update(study_id, short_url_slug=, max_responses=, clear_max_responses=, redirect_url=)` | `PUT /studies/{id}/recruitment` |

Append `&source=<tag>` and/or `&participant_id=<your id>` to participation links; they come back on interviews as `web_source` and `external_participant_id`.

### `client.embed`

| Method | Endpoint |
|--------|----------|
| `list_keys()` | `GET /embed/keys` |
| `create_key(allowed_origins=, study_id=, metadata_max_bytes=)` | `POST /embed/keys` |
| `update_key(key_id, allowed_origins=, status=, metadata_max_bytes=)` | `PATCH /embed/keys/{id}` |
| `get_snippet(study_id, publishable_key=, mode=)` | `GET /studies/{id}/embed/snippet` |

`create_key` returns the `publishable_key` and `signing_secret` **once only**, so store them immediately.

### `client.personas` and `client.simulations`

| Method | Endpoint |
|--------|----------|
| `personas.list(study_id)` | `GET /studies/{id}/personas` |
| `personas.create(study_id, content=)` | `POST /studies/{id}/personas` |
| `personas.update(study_id, persona_id, content=)` | `PATCH /studies/{id}/personas/{pid}` |
| `personas.delete(study_id, persona_id)` | `DELETE /studies/{id}/personas/{pid}` |
| `personas.generate(study_id, count=, save=)` | `POST /studies/{id}/personas/generate` |
| `simulations.run(study_id, persona_id=, persona=, model_tier=, deliver_signals=)` | `POST /studies/{id}/simulations` |
| `simulations.list(study_id, status=, limit=, offset=)` | `GET /studies/{id}/simulations` |
| `simulations.get(simulation_id)` | `GET /simulations/{id}` |
| `simulations.delete(simulation_id)` | `DELETE /simulations/{id}` |

Simulations run in the background. Poll until they finish:

```python
import time

run = client.simulations.run(study.id, persona="A sceptical ICU nurse, short on time.")
while (sim := client.simulations.get(run.id)).status == "running":
    time.sleep(10)
print(sim.status, sim.credits_used, sim.error)
```

### `client.interviews`

| Method | Endpoint |
|--------|----------|
| `list(study_id, completed=, simulated=, test_runs=, external_participant_id=, started_after=, started_before=, limit=, offset=)` | `GET /studies/{id}/interviews` |
| `find_by_external_id(study_id, external_participant_id=, include_simulated=, include_test_runs=)` | `GET /studies/{id}/interviews/by-external-id` |
| `get(interview_id)` | `GET /interviews/{id}` |
| `get_transcript(interview_id)` | `GET /interviews/{id}/transcript` |
| `get_fetches_and_signals(interview_id)` | `GET /interviews/{id}/fetches-and-signals` |

Test runs — your own interviews through the dashboard's Try Interview / Preview — are left out of interview lists, transcripts and search unless you ask for them (`test_runs=True` / `include_test_runs=True`), and are flagged with `test_run` on each result.

### `client.transcripts`

| Method | Endpoint |
|--------|----------|
| `list(study_id, completed=, include_simulated=, include_test_runs=, external_participant_id=, limit=, offset=)` | `GET /studies/{id}/transcripts` |
| `search(study_id, q=, mode=, question_id=, ...)` | `GET /studies/{id}/search` |

```python
hits = client.transcripts.search(study.id, q="pricing is confusing", mode="semantic")
for hit in hits.hits:
    print(f"{hit.score:.2f}  {hit.participant_name}: {hit.content}")
```

### `client.analysis`

| Method | Endpoint |
|--------|----------|
| `list_questions(study_id, category=)` | `GET /studies/{id}/analysis/questions` |
| `get_scale_responses(study_id, question_id=)` | `GET /studies/{id}/analysis/responses/scale` |
| `get_options_responses(study_id, question_id=)` | `GET /studies/{id}/analysis/responses/options` |
| `cluster(study_id, question_id=, n_clusters=)` | `POST /studies/{id}/analysis/cluster` |
| `get_optimal_clusters(study_id, question_id=)` | `POST /studies/{id}/analysis/optimal-clusters` |
| `get_latest_clustering(study_id)` | `GET /studies/{id}/analysis/clustering/latest` |

```python
text_questions = client.analysis.list_questions(study.id, category="text")
question_id = text_questions.questions[0].id

k = client.analysis.get_optimal_clusters(study.id, question_id=question_id).optimal_k
result = client.analysis.cluster(study.id, question_id=question_id, n_clusters=k)
for cluster in result.data_points:
    print(cluster.name, len(cluster.text))
```

### `client.webhooks`

Organization-level event subscriptions.

| Method | Endpoint |
|--------|----------|
| `list_event_types()` | `GET /webhooks/event-types` |
| `list()` | `GET /webhooks` |
| `create(label=, url=, events=, enabled=)` | `POST /webhooks` |
| `update(webhook_id, ...)` | `PATCH /webhooks/{id}` |
| `delete(webhook_id)` | `DELETE /webhooks/{id}` |
| `rotate_secret(webhook_id)` | `POST /webhooks/{id}/rotate-secret` |
| `list_deliveries(webhook_id, event_type=, success=, ...)` | `GET /webhooks/{id}/deliveries` |

`create` and `rotate_secret` are the only calls that return the signing secret.

## Receiving webhooks

`deutero.webhooks` verifies and parses what Deutero POSTs to you. It needs no API key, so it works in a receiver that never calls the API. Deliveries are signed with [Standard Webhooks](https://www.standardwebhooks.com). The same function handles organization events (secret from `client.webhooks.create`) and interview-flow "Send a signal" steps (per-step secret from `client.graph.get_signals`).

```python
from flask import Flask, request

from deutero import webhooks
from deutero.webhooks import InterviewCompletedEvent, StudyFullEvent

app = Flask(__name__)

@app.post("/deutero")
def receive():
    try:
        # Pass the raw body bytes. Re-serialized JSON will not verify.
        event = webhooks.unwrap(request.get_data(), request.headers, secret=SIGNING_SECRET)
    except webhooks.WebhookVerificationError:
        return "", 400

    if already_processed(event.webhook_id):  # dedupe on the webhook-id header
        return "", 204

    if isinstance(event, InterviewCompletedEvent) and event.data.completed:
        reward(event.data.external_participant_id)
    elif isinstance(event, StudyFullEvent):
        close_campaign(event.data.survey_id)
    return "", 204
```

| Event `type` | Model | `data` fields |
|---|---|---|
| `interview.started` | `InterviewStartedEvent` | `interview_id`, `survey_id`, `participant_id`, `external_participant_id`, `web_source` |
| `interview.completed` | `InterviewCompletedEvent` | the above plus `completed` |
| `analysis.completed` | `AnalysisCompletedEvent` | `interview_id`, `survey_id` |
| `simulation.completed` | `SimulationCompletedEvent` | `interview_id`, `survey_id` |
| `study.created` | `StudyCreatedEvent` | `study_id`, `survey_id`, `name`, `project_id`, `created_via` |
| `credits.exhausted` | `CreditsExhaustedEvent` | `organization_id` |
| `study.full` | `StudyFullEvent` | `survey_id`, `survey_name` |

`survey_id` is the study ID under its older name. Flow signals and any event type the SDK doesn't know yet come back as a plain `WebhookEvent`, with `data` as a dict. `event.simulated` is `True` for signals sent from a simulated interview. `external_participant_id` and `web_source` come from the participant's link and are not authenticated. The signature proves the event came from Deutero, not who the participant is.

Other helpers:

- `webhooks.verify(body, headers, secret=)` checks the signature only.
- `webhooks.parse_event(body, headers)` parses without verifying (tests only).
- `webhooks.sign(body, secret=, msg_id=)` builds valid headers so you can exercise your receiver locally.

Deliveries older or newer than 5 minutes are rejected. Change this with `tolerance=` (in seconds), or pass `tolerance=None` to replay stored deliveries.

### `client.credits` and `client.health()`

| Method | Endpoint |
|--------|----------|
| `credits.get_balance()` | `GET /credits/balance` |
| `health()` | `GET /health` |

## Error handling

The SDK raises specific exceptions for different error types:

```python
from deutero import (
    Deutero,
    APIError,
    AuthenticationError,
    ConflictError,
    InsufficientCreditsError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)

client = Deutero(api_key="your-key")

try:
    client.simulations.run(study_id, persona_id=persona_id, model_tier="premium")
except PermissionDeniedError as e:
    print(f"Not available on your plan: {e.message}")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Study or persona not found")
except InsufficientCreditsError as e:
    print(f"Not enough credits: {e.message}")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except RateLimitError:
    print("Too many requests — retry later")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### Exception hierarchy

```
DeuteroError
├── APIError
│   ├── AuthenticationError      (401)
│   │   └── PermissionDeniedError (403)
│   ├── NotFoundError            (404)
│   ├── ConflictError            (409)
│   ├── ValidationError          (400, 422)
│   ├── InsufficientCreditsError (402)
│   ├── RateLimitError           (429)
│   ├── BadGatewayError          (502)
│   └── InternalServerError      (5xx)
├── ConnectionError
├── TimeoutError
└── WebhookVerificationError
```

## Configuration

### Custom base URL

The default is `https://dashboard.deutero.ai/study-api`.

```python
client = Deutero(
    api_key="your-key",
    base_url="https://staging.example.com/study-api",
)
```

### Custom timeout

```python
client = Deutero(
    api_key="your-key",
    timeout=300.0,  # 5 minutes
)
```

### Custom HTTP client

Bring your own `httpx.Client` for proxies, retries, or other transport customization. The SDK still adds its base URL (if your client has none) and the API key header:

```python
import httpx

http_client = httpx.Client(
    proxy="http://proxy.example.com:8080",
    verify="/path/to/cert.pem",
)

client = Deutero(
    api_key="your-key",
    http_client=http_client,
)
```

### Context manager

```python
with Deutero(api_key="your-key") as client:
    balance = client.credits.get_balance()
    print(balance.net_available)
# Connection pool is automatically closed
```

## Development

```bash
uv venv && uv pip install -e ".[dev]"
pytest
```

`tests/fixtures/openapi.json` is a copy of the API spec. `tests/test_resources.py` checks that every endpoint in it is reachable through the SDK and that its response parses into the matching model, so refresh that file when the API changes:

```bash
curl -s https://dashboard.deutero.ai/study-api/api/v1/openapi.json | python -m json.tool --indent 1 > tests/fixtures/openapi.json
pytest tests/test_resources.py
```

## License

MIT — see [LICENSE](LICENSE).
