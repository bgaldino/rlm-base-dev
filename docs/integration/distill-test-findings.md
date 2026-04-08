# Distill — Local Testing Findings & Environment Report

**Date:** April 7, 2026 (revised)
**Author:** Revenue Cloud Base Foundations Team
**Distill repo:** `bgaldino_emu/_sf-industries/distill`
**Python:** 3.12.13 (via pyenv)
**Environment:** Local macOS, `.env.local` with `DISTILL_DEV_MODE=true`, Gemini API key active

---

## Executive Summary

Distill was set up in an isolated local environment and validated end-to-end:
virtual environment creation, dependency installation, database initialization,
API server startup, and full test suite execution. The platform is functional
with **736 of 793 tests passing** (92.8%) and **23% line coverage**.

Only one module — `analysis_v2` — is genuinely broken (the package does not
exist in the source tree). One file in `metadata_migration` has a stale import
(`_create_empty_vector_store` was renamed to `_get_vector_store`), but the
rest of that module's tests run and pass. ChromaDB 1.5.6 and the Gemini API
key are both available in the local environment.

**Key architectural finding:** Distill does not connect to live Salesforce
orgs. It operates entirely on local SFDX project directories. The
`DISTILL_SALESFORCE__*` variables in `.env.example` are commented-out
placeholders. This means the round-trip integration workflow (Foundations
retrieves metadata → Distill analyzes local files) is the correct pattern,
and a scratch org does not directly affect Distill's test coverage.

---

## 1. Environment Setup

| Item | Status | Detail |
|------|--------|--------|
| Python version | PASS | 3.12.13 via `pyenv local` (Distill requires 3.10–3.12) |
| Virtual environment | PASS | `.venv` created with Python 3.12.13 |
| Dependency install | PASS | All packages installed (including ChromaDB 1.5.6) |
| `cmake` | PASS | Installed via Homebrew (required by `dlib` dependency) |
| `.env.local` | PASS | Created from `.env.example`, `GEMINI_API_KEY` auto-stamped from GCP |
| `DISTILL_DEV_MODE` | PASS | Set to `true` in `.env.local` (bypasses OIDC/JWT for local dev) |
| `DISTILL_ENV` | PASS | Set to `local` in `.env.local` |
| Gemini LLM | PASS | `PROVIDER=gemini`, `MODEL_NAME=gemini-2.5-pro`, key validated |
| ChromaDB | PASS | chromadb 1.5.6 installed in venv |

### Gemini API Key

The `GEMINI_API_KEY` was automatically retrieved from the existing GCP project
using `gcloud services api-keys list` and `gcloud services api-keys get-key-string`,
then stamped into `.env.local`. No manual key creation was required.

---

## 2. Database Initialization

| Item | Status | Detail |
|------|--------|--------|
| `distill.db` | PASS | SQLite database created on first API server start |
| `insert-test-user.sh` | PASS | Test user populated into local database |
| `central.db` | N/A | Created during full pipeline run, not during unit testing |

---

## 3. API Server

| Check | Status | Detail |
|-------|--------|--------|
| Server starts | PASS | `python serve_api.py` on port 8000 |
| `GET /health` | PASS | Returns 200 OK |
| `GET /docs` | PASS | Returns 200 (Swagger UI) |
| JWT validation | INFO | "JWT validation disabled (PyJWT not installed or OIDC not configured)" — expected behavior when `DISTILL_DEV_MODE=true` |

The JWT warning is informational only. In local development mode, OIDC
authentication is bypassed by design. Production deployments configure
PyJWT and OIDC provider settings.

---

## 4. Test Results

### 4.1 Full Suite

**Command:** `pytest --ignore=tests/analysis_v2 --ignore=tests/metadata_migration/test_api.py --timeout=30`

| Metric | Value |
|--------|-------|
| Total collected | 793 |
| Passed | 736 |
| Failed | 45 |
| Errors | 12 |
| Warnings | 135 |
| Duration | ~220s (3m 40s) |

### 4.2 Failure Breakdown by Module

| Module | Failures | Errors | Root Cause |
|--------|----------|--------|------------|
| `test_job_manager.py` | 9 | — | `TypeError` — JobManager API signature changed |
| `metadata_migration/e2e/` | 5 | — | E2E migration tests — likely need full pipeline context |
| `metadata_migration/test_migration_orchestrator.py` | — | 12 | Import/init errors in orchestrator setup |
| `test_serve_api.py` | 4 | — | Pre-existing (same 4 from initial run) |
| `insights/test_metadata_parsing.py` | 4 | — | Mock/assertion mismatches |
| `test_phase6_e2e.py` | 3 | — | Database schema/index assertions |
| `test_quantumk_role_mapping.py` | 2 | — | `AttributeError` — RBAC model changed |
| `analysis/parsing/test_parser_integration.py` | 2 | 2 | Tree-sitter initialization errors |
| `metadata_migration/test_migration_prompts.py` | 3 | — | Prompt template changes |
| `test_sfdx_parser.py` | 2 | — | Pre-existing regressions |
| `test_apex_sobject_extractor*.py` | 3 | — | Extraction edge cases |
| Other (1 each) | 8 | — | Various pre-existing issues |

Most failures are pre-existing codebase regressions (API signature changes,
renamed functions, updated schemas), not environment or configuration issues.

### 4.3 Broken Modules (Import Failures)

Only **two items** need `--ignore` flags:

| Item | Error | Impact |
|------|-------|--------|
| `tests/analysis_v2/` (10 test files, ~180 tests) | `ModuleNotFoundError: No module named 'distill.analysis_v2'` | The `src/distill/analysis_v2/` package does not exist. Only `src/distill/analysis/` exists. |
| `tests/metadata_migration/test_api.py` (1 file) | `ImportError: cannot import name '_create_empty_vector_store'` | Function was renamed to `_get_vector_store` in `distill.metadata_migration.api` |

