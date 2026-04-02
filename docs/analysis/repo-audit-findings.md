# Repository Cleanup Review And Tracker

Branch reviewed: `chore/repo-audit-cleanup`  
Baseline: `main`  
Last validated: 2026-04-02

This single document replaces the old split between feature-flag cleanup planning and repo-audit findings. It tracks what was changed on this branch, what still needs action, and what remains as backlog.

---

## Branch Validation Summary

The branch changes compared to `main` are largely valid and coherent:

- moved Product2 UX-binding object metadata from `force-app` to `templates`
- bulkified SOQL-in-loop logic in `RLM_QuoteModelUtility`
- redacted token exposure in `tasks/rlm_sfdmu.py` logs
- cleaned up dead constraints dataset anchors/tasks and updated related docs
- fixed org config filename mismatch (`dev_datacloud` -> `dev-datacloud`)
- removed stale sample/legacy tax DX JSON and helper script files

No regressions were found in those changed files during static review. Remaining work is mostly unfinished security/reliability follow-up from the original audit.

---

## Completed On This Branch

### Security / Reliability

- `tasks/rlm_sfdmu.py`
  - added `_redact_token(...)`
  - redacted command/stdout/stderr token output
  - redacted `accessToken` in logged `export.json`

### Deploy Correctness

- Product2 object binding moved to template source-of-truth:
  - added `templates/objects/base/Product2/Product2.object-meta.xml`
  - added ignore rule in `.forceignore` for `force-app/main/default/objects/Product2/Product2.object-meta.xml`

- `RLM_QuoteModelUtility.cls`
  - removed SOQL-in-loop pattern
  - replaced with preloaded maps by quote line id

### Feature-Flag / Config Hygiene

- declared `project.custom.psg_debug` in `cumulusci.yml`
- removed deprecated constraints dataset anchors/tasks
- tightened constraints-data `when:` conditions to require `constraints=true`
- fixed scratch org config filename reference:
  - `orgs/dev_datacloud.json` -> `orgs/dev-datacloud.json`
- clarified feature-flag comments and TSO terminology in docs/config

---

## Remaining Items (Actionable)

## P0 — Security

### 1) SFDMU CLI identity still falls back to access token

In `tasks/rlm_sfdmu.py`, CLI identity for non-scratch paths still uses:

- `LoadSFDMUData`: `targetusername = ... or self.org_config.access_token`
- `ExtractSFDMUData`: `sourceusername = ... or self.org_config.access_token`

Risk: token still appears in process args/shell history if this fallback path is used.

Action:

- require username for CLI calls (same pattern used by `_get_org_for_cli()` in idempotency task)
- raise explicit error when `org_config.username` is unavailable

### 2) Setup Robot suite still exposes auth URL/session in logs

`robot/rlm-base/resources/SetupToggles.robot` still runs:

- `sf org open --url-only`
- `Go To ${target}`

without temporary `Set Log Level NONE` wrapping.

Action:

- wrap URL fetch and navigation with `Set Log Level NONE` + restore prior level

---

## P2 — Reliability / Usability

### 3) Robot wrappers still allow unreliable alias fallback

These wrappers still fallback to `org_config.name`/alias patterns if username is missing:

- `tasks/rlm_robot_e2e.py`
- `tasks/rlm_reorder_app_launcher.py`
- `tasks/rlm_analytics.py`
- `tasks/rlm_enable_document_builder_toggle.py`
- `tasks/rlm_enable_constraints_settings.py`
- `tasks/rlm_configure_revenue_settings.py`

Action:

- require `org_config.username` for `sf org open` usage; raise `TaskOptionsError` otherwise

### 4) `access_token` remains exposed in task options

Still present in:

- `tasks/rlm_context_service.py`
- `tasks/rlm_extend_stdctx.py`
- `tasks/rlm_modify_context.py`
- `tasks/rlm_sync_pricing_data.py`
- `tasks/rlm_refresh_decision_table.py`

Action:

- remove `access_token` from `task_options`
- always use `self.org_config.access_token` for REST auth

---

## P3 — Quality / Documentation

### 5) Duplicate class access in Admin profile

`force-app/main/default/profiles/Admin.profile-meta.xml` has duplicate `RLM_OrderItemContractingUtility`.

Action: remove duplicate entry.

### 6) Missing `composed: true` on submit event helper

`robot/rlm-base/resources/E2ECommon.robot` dispatches:

- `new Event('submit', {bubbles: true, cancelable: true})`

Action: add `composed: true` for shadow DOM boundary consistency.

### 7) Import guards still missing in several Python tasks

These still import CCI modules without fallback guards:

- `tasks/rlm_context_service.py`
- `tasks/rlm_extend_stdctx.py`
- `tasks/rlm_modify_context.py`
- `tasks/rlm_sync_pricing_data.py`
- `tasks/rlm_refresh_decision_table.py`

Action: add standard `try/except ImportError` fallback symbols.

---

## Deferred Backlog

## SFDMU v5 Bug 3 Data-Plan Migrations

Large backlog remains where relationship-traversal `externalId` uses `Upsert` and is not idempotent under SFDMU v5.

Critical rule for this backlog:

- do not switch to `Insert + deleteOldData: true` without explicit approval and object-level rationale (destructive behavior)

Impacted plan families include `qb-*`, `q3-*`, `mfg-*`, and `procedure-plans` as previously documented.

---

## Historical Notes

This document supersedes prior split planning/finding docs:

- feature-flag cleanup planning content
- repo-audit findings status content

All future updates should be made here so there is a single source of truth.
