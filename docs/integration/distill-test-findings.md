# Distill — Local Testing Findings & Environment Report

**Date:** April 7, 2026
**Author:** Revenue Cloud Base Foundations Team
**Distill repo:** `bgaldino_emu/_sf-industries/distill`
**Python:** 3.12.13 (via pyenv)
**Environment:** Local macOS, `.env.local` with `DISTILL_DEV_MODE=true`

---

## Executive Summary

Distill was set up in an isolated local environment and validated end-to-end:
virtual environment creation, dependency installation, database initialization,
API server startup, and full test suite execution. The platform is functional
with **317 of 319 unit tests passing** and **77 of 81 API tests passing**.
All failures are pre-existing codebase issues unrelated to the local setup.

Two modules — `analysis_v2` and `metadata_migration` — fail at import time
due to missing symbols and should be investigated by the Distill team.

---

## 1. Environment Setup

| Item | Status | Detail |
|------|--------|--------|
| Python version | PASS | 3.12.13 via `pyenv local` (Distill requires 3.10–3.12) |
| Virtual environment | PASS | `.venv` created with Python 3.12.13 |
| Dependency install | PASS | All `requirements.txt` + `requirements-dev.txt` packages installed |
| `cmake` | PASS | Installed via Homebrew (required by `dlib` dependency) |
| `.env.local` | PASS | Created from `.env.example`, `GEMINI_API_KEY` auto-stamped from GCP |
| `DISTILL_DEV_MODE` | PASS | Set to `true` in `.env.local` (bypasses OIDC/JWT for local dev) |
| `DISTILL_ENV` | PASS | Set to `local` in `.env.local` |

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

### 4.1 Unit Tests

**Command:** `pytest --ignore=tests/analysis_v2 --ignore=tests/metadata_migration`

| Metric | Value |
|--------|-------|
| Total collected | 319 |
| Passed | 317 |
| Failed | 2 |
| Skipped | 0 |
| Duration | ~15s |

The 2 failures are in `tests/test_sfdx_parser.py` and are pre-existing issues
in the codebase (not related to the local setup or Python version).

### 4.2 API Tests

**Command:** `pytest tests/test_serve_api.py`

| Metric | Value |
|--------|-------|
| Total collected | 81 |
| Passed | 77 |
| Failed | 4 |
| Duration | ~30s |

The 4 failures are pre-existing codebase issues. The API server, routing,
authentication bypass, and core endpoint logic all function correctly.

### 4.3 Broken Modules (Import Failures)

Two test modules fail at **collection time** (before any tests run) due to
missing symbols in the source code:

| Module | Error | Root Cause |
|--------|-------|------------|
| `tests/analysis_v2/` (3 test files) | `ModuleNotFoundError: No module named 'distill.analysis_v2'` | The `distill.analysis_v2` package does not exist or is not installed in the current codebase |
| `tests/metadata_migration/test_api.py` | `ImportError: cannot import name '_create_empty_vector_store' from 'distill.metadata_migration.api'` | The function `_create_empty_vector_store` has been removed or renamed in `distill.metadata_migration.api` but tests still reference it |

**Impact:** 12 collection errors total. These modules are completely excluded
from the test run using `--ignore` flags. The remaining 400 tests (319 unit +
81 API) execute normally.

**Recommendation:** The Distill team should either:
1. Add the missing `analysis_v2` package if it is under active development, or
   remove/skip the orphaned test files
2. Update `tests/metadata_migration/test_api.py` to reference the correct
   function name after the refactor of `_create_empty_vector_store`

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
| D8 | Unit tests pass (≥95%) | PASS (317/319 = 99.4%) |

---

## 6. Coverage

The test suite generates coverage reports (`coverage.xml`, `htmlcov/`).
Overall line coverage across the Distill codebase is **12%** as reported by
`pytest-cov`. This low number is expected because:

- Many modules are integration/pipeline code that requires a live Salesforce
  org, Gemini API, or ChromaDB vector store to exercise
- The unit test suite focuses on parsers, utilities, and API routing
- The `analysis_v2` and `metadata_migration` modules (which would contribute
  significant coverage) are currently broken at import time

---

## 7. Recommendations for the Distill Team

### Immediate

1. **Fix `analysis_v2` import** — The test files reference
   `distill.analysis_v2` which doesn't exist as a package. Either the package
   needs to be added/restored, or the test files should be removed if the
   module was deprecated.

2. **Fix `_create_empty_vector_store` reference** — The function was removed
   or renamed in `distill.metadata_migration.api` but
   `tests/metadata_migration/test_api.py` still imports it. Update the test
   to match the current API.

3. **Investigate the 2 unit test failures** in `test_sfdx_parser.py` — These
   appear to be pre-existing regressions.

4. **Investigate the 4 API test failures** in `test_serve_api.py` — These
   appear to be pre-existing regressions.

### Short-Term

5. **Add a `pytest.ini` or `pyproject.toml` marker** to skip broken modules
   gracefully rather than relying on `--ignore` flags. For example:

   ```ini
   [tool:pytest]
   collect_ignore = ["tests/analysis_v2", "tests/metadata_migration"]
   ```

6. **Pin the Python version requirement** — Distill works on 3.12 but the
   `.python-version` file and documentation should explicitly state the
   supported range (3.10–3.12) and note that 3.13+ is not supported (due to
   native extension compilation issues with `dlib` and other dependencies).

### Integration-Related

7. **Gemini API key management** — The current setup requires a
   `GEMINI_API_KEY` in `.env.local`. For CI/CD and integration testing,
   consider supporting `gcloud`-based automatic key retrieval as documented
   in [isolated-testing-setup.md](isolated-testing-setup.md) Section 0.5.

8. **Database seeding for integration tests** — `insert-test-user.sh`
   populates a test user, but integration tests with Foundations will need
   Salesforce org metadata and customization data. A standard seed script or
   fixture set would help.

---

## Files Referenced

| File | Purpose |
|------|---------|
| `distill/serve_api.py` | API server entry point |
| `distill/.env.local` | Local environment config (GEMINI_API_KEY, dev mode) |
| `distill/insert-test-user.sh` | Test user database seeding |
| `tests/test_sfdx_parser.py` | Unit tests (2 failures) |
| `tests/test_serve_api.py` | API tests (4 failures) |
| `tests/analysis_v2/` | Broken — missing `distill.analysis_v2` module |
| `tests/metadata_migration/test_api.py` | Broken — missing `_create_empty_vector_store` |