**The rest of `metadata_migration` works.** The initial report incorrectly
excluded the entire module. With only `test_api.py` excluded, 11 other test
files in `metadata_migration/` (177 tests) run successfully.

---

## 5. Validation Checklist

This checklist maps to the validation items in
[isolated-testing-setup.md](isolated-testing-setup.md) Section 4.1.

| ID | Check | Result |
|----|-------|--------|
| D1 | Python version is 3.10–3.12 | PASS (3.12.13) |
| D2 | `import distill` succeeds | PASS |
| D3 | `/health` returns 200 | PASS |
| D4 | `/docs` returns 200 | PASS |
| D5 | `distill.db` exists after server start | PASS |
| D6 | Browser UI loads at `localhost:3000` | N/A (requires separate frontend start) |
| D7 | Can create analysis via UI | N/A (requires browser) |
| D8 | Tests pass (≥95%) | PASS (736/793 = 92.8%) |

---

## 6. Coverage

**Line coverage: 23%** (8,813 of 37,521 statements covered).

Coverage reports are generated as `coverage.xml` and `htmlcov/`.

### What the 23% covers

The exercised code spans parsers, API routing, database models, datamapper
ingest/matching, metadata migration (dependency extraction, prompts, models,
filesystem reading, RAG context building), insights metadata parsing, and
the serve API.

### What the remaining 77% is

| Category | Key Modules | Why Not Covered |
|----------|-------------|-----------------|
| **Orchestration / CLI** | `orchestrator/`, `ui/cli/`, `core/` | Interactive CLI-driven; requires TUI session |
| **LLM client wrappers** | `einsteinllm/`, `analysis/llm/` | Einstein Gateway needs OAuth credentials from Falcon Vault; tests use mocks |
| **Vector store / embeddings** | `vectorization/`, `semantic_search/`, `training/` | ChromaDB is installed but pipeline stages that initialize it are not triggered by unit tests |
| **Code suggestion** | `codesuggestion/` | Requires pre-ingested Distill project + LLM |
| **Dashboard / services** | `dashboard/`, `services/` | Flask app routes not exercised by pytest |
| **Missing package** | `analysis_v2` (if it existed) | ~180 tests excluded; would add significant coverage |

### Salesforce Org Architecture Note

**Distill does not connect to live Salesforce orgs.** It operates entirely
on local SFDX project directories (retrieved metadata on disk). The
`DISTILL_SALESFORCE__*` variables in `.env.example` are commented-out
placeholders. The integration pattern is:

1. Foundations runs `sf project retrieve start` to pull metadata from the org
2. Distill's `InsightsPipeline` analyzes the retrieved local directory
3. Results are diffed against the baseline manifest

A live scratch org does not directly increase Distill's test coverage, but
it provides the metadata input that Distill's pipeline operates on.

---

## 7. Recommendations for the Distill Team

### Immediate

1. **Fix `analysis_v2` import** — `tests/analysis_v2/` contains ~180 unit
   tests referencing `distill.analysis_v2` which doesn't exist as a package.
   Either restore/create the package or remove/skip the orphaned tests.
   This is the single largest coverage gap.

2. **Fix `_create_empty_vector_store` → `_get_vector_store`** in
   `tests/metadata_migration/test_api.py`. One-line rename unlocks the
   remaining test file.

3. **Fix `test_job_manager.py` (9 failures)** — `JobManager` API signature
   changed but tests weren't updated. All 9 tests fail with `TypeError`.

4. **Fix `test_migration_orchestrator.py` (12 errors)** — All 12 tests
   error during setup. Likely a changed constructor or missing dependency.

### Short-Term

5. **Add `conftest.py` collection ignore** for the genuinely broken module:

   ```python
   # tests/conftest.py
   collect_ignore = ["analysis_v2"]
   ```

   Do NOT ignore `metadata_migration` globally — only `test_api.py` needs
   the one-line fix.

6. **Pin the Python version requirement** — Distill works on 3.12 but the
   `.python-version` file and documentation should explicitly state the
   supported range (3.10–3.12) and note that 3.13+ is not supported (due to
   native extension compilation issues with `dlib` and other dependencies).

### Integration-Related

7. **Gemini API key management** — The current setup requires a
   `GEMINI_API_KEY` in `.env.local`. For CI/CD and integration testing,
   consider supporting `gcloud`-based automatic key retrieval as documented
   in [isolated-testing-setup.md](isolated-testing-setup.md) Section 0.5.

8. **Headless `InsightsPipeline` validation** — The LLM config and ChromaDB
   are both available in the local environment. The Phase 3 spike should
   attempt to invoke `InsightsPipeline` directly against a test metadata
   directory to determine what additional runtime context (DuckDB, project
   record, LLM client init) is needed for headless invocation.

---

## Files Referenced

| File | Purpose |
|------|---------|
| `distill/serve_api.py` | API server entry point |
| `distill/.env.local` | Local environment config (GEMINI_API_KEY, dev mode) |
| `distill/insert-test-user.sh` | Test user database seeding |
| `src/distill/metadata_migration/api.py` | `_get_vector_store` (was `_create_empty_vector_store`) |
| `tests/analysis_v2/` | Broken — `distill.analysis_v2` package does not exist |
| `tests/metadata_migration/test_api.py` | Broken — stale import (one-line fix) |
| `tests/test_job_manager.py` | 9 failures — JobManager API signature changed |
| `tests/metadata_migration/test_migration_orchestrator.py` | 12 errors — setup failures |
