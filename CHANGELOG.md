# Changelog

All notable changes to the Deutero Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-26

The SDK now targets the Deutero Study Management API
(`https://dashboard.deutero.ai/study-api`), and every endpoint in its OpenAPI spec is covered.
This is a breaking release: the 0.1.x endpoints (`/api/v1/surveys/...`, thematic analysis,
credit estimates) are not part of that API and have been removed.

### Added

- **Projects**: list, create, get, update.
- **Studies**: create, list per project, get, update, participation stats.
- **Welcome & consent**: get/set the welcome message; list, upsert and delete translations.
- **Screening** and **Characteristics**: settings, plus create/update/delete/reorder questions.
- **Questions**: list, create, update, delete, reorder, validate (ethics, language, redundancy).
- **Interview flow** (`client.graph`): get, set, patch, check, signals, import from questions,
  activate/deactivate, describe node types; typed `FlowDocument`/`FlowNode`/`FlowEdge`/`PatchOp` models.
- **Recruitment**: participation links, short-URL slug, quota and redirect.
- **Embed**: publishable keys and install snippets.
- **Personas & simulations**: persona CRUD and AI generation; start, list, poll and delete simulation runs.
- **Interviews**: list with filters, look up by external participant id, detail, transcript,
  data fetches and signals.
- **Transcripts**: bulk export and string/semantic/hybrid search.
- **Analysis**: analyzable questions, scale/options tallies, k-means clustering, optimal cluster count.
- **Webhooks**: event types, endpoint CRUD, secret rotation, delivery log.
- `client.health()`.
- **Webhook receiving** (`deutero.webhooks`): `unwrap`, `verify`, `parse_event` and `sign` for
  Standard Webhooks-signed deliveries, covering both organization events and interview-flow
  signals. Typed models for all seven organization event types, and `WebhookVerificationError`.
- `PermissionDeniedError` (403, a subclass of `AuthenticationError`) and `ConflictError` (409).
- `ModelTier.STANDARD`; new `NodeType`, `SearchMode` and `AnalysisCategory` enums.
- **AI drafting**: `studies.draft` (from a research brief), `studies.draft_from_site` (from a
  landing page), `questions.generate` and `welcome.generate`.
- **Publication**: `studies.get_publication`, `studies.validate`, `studies.publish` (with
  acknowledgement of methodological issues or a credit shortfall) and `studies.pause`;
  `status` on studies and study summaries.
- **Test runs**: `test_runs` / `include_test_runs` filters on interview lists, lookups,
  transcripts and search; `test_run` on interview, transcript and search-hit models;
  `test_interviews` in study stats.

### Changed

- The default base URL is now `https://dashboard.deutero.ai/study-api`.
- `ModelTier.FRONTIER` is removed; the API treats `frontier` as a deprecated alias for `premium`.
- FastAPI validation errors (a list in `detail`) are now summarised readably in the exception message.

### Fixed

- The `X-API-Key` header is now sent when you pass your own `http_client`.
- A custom `http_client` without a `base_url` now uses the SDK's base URL.

### Removed

- `studies.generate`, `get_participation`, `get_agent_requirements`, `get/set_model_tier`,
  `questions.generate`/`get`, `personas.generate(number_of_personas=)`, `interviews.simulate`,
  the thematic `analysis.*` methods, and `credits.estimate_*`, together with their models.

## [0.1.0] - 2025-04-14

### Added

- Initial release of the Deutero Python SDK.
- Synchronous client (`Deutero`) and asynchronous client (`AsyncDeutero`).
- **Studies**: Generate research studies (UX, sociology, customer development, polling), get participation stats, manage model tiers, get agent requirements.
- **Questions**: Generate interview questions, get/update individual question properties.
- **Personas**: Generate interviewee personas for a study.
- **Interviews**: Simulate interviews with generated personas.
- **Analysis**: Run thematic analysis (phases 1–4), cross-case analysis (phase 5), get status and results.
- **Credits**: Check balance, estimate costs for simulations, analysis, and full surveys.
- Typed models for all request/response payloads using Pydantic v2.
- Comprehensive exception hierarchy with specific classes for common HTTP errors.
- Full type annotations and `py.typed` marker for mypy/pyright.
- Context manager support (`with Deutero(...) as client:`).
