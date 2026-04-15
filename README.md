# Deutero Python SDK

Official Python bindings for the [Deutero](https://deutero.ai) research platform API.

Design, run, and analyse qualitative research studies — interviews, simulations, and thematic analysis — all from Python.

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

# 1. Generate a research study
study = client.studies.generate(
    study_type="user_experience",
    business_context="Our SaaS platform helps remote teams collaborate on documents",
    research_need="Understand why new users drop off during onboarding",
    target_users="Product managers at companies with 50-500 employees",
)
print(f"Created study: {study.study_name} (ID: {study.study_id})")

# 2. Generate interview questions
questions = client.questions.generate(
    study_id=study.study_id,
    number_of_questions=8,
)
print(f"Generated {len(questions.question_list)} questions")

# 3. Generate synthetic personas
personas = client.personas.generate(
    study_id=study.study_id,
    number_of_personas=5,
)

# 4. Simulate interviews
for persona in personas.personas:
    sim = client.interviews.simulate(
        study_id=study.study_id,
        persona_id=persona.persona_id,
    )
    print(f"Simulated interview: {sim.transcript_url}")

# 5. Run thematic analysis
result = client.analysis.run(
    study_id=study.study_id,
    model_tier="premium",
)
print(f"Queued analysis for {result.interviews_queued} interviews")

# 6. Check analysis progress
status = client.analysis.get_status(study_id=study.study_id)
for interview in status.interviews:
    print(f"  {interview.interview_id}: {interview.status} ({interview.phases_completed}/4 phases)")
```

## Authentication

Get your API key from the [Deutero dashboard](https://app.deutero.ai). You can provide it in two ways:

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

## Async support

Every method is available in an async variant via `AsyncDeutero`:

```python
import asyncio
from deutero import AsyncDeutero

async def main():
    async with AsyncDeutero(api_key="your-api-key") as client:
        study = await client.studies.generate(
            study_type="sociology",
            research_question="How do remote workers maintain social connections?",
            population_of_interest="Full-time remote workers in tech companies",
        )
        print(study.study_name)

asyncio.run(main())
```

## API Reference

### `client.studies`

| Method | Description |
|--------|-------------|
| `generate(...)` | Create a new research study (UX, sociology, customer dev, polling) |
| `get_participation(study_id)` | Get interview completion & quota statistics |
| `get_agent_requirements(study_id)` | Get/generate agent requirements markdown |
| `get_model_tier(study_id)` | Get current model tier configuration |
| `set_model_tier(study_id, model_tier=)` | Change the model tier |

#### Study types and their required fields

**User Experience** (`study_type="user_experience"`):
- `business_context` (required) — Overview of the business or product
- `research_need` (required) — Why the research is being conducted
- `target_users` — Primary audience
- `constraints` — Timing or other considerations

**Sociology** (`study_type="sociology"`):
- `research_question` (required) — The research question
- `population_of_interest` (required) — Population being studied
- `context_or_setting` — Where the phenomenon occurs
- `key_concepts` — Main concepts being examined
- `scope_and_boundaries` — What's included/excluded

**Customer Development** (`study_type="customer_development"`):
- `problem_hypothesis` (required) — The problem hypothesis
- `customer_segment` (required) — Target customer segment
- `solution_concept` — Proposed solution
- `key_assumptions` — Assumptions to validate
- `success_criteria` — How to measure success

**Polling** (`study_type="polling"`):
- `research_question` (required) — The research question
- `population_segment` — Target population
- `geographic_scope` — Geographic boundaries
- `survey_context` — Context for the survey
- `data_quality_requirements` — Quality standards

### `client.questions`

| Method | Description |
|--------|-------------|
| `generate(study_id=, number_of_questions=)` | Generate interview questions for a study |
| `get(question_id)` | Get a question's properties |
| `update(question_id, ...)` | Update question text, scale, options, etc. |

```python
# Generate questions with custom instructions
questions = client.questions.generate(
    study_id=study.study_id,
    number_of_questions=10,
    additional_instructions="Focus on emotional aspects of the experience",
)

# Update a question
client.questions.update(
    question_id,
    question="How would you describe your first experience?",
    min_turns=3,
    max_turns=5,
)
```

### `client.personas`

| Method | Description |
|--------|-------------|
| `generate(study_id=, number_of_personas=)` | Generate synthetic interviewee personas |

```python
personas = client.personas.generate(
    study_id=study.study_id,
    number_of_personas=5,
    additional_instructions="Include diverse professional backgrounds",
)
for p in personas.personas:
    print(f"{p.persona_id}: {p.persona[:80]}...")
```

### `client.interviews`

| Method | Description |
|--------|-------------|
| `simulate(study_id=, persona_id=)` | Run a simulated interview (background task) |

```python
sim = client.interviews.simulate(
    study_id=study.study_id,
    persona_id=personas.personas[0].persona_id,
)
print(f"Credits used: {sim.credits_used}")
print(f"Credits remaining: {sim.credits_remaining}")
print(f"Transcript: {sim.transcript_url}")
```

### `client.analysis`

| Method | Description |
|--------|-------------|
| `run(study_id=, model_tier=)` | Run phases 1–4 on all completed interviews |
| `run(interview_id=, model_tier=)` | Run phases 1–4 on a single interview |
| `run(study_id=, cross_case_analysis=True)` | Run cross-case analysis (phase 5) |
| `get_status(study_id=)` | Get analysis progress for all interviews |
| `get_status(interview_id=)` | Get analysis progress for one interview |
| `get_interview_results(interview_id=, phase=)` | Get XML output for a phase |
| `get_survey_results(study_id=)` | Get cross-case analysis XML |

#### Analysis phases

| Phase | Name | Description |
|-------|------|-------------|
| 1 | `initial_engagement` | Initial reading and engagement with the transcript |
| 2 | `initial_noting` | Exploratory comments and initial notes |
| 3 | `emergent_themes` | Identification of emergent themes |
| 4 | `connections` | Connections across themes |
| 5 | Cross-case | Synthesis across all interviews (requires ≥3 completed) |

```python
# Run analysis on all completed interviews
result = client.analysis.run(
    study_id=study.study_id,
    model_tier="premium",
)

# Poll for completion
import time
while True:
    status = client.analysis.get_status(study_id=study.study_id)
    done = all(i.status == "completed" for i in status.interviews)
    if done:
        break
    time.sleep(30)

# Get results
for interview in status.interviews:
    themes = client.analysis.get_interview_results(
        interview_id=interview.interview_id,
        phase="emergent_themes",
    )
    print(themes.xml_output)

# Cross-case analysis
cross = client.analysis.run(
    study_id=study.study_id,
    model_tier="premium",
    cross_case_analysis=True,
)
print(cross.cross_case_xml)
```

### `client.credits`

| Method | Description |
|--------|-------------|
| `get_balance()` | Get current credit balance and reservations |
| `estimate_simulation(survey_id=, ...)` | Estimate credits for simulated interviews |
| `estimate_analysis(survey_id=, ...)` | Estimate credits for thematic analysis |
| `estimate_survey(survey_id=, ...)` | Estimate credits for full survey + analysis |

```python
balance = client.credits.get_balance()
print(f"Available: {balance.net_available} credits")

estimate = client.credits.estimate_simulation(
    survey_id=study.study_id,
    model_tier="premium",
    num_participants=10,
    include_analysis=True,
)
print(f"Estimated cost: {estimate.estimated_credits} credits")
print(f"  Per interview: {estimate.credits_per_interview}")
print(f"  Analysis: {estimate.credits_for_analysis}")
```

### Model tiers

| Tier | Description |
|------|-------------|
| `open_weights` | Cost-effective open-weights model (default) |
| `premium` | Balanced performance with Claude Haiku |
| `frontier` | Best quality with Claude Sonnet |

```python
# Check current tier
info = client.studies.get_model_tier(study.study_id)
print(f"Current: {info.model_tier} ({info.model_id})")

# Upgrade
client.studies.set_model_tier(study.study_id, model_tier="frontier")
```

## Error handling

The SDK raises specific exceptions for different error types:

```python
from deutero import (
    Deutero,
    AuthenticationError,
    NotFoundError,
    InsufficientCreditsError,
    ValidationError,
    RateLimitError,
    APIError,
)

client = Deutero(api_key="your-key")

try:
    study = client.studies.get_participation("nonexistent-id")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Study not found")
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
│   ├── AuthenticationError    (401, 403)
│   ├── NotFoundError          (404)
│   ├── ValidationError        (400, 422)
│   ├── InsufficientCreditsError (402)
│   ├── RateLimitError         (429)
│   ├── BadGatewayError        (502)
│   └── InternalServerError    (5xx)
├── ConnectionError
└── TimeoutError
```

## Configuration

### Custom base URL

```python
client = Deutero(
    api_key="your-key",
    base_url="https://custom.deutero.ai",
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

Bring your own `httpx.Client` for proxies, retries, or other transport customization:

```python
import httpx

http_client = httpx.Client(
    proxies="http://proxy.example.com:8080",
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

## Complete workflow example

```python
"""End-to-end: generate a study, simulate interviews, and analyze results."""

from deutero import Deutero

client = Deutero()

# Step 1: Create the study
study = client.studies.generate(
    study_type="customer_development",
    problem_hypothesis="Small business owners struggle to track expenses across multiple accounts",
    customer_segment="Small business owners with 1-10 employees",
    solution_concept="An AI-powered expense aggregation tool",
    model_tier="premium",
)
print(f"✓ Study created: {study.study_name}")

# Step 2: Generate questions
questions = client.questions.generate(
    study_id=study.study_id,
    number_of_questions=8,
)
print(f"✓ Generated {len(questions.question_list)} questions")

# Step 3: Check cost
estimate = client.credits.estimate_simulation(
    survey_id=study.study_id,
    model_tier="premium",
    num_participants=5,
    include_analysis=True,
)
print(f"✓ Estimated cost: {estimate.estimated_credits} credits")

# Step 4: Generate personas and run simulations
personas = client.personas.generate(
    study_id=study.study_id,
    number_of_personas=5,
)

for persona in personas.personas:
    sim = client.interviews.simulate(
        study_id=study.study_id,
        persona_id=persona.persona_id,
    )
    print(f"  ✓ Simulated: {sim.transcript_url}")

# Step 5: Run analysis
result = client.analysis.run(
    study_id=study.study_id,
    model_tier="premium",
)
print(f"✓ Analysis queued for {result.interviews_queued} interviews")

# Step 6: Wait and retrieve results
import time

while True:
    status = client.analysis.get_status(study_id=study.study_id)
    completed = sum(1 for i in status.interviews if i.status == "completed")
    print(f"  Progress: {completed}/{status.total_interviews} completed")
    if completed == status.total_interviews:
        break
    time.sleep(30)

# Step 7: Cross-case analysis
cross_case = client.analysis.run(
    study_id=study.study_id,
    model_tier="premium",
    cross_case_analysis=True,
)
print(f"✓ Cross-case analysis complete")

# Step 8: Generate agent requirements
requirements = client.studies.get_agent_requirements(study.study_id)
with open(requirements.filename, "w") as f:
    f.write(requirements.markdown)
print(f"✓ Saved requirements to {requirements.filename}")
```

## Development

```bash
git clone https://github.com/deutero-ai/deutero-python.git
cd deutero-python
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
