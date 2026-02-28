# Revenue Cloud Foundations × Distill: Integration Living Document

> **Status:** In Progress
> **Last Updated:** 2026-02-27
> **Scope:** Round-trip customization capture across data shapes (no custom fields, target-org-agnostic)
>
> **Part of:** [Revenue Cloud Engineering Platform](revenue-cloud-platform.md)
>
> **Related documents:**
> - [revenue-cloud-platform.md](revenue-cloud-platform.md) — platform overview (start here)
> - [project-analysis.md](project-analysis.md) — comprehensive capabilities reference for both projects
> - [datasets-reorganization.md](datasets-reorganization.md) — prerequisite structural proposal (must be approved before Phase 1)

---

## Table of Contents

1. [Project Overviews](#1-project-overviews)
2. [Strategic Integration POV](#2-strategic-integration-pov)
3. [The Round-Trip Workflow](#3-the-round-trip-workflow)
4. [Distill REST API: Relevant Endpoints](#4-distill-rest-api-relevant-endpoints)
5. [Shape Manifest: Data Model Design](#5-shape-manifest-data-model-design)
6. [Integration Task Design: `capture_org_customizations`](#6-integration-task-design-capture_org_customizations)
7. [CumulusCI Configuration](#7-cumulusci-configuration)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Open Questions & Decisions](#9-open-questions--decisions)

---

## 1. Project Overviews

> Full technical detail for both projects is in [project-analysis.md](project-analysis.md). This section captures the integration-relevant summary.

### 1.1 Revenue Cloud Foundations

An enterprise CumulusCI automation framework for standing up Salesforce Revenue Cloud (RLM) orgs from scratch. Its core job: *"How do I deploy and configure a correctly structured Revenue Cloud org?"*

**Integration-relevant facts:**
- 3 data shape families: **QB** (en-US + ja), **Q3** (en-US, pending v5 migration), **MFG** (en-US, draft)
- 28 named flows (including `prepare_rlm_org`, a 29-step primary orchestration flow), 24 custom Python task modules, 50+ feature flags drive conditional deployment
- All data plans are target-org-agnostic (standard RLM fields only, no custom fields)
- SFDMU v5 composite key patterns throughout qb/en-US; q3 pending migration
- CML constraint models are QB-shape-specific (moving into shape folder — see [datasets-reorganization.md](datasets-reorganization.md))
- **What it does NOT do today:** detect post-deployment org drift, ingest customizations back from running orgs

### 1.2 Distill (`sf-industries/distill`)

An AI-powered Salesforce customization migration platform built exclusively on the Claude Agent SDK. Its core job: *"What customizations exist in a Salesforce codebase, what do they mean for the business, and how do I translate them to a target platform?"*

**LLM access:** Vertex AI via GCP/Embark (not direct Anthropic API). Models: `claude-sonnet-4-5@20250929` (orchestration), `claude-haiku-4-5@20251001` (agents).

**Integration-relevant agents — current status:**

| Agent | Status | Purpose | Integration Phase |
|---|---|---|---|
| **CodeSuggestionAgent** | ✅ Implemented | `run_file_migration(file_path)` — migrates a `.cls`/`.trigger` to target org structure | **Phase 1 (available now)** |
| **DataMapperAgent** | ✅ Implemented | Interactive entity/field mapping (1:1, 1:N, N:M); human-driven, not automatable today | Phase 5 (future automation) |
| **DeploymentAgent** | ✅ Implemented | Deploys migrated code to Salesforce *(requires Claude Code context — not invocable from CCI subprocess)* | Supports Phase 1 (with constraint) |
| **DeploymentAgentDataMapper** | ✅ Implemented | DataMapper-aware deployment variant for mapped entities | Supports Phase 1 (with constraint) |
| **IngestionAgent** | 🔲 Not registered | Ingests retrieved org metadata for analysis; `src/distill/insights/` module exists — agent registration pending | Phase 3 spike bypasses agent layer via direct Python import |
| **AnalysisAgent** | 🔲 Not registered | Feature/capability extraction, drift detection, impact analysis; `src/distill/analysis/` module exists — agent registration pending | Phase 3 spike bypasses agent layer via direct Python import |
| **REST API (Web mode)** | 🔲 Future | FastAPI HTTP interface for programmatic integration | Not required for CCI integration (Python import path) |

**Today's integration entry point:** `CodeSuggestionAgent.run_file_migration` — importable as a Python API (`from distill.codesuggestion.api import run_file_migration`). Takes an Apex file path, returns migrated code. Engineer-triggered, not automated.

> ⚠️ **Integration constraints:**
> - `./distill start` is an interactive, menu-driven CLI — it cannot be driven non-interactively from a CCI subprocess. The correct integration path is a **direct Python package import**.
> - `run_file_migration` internally routes through **Gemini** (hardcoded), not Claude. The orchestration shell runs on Haiku, but the actual code translation is Gemini-powered.
> - `DeploymentAgent` uses Claude Code built-in tools (`Read`, `Grep`, `Glob`, `Write`, `Edit`, `Bash`) and is only operable within a Claude Code session — it cannot be invoked from CCI.

**Full automated drift detection** (the round-trip workflow in §3) requires the `insights/` pipeline to be callable headlessly from a CCI Python task — validated via the Phase 3 spike. Agent registration and REST API are **not required** for the CCI integration path (direct Python import). The underlying `insights/` and `analysis/` modules exist in the repo. See §8 for the phased roadmap.

---

## 2. Strategic Integration POV

### 2.1 Where They Operate

These tools function at different layers of the implementation lifecycle:

| Phase | Activity | Tool |
|---|---|---|
| Analysis | Source org feature discovery | Distill (Insights) |
| Analysis | Schema & entity mapping | Distill (DataMapper) |
| Migration | Apex / Flows / LWC translation | Distill (CodeSuggestion + Metadata Migration) |
| **Capture** | **Detect post-deployment customization drift** | **Distill → Revenue Cloud Foundations (new integration)** |
| Deployment | Org provisioning, scratch org creation | Revenue Cloud Foundations (CumulusCI) |
| Deployment | Metadata deployment (conditional bundles) | Revenue Cloud Foundations |
| Deployment | Reference data loading (SFDMU) | Revenue Cloud Foundations |
| Configuration | Context extensions, DT lifecycle, PSL/PSG | Revenue Cloud Foundations |
| Validation | Environment validation, idempotency tests | Revenue Cloud Foundations |

### 2.2 The Integration Opportunity (This Document's Focus)

**The scenario:** Orgs created by Revenue Cloud Foundations accumulate customizations over time — new Apex classes, modified Flows, extended LWC components, additional context attributes, new product-related objects. Currently there's no structured pipeline to:
1. Detect what has diverged from the project baseline
2. Understand what those changes mean semantically (are they billing-related? PCM-related?)
3. Decide whether to promote them back into the project

Distill's Insights engine provides the semantic analysis layer. The integration creates a **round-trip feedback loop** from running org back to the project.

### 2.3 Design Principles for This Integration

- **Optional, not mandatory.** Users without Distill access should experience no change to existing flows.
- **Non-blocking.** The integration never fails the main `prepare_rlm_org` flow.
- **Scoped to qb/en-US.** Only the 9 plans in `datasets/sfdmu/qb/en-US/` are in scope. Other plan folders are excluded until they are updated for SFDMU v5 composite key patterns.
- **No custom fields.** The baseline manifest only tracks standard RLM fields. Custom field drift is out of scope.
- **Read-only from Revenue Cloud Foundations' perspective.** The integration produces a report; no automatic merging or promotion happens.

---

## 3. The Round-Trip Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROUND-TRIP WORKFLOW                           │
│                                                                  │
│  Foundations             Running Org             Distill         │
│  ─────────────           ──────────              ──────────      │
│                                                                  │
│  prepare_rlm_org ──────► Baseline org state                      │
│                          (known, from project)                   │
│                                │                                 │
│                          Customization                           │
│                          by admins/devs                          │
│                                │                                 │
│                          Customized org                          │
│                          (unknown delta)                         │
│                                │                                 │
│                    sf project retrieve start                     │
│                                │                                 │
│                          Retrieved metadata                      │
│                          on local filesystem                     │
│                                │                                 │
│                                └──────────────► Insights engine  │
│                                                 (10-stage scan)  │
│                                                       │          │
│                                                 Feature/         │
│                                                 capability       │
│                                                 inventory        │
│                                                       │          │
│  baseline_manifest.json ◄─────────────────────── diff()         │
│                                                       │          │
│  drift_report.json ◄──────────────────────────────── │          │
│  (new objects, fields,                                           │
│   features, LWC, Apex)                                           │
│                                                                  │
│  Human decision:                                                 │
│  PROMOTE / OVERLAY / DISCARD                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.1 The Three Outcomes for Each Drift Item

| Decision | Meaning | Where It Goes |
|---|---|---|
| **Promote** | Generic improvement to the reference implementation | Merged into `force-app/` or appropriate `unpackaged/post_*/` bundle; new feature flag if needed |
| **Overlay** | Customer/org-specific, not appropriate for the base | New downstream CCI project that extends `revenue-cloud-foundations` as a dependency |
| **Discard** | Experimental, broken, or org-specific workaround | Documented but not promoted |

Distill's capability clustering output provides the semantic signal to make this decision consistently — it tells you *what domain* each change belongs to (billing capability, PCM feature, etc.) rather than just "this file is different."

---

## 4. Distill REST API: Integration Contract *(Future — Web Mode Not Yet Built)*

> ⚠️ **Status:** The Distill REST API (Web mode / FastAPI) is planned but not yet implemented. The endpoints below represent the **target integration contract** — the API surface that Phase 4 of the integration will call once Distill's Web mode is built. This section should be treated as a forward-looking specification, not current capability.
>
> **Today's integration path** is CLI-based (Phase 1 — CodeSuggestionAgent via `./distill start`). See §8 for the phased roadmap.

### 4.1 Full API Reference (Target Contract)

Base URL: configurable (default `http://localhost:8000`)
OpenAPI spec: `GET /openapi.json` | Swagger UI: `GET /docs`

#### Health & Discovery

| Method | Path | Purpose | Response |
|---|---|---|---|
| `GET` | `/health` | Connectivity check | `{"status": "ok"}` |
| `GET` | `/api/projects` | List all projects | Array of project objects |
| `GET` | `/api/projects/{id}` | Get single project | Project object |
| `GET` | `/api/workspace/active` | Get active project | `{active_project_id, project}` |

**Project object schema:**
```json
{
  "id": "<uuid>",
  "project_name": "<string>",
  "domain": "<string>",
  "status": "active|in_progress|completed|failed|archived",
  "vectorization_complete": false,
  "created_at": "<datetime>",
  "source_folder_location": "<string>",
  "target_folder_location": "<string>",
  "customization_folder_location": "<string|null>"
}
```

#### Analysis (Insights Pipeline)

| Method | Path | Purpose | Key Body / Query Params |
|---|---|---|---|
| `POST` | `/api/analysis/run` | Trigger Insights pipeline | `project_id`, `source_path`, `repo_type` (default: `"Source"`), `skip_stages[]` |
| `GET` | `/api/analysis/{id}/summary` | Poll for completion / get stats | `mode` (`fast`\|`thorough`), `repo_type` |
| `GET` | `/api/analysis/{id}/features` | Get extracted business features | `mode`, `repo_type` |

**`POST /api/analysis/run` request:**
```json
{
  "project_id": "<uuid>",
  "source_path": "/path/to/retrieved/metadata",
  "repo_type": "Source",
  "skip_stages": []
}
```

**`GET /api/analysis/{id}/summary` response:**
```json
{
  "total_artifacts": 142,
  "entry_points": 23,
  "entry_point_tiers": { "TIER_1_DEFINITIVE": 12, "TIER_2_PROBABLE": 11 },
  "unique_entities_accessed": 31,
  "total_flows": 87,
  "total_capabilities": 19,
  "total_features": 8
}
```

**`GET /api/analysis/{id}/features` response (array):**
```json
[
  {
    "business_feature_id": "<string>",
    "name": "<string>",
    "description": "<string>",
    "flows": ["<flow_id>"],
    "entities": ["Product2", "PricebookEntry"],
    "operations": ["C", "R", "U", "D"],
    "files": ["<file_path>"],
    "artifacts": ["<artifact_id>"],
    "ui_components": ["<component_id>"],
    "mode": "fast|thorough"
  }
]
```

#### DataMapper (for future phase)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/datamapper/run` | Run schema mapping pipeline |
| `GET` | `/api/datamapper/{id}/schema/{type}` | Get schema (`source`\|`target`\|`mapping`) |

#### Feature Mapping (for future phase)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/feature-mapping/run` | Map features between source and target inventories |

**`POST /api/feature-mapping/run` request:**
```json
{
  "source": "/path/to/source_features.json",
  "target": "/path/to/target_features.json",
  "entity_map": "/path/to/entity_map.json",
  "top_n": 3,
  "min_confidence": 0.3,
  "use_llm": true
}
```

### 4.2 API Call Sequence for `capture_org_customizations`

```
1. GET  /health                              → confirm reachable
2. GET  /api/projects                        → find project by name
   (or) GET /api/workspace/active            → use active project
3. POST /api/analysis/run                    → trigger Insights on retrieved/ path
         body: { project_id, source_path, repo_type: "Source" }
4. POLL GET /api/analysis/{id}/summary       → check total_features > 0
         repeat every poll_interval until complete or timeout
5. GET  /api/analysis/{id}/features          → get full feature inventory
6. [local] diff(features, baseline_manifest) → compute drift report
7. [local] write drift_report.json           → output artifact
```

### 4.3 Known Gap: Project Creation via REST API

**Current state:** Projects must be created via the Distill CLI (`/configure` slash command). There is no `POST /api/projects` endpoint.

**Impact:** The CCI task requires a Distill project to be pre-configured before first use.

**Workaround (Phase 1):**
- Users run `./distill start` once, use `/configure` to create a named project pointing at their retrieved metadata directory
- Record the project UUID in `cumulusci.yml` as the `distill_project_id` option

**Future enhancement (Phase 2):**
Contribute a `POST /api/projects` endpoint to Distill that accepts `{project_name, domain, source_folder_location}` and returns a project object with UUID. This removes the manual pre-configuration step.

---

## 5. Shape Manifest: Data Model Design

> **Prerequisite:** The datasets folder reorganization described in [datasets-reorganization.md](datasets-reorganization.md) must be completed before manifest generation. Specifically: `constraints/` must be co-located inside the shape folder, and `shapes.json` must exist at `datasets/`.

### 5.1 Design Goals

Each data shape/locale has a `shape_manifest.json` that captures the **expected schema state** of all plans in that folder. It is:

- **One manifest per shape/locale** — not per plan, not per object. `qb/en-US` gets one manifest covering all 13+ plans.
- **Derived, not hand-authored.** Generated by the `generate_baseline_manifest` CCI task from existing `export.json` files.
- **Feature-flag-aware.** Contains a `feature_matrix` mapping each CCI flag to the objects it introduces, so drift detection can be scoped to the flags that were active when the org was built.
- **Standard fields only.** No custom fields (`__c` suffix) — plans are target-org-agnostic.
- **Multi-shape aware.** Each shape registers in `datasets/shapes.json`. The `capture_org_customizations` task accepts a `data_shape` parameter to select which manifest to diff against.
- **Versioned with the project.** Committed to git; regenerated when data plans change.

### 5.2 Shape Registry (`datasets/shapes.json`)

The registry is the single source of truth for all available shapes. See `docs/datasets-reorganization.md §9` for the full initial content.

**Key fields per shape entry:**

```json
{
  "id": "qb-en-US",
  "path": "datasets/sfdmu/qb/en-US",
  "status": "active | partial | pending | draft",
  "source": "hand-authored | distill",
  "sfdmu_version": "5",
  "required_flags": ["qb"],
  "optional_flags": ["billing", "tax", "dro", "rating", "rates", "clm"],
  "includes_constraints": true,
  "manifest": "datasets/sfdmu/qb/en-US/shape_manifest.json"
}
```

**Status values:**
- `active` — v5 plans, manifest generated, ready for drift detection
- `partial` — incomplete plan coverage (e.g., `qb/ja` has pcm + pricing only)
- `pending` — needs SFDMU v4→v5 migration before manifest can be generated (e.g., `q3/en-US`)
- `draft` — in development (e.g., `mfg/en-US`)

### 5.3 Shape Manifest Schema (`shape_manifest.json`)

**File location:** `datasets/sfdmu/<shape>/<locale>/shape_manifest.json`

```json
{
  "$schema": "https://rlm-base.schema/shape-manifest/v1",
  "version": "1.0.0",
  "generated_at": "<ISO-8601 datetime>",
  "generator": "cci task run generate_baseline_manifest --option shape_id qb-en-US",
  "shape_id": "qb-en-US",
  "release": "260",
  "api_version": "66.0",

  "feature_matrix": {
    "qb": {
      "objects": ["Product2", "ProductCatalog", "ProductCategory",
                  "AttributeDefinition", "ProductClassification",
                  "ProductSellingModel", "Pricebook2", "PricebookEntry",
                  "TransactionProcessingType"],
      "plans": ["qb-pcm", "qb-pricing", "qb-product-images",
                "qb-transactionprocessingtypes"]
    },
    "billing": {
      "objects": ["BillingPolicy", "BillingTreatment", "BillingTreatmentItem",
                  "LegalEntity", "PaymentTerm", "PaymentTermItem",
                  "GeneralLedgerAccount", "AccountingPeriod"],
      "plans": ["qb-billing"]
    },
    "tax": {
      "objects": ["TaxPolicy", "TaxTreatment", "TaxEngine", "TaxEngineProvider"],
      "plans": ["qb-tax"]
    },
    "dro": {
      "objects": ["FulfillmentStepDefinition", "FulfillmentStepDefinitionGroup",
                  "ProductFulfillmentScenario", "FulfillmentWorkspace"],
      "plans": ["qb-dro"]
    },
    "rating": {
      "objects": ["UsageResource", "UsageResourceBillingPolicy",
                  "ProductUsageResource", "RatingFrequencyPolicy"],
      "plans": ["qb-rating"]
    },
    "rates": {
      "objects": ["RateCard", "RateCardEntry", "RateAdjustmentByTier"],
      "plans": ["qb-rates"]
    }
  },

  "plans": {
    "<plan-name>": {
      "path": "datasets/sfdmu/qb/en-US/<plan-name>",
      "feature_flags": ["<flag>"],
      "multi_pass": true,
      "pass_count": 3,
      "passes": [
        {
          "pass_index": 0,
          "label": "<objectSet name from export.json>",
          "objects": [
            {
              "api_name": "<SObject API name>",
              "operation": "Upsert | Update | Insert | Readonly | default",
              "external_id": "<field or composite expression>",
              "external_id_type": "single | composite | composite_dollar",
              "external_id_fields": ["<field1>", "<field2>"],
              "fields": ["<field1>", "<field2>"],
              "field_fingerprint": "<sha256 of sorted field list>",
              "skip_existing_records": false,
              "delete_old_data": false,
              "excluded": false,
              "query_filter": "<WHERE clause | null>"
            }
          ]
        }
      ]
    }
  },

  "object_index": {
    "<SObject API name>": {
      "plans": ["<plan-name>"],
      "feature_flags": ["<flag>"],
      "operations": ["Upsert"],
      "all_fields": ["<field1>"],
      "primary_external_id": "<field or expression>"
    }
  },

  "composite_key_registry": {
    "<plan-name>.<SObject>": {
      "type": "standard | dollar_notation",
      "fields": ["<field1>", "<field2>"],
      "expression": "<external_id string as written in export.json>"
    }
  },

  "metadata": {
    "total_plans": 13,
    "total_objects": 95,
    "total_composite_keys": 29,
    "dollar_notation_keys": 13,
    "multi_pass_plans": ["qb-billing", "qb-tax", "qb-rating"]
  }
}
```

### 5.4 Composite Key Notation Reference

Three composite key types exist in the qb/en-US plans:

| Type | Example | Notation in export.json | `external_id_type` value |
|---|---|---|---|
| **Single** | `StockKeepingUnit` | Plain field name | `"single"` |
| **Standard composite** | `Name;SellingModelType` | Semicolon-separated | `"composite"` |
| **Dollar composite** | `$$Name$BillingTreatment.Name` | `$$` prefix, `$` separator | `"composite_dollar"` |

Dollar notation (`$$`) is SFDMU v5-specific — computed columns in the CSV concatenating multiple traversal paths. The manifest captures them verbatim so diff logic can correctly identify field-level changes vs. key-structural changes.

### 5.5 Key Object Index (qb/en-US)

| SObject | Plans | Feature Flag | Primary External ID |
|---|---|---|---|
| `Product2` | pcm, pricing, product-images, billing, dro, rating, rates | `qb` | `StockKeepingUnit` |
| `ProductSellingModel` | pcm, pricing | `qb` | `Name;SellingModelType` |
| `Pricebook2` | pricing | `qb` | `Name;IsStandard` |
| `PricebookEntry` | pricing | `qb` | `Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` |
| `PriceAdjustmentTier` | pricing | `qb` | 9-field composite |
| `LegalEntity` | billing, tax | `billing` / `tax` | `Name` |
| `BillingPolicy` | billing | `billing` | `Name` |
| `BillingTreatmentItem` | billing | `billing` | `$$Name$BillingTreatment.Name` |
| `PaymentTermItem` | billing | `billing` | `$$PaymentTerm.Name$Type` |
| `TaxPolicy` | tax | `tax` | `Name` |
| `FulfillmentStepDefinition` | dro | `dro` | `Name` |
| `ProductFulfillmentScenario` | dro | `dro` | `Name` |
| `UsageResource` | rating | `rating` | `Code` |
| `ProductUsageResourcePolicy` | rating | `rating` | `$$` composite |
| `RateCard` | rates | `rates` | `Name;Type` |
| `RateCardEntry` | rates | `rates` | 4-field composite |
| `TransactionProcessingType` | transactionprocessingtypes | `qb` | `DeveloperName` |

> Full object index (all 95 objects) is generated into `shape_manifest.json` by the generator task.

### 5.6 Manifest Generator

**CCI task:** `generate_baseline_manifest`
**Script:** `scripts/generate_baseline_manifest.py` *(to be created — Phase 0)*

**Usage:**
```bash
# Generate manifest for a specific shape
cci task run generate_baseline_manifest --option shape_id qb-en-US

# Regenerate all active shapes
cci task run generate_baseline_manifest --option shape_id all
```

**What it does:**
1. Reads `datasets/shapes.json` to find all shapes with `status: active`
2. For each shape, reads every `export.json` in the shape folder
3. Extracts: object API names, operations, external IDs (classifies single/composite/dollar), field lists from SELECT queries
4. Computes `field_fingerprint` as SHA-256 of sorted field list per object
5. Builds `feature_matrix` by cross-referencing plan `feature_flags`
6. Writes `shape_manifest.json` into the shape folder
7. Skips shapes with `status: pending` or `draft` (logs warning)

```json
{
  "$schema": "https://rlm-base.schema/baseline-manifest/v1",
  "version": "1.0.0",
  "generated_at": "<ISO-8601 datetime>",
  "generator_script": "scripts/generate_baseline_manifest.py",
  "release": "260",
  "api_version": "66.0",
  "scope": "qb/en-US",

  "plans": {
    "<plan-name>": {
      "path": "datasets/sfdmu/qb/en-US/<plan-name>",
      "feature_flags": ["<flag>"],
      "multi_pass": true | false,
      "pass_count": 1 | 2 | 3,
      "passes": [
        {
          "pass_index": 0,
          "label": "<human label from export.json objectSet name>",
          "objects": [
            {
              "api_name": "<SObject API name>",
              "operation": "Upsert | Update | Insert | Readonly | default",
              "external_id": "<field or composite expression>",
              "external_id_type": "single | composite | composite_dollar",
              "external_id_fields": ["<field1>", "<field2>"],
              "fields": ["<field1>", "<field2>"],
              "field_fingerprint": "<sha256 of sorted field list>",
              "skip_existing_records": false,
              "delete_old_data": false,
              "excluded": false,
              "query_filter": "<WHERE clause if present | null>"
            }
          ]
        }
      ]
    }
  },

  "object_index": {
    "<SObject API name>": {
      "plans": ["<plan-name>"],
      "operations": ["Upsert"],
      "all_fields": ["<field1>"],
      "primary_external_id": "<field or expression>"
    }
  },

  "composite_key_registry": {
    "<plan-name>.<SObject>": {
      "type": "standard | dollar_notation",
      "fields": ["<field1>", "<field2>"],
      "expression": "<external_id string as written in export.json>"
    }
  },

  "metadata": {
    "total_plans": 9,
    "total_objects": 95,
    "total_composite_keys": 29,
    "dollar_notation_keys": 13,
    "multi_pass_plans": ["qb-billing", "qb-tax", "qb-rating"]
  }
}
```

### 5.3 Composite Key Notation Reference

The manifest distinguishes three composite key types found in the qb/en-US plans:

| Type | Example | Notation in export.json | Field in manifest |
|---|---|---|---|
| **Single** | `StockKeepingUnit` | Plain field name | `"single"` |
| **Standard composite** | `Name;SellingModelType` | Semicolon-separated field names | `"composite"` |
| **Dollar composite** | `$$Name$BillingTreatment.Name` | `$$` prefix with `$` separator | `"composite_dollar"` |

Dollar notation composites (`$$`) are particularly important — these are SFDMU v5-specific and represent computed columns in the CSV that concatenate multiple traversal paths. The manifest captures them verbatim so the diff logic knows to ignore standard-field changes within composite key components.

### 5.4 Object Index: qb/en-US Plans

The object index maps every SObject to the plans that include it. This is used during diff to understand which domain a new/modified object belongs to.

| SObject | Plans | Primary External ID |
|---|---|---|
| `Product2` | pcm, pricing, product-images, billing, dro, rating, rates | `StockKeepingUnit` |
| `ProductSellingModel` | pcm, pricing | `Name;SellingModelType` |
| `Pricebook2` | pricing | `Name;IsStandard` |
| `PricebookEntry` | pricing | `Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` |
| `PriceAdjustmentSchedule` | pricing | `Name;CurrencyIsoCode` |
| `PriceAdjustmentTier` | pricing | 9-field composite |
| `LegalEntity` | billing, tax | `Name` |
| `BillingPolicy` | billing | `Name` |
| `BillingTreatment` | billing | `Name` |
| `BillingTreatmentItem` | billing | `$$Name$BillingTreatment.Name` |
| `PaymentTerm` | billing | `Name` |
| `PaymentTermItem` | billing | `$$PaymentTerm.Name$Type` |
| `GeneralLedgerAccount` | billing | `Name` |
| `TaxPolicy` | tax | `Name` |
| `TaxTreatment` | tax | `Name` |
| `FulfillmentStepDefinitionGroup` | dro | `Name` |
| `FulfillmentStepDefinition` | dro | `Name` |
| `ProductFulfillmentScenario` | dro | `Name` |
| `UnitOfMeasure` | pcm, rating | `UnitCode` |
| `UnitOfMeasureClass` | pcm, rating | `Code` |
| `UsageResource` | rating | `Code` |
| `RateCard` | rates | `Name;Type` |
| `RateCardEntry` | rates | 4-field composite |
| `AttributeDefinition` | pcm | `Code` |
| `ProductCatalog` | pcm | `Code` |
| `ProductCategory` | pcm | `Code` |
| `TransactionProcessingType` | transactionprocessingtypes | `DeveloperName` |

> **Note:** This table lists key objects. The full manifest includes all 95 objects across all 9 plans.

### 5.5 Manifest Generator Script

**File:** `scripts/generate_baseline_manifest.py`

This script reads all `export.json` files in `datasets/sfdmu/qb/en-US/` and produces `baseline_manifest.json`. It should be re-run whenever a data plan is updated.

**Pseudocode:**

```python
PLANS = [
    ("qb-pcm",                     ["qb"]),
    ("qb-pricing",                 ["qb"]),
    ("qb-product-images",          ["qb"]),
    ("qb-billing",                 ["qb", "billing"]),
    ("qb-tax",                     ["qb", "tax"]),
    ("qb-dro",                     ["qb", "dro"]),
    ("qb-rating",                  ["qb", "rating"]),
    ("qb-rates",                   ["qb", "rates"]),
    ("qb-transactionprocessingtypes", ["qb"]),
]

def generate():
    manifest = { "plans": {}, "object_index": {}, "composite_key_registry": {} }

    for plan_name, flags in PLANS:
        export_json = load(f"datasets/sfdmu/qb/en-US/{plan_name}/export.json")
        passes = extract_passes(export_json)  # handles objectSets[] and flat arrays

        for pass_idx, pass_objects in enumerate(passes):
            for obj in pass_objects:
                # extract: api_name, operation, externalId, query fields
                # classify external_id_type: single/composite/composite_dollar
                # compute field_fingerprint: sha256(sorted(fields))
                # update object_index
                # register composite keys

    manifest["metadata"] = compute_stats(manifest)
    manifest["generated_at"] = datetime.utcnow().isoformat()
    write("datasets/sfdmu/qb/en-US/baseline_manifest.json", manifest)
```

**CCI task to regenerate:**
```yaml
tasks:
  generate_baseline_manifest:
    description: "Regenerate the qb/en-US baseline manifest from export.json files"
    class_path: tasks.rlm_generate_baseline_manifest.GenerateBaselineManifest
```

---

## 6. Integration Task Design: `capture_org_customizations`

### 6.1 Task Overview

| Attribute | Value |
|---|---|
| **Class** | `tasks.rlm_distill_capture.DistillCaptureDrift` |
| **CCI task name** | `capture_org_customizations` |
| **Mandatory** | No — gracefully skips if Distill is not configured or unreachable |
| **Inputs** | Retrieved metadata path, Distill project ID, API URL |
| **Outputs** | `output/distill_drift_report.json` |
| **Side effects** | None — read-only from org and Distill perspective |
| **Fails flow** | Never — on any error, logs warning and exits cleanly |

### 6.1.1 Multi-Tier Agent Model

The task is designed for execution by a **tiered agent model** rather than a single monolithic LLM call. This keeps reasoning cost proportional to reasoning complexity:

| Step | Model Tier | Rationale |
|---|---|---|
| Determine analysis scope; interpret final drift report | High-capability (e.g. Opus) | Requires strong contextual reasoning and cross-domain synthesis |
| API calls, status polling, JSON parsing, manifest loading | Fast/efficient (e.g. Haiku) | Deterministic, low-reasoning work — cost optimization opportunity |
| Domain classification, bundle suggestion, promotion hints | Balanced (e.g. Sonnet) | Moderate reasoning; runs once per drift item so model selection has high leverage |

This mirrors the sub-agent pattern already used inside Distill, and positions the task to benefit immediately from **prompt caching** when that becomes available — the shape manifest is cached as a system-prompt prefix, with only the variable metadata summary and Distill feature list processed fresh per run (estimated 80% cost reduction at scale).

### 6.2 Task Options

```yaml
# In cumulusci.yml under tasks.capture_org_customizations
options:
  distill_api_url:
    description: >
      Base URL for Distill API server (e.g. http://localhost:8000).
      If not set, the task skips gracefully. Set in local.cumulusci.yml
      or CI environment to enable.
    required: false
    default: null

  distill_project_id:
    description: >
      UUID of the pre-configured Distill project to use for analysis.
      Create via Distill CLI: ./distill start → /configure
      Run: cci task info capture_org_customizations to see current value.
    required: false
    default: null

  distill_domain:
    description: Domain hint for Distill analysis context.
    required: false
    default: "revenue-cloud"

  metadata_path:
    description: >
      Path to retrieved org metadata (relative to project root).
      Run 'sf project retrieve start --output-dir retrieved/' first.
    required: false
    default: "retrieved/"

  baseline_manifest_path:
    description: Path to the qb/en-US baseline manifest JSON file.
    required: false
    default: "datasets/sfdmu/qb/en-US/baseline_manifest.json"

  output_path:
    description: Where to write the drift report JSON.
    required: false
    default: "output/distill_drift_report.json"

  analysis_mode:
    description: "Distill analysis depth: 'fast' or 'thorough'."
    required: false
    default: "fast"

  poll_interval_seconds:
    description: Seconds between status polls while waiting for Distill.
    required: false
    default: 5

  timeout_seconds:
    description: Maximum seconds to wait for Distill analysis to complete.
    required: false
    default: 300

  data_shape:
    description: >
      Which data shape to target for baseline manifest comparison (e.g. 'qb', 'q3', 'mfg').
      Determines which shape_manifest.json is loaded from
      datasets/sfdmu/<data_shape>/en-US/shape_manifest.json.
      Defaults to 'qb' (the only shape with a complete v5 manifest).
    required: false
    default: "qb"

  active_flags:
    description: >
      Comma-separated list of active CCI feature flags for this org
      (e.g. 'billing,tax,dro,rating'). Used to scope drift detection
      to only those objects introduced by the enabled flags.
      When null, all objects in the shape manifest are included.
      Matches flag names from the manifest's feature_matrix section.
    required: false
    default: null
```

### 6.3 Task Logic (Pseudocode)

```python
class DistillCaptureDrift(BaseTask):

    def _run(self):
        # ── Guard: Distill configured? ──────────────────────────────────
        api_url = self.options.get("distill_api_url")
        if not api_url:
            self.logger.warning(
                "⏭  Distill capture skipped: distill_api_url not configured.\n"
                "   To enable, add distill_api_url to task options or local.cumulusci.yml."
            )
            return

        # ── Guard: Distill reachable? ────────────────────────────────────
        if not self._health_check(api_url):
            self.logger.warning(f"⏭  Distill capture skipped: API at {api_url} not reachable.")
            return

        # ── Guard: Metadata path exists? ────────────────────────────────
        metadata_path = Path(self.options.get("metadata_path", "retrieved/"))
        if not metadata_path.exists():
            self.logger.warning(
                f"⏭  Distill capture skipped: {metadata_path} not found.\n"
                "   Run 'sf project retrieve start --output-dir retrieved/' first."
            )
            return

        # ── Guard: Baseline manifest exists? ────────────────────────────
        manifest_path = Path(self.options.get("baseline_manifest_path"))
        if not manifest_path.exists():
            self.logger.warning(
                f"⏭  Distill capture skipped: {manifest_path} not found.\n"
                "   Run 'cci task run generate_baseline_manifest' first."
            )
            return

        # ── Core workflow ────────────────────────────────────────────────
        try:
            project_id  = self._resolve_project_id(api_url)
            _           = self._run_analysis(api_url, project_id, str(metadata_path))
            features    = self._poll_until_complete(api_url, project_id)
            baseline    = self._load_baseline(manifest_path)
            drift       = self._compute_drift(features, baseline)
            self._write_report(drift)
            self._log_summary(drift)

        except Exception as e:
            self.logger.warning(f"⏭  Distill capture failed with error: {e}\n"
                                "   This is non-blocking — main flow will continue.")

    # ── Helpers ──────────────────────────────────────────────────────────

    def _health_check(self, api_url) -> bool:
        resp = requests.get(f"{api_url}/health", timeout=5)
        return resp.ok and resp.json().get("status") == "ok"

    def _resolve_project_id(self, api_url) -> str:
        """Use configured project_id, or find by domain in project list."""
        project_id = self.options.get("distill_project_id")
        if project_id:
            return project_id
        # Fall back to active workspace
        workspace = requests.get(f"{api_url}/api/workspace/active").json()
        if workspace.get("active_project_id"):
            return workspace["active_project_id"]
        raise ValueError(
            "No distill_project_id configured and no active Distill workspace found.\n"
            "Run: ./distill start → /configure to create a project."
        )

    def _run_analysis(self, api_url, project_id, source_path):
        resp = requests.post(f"{api_url}/api/analysis/run", json={
            "project_id": project_id,
            "source_path": source_path,
            "repo_type": "Source"
        })
        resp.raise_for_status()
        return resp.json()

    def _poll_until_complete(self, api_url, project_id) -> list:
        mode     = self.options.get("analysis_mode", "fast")
        interval = int(self.options.get("poll_interval_seconds", 5))
        timeout  = int(self.options.get("timeout_seconds", 300))
        elapsed  = 0

        while elapsed < timeout:
            summary = requests.get(
                f"{api_url}/api/analysis/{project_id}/summary",
                params={"mode": mode}
            ).json()

            if summary.get("total_features", 0) > 0:
                self.logger.info(f"   Distill analysis complete: "
                                 f"{summary['total_features']} features, "
                                 f"{summary['total_artifacts']} artifacts")
                break

            time.sleep(interval)
            elapsed += interval
        else:
            raise TimeoutError(f"Distill analysis timed out after {timeout}s")

        features = requests.get(
            f"{api_url}/api/analysis/{project_id}/features",
            params={"mode": mode}
        ).json()
        return features

    def _compute_drift(self, features: list, baseline: dict) -> dict:
        """
        Compare Distill's feature inventory against the baseline manifest.
        Returns a structured drift report.
        """
        baseline_objects = set(baseline["object_index"].keys())
        baseline_fields  = {
            obj: set(data["all_fields"])
            for obj, data in baseline["object_index"].items()
        }

        new_entities     = []
        extended_entities = []
        new_features     = []
        new_artifacts    = []

        for feature in features:
            # Check entities (SObjects) referenced by this feature
            for entity in feature.get("entities", []):
                if entity not in baseline_objects:
                    new_entities.append({
                        "entity": entity,
                        "feature": feature["name"],
                        "operations": feature["operations"]
                    })
                # (Field-level diff would require DataMapper integration - Phase 2)

            # Classify the feature by proximity to known plan domains
            domain = self._classify_domain(feature, baseline)
            new_features.append({
                "feature_id":   feature["business_feature_id"],
                "name":         feature["name"],
                "description":  feature["description"],
                "entities":     feature["entities"],
                "operations":   feature["operations"],
                "files":        feature["files"],
                "ui_components": feature["ui_components"],
                "inferred_domain": domain,
                "suggested_bundle": self._suggest_bundle(domain),
                "promotion_hint": self._promotion_hint(feature, domain)
            })

        return {
            "generated_at":       datetime.utcnow().isoformat(),
            "org_alias":          self.org_config.name,
            "distill_project_id": self.options.get("distill_project_id"),
            "analysis_mode":      self.options.get("analysis_mode", "fast"),
            "baseline_version":   baseline["version"],
            "summary": {
                "total_features_detected": len(features),
                "new_entities":           len(new_entities),
                "total_drift_items":      len(new_features)
            },
            "new_entities":   new_entities,
            "features":       new_features
        }

    def _classify_domain(self, feature, baseline) -> str:
        """Map a Distill feature to the closest Revenue Cloud Foundations domain."""
        DOMAIN_ENTITY_MAP = {
            "pcm":      {"Product2", "ProductCatalog", "ProductCategory",
                          "ProductClassification", "ProductRelatedComponent"},
            "pricing":  {"PricebookEntry", "PriceAdjustmentSchedule",
                          "PriceAdjustmentTier", "Pricebook2"},
            "billing":  {"BillingPolicy", "BillingTreatment", "LegalEntity",
                          "PaymentTerm", "GeneralLedgerAccount"},
            "tax":      {"TaxPolicy", "TaxTreatment", "TaxEngine"},
            "dro":      {"FulfillmentStepDefinition", "ProductFulfillmentScenario",
                          "FulfillmentStepDefinitionGroup"},
            "rating":   {"UsageResource", "RatingFrequencyPolicy",
                          "ProductUsageResource"},
            "rates":    {"RateCard", "RateCardEntry", "RateAdjustmentByTier"},
        }
        entities = set(feature.get("entities", []))
        scores = {domain: len(entities & domain_entities)
                  for domain, domain_entities in DOMAIN_ENTITY_MAP.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "unknown"

    def _suggest_bundle(self, domain) -> str:
        BUNDLE_MAP = {
            "pcm":     "unpackaged/post_quantumbit",
            "pricing": "unpackaged/post_quantumbit",
            "billing": "unpackaged/post_billing",
            "tax":     "unpackaged/post_quantumbit",
            "dro":     "unpackaged/post_quantumbit",
            "rating":  "unpackaged/post_quantumbit",
            "rates":   "unpackaged/post_quantumbit",
        }
        return BUNDLE_MAP.get(domain, "force-app/main/default")

    def _promotion_hint(self, feature, domain) -> str:
        """Generate a human-readable promotion hint."""
        ops = feature.get("operations", [])
        files = feature.get("files", [])
        if any(f.endswith(".cls") for f in files):
            return "Contains Apex — review for promotion to force-app/main/default/classes/"
        if any(f.endswith(".flow-meta.xml") for f in files):
            return f"Contains Flow — review for promotion to {self._suggest_bundle(domain)}"
        if feature.get("ui_components"):
            return "Contains LWC/UI component — review for promotion to force-app/main/default/lwc/"
        return "Review manually"
```

### 6.4 Drift Report Output Schema

**File:** `output/distill_drift_report.json`

```json
{
  "generated_at": "2026-02-27T14:30:00Z",
  "org_alias": "dev",
  "distill_project_id": "<uuid>",
  "analysis_mode": "fast",
  "baseline_version": "1.0.0",

  "summary": {
    "total_features_detected": 12,
    "new_entities": 3,
    "total_drift_items": 7
  },

  "new_entities": [
    {
      "entity": "CustomBillingRule__c",
      "feature": "Custom Billing Override",
      "operations": ["C", "U"]
    }
  ],

  "features": [
    {
      "feature_id": "feat-abc123",
      "name": "Custom Product Bundling Logic",
      "description": "Apex-driven bundle validation extending standard PCM behaviour",
      "entities": ["Product2", "ProductRelatedComponent"],
      "operations": ["R", "U"],
      "files": ["force-app/main/default/classes/BundleValidator.cls"],
      "ui_components": [],
      "inferred_domain": "pcm",
      "suggested_bundle": "unpackaged/post_quantumbit",
      "promotion_hint": "Contains Apex — review for promotion to force-app/main/default/classes/"
    }
  ]
}
```

---

## 7. CumulusCI Configuration

### 7.1 cumulusci.yml Additions

```yaml
# ── Feature flags ──────────────────────────────────────────────────────────
project:
  custom:
    # ... existing flags ...
    distill_enabled: false   # Set to true in local.cumulusci.yml if Distill is available

# ── Tasks ─────────────────────────────────────────────────────────────────
tasks:
  generate_baseline_manifest:
    description: >
      Regenerate the qb/en-US baseline manifest from export.json files.
      Run after any data plan update.
    class_path: tasks.rlm_generate_baseline_manifest.GenerateBaselineManifest
    options:
      scope: "qb/en-US"
      output_path: "datasets/sfdmu/qb/en-US/baseline_manifest.json"

  capture_org_customizations:
    description: >
      [OPTIONAL] Analyze org customizations against the qb/en-US baseline using
      Distill AI. Requires Distill API server running and distill_api_url configured.
      Gracefully skips if Distill is not available.
    class_path: tasks.rlm_distill_capture.DistillCaptureDrift
    options:
      distill_api_url: null                 # Override in local.cumulusci.yml
      distill_project_id: null              # Override with your Distill project UUID
      metadata_path: "retrieved/"
      baseline_manifest_path: "datasets/sfdmu/qb/en-US/baseline_manifest.json"
      output_path: "output/distill_drift_report.json"
      analysis_mode: "fast"
      poll_interval_seconds: 5
      timeout_seconds: 300

# ── Flows ──────────────────────────────────────────────────────────────────
flows:
  analyze_org_drift:
    description: >
      Retrieve org metadata and run Distill customization analysis.
      Requires: sf CLI authenticated to target org, Distill API running.
      Produces: output/distill_drift_report.json
    steps:
      1:
        task: retrieve_changes
        description: "Pull current org metadata to retrieved/"
      2:
        task: capture_org_customizations
        description: "Analyze drift against qb/en-US baseline (optional - skips if Distill unavailable)"
```

### 7.2 Local Override (Not Committed)

Users with Distill access add to `local.cumulusci.yml` (gitignored):

```yaml
tasks:
  capture_org_customizations:
    options:
      distill_api_url: "http://localhost:8000"
      distill_project_id: "<your-distill-project-uuid>"
```

### 7.3 CI/CD (Optional)

```yaml
# .github/workflows/analyze-drift.yml (future)
env:
  DISTILL_API_URL: ${{ secrets.DISTILL_API_URL }}
  DISTILL_PROJECT_ID: ${{ secrets.DISTILL_PROJECT_ID }}
```

---

## 8. Implementation Roadmap

> **How this roadmap is structured:** Phases 0–2 are buildable today using what's currently available in both Foundations and Distill. Phase 3 is a focused spike to validate whether Distill's existing `insights/` module can be invoked headlessly from CCI. Phase 4 delivers the full automated drift detection pipeline, gated on Phase 3 success. Phase 5 is forward-looking. Phase gates are noted explicitly.
>
> **Key architectural decision (validated via Opus judgment-call review):** CCI integration uses **direct Python package imports** — not subprocess invocation of `./distill start`, not HTTP calls to a REST API. This eliminates two false gates from the original roadmap: (1) agent registration (CCI calls the service layer directly, bypassing the agent/controller layer), and (2) REST API availability (CCI runs in-process, not over HTTP). The critical remaining gate is whether `distill.insights.api` can be initialized and invoked headlessly — this is the Phase 3 spike.

---

### Phase 0: Datasets Reorganization *(No Distill dependency)*

> **Full proposal and migration steps:** [datasets-reorganization.md](datasets-reorganization.md)
>
> Parallelizable with Phase 1 and 2. The manifest paths (`datasets/sfdmu/qb/en-US/shape_manifest.json`) and `shapes.json` registry depend on the reorganized structure, but Phase 1–2 work can use current paths during development.

| # | Task | Owner | Status |
|---|---|---|---|
| 0.1 | Review and approve [datasets-reorganization.md](datasets-reorganization.md) | | 🔲 TODO |
| 0.2 | Execute folder restructure per migration script in that doc | | 🔲 TODO |
| 0.3 | Update path defaults in `tasks/rlm_cml.py` (`import_cml`, `export_cml`, `validate_cml`) | | 🔲 TODO |
| 0.4 | Update `cumulusci.yml` option defaults for `insert_scratch_data` and `insert_procedure_plans_data` | | 🔲 TODO |
| 0.5 | Create initial `datasets/shapes.json` registry (4 shapes: qb-en-US active, qb-ja partial, q3-en-US pending, mfg-en-US draft) | | 🔲 TODO |
| 0.6 | Verify all existing CCI flows pass with updated paths (`prepare_rlm_org` smoke test) | | 🔲 TODO |

---

### Phase 1: CodeSuggestion Integration — Apex Translation *(Available now)*

> **Distill requirement:** `CodeSuggestionAgent` — ✅ implemented.
> **Additional prerequisite:** `GEMINI_API_KEY` — required because `run_file_migration` is hardcoded to Gemini (see LLM note below).
>
> This phase delivers the first live integration point: an engineer who has identified an Apex customization worth promoting can invoke Distill's CodeSuggestion agent from a Foundations CCI task to translate that file for the target org structure. This is **engineer-triggered**, not automated — the drift detection step is still manual at this phase.
>
> **Scope: translation only, no automated deployment.** The CCI task calls `run_file_migration`, captures the migrated code, and writes it to a local output directory. The engineer reviews the output and merges manually into `force-app/` or an `unpackaged/post_*` bundle. `DeploymentAgent` is out of scope for CCI integration — it requires Claude Code built-in tools that only exist inside a Claude Code session.
>
> **How it works:** A CCI Python task imports `run_file_migration` directly from Distill's Python package (`from distill.codesuggestion.api import run_file_migration`). The task passes a `.cls` or `.trigger` file path and captures the migrated code output.
>
> **Why not subprocess?** `./distill start` is an interactive, menu-driven CLI that cannot be driven non-interactively. Direct Python import integrates cleanly with CumulusCI's Python task system.
>
> **LLM note:** `run_file_migration` internally routes through **Gemini** (hardcoded), not Claude. The `llm_provider` config field exists but `migration_tools.py` explicitly logs `"⚠️ Anthropic/Claude Vertex DISABLED - Gemini is HARDCODED for all migrations"`. The integration plumbing is model-agnostic — when the Distill team re-enables Claude, the CCI task requires zero changes. Until then, a valid `GEMINI_API_KEY` is required.

| # | Task | Owner | Status |
|---|---|---|---|
| 1.1 | Write `tasks/rlm_distill_migrate.py` — CCI Python task that imports `distill.codesuggestion.api.run_file_migration` directly (Python package import, not subprocess) | | 🔲 TODO |
| 1.2 | Add `migrate_apex_customization` task to `cumulusci.yml` with `file_path` and `output_dir` options | | 🔲 TODO |
| 1.3 | Add guard logic: Distill package installed? `GEMINI_API_KEY` set? File path valid? File is `.cls` or `.trigger`? | | 🔲 TODO |
| 1.4 | Test with a real Apex class from a customized qb/en-US dev org | | 🔲 TODO |
| 1.5 | Document the engineer-triggered promote workflow (retrieve → identify → translate → review → merge) — note: translation only, no automated deployment | | 🔲 TODO |

---

### Phase 2: Shape Manifest + CCI Scaffold *(Available now — pre-wires Phase 4)*

> **Distill requirement:** None — this phase is entirely on the Foundations side. **Highest-priority Foundations-only deliverable** — the shape manifest is the architectural foundation that all subsequent drift detection builds on.
>
> Build the shape manifest and the `capture_org_customizations` task skeleton with full guard logic. The task will be wired to call Distill's `insights/` module via direct Python import in Phase 4 — for now it validates its inputs and produces a stub report. This lets the full workflow be tested end-to-end without a live Distill connection, and establishes the drift report schema that Phase 4 will populate.
>
> **Minimal viable demo path (Phases 0–2 only, no Distill API required):**
> 1. Run `generate_baseline_manifest` against `datasets/sfdmu/qb/en-US/`
> 2. Run `capture_org_customizations` against a customized dev org
> 3. Show `output/distill_drift_report.json` — stub structure with guard logic and schema validated

| # | Task | Owner | Status |
|---|---|---|---|
| 2.1 | Write `scripts/generate_baseline_manifest.py` — reads SFDMU plans, generates `shape_manifest.json` | | 🔲 TODO |
| 2.2 | Generate and commit `datasets/sfdmu/qb/en-US/shape_manifest.json` | | 🔲 TODO |
| 2.3 | Add `generate_baseline_manifest` CCI task | | 🔲 TODO |
| 2.4 | Write `tasks/rlm_distill_capture.py` — full guard logic, `drift_report.json` schema, stub Distill call | | 🔲 TODO |
| 2.5 | Add `capture_org_customizations` and `analyze_org_drift` to `cumulusci.yml` | | 🔲 TODO |
| 2.6 | Test graceful skip when Distill not configured | | 🔲 TODO |
| 2.7 | Register `shape_manifest.json` as a prompt-cache candidate once caching infrastructure is available | | 🔲 TODO |

---

### Phase 3: Insights API Spike — Headless Validation *(Available now — focused exploration)*

> **Distill requirement:** Access to `sf-industries/distill` repo + ability to install the package.
>
> **What this phase validates:** Can `distill.insights.api` (or `distill.insights.pipeline`) be imported and invoked from a standalone Python process — without the interactive CLI, TUI, or Claude Code session?
>
> **Why this is the critical path question:** The `insights/` module exists in the Distill repo with `api.py`, `pipeline.py`, and a full pipeline directory structure (`capabilities/`, `features/`, `flows/`, `graph/`, `ingestion/`, `parsing/`, `reporting/`, `verification/`). `enable_insights: true` is set in `base.yaml`. The `/insights [fast|thorough]` slash command runs the pipeline today through the CLI. If this pipeline can be called headlessly, Phases 3+4 of the original roadmap collapse into a single implementation phase — no agent registration needed, no REST API needed. CCI calls the service layer directly, consistent with the Phase 1 pattern.
>
> **Module architecture hypothesis (to confirm with Distill team):** `insights/` is the pipeline orchestrator (ingest → parse → extract features → build graph → report). `analysis/` provides LLM-powered analysis capabilities that `insights/` invokes at specific stages. They are complementary, not competing implementations. `insights/api.py` is the integration target.
>
> **Spike success criteria:** A standalone Python script (no CLI, no TUI) successfully runs `distill.insights.api` against a test metadata directory and produces a feature inventory as structured output (JSON or equivalent).
>
> **Spike failure path:** If headless invocation requires Distill runtime context that cannot be bootstrapped from CCI (e.g., event bus, plugin system, active database session), document the specific blockers and coordinate with Distill team on exposing a lightweight headless API.

| # | Task | Owner | Status |
|---|---|---|---|
| 3.1 | Coordinate with Distill team: confirm `insights/` vs `analysis/` module relationship — is `analysis/` consumed by `insights/` or a parallel implementation? | | 🔲 TODO |
| 3.2 | Identify `distill.insights.api` entry points and required initialization (config loading, DB setup, event bus, LLM client) | | 🔲 TODO |
| 3.3 | Write a standalone Python script that imports and calls `distill.insights.api` with a test metadata directory — no CLI, no TUI, no Claude Code | | 🔲 TODO |
| 3.4 | Document: what Distill runtime dependencies must be initialized? Can they be bootstrapped from a CCI task context? | | 🔲 TODO |
| 3.5 | If spike succeeds: define stable API contract for CCI consumption (input: directory path + config, output: feature inventory JSON) | | 🔲 TODO |
| 3.6 | If spike fails: document blockers, propose minimal changes to Distill to enable headless API, coordinate with Distill team | | 🔲 TODO |

---

### Phase 4: Automated Drift Detection *(Gated on Phase 3 spike success)*

> **Gate:** Phase 3 spike confirms that `distill.insights.api` can be invoked headlessly from a CCI Python task. If the spike failed, this phase is blocked until the Distill team exposes a headless API (see Phase 3 task 3.6).
>
> **What changed from the original roadmap:** The original Phase 4 was gated on `AnalysisAgent` registration + REST API (Web mode). Neither gate is required for CCI integration:
> - **Agent registration:** CCI imports the service layer (`distill.insights.api`) directly, bypassing the agent/controller layer. This is the same pattern used in Phase 1 (`distill.codesuggestion.api`).
> - **REST API:** CCI runs in-process via Python import, not over HTTP. The REST API is useful for external consumers (dashboards, CI/CD services) but is not on the critical path for the CCI integration.
>
> This is the full round-trip workflow designed in §3. The CCI task `capture_org_customizations` calls `distill.insights.api` (per the contract established in Phase 3), diffs the results against `shape_manifest.json`, and produces `distill_drift_report.json` with domain classification and promotion hints.
>
> The Phase 2 task skeleton and guard logic slot directly into this phase — the stub Distill call is replaced with the real `insights/` API call.

| # | Task | Owner | Status |
|---|---|---|---|
| 4.1 | Wire `distill.insights.api` into `capture_org_customizations` — replace stub call with real insights pipeline invocation (per Phase 3 contract) | | 🔲 TODO |
| 4.2 | Define `sf project retrieve start` filter — likely `ApexClass,Flow,LightningComponentBundle,CustomObject` — scoped to what insights pipeline analyzes | | 🔲 TODO |
| 4.3 | Implement diff logic: insights feature inventory vs `shape_manifest.json` | | 🔲 TODO |
| 4.4 | Populate `drift_report.json` with new entities, features, domain classification, promotion hints | | 🔲 TODO |
| 4.5 | Handle Distill project context initialization from CCI (may require programmatic project creation or pre-configuration) | | 🔲 TODO |
| 4.6 | Test full round-trip: retrieve → insights API → diff → report | | 🔲 TODO |

---

### Phase 5: Field-Level Drift + Cross-Platform Integration *(Future)*

> **Distill requirement:** DataMapper automation API (currently interactive-only) + stable `insights/` API from Phase 4.

| # | Task | Owner | Status |
|---|---|---|---|
| 5.1 | Run DataMapper programmatically against retrieved metadata for field-level drift detection | | 🔲 TODO |
| 5.2 | Extend drift report with per-object field additions and SFDMU export.json suggestions | | 🔲 TODO |
| 5.3 | Include context definition XML in retrieved metadata; diff against `force-app/main/default/contextDefinitions/` | | 🔲 TODO |
| 5.4 | Evaluate `shapes.json` as a cross-platform contract for Aegis test-scenario selection (see O9) | | 🔲 TODO |
| 5.5 | Register `shape_manifest.json` prompt-cache once caching infrastructure is confirmed | | 🔲 TODO |

---

## 9. Open Questions & Decisions

### 9.1 Resolved Decisions

| # | Question | Status | Decision |
|---|---|---|---|
| R1 | One manifest per plan or one per shape? | ✅ Resolved | **Per shape/locale.** Multiple plans share objects; a per-plan manifest would create duplication and couldn't express cross-plan feature flag relationships. |
| R2 | Where does the manifest live with multiple shapes? | ✅ Resolved | `datasets/sfdmu/<shape>/<locale>/shape_manifest.json` (e.g. `qb/en-US/shape_manifest.json`). Top-level `datasets/shapes.json` is the registry. |
| R3 | How do feature flag combinations affect the manifest? | ✅ Resolved | `feature_matrix` block in the manifest maps each CCI flag to the objects it introduces. `capture_org_customizations` accepts `active_flags` option to scope the diff. |
| R4 | How do Distill-generated new shapes slot in? | ✅ Resolved | New shape folder under `sfdmu/<shape-name>/en-US/`, `shape_manifest.json` generated with `"source": "distill"`, registered in `shapes.json` with `"status": "draft"`. No special-casing required. |
| R5 | Where do QB CML constraint models live? | ✅ Resolved | Move `datasets/constraints/qb/` → `datasets/sfdmu/qb/en-US/constraints/`. Shape self-contained. See [datasets-reorganization.md](datasets-reorganization.md). |
| R6 | Where do `procedure-plans` and `scratch_data` live? | ✅ Resolved | `datasets/sfdmu/_shared/procedure-plans/` and `datasets/sfdmu/_shared/scratch_data/`. Both are multi-shape by nature. |
| R7 | Is the integration mandatory? | ✅ Resolved | **No — optional and non-blocking.** `capture_org_customizations` guards on `distill_api_url`, API reachability, metadata path, and manifest existence. All failures log a warning and return cleanly. |
| R8 | Which data shapes are in scope for Phase 1? | ✅ Resolved | **`qb/en-US` only.** Q3 and MFG are excluded until they are updated for SFDMU v5 composite key patterns. |

### 9.2 Open Questions

| # | Question | Status | Notes |
|---|---|---|---|
| O1 | Should `analyze_org_drift` be a sub-step of `prepare_rlm_org` or always a standalone flow? | Open | Standalone is safer (optional by design); sub-step would require wrapping in a `when:` condition. |
| O2 | Should the drift report be human-readable (Markdown) in addition to JSON? | Open | A Markdown summary table would make it easier to review in PRs. Low effort — `_write_report()` could emit both. |
| O3 | Which `sf project retrieve start` filter to use? | Open | Likely: `--metadata "ApexClass,Flow,LightningComponentBundle,CustomObject"` — scoped to what Distill's Insights engine analyzes. Full org retrieve is noisy. |
| O4 | How to handle multi-currency (q3) plans once updated for SFDMU v5? | Deferred | Phase 3+. Requires completing v5 migration of q3/en-US plans first. When ready: add `q3` entry to `shapes.json` and set status to `active`. |
| O5 | Should `generate_baseline_manifest` run as a pre-commit hook? | Open | Would ensure manifest is never stale. Risk: slow commit for minor changes. Alternative: document as a manual step after plan updates. |
| O6 | Does Distill `repo_type: "Source"` vs `"Target"` affect output for the drift use case? | Needs testing | Hypothesis: use `"Source"` for org-state snapshots (retrieved metadata looks like a source project). Needs an end-to-end test run to confirm. |
| O7 | Should `generate_baseline_manifest` automatically update `shapes.json` when a new shape manifest is created? | Open | Natural fit — the script already knows the shape name and locale. Would keep `shapes.json` as a derived artifact rather than manually maintained. |
| O8 | How should `active_flags` be passed in CI scenarios? | Open | Options: (a) hardcoded in `cumulusci.yml` per environment, (b) env var mapped in CI YAML, (c) read from a `shapes.json` `"default_flags"` field. |
| O9 | Should `shapes.json` become the shared protocol for Aegis test-scenario selection as well as Distill drift detection? | Open | If Aegis consumes `shapes.json` to determine which test scenarios are applicable for a given data shape and flag combination, the manifest becomes a true cross-platform contract rather than a Distill-specific artifact. This would make the manifest format a foundational design decision that should be finalized before Phase 5. |
| O10 | What is the correct open-source/IP sequencing for this platform? | Open | The workflow (feature-flag-aware manifest generation + AI drift detection + Promote/Overlay/Discard classification) may be patentable. Legal review and patent filing — if pursued — must precede any open-source publication. Internal distribution (sfLabs) may be possible before external publication depending on licensing strategy. |
| O11 | Should Phase 1 wait for Claude re-enablement in `run_file_migration`, or proceed with Gemini dependency? | Resolved | **Proceed with Gemini.** The integration plumbing is model-agnostic — when Distill re-enables Claude, the CCI task requires zero changes. `GEMINI_API_KEY` is a documented prerequisite. The hardcode reads as a workaround (`"DISABLED"`), not a permanent design choice. |
| O12 | What is the initialization sequence for `distill.insights.api` in headless mode? | Phase 3 spike | Core question for the Phase 3 spike: does `insights/api.py` require the full Distill runtime (event bus, plugin system, active DB session), or can it be bootstrapped with minimal config? The answer determines whether Phase 4 is a 2-week implementation or requires Distill-side changes first. |
| O13 | Are `insights/` and `analysis/` complementary pipeline stages or parallel implementations? | Phase 3 spike | Architectural hypothesis: `insights/` is the pipeline orchestrator; `analysis/` provides LLM-powered analysis at specific stages. Confirm with Distill team in Phase 3. If parallel implementations, determine which is the "blessed" integration target. |
