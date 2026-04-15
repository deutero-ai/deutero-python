# Changelog

All notable changes to the Deutero Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
