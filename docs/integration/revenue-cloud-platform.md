# Revenue Cloud Engineering Platform

> **Document Type:** Integration Overview — Living Document
> **Last Updated:** 2026-04-07
> **Audience:** Engineering Leadership
>
> **Three platforms. One integrated engineering workflow for Revenue Cloud.**
>
> | Platform | Identity | Core Phase |
> |---|---|---|
> | **[Revenue Cloud Foundations](#revenue-cloud-foundations)** | `salesforce-internal/revenue-cloud-foundations` | Build |
> | **[Distill](#distill)** | `sf-industries/distill` | Evolve |
> | **[Aegis](#aegis)** | `industries/Automated-Remote-Org-Test` | Verify |

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Revenue Cloud Foundations](#2-revenue-cloud-foundations)
3. [Distill](#3-distill)
4. [Aegis](#4-aegis)
5. [Integration Architecture](#5-integration-architecture)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Document Navigator](#7-document-navigator)

---

## 1. Platform Overview

The Revenue Cloud org engineering lifecycle has three phases — **Build**, **Evolve**, and **Verify**. Each platform owns one phase:

| Phase | Platform | Core Question |
|---|---|---|
| **Build** | Revenue Cloud Foundations | How do I stand up a correctly configured Revenue Cloud org — repeatably, from scratch, across any environment? |
| **Evolve** | Distill | What has changed in a running org? What do those changes mean semantically, and which should be promoted back into the project? |
| **Verify** | Aegis | Does the org behave correctly end-to-end? Are all Revenue Cloud integration touchpoints working as expected? |

**The integration creates a closed feedback loop:**

Foundations builds the baseline → the org evolves through real use → Distill captures and semantically classifies the delta → engineering decides to promote, overlay, or discard each change → Aegis validates correctness of the updated baseline → approved changes fold back into Foundations.

---

## 2. Revenue Cloud Foundations

**Repository:** [`salesforce-internal/revenue-cloud-foundations`](../README.md)
**Technology:** CumulusCI 4.x · SFDMU v5 · Python 3.8+ · Robot Framework · Salesforce CLI
**Salesforce Release:** 260 (Spring '26) · API 66.0

Revenue Cloud Foundations is an enterprise CumulusCI automation framework for building and configuring Salesforce Revenue Cloud orgs from scratch. It answers: *"How do I stand up a correctly configured Revenue Cloud org — with the right data, permissions, and settings — repeatably across any org type?"*

### 2.1 What It Does

**Org Provisioning**
- 30+ automation flows — including `prepare_rlm_org`, the primary orchestration flow — manage scratch orgs and sandbox environments from first command to a fully configured state
- 24 scratch org definitions covering dev, QA, test, CI, enterprise, release, and environment-specific variants (including new `ent.json`, `ent-r1.json`, `ent-sb0.json`, `feature.json`, `release.json`)
- ~95% of org setup is fully automated; only Salesforce CLI authentication and Dev Hub setup remain manual

**Feature-Flag-Driven Deployment**
- 58+ flags in `cumulusci.yml` control which of 30+ metadata bundles and 11 data plans are deployed
- New edition flags (`pde`, `trial`, `dev_ed`) control PS/PSL assignments for different org editions; `billing_ui` controls the new Billing UI LWC module
- A single flag (`billing: true`) triggers the billing metadata bundle, the QB billing data plan, and the Apex activation scripts — with no other configuration required
- Flags are composable: any combination of features can be deployed to any org type

**Reference Data — Data Plans**
Three product shape families, each representing a distinct Revenue Cloud product/pricing model:

| Shape | Locale | Plans | Objects | Status |
|---|---|---|---|---|
| **QB (QuantumBit)** | en-US | 9 active plans | 95 Salesforce objects | ✅ Active (SFDMU v5) |
| **QB** | ja (Japanese) | 2 plans | 28 objects | ✅ Partial |
| **Q3** (multi-currency) | en-US | 6 plans | 40+ objects | 🔄 Pending v5 migration |
| **MFG** (manufacturing) | en-US | 4 plans | — | 📝 Draft |

All plans are target-org-agnostic (standard RLM fields only, no custom fields), enabling deployment to any correctly licensed org.

**Custom Python Task Library (30+ task modules)**
| Category | Tasks |
|---|---|
| Data loading | `load_sfdmu_data`, `post_process_extraction`, 9 extract tasks, 9 idempotency test tasks |
| CML constraints | `export_cml`, `import_cml`, `validate_cml` |
| Decision tables | `manage_decision_tables`, `activate_decision_tables`, 6 refresh tasks |
| Flows & expression sets | `manage_flows`, `manage_expression_sets` |
| Context definitions | `manage_context_definition`, `extend_standard_context` |
| Permissions | `assign_permission_set_groups_tolerant`, `recalculate_permission_set_groups` |
| Environment | `validate_setup`, `cleanup_settings_for_dev` |

**Browser Automation (Robot Framework)**
Setup test suites handle Salesforce Setup UI configuration where no Metadata API equivalent exists: Document Builder, Constraints Engine, Revenue Settings, Analytics, Timeline, App Launcher reordering. Additionally, a new **E2E test framework** (`robot/rlm-base/tests/e2e/`) provides Quote-to-Order UI test flows for post-provision validation.

**Idempotency**
All QB/en-US data plans support load-twice-no-change semantics via SFDMU v5 composite key patterns (`Name;Type`, `$Name$Parent.Name`). Idempotency is enforced by the `validate_setup` task (blocks v4 SFDMU) and verified by the `run_qb_idempotency_tests` flow.

### 2.2 Architecture Summary

```
revenue-cloud-foundations/
├── cumulusci.yml           (flags, flows, tasks, orgs — 58+ flags, 30+ flows)
├── tasks/                  (30+ custom Python task modules)
├── force-app/              (Salesforce metadata — Apex, LWC, Flows, Objects)
├── unpackaged/             (conditional deployment bundles, post_* folders)
├── robot/                  (7+ Robot Framework test suites — UI setup + E2E tests)
├── scripts/                (24 anonymous Apex scripts, 4 Python utilities)
├── datasets/
│   ├── sfdmu/qb/en-US/     (9 active data plans, 95 objects, 154 queries)
│   ├── sfdmu/qb/ja/        (2 localized Japanese plans)
│   ├── sfdmu/q3/en-US/     (6 plans — pending SFDMU v5 migration)
│   ├── sfdmu/mfg/en-US/    (4 plans — draft)
│   └── constraints/qb/     (2 CML constraint datasets with .ffxblob files)
└── docs/                   (this document and all referenced docs below)
```

---

## 3. Distill

**Repository:** `sf-industries/distill` (Salesforce enterprise — requires SSO + GCP/Embark setup)
**Technology:** Python 3.10–3.12 · Claude Agent SDK · Einstein LLM Gateway (production, including embeddings) · Vertex AI/GCP/Embark (local fallback) · Falcon Vault (secrets) · OIDC/QuantumK (API auth, refactored to `auth/` module) · SQLite (kits/projects) · PostgreSQL/Falcon (users — as of PR #121) · DuckDB · ChromaDB · S3 · Textual TUI
**Interface:** Interactive CLI (`./distill start`) · Textual TUI · Flask REST API (`src/distill/dashboard/app.py` — RBAC + OIDC-protected)

Distill is an AI-powered Salesforce customization migration platform built **exclusively on the Claude Agent SDK**. It answers: *"What customizations exist in a Salesforce codebase, what do they mean for the business, and how do I translate them to a target platform?"*

### 3.1 Agent Architecture

Four agents currently registered:

| Agent | Status | Purpose |
|---|---|---|
| **CodeSuggestionAgent** | ✅ Registered | Three async entry points: `run_file_migration()` (Mode 1 file-level, Gemini), `run_feature_migration()` (Mode 2 graph-first), `run_migration()` (router). Supports Apex and LWC. |
| **DataMapperAgent** | ✅ Registered | Interactive entity/field mapping (1:1, 1:N, N:M cardinalities) |
| **DeploymentAgent** | ✅ Registered | Deploys migrated code to Salesforce *(requires Claude Code session context — out of scope for CCI)* |
| **DeploymentAgentDataMapper** | ✅ Registered | DataMapper-aware deployment variant *(requires Claude Code context — out of scope for CCI)* |
| **IngestionAgent** | 🔲 Not registered | No agent yet; CCI bypasses agent layer via `InsightsPipeline` direct import |
| **AnalysisAgent** | 🔲 Not registered | No agent yet; `analysis/` reduced to support library for `insights/` pipeline |

### 3.2 AI Architecture

- **Claude Agent SDK exclusively** — no custom Anthropic client wrapper; all LLM calls go through `ClaudeSDKClient`
- **Clean Architecture:** Core (domain/services) → Controllers → UI — zero UI dependencies in business logic
- **LLM access (production):** Einstein LLM Gateway (`src/distill/einsteinllm/`) — OAuth credentials from Falcon Vault. As of PR #116, also used for standalone API invocations in `serve_api.py`. New Einstein embeddings module (`src/distill/einsteinllm/embeddings.py`). **LLM access (local/dev):** Vertex AI via GCP/Embark (`claude_vertex_adapter.py`). Models: `claude-sonnet-4-5@20250929`, `claude-haiku-4-5@20251001`
- **Auth:** RBAC API key (30+ permissions, 4 roles) + OIDC JWT via QuantumK SSO (refactored to `src/distill/auth/` module, PR #113 2026-03-23)
- **Storage (updated 2026-04-07):** SQLite (kits, projects — `users` table removed), **PostgreSQL/Falcon** (users — new primary backend, PR #121), DuckDB (insights data — thread-safe singleton), ChromaDB (vector store for RAG), S3/boto3 (cloud artifact storage). `DISTILL_CENTRAL_DB_BACKEND` config controls backend selection. New `customization_folder_location` field on projects table (PR #115).

### 3.3 How It Plugs Into Foundations

Integration is **phased** based on what's available today vs. what Distill's roadmap delivers:

**Today (Phase 1 — CodeSuggestion Python API):**
```
Engineer identifies Apex or LWC customization worth promoting
→ cci task run migrate_apex_customization  file_path=<path/to/Custom.cls>
     └── asyncio.run(distill.codesuggestion.api.run_file_migration(...))
         └── Output: migrated code (Gemini-translated) written to output_dir/ for engineer review
```
> ⚠️ All CodeSuggestion entry points are **async**. `GEMINI_API_KEY` required. No automated deployment — engineer reviews and merges output manually.

**Future (Phase 4 — full drift detection, gated on Phase 3 insights API spike):**
```
1. prepare_rlm_org → baseline org
2. Org accumulates customizations
3. sf project retrieve start → retrieved/
4. cci task run capture_org_customizations  [optional, non-blocking]
     └── InsightsPipeline(project_id, source_path).run()  ← Path A (preferred, no server)
     OR  POST /api/analysis/{project_id}/run-insights     ← Path B (Flask REST fallback)
         └── Diff vs shape_manifest.json → distill_drift_report.json
                ├── new_entities[]  (SObjects not in baseline)
                ├── features[]      (with inferred_domain, promotion_hint)
                └── decision: PROMOTE / OVERLAY / DISCARD
```

**Key design principle:** All Distill integration tasks are **optional and non-blocking**. Users without Distill access experience zero disruption to existing Foundations flows. See [distill-integration.md](distill-integration.md) for the full phased roadmap.

---

## 4. Aegis

**Repository:** `industries/Automated-Remote-Org-Test` at `git.soma.salesforce.com/industries/Automated-Remote-Org-Test`
**Technology:** Python · Behave 1.2.6 (BDD/Gherkin) · Selenium 4.35.0 · Playwright 1.56.0 · Jenkins CI
**Built by:** Revenue Cloud engineering team (24 product team folders, 25 registered teams in `team_config.json`)
**Authors:** Krishan Gopal Bhansalee, Rohan Sarap, Niranjana D P

Aegis is a **Salesforce Revenue Cloud BDD test automation framework** built on Behave + Selenium/Playwright. It validates end-to-end business flows across 24 RLM product teams — from product configuration through pricing, billing, usage, and fulfillment — running against live Salesforce Steam orgs.

**Architecture:**
- **Gherkin feature files** per team under `features/<TeamName>/`
- **Dual UI engine:** Playwright (via `@playwright` tag) or Selenium — feature-level choice
- **Composite API graph collections** for test data setup (multi-SObject setup in one HTTP call)
- **Persona-based testing** via `shared/data/personas.json` — named users for role-based scenario validation
- **CI/CD:** Jenkins runs all teams in parallel on Docker Selenium Grid; per-team email notifications via `team_config.json`
- **PRD-to-test AI assist:** PRDs analyzed by Cursor (AI agent) to generate Gherkin feature files — now covering both **Usage** (`usage-pr-aegis-scenario-gen`) and **Pricing** (`pricing-pr-aegis-scenario-gen`) domains, with dedicated AI knowledgebases (`NGP_PRICING_KNOWLEDGEBASE.md`, `NGP_PRICING_WATERFALL_TEST_KNOWLEDGEBASE.md`)

**Teams (updated 2026-04-07) include:** BillingCreditMemo, BillingInvoicing, BillingPayments, BillingUsageInvoicing, PriceManagement, ProductCatalogManagement, UsageManagement, UsageSelling, UsageConsumption, **UsageGuidedSetup** (new), SalesforceContracts, **RevenueGoFoundation** (direct Foundations touchpoint — see below), and others. Teams `UsageCustomerData` and `RLMSuite` were removed in March 2026.

### 4.1 RevenueGoFoundation Team — Direct Integration Touchpoint

`features/RevenueGoFoundation/` is the existing Aegis team that directly tests Revenue Cloud Foundations-provisioned orgs. **Expanded from 2 to 7 feature files since March 2026:**

| Feature File | What It Tests |
|---|---|
| `RevenueCloudInitialSetup.feature` | Revenue Cloud Initial Setup (enable RC, create quotes/orders via UI) |
| `DynamicRevenueOrchestrator.feature` | DRO flows on a Foundations-provisioned org |
| `AssetLifecycleManagement.feature` | Asset Lifecycle Management setup, redirections, help links (NEW) |
| `Quotes.feature` | Quote creation and management scenarios (NEW) |
| `Orders.feature` | Order placement and management scenarios (NEW) |
| `PriceManagement.feature` | Pricing configuration and management (NEW) |
| `ProductConfigurator.feature` | Product configuration and bundle scenarios (NEW) |

**Known gap:** The feature file notes — *"Aegis framework currently does not support creation of fresh orgs. We are only testing feature page functionalities. For fresh org initial setup, Revenue Cloud needs to be enabled manually for the first time."* This means Aegis tests run against a **pre-provisioned org** (created by `prepare_rlm_org`) rather than provisioning one itself.

**Org connection:** Env vars only (`SF_URL`, `SF_USERNAME`, `SF_PASSWORD`, `SF_TOKEN`). Team credentials stored in `RevenueGoFoundationCreds.json`.

### 4.2 Integration Role

| Touchpoint | How Aegis Connects | Current State |
|---|---|---|
| **Post-provision validation** | Run `RevenueGoFoundation` suite after `prepare_rlm_org` to verify org behaves correctly | `RevenueGoFoundation` team folder has 7 feature files covering Initial Setup, DRO, Asset Lifecycle, Quotes, Orders, Pricing, Configurator |
| **Post-promote regression** | After Distill-identified customizations are promoted into Foundations, Aegis provides the regression safety net | Manually coordinated today — no automated trigger from CCI |
| **Continuous verification** | Ongoing org health checks as the baseline evolves across releases | Jenkins cron on existing Steam orgs |

### 4.3 Current Gaps for CCI Integration

1. **No fresh-org provisioning:** Aegis cannot create orgs — it must be pointed at an existing one. CCI provisions the org; Aegis is pointed at it post-provision. A CCI task that outputs `SF_URL` + credentials and triggers the relevant Aegis Jenkins job would close this gap.
2. **No shapes/manifest awareness:** Aegis has no concept of data shapes, feature flags, or `shapes.json`. Test scenarios are written per-team and don't adapt to which QB/Q3/MFG shape was loaded. Cross-referencing shape metadata with Aegis scenario selection is an open design question (see O9 in [distill-integration.md](distill-integration.md)).
3. **No CCI integration today:** The Aegis repo has no `cumulusci.yml`, no CCI task classes, and no reference to Foundations. The `RevenueGoFoundation` team is the closest existing touchpoint.

**Note (2026-04-07):** Foundations now includes its own E2E Robot Framework test suite (`robot/rlm-base/tests/e2e/`) covering Quote-to-Order flows. This provides a fast self-check capability within the CCI pipeline before invoking the heavier Aegis BDD suite. The two are complementary: Robot tests for fast CCI-native validation, Aegis for comprehensive cross-team regression.

**Full integration plan:** [aegis-integration.md](aegis-integration.md) — credential handoff design, CCI task design, feature flag→team mapping, Jenkins API trigger, phased roadmap.

### 4.4 Running Aegis Against a Foundations Org (Manual Steps Today)

```bash
# 1. Provision the org via Foundations
cci flow run prepare_rlm_org --org <scratch-org>

# 2. Get the org URL and credentials
cci org info <scratch-org>

# 3. Clone and set up Aegis
git clone https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test
cd Automated-Remote-Org-Test
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 4. Point Aegis at the provisioned org
export SF_URL="<org-url-from-step-2>"
export SF_USERNAME="<username>"
export SF_PASSWORD="<password>"
export SF_TOKEN=""  # Not required for scratch orgs

# 5. Run the RevenueGoFoundation suite
behave features/RevenueGoFoundation/
```

---

## 5. Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 REVENUE CLOUD ENGINEERING PLATFORM                       │
│                                                                          │
│  ┌──────────────────┐       ┌─────────────────┐    ┌─────────────────┐  │
│  │    FOUNDATIONS   │       │     DISTILL     │    │      AEGIS      │  │
│  │    (Build)       │       │     (Evolve)    │    │     (Verify)    │  │
│  └──────────────────┘       └─────────────────┘    └─────────────────┘  │
│           │                         │                       │            │
│   prepare_rlm_org                   │                       │            │
│           │                         │                  e2e test runs     │
│           ▼                         │                       │            │
│   ┌──────────────┐                  │                       │            │
│   │  Revenue     │  sf retrieve →   │                       │            │
│   │  Cloud Org   │  ──────────────► │  Insights pipeline    │            │
│   │  (running)   │                  │  (10-stage scan)      │            │
│   └──────────────┘                  │       │               │            │
│           ▲                         │  drift_report.json    │            │
│           │                         │       │               │            │
│   ┌──────────────┐ ◄── promote ─────┘       │               │            │
│   │  shape       │                          │               │            │
│   │  manifest    │ ◄── validate ────────────────────────────┘            │
│   └──────────────┘                                                        │
│                                                                          │
│   For each drift item detected:                                          │
│   ├── PROMOTE  → merge into force-app/ or feature bundle                 │
│   ├── OVERLAY  → new downstream CCI project extending Foundations        │
│   └── DISCARD  → documented, not promoted                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.1 The Shape Manifest — Integration Glue

The **shape manifest** (`datasets/sfdmu/<shape>/<locale>/shape_manifest.json`) is the key artifact that connects Foundations to Distill. It describes the known baseline of what Foundations installs for a given data shape:

- **Object footprint:** all 95 SObjects, their fields, and SFDMU composite keys
- **Feature matrix:** maps each CCI flag (`billing`, `tax`, `dro`, `rating`, etc.) to the objects it introduces
- **Source:** generated from `export.json` files by `scripts/generate_baseline_manifest.py`

When Distill detects a new entity or feature, it is checked against the shape manifest. If the entity is absent → drift. If the feature flag for that entity was disabled → expected absence, not drift.

### 5.2 Multi-Tier Agent Model

The integration is designed around a **tiered agent architecture** that concentrates reasoning cost where it matters:

| Role | Model Tier | Responsibilities |
|---|---|---|
| **Orchestrator** | High-capability (e.g. Opus) | Determine analysis scope, interpret drift findings, generate promotion recommendations |
| **Executor** | Fast/efficient (e.g. Haiku) | API calls, status polling, manifest comparison, JSON parsing |
| **Reasoner** | Balanced (e.g. Sonnet) | Domain classification, bundle suggestion, promotion hint generation per drift item |

This mirrors the sub-agent pattern already used inside Distill, and maps naturally to the `capture_org_customizations` task structure — heavy reasoning is concentrated at the orchestration layer while deterministic execution steps use cost-efficient models.

### 5.3 Prompt Caching & Cost Optimization

The `shape_manifest.json` is a large (~10–20K token), **stable** artifact — identical across every run for a given data shape. It is an ideal candidate for **prompt caching**: registering the manifest as a system-prompt prefix so repeated calls do not retokenize it on every invocation.

An internal research effort is under way to apply context payload caching across agent workflows, targeting an estimated **80% reduction in per-run token cost**. The manifest design (pre-rendered flat JSON, not computed at analysis time) is already optimized for this pattern.

**When context caching becomes available, the priority artifacts to register are:**
1. `shape_manifest.json` — largest stable context, primary caching target
2. Distill API schema description — stable across minor versions
3. CCI feature flag list — changes only on major releases

Only the variable portion of each run (retrieved metadata summary + Distill feature inventory) is processed fresh. Everything else hits the cache.

### 5.4 Access Model

| Access Path | Suitable For |
|---|---|
| **Direct Anthropic API** (via Cursor / Claude Code) | Individual contributors; subject to personal spending limits |
| **AWS Bedrock via Embark** | Salesforce teams without direct API access; Embark provides temporary sandbox cloud accounts with no personal billing |
| **Enterprise license** | Org-wide access; enables higher model tiers (Opus) and increased rate limits; under evaluation |

Distill's provider configuration already supports multiple LLM backends (Anthropic direct, Bedrock adapter, OpenAI fallback), so switching the underlying access model requires no changes to integration code.

### 5.5 Open Source & IP Strategy

The integrated platform — specifically the combination of (1) CCI feature-flag-aware shape manifest generation, (2) AI-powered semantic drift detection, and (3) automated Promote/Overlay/Discard classification — represents a novel engineering workflow without a clear prior art equivalent in the Salesforce ecosystem.

**Recommended sequencing:**
1. Consult legal on patentability of the core workflow before any public publication
2. File patent application (or provisional) if proceeding — public disclosure prior to filing forfeits most patent rights
3. Collaborate with legal on open-source licensing strategy
4. Publish to an appropriate internal open-source forum per open-source policies
5. Engage broader engineering community as contributors

> ⚠️ **Open-source publication must follow, not precede, any patent filing.**

---

## 6. Implementation Roadmap

| Phase | Name | Status | Key Deliverable |
|---|---|---|---|
| **Phase 0** | Datasets Reorganization | 🔲 Pending approval | Restructured `datasets/` folder with `shapes.json` registry |
| **Phase 1** | CodeSuggestion Integration | 🔲 TODO *(parallelizable with Phase 0)* | `migrate_apex_customization` CCI task — Apex translation via Python import (Gemini-powered) |
| **Phase 2** | Shape Manifest + CCI Scaffold | 🔲 TODO *(parallelizable with Phase 0–1)* | `generate_baseline_manifest` + `capture_org_customizations` CCI tasks (stub) |
| **Phase 3** | Insights API Spike | 🔲 TODO | Validate headless `distill.insights.api` invocation from CCI — critical path question |
| **Phase 4** | Automated Drift Detection | 🔲 Gated on Phase 3 | Full round-trip: retrieve → insights API → diff vs manifest → `drift_report.json` |
| **Phase 5** | Field-Level Drift + Cross-Platform | 🔲 TBD | DataMapper integration, context def diffing, Aegis test-scenario selection via `shapes.json` |

> **Minimal viable demo (Phase 1 only, no Phase 0 required):**
> Generate a `shape_manifest.json` from the current `qb/en-US` plans → point `baseline_manifest_path` at its current location → run `capture_org_customizations` against a customized dev org → show `distill_drift_report.json` output. Phase 0 folder restructuring can proceed in parallel without blocking the demo path.

→ *Full technical roadmap:* [distill-integration.md §8](distill-integration.md#8-implementation-roadmap)

---

## 7. Document Navigator

### 7.1 Primary Living Documents

| Document | Purpose | Audience |
|---|---|---|
| **[This document](revenue-cloud-platform.md)** | Platform overview — entry point for all stakeholders | All |
| **[Distill Integration Plan](distill-integration.md)** | Full technical spec: insights pipeline integration, shape manifest schema, CCI task design, open questions, phased roadmap | Engineering |
| **[Aegis Integration Plan](aegis-integration.md)** | Credential handoff design, CCI task design, flag-to-team mapping, Jenkins API trigger, phased roadmap | Engineering |
| **[Project Analysis Reference](project-analysis.md)** | Comprehensive inventory of both Foundations and Distill — tasks, flows, APIs, DB schemas | Engineering |
| **[Datasets Reorganization Proposal](datasets-reorganization.md)** | Phase 0: before/after structure, migration script, CCI path changes required | Engineering |

### 7.2 Revenue Cloud Foundations — Deep Dives

| Document | Contents |
|---|---|
| **[README — Main](../README.md)** | Setup, prerequisites, feature flags, custom tasks, flows, data plans, common workflows, troubleshooting |
| **[Constraints Utility Guide (CML)](../datasets/constraints/README.md)** | Export/import/validate architecture, 4-class design, polymorphic ID resolution |
| **[Constraints Setup & Flow Order](../guides/constraints-setup.md)** | `prepare_constraints` flow dependencies, 9-step deployment sequence with conditions |
| **[SFDMU v5 Composite Key Optimizations](../references/sfdmu-composite-key-optimizations.md)** | v4→v5 migration guide, `$$` notation, extraction post-processing workflow |
| **[Context Service Utility](../references/context-service-utility.md)** | Context definition management via Context Service APIs (not Metadata API); plan file structure |
| **[Decision Table Examples](../references/decision-table-examples.md)** | `manage_decision_tables` task: list, query, refresh, activate, deactivate, validate |
| **[Flow & Expression Set Examples](../references/task-examples.md)** | `manage_flows` and `manage_expression_sets` task examples |
| **[Spring '26 Tooling Opportunities](../archive/tooling-opportunities.md)** | New API surface in Release 260 and candidate new CCI tasks |
| **[Robot Framework Setup Automation](../robot/rlm-base/tests/setup/README.md)** | Headless browser automation for Setup UI toggles (Document Builder, Constraints Engine, Revenue Settings) |
| **[Postman Collections — v260 Analysis](../postman/README_V260_ANALYSIS.md)** | Analysis of 129 RLM/RCA endpoints in Spring '26 with implementation status |

### 7.3 Data Plan READMEs — QB Shape (en-US)

| Plan | Objects | Domain |
|---|---|---|
| **[qb-pcm](../datasets/sfdmu/qb/en-US/qb-pcm/README.md)** | 28 | Product catalog, attribute definitions, selling models, bundles, catalogs, categories |
| **[qb-pricing](../datasets/sfdmu/qb/en-US/qb-pricing/README.md)** | 16 | Pricebook entries, price adjustment schedules/tiers, attribute-based adjustments, derived prices |
| **[qb-billing](../datasets/sfdmu/qb/en-US/qb-billing/README.md)** | 11 | Legal entities, billing policies/treatments/items, payment terms, GL accounts |
| **[qb-tax](../datasets/sfdmu/qb/en-US/qb-tax/README.md)** | 6 | Tax engine, tax policies, tax treatments (2-pass: draft → activate) |
| **[qb-dro](../datasets/sfdmu/qb/en-US/qb-dro/README.md)** | 13 | DRO fulfillment step definitions, groups, dependencies, scenarios, orchestration rules |
| **[qb-rating](../datasets/sfdmu/qb/en-US/qb-rating/README.md)** | 14 | Usage resources, product-resource associations, rating policies (2-pass) |
| **[qb-rates](../datasets/sfdmu/qb/en-US/qb-rates/README.md)** | 5 | Rate cards, rate card entries, tiered rate adjustments |
| **[qb-product-images](../datasets/sfdmu/qb/en-US/qb-product-images/README.md)** | 1 | Product image URL updates (update-only pass) |
| **[qb-transactionprocessingtypes](../datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md)** | 1 | Transaction Processing Type records |
| **[procedure-plans](../datasets/sfdmu/procedure-plans/README.md)** | 3 | Cross-shape: Procedure Plan sections and options (2-pass) |

---

*Revenue Cloud Engineering Platform — Living Document*
*Branch: `feat/distill-aegis-integration` · Repo: `salesforce-internal/revenue-cloud-foundations`*
