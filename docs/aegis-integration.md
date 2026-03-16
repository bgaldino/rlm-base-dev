# Revenue Cloud Foundations × Aegis: Integration Plan

> **Status:** Planning
> **Last Updated:** 2026-03-16
> **Scope:** Automated post-provision validation of Foundations-provisioned orgs using the Aegis BDD test framework
>
> **Part of:** [Revenue Cloud Engineering Platform](revenue-cloud-platform.md)
>
> **Related documents:**
> - [revenue-cloud-platform.md](revenue-cloud-platform.md) — platform overview
> - [distill-integration.md](distill-integration.md) — Distill integration (drift detection)
> - [datasets-reorganization.md](datasets-reorganization.md) — prerequisite for shape-aware suite selection

---

## Table of Contents

1. [Project Overviews](#1-project-overviews)
2. [The Integration Opportunity](#2-the-integration-opportunity)
3. [The Integration Workflow](#3-the-integration-workflow)
4. [Credential Handoff Design](#4-credential-handoff-design)
5. [CCI Task Design: `run_aegis_suite`](#5-cci-task-design-run_aegis_suite)
6. [Feature Flag → Aegis Team Mapping](#6-feature-flag--aegis-team-mapping)
7. [CumulusCI Configuration](#7-cumulusci-configuration)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Open Questions & Decisions](#9-open-questions--decisions)

---

## 1. Project Overviews

### 1.1 Revenue Cloud Foundations

CumulusCI automation framework that provisions fully-configured Salesforce Revenue Cloud (RLM) orgs. After `cci flow run prepare_rlm_org`, the org has the correct data shapes, metadata, and configuration loaded — but no automated validation that everything actually works end-to-end.

### 1.2 Aegis (`industries/Automated-Remote-Org-Test`)

**Repository:** `git.soma.salesforce.com/industries/Automated-Remote-Org-Test`
**Technology:** Python · Behave 1.2.6 (BDD/Gherkin) · Selenium 4.35.0 · Playwright 1.56.0
**CI:** Jenkins (25 teams in parallel on Docker Selenium Grid, 2× daily cron)

Aegis is a Revenue Cloud BDD test automation framework. It validates end-to-end business flows against live Salesforce orgs using Gherkin scenarios written by each product team.

**Integration-relevant facts:**
- 26 team folders under `features/`, 25 registered in `team_config.json`
- `features/RevenueGoFoundation/` — the existing team that tests Foundations-provisioned orgs; contains **2 feature files**: `RevenueCloudInitialSetup.feature` (Playwright) and `DynamicRevenueOrchestrator.feature` (Playwright)
- Session injection supported natively: `Given login to Salesforce with sessionId and verify login successful` step exists across 26+ feature files including both RevenueGoFoundation files — **no Aegis code changes needed for CCI OAuth integration**
- Session utilities (`shared/utils/authentication/session_utils.py`) provide `init_selenium_session(context, session_id, instance_url)` — accepts OAuth tokens directly via frontdoor.jsp
- Org connection via env vars: `SF_URL`, `SF_USERNAME`, `SF_PASSWORD`, `SF_TOKEN`
- Team creds JSON format: `{ "ORG_KEY": { "SF_URL", "SF_USERNAME", "SF_PASSWORD", "SF_TOKEN" } }`
- Jenkins job supports `TEST_PATH` param to target a single team or feature file
- Auto-cleanup feature (`shared/steps/platform/graph_collection_steps.py`): graph collection test data is auto-deleted after each scenario (failed scenarios delete all records; passed scenarios delete only created records)
- **Known gap:** Aegis cannot create or provision orgs — it must be pointed at an existing one

**Aegis does NOT:**
- Create Salesforce orgs
- Load data or deploy metadata
- Know about CCI data shapes, feature flags, or SFDMU plans

---

## 2. The Integration Opportunity

**The gap today:** `prepare_rlm_org` provisions an org and loads reference data, then stops. There is no automated check that the org is functionally correct — that you can actually create a quote, place an order, or trigger a billing run. Failures are discovered manually by the engineer who provisioned the org.

**What the integration delivers:**

| Before | After |
|---|---|
| Engineer manually navigates the org to verify it works | `run_aegis_smoke` runs automatically at the end of `prepare_rlm_org` |
| Failures discovered after hand-off | Failures caught before the org is handed to users |
| No link between data shape and which tests to run | Feature flags drive which Aegis teams are invoked |
| Distill promotion requires manual regression | Post-promote regression triggered automatically by a Foundations CCI flow |

**The natural seam:** CCI already knows the org URL and credentials (it just provisioned it). Aegis already knows how to test that org — it just needs to be pointed at it. The integration is a credential handoff + invocation.

---

## 3. The Integration Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│                    CCI ↔ AEGIS INTEGRATION FLOW                         │
│                                                                          │
│  CumulusCI (Foundations)              Aegis                              │
│  ─────────────────────────            ─────────────────────────          │
│                                                                          │
│  cci flow run prepare_rlm_org                                            │
│    ├── deploy metadata                                                   │
│    ├── load SFDMU data plans                                             │
│    ├── configure org                                                     │
│    └── [activation tasks]                                               │
│              │                                                           │
│              ▼                                                           │
│  validate_aegis_environment          ← check: behave installed?         │
│              │                          Aegis repo present?             │
│              ▼                                                           │
│  export_aegis_credentials            ← writes SF_URL, SF_USERNAME,     │
│    (from CCI org context)               SF_PASSWORD, SF_TOKEN          │
│              │                                                           │
│              ▼                                                           │
│  run_aegis_suite                                                         │
│    ├── test_path=features/RevenueGoFoundation/      ← smoke: always    │
│    ├── tags=@smoke                                                       │
│    ├── + shape-aware teams (Phase 3)                                    │
│    │         │                                                           │
│    │         └──────────────────────► behave features/RevenueGoFoundation/
│    │                                    ├── RevenueCloudInitialSetup    │
│    │                                    └── DynamicRevenueOrchestrator  │
│    │                                            │                        │
│    │                                    pass/fail result                 │
│    │                                            │                        │
│    └──────────────────────────────────◄─────────┘                       │
│              │                                                           │
│       result: PASS → org handed off                                     │
│       result: FAIL → CCI logs failure + raises warning                  │
│                       (flow continues — non-blocking by default)        │
│                                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Two Invocation Modes

| Mode | When | Mechanism | Output |
|---|---|---|---|
| **Local** | Developer runs `prepare_rlm_org` | CCI task calls `behave` as subprocess | Pass/fail logged to CCI output |
| **Jenkins** | CI pipeline post-provision | CCI task POSTs to Jenkins `/buildWithParameters` | Cucumber JSON + JUnit XML in Jenkins |

Phase 1–2 implement local mode. Phase 3 adds Jenkins API trigger.

### 3.2 Non-Blocking by Default

Aegis failures should not abort the CCI flow — an org that fails smoke tests is still useful for debugging. The default behavior is:
- **PASS** → log success, continue flow
- **FAIL** → log warning with scenario details, continue flow
- **ERROR** (Aegis not installed / org unreachable) → log warning, skip gracefully

A `fail_on_aegis_failure` option (default `False`) lets callers opt into hard failure.

---

## 4. Credential Handoff Design

### 4.1 How CCI Knows the Org Credentials

CCI manages orgs via `keychain` — each named org has a stored access token, instance URL, and username. From a Python task, these are accessible via:

```python
self.org_config.instance_url   # SF_URL equivalent
self.org_config.username       # SF_USERNAME
# SF_PASSWORD and SF_TOKEN are not stored — CCI uses OAuth access tokens
```

**Authentication approach: OAuth session injection — confirmed working.** CCI uses OAuth access tokens (not username/password). Aegis's `session_utils.py` (`init_selenium_session`) accepts `session_id` + `instance_url` directly, authenticating the browser via Salesforce's `frontdoor.jsp` endpoint. Both `RevenueGoFoundation` feature files already use `Given login to Salesforce with sessionId and verify login successful` — **no Aegis code changes are required**.

The full credential flow:
1. CCI passes `self.org_config.access_token` → `SF_SESSION_ID` in `cci_aegis_creds.json`
2. CCI passes `self.org_config.instance_url` → `SF_URL` in `cci_aegis_creds.json`
3. Aegis loads the creds file, calls `login_manager.authenticate_salesforce()` with the session ID
4. `session_utils.init_selenium_session()` authenticates the browser via `{instance_url}/secur/frontdoor.jsp?sid={session_id}`

**Fallback options (only if session injection fails):**

| Option | Mechanism | Notes |
|---|---|---|
| **B — Password auth** | User provides `org_password` option to the CCI task | Requires knowing the org password; works for scratch orgs with known passwords |
| **C — Connected App** | CCI generates access token via Connected App + JWT flow | More robust for long-running suites; adds setup complexity |

### 4.2 Credentials File Format

CCI writes a temporary `cci_aegis_creds.json` in the Aegis repo tree (gitignored):

```json
{
  "CCI_PROVISIONED_ORG": {
    "SF_URL": "<instance_url from CCI>",
    "SF_USERNAME": "<username from CCI>",
    "SF_SESSION_ID": "<access_token from CCI>",
    "SF_TOKEN": ""
  }
}
```

The `RevenueGoFoundation` Background step references this file:

```gherkin
Background:
  Given the CCI_PROVISIONED_ORG credentials from "features/RevenueGoFoundation/cci_aegis_creds.json"
  Given login to Salesforce with sessionId and verify login successful
```

> **Note:** This requires a small Aegis-side change: a `cci_aegis_creds.json` file entry in `.gitignore` and either using the existing `UsageManagementCreds.json` pattern (parameterized feature file) or adding a new `CCI_PROVISIONED_ORG` key to the existing `RevenueGoFoundationCreds.json`. No Aegis code changes required — only a data file change.

### 4.3 Credential Cleanup

The CCI task deletes `cci_aegis_creds.json` after the suite completes (success or failure) to avoid credentials persisting on disk.

---

## 5. CCI Task Design: `run_aegis_suite`

### 5.1 Task Class (`tasks/rlm_aegis.py`)

```python
class ValidateAegisEnvironment(BaseSalesforceTask):
    """Validates that Aegis prerequisites are met before attempting a run."""
    task_options = {
        "aegis_repo_path": {"description": "Path to Aegis repo", "required": True},
    }
    # Checks: repo exists, behave installed in venv, requirements satisfied

class RunAegisSuite(BaseSalesforceTask):
    """Runs Aegis BDD suite against the current CCI org."""
    task_options = {
        "aegis_repo_path": {
            "description": "Local path to Automated-Remote-Org-Test repo",
            "required": True,
        },
        "test_path": {
            "description": "Behave test path (e.g. features/RevenueGoFoundation/)",
            "required": False,
            "default": "features/RevenueGoFoundation/",
        },
        "tags": {
            "description": "Behave tag filter (e.g. @smoke, @sanity_test)",
            "required": False,
            "default": "@smoke",
        },
        "scenario_name": {
            "description": "Optional: run a single scenario by name",
            "required": False,
            "default": None,
        },
        "fail_on_aegis_failure": {
            "description": "Raise TaskOptionsError if Aegis scenarios fail (default: False)",
            "required": False,
            "default": False,
        },
        "timeout_seconds": {
            "description": "Max seconds to wait for suite completion",
            "required": False,
            "default": 600,
        },
    }
```

### 5.2 Task Logic

```
1. Write cci_aegis_creds.json to aegis_repo_path/features/RevenueGoFoundation/
   - SF_URL = self.org_config.instance_url
   - SF_USERNAME = self.org_config.username
   - SF_SESSION_ID = self.org_config.access_token
   - SF_TOKEN = ""

2. Build behave command:
   behave <test_path>
     --no-capture
     --format json --outfile reports/cci_run/cucumber.json
     --format progress
     [--tags <tags>]
     [--name "<scenario_name>"]

3. Run behave subprocess from aegis_repo_path
   - stream stdout/stderr to CCI logger
   - capture return code

4. Parse reports/cci_run/cucumber.json for pass/fail summary
   - count passed / failed / skipped scenarios
   - collect failed scenario names + feature files

5. Delete cci_aegis_creds.json (always — in finally block)

6. Log result summary:
   - "Aegis: 12 passed, 0 failed (features/RevenueGoFoundation/)"
   - If failures: log each failed scenario name

7. If fail_on_aegis_failure=True and failures > 0:
   raise TaskOptionsError(f"Aegis suite failed: {failed_scenarios}")
```

### 5.3 Guard Logic

Before running, the task checks:
- Aegis repo path exists and is a git repo
- `behave` is executable (via venv or system path)
- `features/RevenueGoFoundation/` exists in repo
- `self.org_config.access_token` is non-empty
- Org is reachable (GET `/services/data` → 200)

Any guard failure logs a warning and skips the suite — it does not abort the CCI flow.

---

## 6. Feature Flag → Aegis Team Mapping

For Phase 3, the CCI task reads active feature flags from the project context and runs additional Aegis teams beyond the baseline `RevenueGoFoundation` smoke suite.

### 6.1 Proposed Mapping

| CCI Feature Flag (`project.custom.*`) | Aegis Team Folder(s) | Rationale |
|---|---|---|
| `qb: true` (always true for QB shape) | `RevenueGoFoundation/` | Core QB org validation — always run |
| `billing: true` | `BillingInvoicing/`, `BillingCreditMemo/`, `BillingPayments/` | Billing policies and treatments loaded by `qb-billing` plan |
| `rating: true` | `UsageManagement/` | PUR/PURP/PUG records loaded by `qb-rating` plan |
| `rates: true` | `UsageManagement/` | Rate cards loaded by `qb-rates` plan |
| `dro: true` | `RevenueGoFoundation/DynamicRevenueOrchestrator.feature` | DRO flows loaded by `qb-dro` plan |
| `tax: true` | *(no dedicated team yet — `RLMSuite/` candidate)* | Tax treatments loaded by `qb-tax` plan |
| `clm: true` | `SalesforceContracts/` | Contract lifecycle — CLM plan |

### 6.2 CCI Task Option: `shape_aware`

```yaml
run_aegis_suite:
  options:
    shape_aware: true   # reads active flags, runs mapped teams
    test_path: features/RevenueGoFoundation/  # always included as baseline
```

When `shape_aware: true`, the task:
1. Reads `project.custom` flags from `cumulusci.yml`
2. Builds an expanded `test_path` list from the mapping above
3. Runs each team sequentially (or passes a comma-separated list to Jenkins)

### 6.3 Open Design: Flag Mapping Location

The flag-to-team mapping could live in:
- **`cumulusci.yml`** — under a `aegis_team_mapping` custom block
- **`datasets/shapes.json`** — as a `aegis_teams` array per shape (connects to O9)
- **`tasks/rlm_aegis.py`** — hardcoded in the task (simplest, least flexible)

Recommendation: start hardcoded in the task (Phase 3), move to `shapes.json` in Phase 4 (this resolves O9 in distill-integration.md).

---

## 7. CumulusCI Configuration

### 7.1 Task Definitions

```yaml
tasks:
  validate_aegis_environment:
    group: Verification
    description: >
      Checks that Aegis prerequisites are met: repo present, behave installed,
      RevenueGoFoundation team folder exists. Skips gracefully if Aegis is not
      configured. Run before run_aegis_suite to surface setup issues early.
    class_path: tasks.rlm_aegis.ValidateAegisEnvironment
    options:
      aegis_repo_path: "~/Automated-Remote-Org-Test"

  run_aegis_smoke:
    group: Verification
    description: >
      Runs the Aegis RevenueGoFoundation smoke suite (@smoke tag) against the
      current CCI org. Validates Revenue Cloud Initial Setup and DRO flows.
      Non-blocking by default — failures log a warning but do not abort the flow.
    class_path: tasks.rlm_aegis.RunAegisSuite
    options:
      aegis_repo_path: "~/Automated-Remote-Org-Test"
      test_path: "features/RevenueGoFoundation/"
      tags: "@smoke"
      fail_on_aegis_failure: false

  run_aegis_full:
    group: Verification
    description: >
      Runs the full Aegis RevenueGoFoundation suite (all scenarios) against the
      current CCI org. Use for post-provision full validation or pre-release checks.
    class_path: tasks.rlm_aegis.RunAegisSuite
    options:
      aegis_repo_path: "~/Automated-Remote-Org-Test"
      test_path: "features/RevenueGoFoundation/"
      fail_on_aegis_failure: false

  run_aegis_shape_suite:
    group: Verification
    description: >
      Runs Aegis teams selected by active CCI feature flags (billing, rating,
      rates, dro, clm). Always includes RevenueGoFoundation baseline.
      Requires Phase 3 implementation.
    class_path: tasks.rlm_aegis.RunAegisSuite
    options:
      aegis_repo_path: "~/Automated-Remote-Org-Test"
      shape_aware: true
      fail_on_aegis_failure: false
```

### 7.2 Flow Integration

```yaml
flows:
  prepare_rlm_org:
    steps:
      # ... existing steps ...
      30:
        task: validate_aegis_environment
        when: "$project_config.project__custom__aegis"
        ui_options:
          name: Validate Aegis environment
      31:
        task: run_aegis_smoke
        when: "$project_config.project__custom__aegis"
        ui_options:
          name: Run Aegis smoke suite

  # Standalone verification flow
  verify_org_with_aegis:
    description: >
      Runs the full Aegis RevenueGoFoundation suite against the org.
      Useful for post-setup validation or regression before a release cut.
    steps:
      1:
        task: validate_aegis_environment
      2:
        task: run_aegis_full
```

### 7.3 Feature Flag

```yaml
project:
  custom:
    aegis: false   # Set true to enable Aegis validation in prepare_rlm_org
```

The `aegis` flag is `false` by default — engineers opt in by setting it to `true` in their local `cumulusci.yml` or passing `--aegis true` to the flow.

---

## 8. Implementation Roadmap

> **How this roadmap is structured:** Phases 0–2 deliver the core credential-handoff + local invocation path. Phase 3 adds Jenkins API integration and shape-aware team selection. Phase 4 closes the Distill post-promote loop. All phases are optional and non-blocking — each delivers standalone value.

---

### Phase 0: Aegis Environment Validation *(No Aegis changes required)*

> **Distill/Aegis requirement:** None — this phase is entirely on the Foundations side.
>
> Build the `validate_aegis_environment` task and confirm the credential handoff approach works with session injection against a real Aegis run.

| # | Task | Owner | Status |
|---|---|---|---|
| 0.1 | Write `tasks/rlm_aegis.py` — `ValidateAegisEnvironment` task class with guard logic | | 🔲 TODO |
| 0.2 | Add `validate_aegis_environment` task to `cumulusci.yml` | | 🔲 TODO |
| 0.3 | ~~Confirm session injection works~~ — **already confirmed.** Both `RevenueGoFoundation` feature files use `Given login to Salesforce with sessionId`; `session_utils.py` accepts `session_id` + `instance_url` directly. No Aegis code changes needed. | | ✅ Confirmed |
| 0.4 | Add `CCI_PROVISIONED_ORG` key to `RevenueGoFoundationCreds.json` (or a separate `cci_aegis_creds.json`) + add file to Aegis `.gitignore` — small Aegis PR | | 🔲 TODO |
| 0.5 | Verify guard logic: missing repo, missing behave, expired token — all produce warnings not errors | | 🔲 TODO |

---

### Phase 1: Local Post-Provision Smoke *(Available now — core value delivery)*

> **Requirement:** Aegis repo cloned locally, Behave installed in its venv, CCI org with active session.
>
> This phase delivers the core value: a smoke suite runs automatically at the end of `prepare_rlm_org` and the engineer sees pass/fail in CCI output without leaving the terminal.

| # | Task | Owner | Status |
|---|---|---|---|
| 1.1 | Write `RunAegisSuite` task class: credential write → behave subprocess → result parse → credential cleanup | | 🔲 TODO |
| 1.2 | Add `run_aegis_smoke` and `run_aegis_full` tasks to `cumulusci.yml` | | 🔲 TODO |
| 1.3 | Add `aegis` feature flag to `project.custom` in `cumulusci.yml` (default `false`) | | 🔲 TODO |
| 1.4 | Add `run_aegis_smoke` as step 30–31 in `prepare_rlm_org` flow (gated on `aegis` flag) | | 🔲 TODO |
| 1.5 | Implement JUnit XML / Cucumber JSON result parser — extract pass/fail counts and failed scenario names | | 🔲 TODO |
| 1.6 | Test full round-trip: `cci flow run prepare_rlm_org --org beta` → Aegis smoke → pass/fail in CCI log | | 🔲 TODO |
| 1.7 | Add `verify_org_with_aegis` standalone flow | | 🔲 TODO |

---

### Phase 2: Full RevenueGoFoundation Suite + Shape-Specific Scenarios *(Requires `dro: true` flag)*

> **Requirement:** Phase 1 complete + a Foundations org with DRO data loaded (`qb-dro` plan).
>
> Both `RevenueGoFoundation` feature files are now **Playwright-based** (migrated from Selenium as of commits `7643bfd` and `e5902da`). Phase 1 smoke may target just one; Phase 2 runs both explicitly and wires DRO invocation to the `dro` feature flag.
>
> `RevenueGoFoundation/` currently contains:
> - `RevenueCloudInitialSetup.feature` — Initial Setup validation (Playwright)
> - `DynamicRevenueOrchestrator.feature` — DRO setup, redirections, feature toggles (Playwright)

| # | Task | Owner | Status |
|---|---|---|---|
| 2.1 | Add `dro` flag handling to `RunAegisSuite`: when `dro: true`, explicitly include `DynamicRevenueOrchestrator.feature`; always include `RevenueCloudInitialSetup.feature` | | 🔲 TODO |
| 2.2 | Test both feature files against a `qb-dro`-loaded org — confirm all scenarios pass | | 🔲 TODO |
| 2.3 | Document which scenarios require activation steps from `prepare_rlm_org` to have run first (e.g. `activate_dro_records` before DRO scenarios) | | 🔲 TODO |
| 2.4 | Handle ordering: Aegis must run after all activation tasks (`activate_rating_records`, `activate_dro_records` etc.) — enforce in flow step order | | 🔲 TODO |

---

### Phase 3: Jenkins API Integration + Shape-Aware Selection *(CI/CD path)*

> **Requirement:** Jenkins API access + a Jenkins job configured with the Aegis pipeline.
>
> Two deliverables: (1) CCI can trigger the Aegis Jenkins job programmatically, so CI runs use the Jenkins infrastructure (Docker Selenium Grid, parallel execution, HTML reports) rather than a local behave subprocess. (2) Active CCI feature flags drive which Aegis team folders are invoked.
>
> **Jenkins trigger mechanism:** `POST https://<jenkins-host>/job/Automated-Remote-Org-Test/buildWithParameters` with params `TEST_PATH`, `SF_URL`, `SF_USERNAME`, `SF_TOKEN` + Jenkins API token auth.

| # | Task | Owner | Status |
|---|---|---|---|
| 3.1 | Confirm Jenkins API endpoint and auth method with Aegis team (API token? OAuth? Service account?) | | 🔲 TODO |
| 3.2 | Add `TriggerAegisPipeline` task class: HTTP POST to Jenkins `/buildWithParameters`, poll queue → build → result | | 🔲 TODO |
| 3.3 | Add `jenkins_url` and `jenkins_api_token` options + `AEGIS_JENKINS_URL` / `AEGIS_JENKINS_TOKEN` env var fallbacks | | 🔲 TODO |
| 3.4 | Implement polling: `GET /job/Automated-Remote-Org-Test/<build_num>/api/json` until `result != null`; respect `timeout_seconds` | | 🔲 TODO |
| 3.5 | Implement flag-to-team mapping in `RunAegisSuite` — read `project.custom` flags, build expanded `TEST_PATH` list | | 🔲 TODO |
| 3.6 | Add `run_aegis_shape_suite` task to `cumulusci.yml` | | 🔲 TODO |
| 3.7 | Test Jenkins trigger with a real Foundations org against the Aegis Jenkins instance | | 🔲 TODO |
| 3.8 | Evaluate moving flag-to-team mapping from task hardcode to `datasets/shapes.json` (see O4) | | 🔲 TODO |

---

### Phase 4: Post-Promote Regression Loop *(Closes the Distill feedback loop)*

> **Requirement:** Phase 1 (local smoke) or Phase 3 (Jenkins) + Distill Phase 4 (drift detection + promote workflow) from [distill-integration.md](distill-integration.md).
>
> When a Distill drift report results in a promotion (customization merged into `force-app/` or an `unpackaged/post_*` bundle), the affected org should be re-validated. This phase adds a `post_promote_regression` flow that: re-deploys the promoted changes to a clean org, re-provisions data, and runs the relevant Aegis teams as a regression gate.

| # | Task | Owner | Status |
|---|---|---|---|
| 4.1 | Define `post_promote_regression` flow: deploy promoted bundle → load data → run Aegis shape suite | | 🔲 TODO |
| 4.2 | Determine which Aegis teams are relevant for each promotion type (Apex → RevenueGoFoundation; billing Apex → BillingInvoicing etc.) | | 🔲 TODO |
| 4.3 | Add `fail_on_aegis_failure: true` option to post-promote flow — promoted changes must pass regression before merging | | 🔲 TODO |
| 4.4 | Coordinate with Distill team: should the drift report include a `suggested_aegis_teams` field based on feature domain classification? | | 🔲 TODO |
| 4.5 | Test full feedback loop: `capture_org_customizations` → drift report → promote → `post_promote_regression` → Aegis pass | | 🔲 TODO |

---

## 9. Open Questions & Decisions

### 9.1 Resolved Decisions

| # | Question | Status | Decision |
|---|---|---|---|
| R1 | Is the integration blocking or non-blocking? | ✅ Resolved | **Non-blocking by default.** `fail_on_aegis_failure` option (default `false`) — failures log a warning and flow continues. Post-promote regression is the exception — it will use `fail_on_aegis_failure: true`. |
| R2 | Which authentication flow: OAuth session injection or username/password? | ✅ Resolved | **Session injection confirmed.** CCI passes `access_token` + `instance_url`; Aegis uses `Given login to Salesforce with sessionId and verify login successful` via `session_utils.init_selenium_session()` (frontdoor.jsp). Used by both `RevenueGoFoundation` feature files and 24 other teams. No Aegis code changes needed. |
| R3 | Should Aegis be invoked locally (behave subprocess) or via Jenkins API? | ✅ Resolved | **Both — phased.** Phase 1 delivers local subprocess (developer workflow). Phase 3 adds Jenkins API trigger (CI workflow). Feature flag `aegis: true` opts in. |

### 9.2 Open Questions

| # | Question | Status | Notes |
|---|---|---|---|
| O1 | What Jenkins API auth mechanism should CCI use? | Needs confirmation | Options: API token, OAuth2, Service Account. Confirm with Aegis team. Token should be stored in CCI keychain or `AEGIS_JENKINS_TOKEN` env var — never in `cumulusci.yml`. |
| O2 | Should `prepare_rlm_org` run Aegis by default, or opt-in only? | Open | Default `false` is safe for now — Aegis requires local repo clone and adds ~5 min. Could graduate to `true` for CI environments once reliability is established. |
| O3 | How should Aegis scenario failures surface in CCI output? | Open | Options: (a) raw behave output in log, (b) parsed summary table, (c) link to Allure report. A parsed summary (scenario names + feature file paths) is most actionable. |
| O4 | Should the flag-to-team mapping live in `shapes.json` or be hardcoded in the task? | Open | Hardcode in task for Phase 3 (fastest path). Move to `shapes.json` in Phase 4 — this resolves O9 in [distill-integration.md](distill-integration.md) and makes the manifest a true cross-platform contract. |
| O5 | Does CCI access token have sufficient Salesforce permissions for Aegis UI tests? | Needs testing | Aegis UI tests (Playwright/Selenium) use session injection. The CCI-provisioned user must have Lightning UI access. Scratch org admin users should — confirm for sandbox/Steam orgs. |
| O6 | Can `@smoke` tag be added to the most critical `RevenueGoFoundation` scenarios? | Aegis team | Current smoke coverage unknown — need to coordinate with Aegis `RevenueGoFoundation` authors to tag the ~5 most critical scenarios `@smoke` for fast-path validation. |
| O7 | What is the expected runtime of the `RevenueGoFoundation` full suite? | Needs measurement | Determines whether Phase 1 local run is practical in `prepare_rlm_org` (target: under 5 min for smoke, under 15 min for full). Run and measure against a real Foundations org. |
| O8 | How should the Aegis repo path be configured per-developer? | Open | Options: (a) `aegis_repo_path` task option (current), (b) `AEGIS_REPO_PATH` env var, (c) `cumulusci.yml` project-level default pointing to a standard location. A `~/.cumulusci/aegis.yml` personal config would avoid committing local paths. |
| O9 | Should `RevenueGoFoundationCreds.json` be updated to accept a CCI-provisioned org key? | Small Aegis PR | Both feature files already use session injection (`Given login to Salesforce with sessionId`). The only change needed: add a `CCI_PROVISIONED_ORG` key to `RevenueGoFoundationCreds.json` and add `cci_aegis_creds.json` to `.gitignore`. Background steps require no code change — they already accept any ORG_KEY from the creds file. |
