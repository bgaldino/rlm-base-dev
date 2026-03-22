# Datasets Folder Reorganization Proposal

> **Document Type:** Standalone Proposal
> **Status:** Draft — Awaiting Approval
> **Branch:** `distill-integration`
> **Last Updated:** 2026-02-27
> **Part of:** [Revenue Cloud Engineering Platform](revenue-cloud-platform.md)
> **Prerequisite for:** [distill-integration.md](distill-integration.md) — shape manifest generation requires this structure

---

## Table of Contents

1. [Purpose & Goals](#1-purpose--goals)
2. [Current State Analysis](#2-current-state-analysis)
3. [Classification Matrix](#3-classification-matrix)
4. [Proposed Structure](#4-proposed-structure)
5. [Decision Rationale — Per Folder](#5-decision-rationale--per-folder)
6. [Before / After Comparison](#6-before--after-comparison)
7. [CumulusCI Path Changes Required](#7-cumulusci-path-changes-required)
8. [Migration Steps](#8-migration-steps)
9. [Prerequisites for Shape Manifest Generation](#9-prerequisites-for-shape-manifest-generation)
10. [Risks & Mitigations](#10-risks--mitigations)
11. [Approval & Status](#11-approval--status)

---

## 1. Purpose & Goals

The current `datasets/` folder has accumulated structure organically as new shapes and plans were added. Several structural issues have emerged:

- **Constraints data is QB-specific but lives outside the QB shape folder**, making the QB shape not self-contained
- **Cross-shape plans (`procedure-plans`, `scratch_data`) have no designated home** — they sit as siblings of shape folders inside `sfdmu/`
- **Tooling/operational folders (`reconcile/`, `extractions/`, `test/`, `_archived/`) are mixed with production data**, creating ambiguity about what's reference material vs. working data
- **No registry** linking shape names, locale variants, feature flags, and their plan folders
- **No manifest files** describing each shape's object footprint (prerequisite for Distill integration)

**Goals of this reorganization:**
1. Make each data shape self-contained (SFDMU plans + constraints + shape manifest all co-located)
2. Give cross-shape plans a clear, designated home
3. Separate production data from tooling/operational data
4. Introduce a `shapes.json` registry as the single source of truth for shape discovery
5. Create a natural home for future Distill-generated shapes
6. Enable `shape_manifest.json` generation per shape/locale (prerequisite for [distill-integration.md](distill-integration.md))

**Out of scope:** This reorganization does NOT change:
- The content or structure of any `export.json` file
- Any SFDMU plan logic or composite key patterns
- CML blob files or constraint CSV content
- Context plan content
- The `cumulusci.yml` flow/task logic (only path options change)

---

## 2. Current State Analysis

### Full Inventory

```
datasets/
├── constraints/                        # CML data — QB-specific, but lives outside QB
│   ├── qb/
│   │   ├── QuantumBitComplete/         # 43 ESC records, 22 products, ESDV blob
│   │   │   ├── ExpressionSet.csv
│   │   │   ├── ExpressionSetConstraintObj.csv
│   │   │   ├── ExpressionSetDefinitionVersion.csv
│   │   │   ├── ExpressionSetDefinitionContextDefinition.csv
│   │   │   ├── Product2.csv
│   │   │   ├── ProductClassification.csv
│   │   │   ├── ProductRelatedComponent.csv
│   │   │   └── blobs/ESDV_QuantumBitComplete_V1.ffxblob
│   │   └── Server2/                    # 81 ESC records, 41 products, ESDV blob
│   │       └── (same CSV structure + ESDV_Server2_V1.ffxblob)
│   └── README.md                       # CML export/import/validate guide (417 lines)
│
├── context_plans/                      # Context definition manifests — cross-shape
│   ├── archive/                        # Deprecated context plans
│   │   ├── rlm_salestransaction.json
│   │   ├── rlm_salestransaction_update.json
│   │   └── manifest.json
│   ├── ConstraintEngineNodeStatus/     # Active: Constraint engine context mapping
│   │   ├── constraint_engine_node_status.json
│   │   └── manifest.json
│   └── contexts/                       # (empty, reserved for expansion)
│
├── dx/                                 # Minimal: tax treatment configs
│
└── sfdmu/
    ├── _archived/                      # Deprecated plans — TOOLING
    │
    ├── extractions/                    # Extraction run outputs — TOOLING
    │   └── qb-pcm/ (timestamped runs)
    │
    ├── test/                           # Test fixture data — TOOLING
    │
    ├── reconcile/                      # Round-trip validation snapshots — TOOLING
    │   ├── qb-extractdata/en-US/       # Extraction from source org
    │   │   ├── qb-billing/  qb-constraints-component/  qb-constraints-product/
    │   │   ├── qb-dro/      qb-pcm/   qb-pricing/      qb-product-images/
    │   │   ├── qb-rates/    qb-rating/ qb-tax/          qb-transactionprocessingtypes/
    │   └── qb-migrate/en-US/           # Migration target snapshots
    │
    ├── scratch_data/                   # Cross-shape: Account + Contact seed — NO HOME
    │   └── export.json                 # Upsert Account, Upsert Contact by Name
    │
    ├── procedure-plans/                # Cross-shape: Procedure plan sections — NO HOME
    │   └── export.json                 # 2-pass: ProcedurePlanSection + ProcedurePlanOption
    │
    ├── qb/                             # Shape: QuantumBit
    │   ├── en-US/                      # Locale: English US (13 plans, SFDMU v5)
    │   │   ├── qb-pcm/                 # 28 objects, 26 CSVs, 10 composite keys
    │   │   ├── qb-pricing/             # 16 objects, 15 CSVs, 8 composite keys
    │   │   ├── qb-billing/             # 11 objects, 3-pass, $$ notation
    │   │   ├── qb-tax/                 # 6 objects, 2-pass
    │   │   ├── qb-dro/                 # 13 objects, dynamic user resolution
    │   │   ├── qb-rating/              # 14 objects, 2-pass, $$ notation
    │   │   ├── qb-rates/               # 5 objects, deleteOldData
    │   │   ├── qb-product-images/      # 1 object, 2-pass, blobs
    │   │   ├── qb-transactionprocessingtypes/  # 1 object, Insert-only
    │   │   ├── qb-accounting/          # GL accounts — reference export
    │   │   ├── qb-clm/                 # Contract Lifecycle Management
    │   │   ├── qb-guidedselling/       # Guided selling, 2-pass
    │   │   ├── qb-constraints-component/  # Constraint export (no import CSVs)
    │   │   └── qb-constraints-exported/   # Constraint blob export
    │   └── ja/                         # Locale: Japanese (2 plans, SFDMU v5, partial coverage)
    │       ├── qb-pcm/                 # Same objects, simplified composite keys
    │       └── qb-pricing/             # Simplified variant
    │
    ├── q3/                             # Shape: Q3 Multi-Currency
    │   └── en-US/                      # Locale: English US (6 plans, SFDMU v4 — PENDING)
    │       ├── q3-billing/             ├── q3-dro/     ├── q3-multicurrency/ (40+ objects)
    │       ├── q3-rates/               ├── q3-rating/  └── q3-tax/
    │
    └── mfg/                            # Shape: Manufacturing
        └── en-US/                      # Locale: English US (4 plans, Draft)
            ├── mfg-configflow/         # ProductConfigurationFlow (2 objects)
            ├── mfg-constraints-p/      # MFG product constraints
            ├── mfg-constraints-prc/    # MFG PRC constraints
            └── mfg-multicurrency/      # MFG multi-currency
```

---

## 3. Classification Matrix

| Folder | Type | Self-Contained? | Notes |
|---|---|---|---|
| `sfdmu/qb/en-US/` | Shape-specific | **Partially** — missing constraints | SFDMU v5, active, 13 plans |
| `sfdmu/qb/ja/` | Shape + locale specific | **Partially** — 2 of 13 plans | SFDMU v5, partial coverage |
| `sfdmu/q3/en-US/` | Shape-specific | No | SFDMU v4, pending v5 migration |
| `sfdmu/mfg/en-US/` | Shape-specific | No | Draft, 4 plans |
| `constraints/qb/` | Shape-specific (QB) | No — orphaned from QB | Active CML data |
| `context_plans/` | Cross-shape | Yes | API-managed, not SFDMU |
| `sfdmu/procedure-plans/` | Cross-shape | Yes | 2-pass, shape-agnostic |
| `sfdmu/scratch_data/` | Cross-shape | Yes | Account + Contact only |
| `sfdmu/reconcile/` | Tooling | Yes | QB-specific validation snapshots |
| `sfdmu/extractions/` | Tooling | Yes | Dev extraction outputs |
| `sfdmu/test/` | Tooling | Yes | Test fixtures |
| `sfdmu/_archived/` | Tooling | Yes | Deprecated plans |
| `dx/` | Misc | Yes | Minimal, tax configs |

---

## 4. Proposed Structure

```
datasets/
├── shapes.json                             ← NEW: registry of all data shapes
│
├── context_plans/                          ← UNCHANGED location; internal cleanup only
│   ├── _shared/                            ← RENAMED from mixed root contents
│   │   └── ConstraintEngineNodeStatus/
│   └── _archive/                           ← RENAMED from archive/
│       ├── rlm_salestransaction.json
│       ├── rlm_salestransaction_update.json
│       └── manifest.json
│
├── dx/                                     ← UNCHANGED
│
└── sfdmu/
    │
    ├── _shared/                            ← NEW: cross-shape SFDMU plans
    │   ├── procedure-plans/                ← MOVED from sfdmu/procedure-plans/
    │   └── scratch_data/                   ← MOVED from sfdmu/scratch_data/
    │
    ├── _tooling/                           ← NEW: operational/dev data (not production)
    │   ├── _archived/                      ← MOVED from sfdmu/_archived/
    │   ├── extractions/                    ← MOVED from sfdmu/extractions/
    │   ├── reconcile/                      ← MOVED from sfdmu/reconcile/
    │   └── test/                           ← MOVED from sfdmu/test/
    │
    ├── qb/
    │   ├── en-US/
    │   │   ├── shape_manifest.json         ← NEW: generated by generate_baseline_manifest task
    │   │   ├── constraints/                ← MOVED from datasets/constraints/qb/
    │   │   │   ├── README.md               ← MOVED (was datasets/constraints/README.md)
    │   │   │   ├── QuantumBitComplete/
    │   │   │   │   ├── *.csv (7 files)
    │   │   │   │   └── blobs/ESDV_QuantumBitComplete_V1.ffxblob
    │   │   │   └── Server2/
    │   │   │       ├── *.csv (7 files)
    │   │   │       └── blobs/ESDV_Server2_V1.ffxblob
    │   │   ├── qb-pcm/
    │   │   ├── qb-pricing/
    │   │   ├── qb-billing/
    │   │   ├── qb-tax/
    │   │   ├── qb-dro/
    │   │   ├── qb-rating/
    │   │   ├── qb-rates/
    │   │   ├── qb-product-images/
    │   │   ├── qb-transactionprocessingtypes/
    │   │   ├── qb-accounting/
    │   │   ├── qb-clm/
    │   │   ├── qb-guidedselling/
    │   │   ├── qb-constraints-component/
    │   │   └── qb-constraints-exported/
    │   └── ja/
    │       ├── shape_manifest.json         ← NEW (status: partial)
    │       ├── qb-pcm/
    │       └── qb-pricing/
    │
    ├── q3/
    │   └── en-US/
    │       ├── shape_manifest.json         ← NEW (status: pending — v4, not generated yet)
    │       ├── q3-billing/
    │       ├── q3-dro/
    │       ├── q3-multicurrency/
    │       ├── q3-rates/
    │       ├── q3-rating/
    │       └── q3-tax/
    │
    └── mfg/
        └── en-US/
            ├── shape_manifest.json         ← NEW (status: draft)
            ├── constraints/                ← NEW: placeholder for future MFG CML data
            ├── mfg-configflow/
            ├── mfg-constraints-p/
            ├── mfg-constraints-prc/
            └── mfg-multicurrency/
```

---

## 5. Decision Rationale — Per Folder

### `constraints/qb/` → `sfdmu/qb/en-US/constraints/`

**Reason:** CML data is QB-shape-specific — `QuantumBitComplete` and `Server2` are expression set models built for the QuantumBit product catalog. They have no meaning outside of a QB org. Moving them inside the QB shape folder makes the shape self-contained: everything needed to fully reconstruct a QB org lives in one folder tree. The `rlm_cml.py` task already accepts a configurable path — this is a one-line default change.

When MFG develops CML data, it goes in `sfdmu/mfg/en-US/constraints/`. This pattern is now consistent.

### `procedure-plans/` + `scratch_data/` → `sfdmu/_shared/`

**Reason:** Both are shape-agnostic. `procedure-plans` contains metadata (ProcedurePlanSection + ProcedurePlanOption) that applies regardless of whether you're running QB, Q3, or MFG. `scratch_data` is generic Account + Contact seed data. The underscore prefix signals "not a shape folder." Any future shape that needs procedure plans references `_shared/procedure-plans/` — no duplication.

### `reconcile/`, `extractions/`, `test/`, `_archived/` → `sfdmu/_tooling/`

**Reason:** These are not production data — they are development and validation infrastructure. `reconcile/` contains round-trip validation snapshots. `extractions/` contains point-in-time extraction outputs. `test/` contains fixture data. None of these should be deployed to an org or referenced by production flows. Grouping under `_tooling/` makes the distinction explicit. CCI production flows will never reference `_tooling/`.

### `context_plans/` — stays at `datasets/` level

**Reason:** Context definitions are managed through the Context Service API, not SFDMU. They are a different data type entirely, managed by `rlm_context_service.py` and `rlm_extend_stdctx.py`. They are genuinely cross-shape — `ConstraintEngineNodeStatus` applies to any Revenue Cloud org regardless of product model. Pulling them into a shape folder would be incorrect. Internal cleanup: rename `archive/` → `_archive/` and create `_shared/` for the active plans.

### `shape_manifest.json` — added to each locale folder

**Reason:** One manifest per shape/locale, covering all plans in that folder. Generated by `generate_baseline_manifest` CCI task from the existing `export.json` files. Committed to git and updated whenever data plans change. Status values: `active` (ready), `partial` (incomplete coverage, like `qb/ja`), `pending` (needs v5 migration, like `q3/en-US`), `draft` (in development, like `mfg/en-US`). Distill integration depends on these manifests for drift detection.

### `shapes.json` — new at `datasets/` level

**Reason:** A single registry that answers: what shapes exist, what flags activate them, what locale variants are available, and which ones are ready for manifest generation. Consumed by the `capture_org_customizations` task and the `generate_baseline_manifest` task. Also serves as documentation for anyone trying to understand the data plan landscape.

---

## 6. Before / After Comparison

| Item | Before | After | Type |
|---|---|---|---|
| QB CML data | `datasets/constraints/qb/QuantumBitComplete/` | `datasets/sfdmu/qb/en-US/constraints/QuantumBitComplete/` | Move |
| QB CML README | `datasets/constraints/README.md` | `datasets/sfdmu/qb/en-US/constraints/README.md` | Move |
| Procedure plans | `datasets/sfdmu/procedure-plans/` | `datasets/sfdmu/_shared/procedure-plans/` | Move |
| Scratch data | `datasets/sfdmu/scratch_data/` | `datasets/sfdmu/_shared/scratch_data/` | Move |
| Archived plans | `datasets/sfdmu/_archived/` | `datasets/sfdmu/_tooling/_archived/` | Move |
| Extractions | `datasets/sfdmu/extractions/` | `datasets/sfdmu/_tooling/extractions/` | Move |
| Reconcile | `datasets/sfdmu/reconcile/` | `datasets/sfdmu/_tooling/reconcile/` | Move |
| Test data | `datasets/sfdmu/test/` | `datasets/sfdmu/_tooling/test/` | Move |
| Context archive | `datasets/context_plans/archive/` | `datasets/context_plans/_archive/` | Rename |
| Context shared | `datasets/context_plans/ConstraintEngineNodeStatus/` | `datasets/context_plans/_shared/ConstraintEngineNodeStatus/` | Move |
| QB en-US manifest | *(none)* | `datasets/sfdmu/qb/en-US/shape_manifest.json` | New |
| QB ja manifest | *(none)* | `datasets/sfdmu/qb/ja/shape_manifest.json` | New |
| Q3 en-US manifest | *(none)* | `datasets/sfdmu/q3/en-US/shape_manifest.json` | New (pending) |
| MFG en-US manifest | *(none)* | `datasets/sfdmu/mfg/en-US/shape_manifest.json` | New (draft) |
| MFG constraints dir | *(none)* | `datasets/sfdmu/mfg/en-US/constraints/` | New (placeholder) |
| Shapes registry | *(none)* | `datasets/shapes.json` | New |

---

## 7. CumulusCI Path Changes Required

All path changes are in task option defaults — no flow logic changes needed.

### `cumulusci.yml` Option Defaults

| Task | Option | Old Default | New Default |
|---|---|---|---|
| `import_cml` | `dataset_path` | `datasets/constraints/qb` | `datasets/sfdmu/qb/en-US/constraints` |
| `export_cml` | `dataset_path` | `datasets/constraints/qb` | `datasets/sfdmu/qb/en-US/constraints` |
| `validate_cml` | `dataset_path` | `datasets/constraints/qb` | `datasets/sfdmu/qb/en-US/constraints` |
| `insert_scratch_data` | `data_folder` | `datasets/sfdmu/scratch_data` | `datasets/sfdmu/_shared/scratch_data` |
| `insert_procedure_plans_data` | `data_folder` | `datasets/sfdmu/procedure-plans` | `datasets/sfdmu/_shared/procedure-plans` |
| `capture_org_customizations` *(new)* | `baseline_manifest_path` | `datasets/sfdmu/qb/en-US/baseline_manifest.json` | `datasets/sfdmu/qb/en-US/shape_manifest.json` |

### `tasks/rlm_cml.py`

```python
# Before
DEFAULT_DATASET_PATH = "datasets/constraints/qb"

# After
DEFAULT_DATASET_PATH = "datasets/sfdmu/qb/en-US/constraints"
```

### `tasks/rlm_sfdmu.py`

Check for any hardcoded references to:
- `datasets/sfdmu/scratch_data` → `datasets/sfdmu/_shared/scratch_data`
- `datasets/sfdmu/procedure-plans` → `datasets/sfdmu/_shared/procedure-plans`
- `datasets/sfdmu/reconcile` → `datasets/sfdmu/_tooling/reconcile`

### `scripts/` and `docs/`

Any hardcoded paths in:
- `scripts/post_process_extraction.py`
- `scripts/compare_sfdmu_content.py`
- `scripts/reconcile_detail_qb_tax_billing_rating_rates.py`
- [docs/guides/constraints-setup.md](../guides/constraints-setup.md)
- [README.md](../README.md)

---

## 8. Migration Steps

> **Branch:** All work on `distill-integration` branch.
> **Estimated effort:** ~2 hours including testing.

### Step 1: Create new directories
```bash
mkdir -p datasets/sfdmu/_shared
mkdir -p datasets/sfdmu/_tooling
mkdir -p datasets/sfdmu/qb/en-US/constraints
mkdir -p datasets/sfdmu/mfg/en-US/constraints
mkdir -p datasets/context_plans/_shared
mkdir -p datasets/context_plans/_archive
```

### Step 2: Move constraints into QB shape
```bash
# Move CML data
mv datasets/constraints/qb/QuantumBitComplete \
   datasets/sfdmu/qb/en-US/constraints/
mv datasets/constraints/qb/Server2 \
   datasets/sfdmu/qb/en-US/constraints/
mv datasets/constraints/README.md \
   datasets/sfdmu/qb/en-US/constraints/README.md

# Remove now-empty constraints directory
rmdir datasets/constraints/qb
rmdir datasets/constraints
```

### Step 3: Move cross-shape plans to `_shared/`
```bash
mv datasets/sfdmu/procedure-plans  datasets/sfdmu/_shared/
mv datasets/sfdmu/scratch_data     datasets/sfdmu/_shared/
```

### Step 4: Move tooling folders to `_tooling/`
```bash
mv datasets/sfdmu/_archived   datasets/sfdmu/_tooling/
mv datasets/sfdmu/extractions datasets/sfdmu/_tooling/
mv datasets/sfdmu/reconcile   datasets/sfdmu/_tooling/
mv datasets/sfdmu/test        datasets/sfdmu/_tooling/
```

### Step 5: Clean up context_plans
```bash
mv datasets/context_plans/archive \
   datasets/context_plans/_archive
mkdir -p datasets/context_plans/_shared
mv datasets/context_plans/ConstraintEngineNodeStatus \
   datasets/context_plans/_shared/
```

### Step 6: Update path defaults in code
- `tasks/rlm_cml.py` — update `DEFAULT_DATASET_PATH`
- `cumulusci.yml` — update task option defaults (see §7)
- `tasks/rlm_sfdmu.py` — check for hardcoded paths
- `scripts/*.py` — update any hardcoded references

### Step 7: Create `datasets/shapes.json`
```bash
# Create registry (content in §9 below)
touch datasets/shapes.json
```

### Step 8: Run validation
```bash
cci task run validate_setup
cci task run validate_cml
# Smoke test a data load with --dry-run or simulation mode
```

### Step 9: Update documentation
- [README.md](../README.md) — update any path references
- [docs/guides/constraints-setup.md](../guides/constraints-setup.md) — update CML path references
- [docs/project-analysis.md](project-analysis.md) — paths already reflect new structure

---

## 9. Prerequisites for Shape Manifest Generation

Once the reorganization is complete, shape manifests can be generated.

### `datasets/shapes.json` (initial content)

```json
{
  "$schema": "https://rlm-base.schema/shapes/v1",
  "version": "1.0.0",
  "last_updated": "2026-02-27",
  "shapes": [
    {
      "id": "qb-en-US",
      "path": "datasets/sfdmu/qb/en-US",
      "label": "QuantumBit (English US)",
      "locale": "en-US",
      "status": "active",
      "source": "hand-authored",
      "sfdmu_version": "5",
      "required_flags": ["qb"],
      "optional_flags": ["billing", "tax", "dro", "rating", "rates",
                         "clm", "clm_data", "guidedselling", "constrains"],
      "includes_constraints": true,
      "constraints_path": "datasets/sfdmu/qb/en-US/constraints",
      "manifest": "datasets/sfdmu/qb/en-US/shape_manifest.json",
      "plan_count": 13,
      "notes": "Primary reference shape. SFDMU v5 with composite keys."
    },
    {
      "id": "qb-ja",
      "path": "datasets/sfdmu/qb/ja",
      "label": "QuantumBit (Japanese)",
      "locale": "ja",
      "status": "partial",
      "source": "hand-authored",
      "sfdmu_version": "5",
      "required_flags": ["qb"],
      "optional_flags": [],
      "includes_constraints": false,
      "manifest": "datasets/sfdmu/qb/ja/shape_manifest.json",
      "plan_count": 2,
      "covered_plans": ["qb-pcm", "qb-pricing"],
      "missing_plans": ["qb-billing", "qb-tax", "qb-dro",
                        "qb-rating", "qb-rates", "qb-clm",
                        "qb-guidedselling"],
      "notes": "Initial Japanese localization. PCM and Pricing only."
    },
    {
      "id": "q3-en-US",
      "path": "datasets/sfdmu/q3/en-US",
      "label": "Q3 Multi-Currency (English US)",
      "locale": "en-US",
      "status": "pending",
      "source": "hand-authored",
      "sfdmu_version": "4",
      "required_flags": ["q3"],
      "optional_flags": ["billing", "tax", "dro", "rating", "rates"],
      "includes_constraints": false,
      "manifest": null,
      "plan_count": 6,
      "notes": "Pending SFDMU v4 → v5 composite key migration. Manifest not generated until migration complete."
    },
    {
      "id": "mfg-en-US",
      "path": "datasets/sfdmu/mfg/en-US",
      "label": "Manufacturing (English US)",
      "locale": "en-US",
      "status": "draft",
      "source": "hand-authored",
      "sfdmu_version": "5",
      "required_flags": ["mfg"],
      "optional_flags": [],
      "includes_constraints": false,
      "manifest": "datasets/sfdmu/mfg/en-US/shape_manifest.json",
      "plan_count": 4,
      "notes": "Draft manufacturing shape. Constraints placeholder created but not yet populated."
    }
  ],
  "shared": {
    "procedure_plans": "datasets/sfdmu/_shared/procedure-plans",
    "scratch_data": "datasets/sfdmu/_shared/scratch_data",
    "context_plans": "datasets/context_plans/_shared"
  }
}
```

### Generating `shape_manifest.json` for `qb/en-US`

Once the reorganization is complete, run:
```bash
cci task run generate_baseline_manifest \
  --org dev \
  --option shape_id qb-en-US
```

This reads all `export.json` files under `datasets/sfdmu/qb/en-US/`, extracts the complete object/field/key inventory, and writes `datasets/sfdmu/qb/en-US/shape_manifest.json`.

See [distill-integration.md §5](distill-integration.md#5-shape-manifest-data-model-design) for the full manifest schema design.

---

## 10. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| CML import task uses old path, fails on run | High (if not caught) | High | Update `rlm_cml.py` default + add validation in `validate_setup` |
| SFDMU task hardcodes scratch_data path | Medium | Medium | Grep `tasks/rlm_sfdmu.py` for literal path strings before migration |
| README / doc references become stale | High | Low | Update README.md and constraints_setup.md as part of Step 9 |
| q3 plans broken by `_tooling` separation | None | None | q3 plans don't move — only tooling folders move |
| CI/CD references old paths | Low (no CI currently) | Low | Note for when GitHub Actions are added |
| reconcile/ scripts reference old paths | Medium | Low | Update `scripts/reconcile_*.py` path constants |

---

## 11. Approval & Status

| Decision | Status | Notes |
|---|---|---|
| Reorganization approach approved | 🔲 Pending | Review this document |
| `constraints/` moves into QB shape | 🔲 Pending | Key decision — changes CML task defaults |
| `_shared/` grouping for cross-shape plans | 🔲 Pending | |
| `_tooling/` grouping for operational data | 🔲 Pending | |
| `shapes.json` registry format approved | 🔲 Pending | |
| `shape_manifest.json` naming convention | 🔲 Pending | (vs. `baseline_manifest.json`) |
| Ready to execute migration steps | 🔲 Pending | After all decisions approved |
