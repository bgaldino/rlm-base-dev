# Data Plans

[Home](../../README.md) · [Documentation](../index.md) · [Data-plan skill](../../.cursor/skills/sfdmu-data-plans/SKILL.md)

Run commands from the repository root. Generated validation reports belong in the
gitignored `.agents/artifacts/` directory.

- [SFDMU plans and validation](#sfdmu-data-plans)
- [QuantumBit plan catalog](#quantumbit-qb-data-plans)
- [Constraint model plans](#constraint-model-data-plans)


Data plans provide the reference data loaded during org setup. This project uses two mechanisms:

### SFDMU Data Plans

> **Requires SFDMU v5.6.4+.** Re-run safety depends on the plan, its orchestration,
> and the target org's existing data. Read the per-plan README before reloading:
> `qb-pricing` retains Insert objects and uses a separate delete task in its flow;
> `qb-rating` and `qb-rates` retain Insert + `deleteOldData` operations whose deletes
> can be blocked by live records. See [reloading a plan into a live org](../../.cursor/skills/sfdmu-data-plans/SKILL.md#reloading-a-plan-into-a-live-org)
> for these limitations and [Composite Key Optimizations](../../docs/references/sfdmu-composite-key-optimizations.md)
> for migration history.

SFDMU data plans are located under `datasets/sfdmu/` and are loaded by the `load_sfdmu_data` task infrastructure. Each plan contains an `export.json` defining the objects, fields, and ordering for SFDMU.

#### Validating SFDMU Data Plans

The project includes `scripts/validate_sfdmu_v5_datasets.py` for validating SFDMU v5 compliance:

**Validation:**

```bash
# Validate all SFDMU datasets
python scripts/validate_sfdmu_v5_datasets.py

# Validate specific dataset
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-billing

# Validate all QB datasets
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb

# Generate report file
mkdir -p .agents/artifacts
python scripts/validate_sfdmu_v5_datasets.py --output .agents/artifacts/sfdmu-v5-validation-report.md
```

**Automatic Fixes:**

```bash
# Fix empty CSV headers
python scripts/validate_sfdmu_v5_datasets.py --fix-headers

# Fix missing composite key columns
python scripts/validate_sfdmu_v5_datasets.py --fix-composite-keys

# Fix all issues (dry-run first recommended)
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run
python scripts/validate_sfdmu_v5_datasets.py --fix-all
```

The validator checks for:

- Legacy `$$` notation in externalId definitions (v5 requires semicolon format)
- Missing composite key columns in CSVs
- Empty CSV files without headers
- Nested relationship paths that cause v5 flattening errors

To generate a validation report:

```bash
# Console output
python scripts/validate_sfdmu_v5_datasets.py

# Save to file
mkdir -p .agents/artifacts
python scripts/validate_sfdmu_v5_datasets.py --output .agents/artifacts/sfdmu-v5-validation-report.md
```

#### Data plan directory structure

Plans follow a **shape / locale / plan-name** tree so multiple data shapes (e.g. QuantumBit, Manufacturing) can coexist:

```
datasets/sfdmu/
├── <shape>/           # e.g. qb, mfg, q3
│   └── <locale>/      # e.g. en-US
│       └── <plan-name>/   # e.g. qb-pcm, mfg-pcm
│           ├── export.json
│           ├── Object1.csv
│           ├── Object2.csv
│           └── (optional) objectset_source/   # for multi-pass plans
├── procedure-plans/
└── extractions/       # extract output: <plan-name>/<timestamp>/ and .../processed/
```

**Examples:** `datasets/sfdmu/qb/en-US/qb-pcm`, `datasets/sfdmu/mfg/en-US/mfg-pcm`.
For this standard shape/locale/plan layout, `ExtractSFDMUData` defaults to
`datasets/sfdmu/extractions/<plan-name>/<timestamp>/`, with post-processed CSVs
under `processed/`. The default base is derived from the plan's directory depth:
`datasets/sfdmu/procedure-plans`, for example, would write under repository-level
`extractions/`. For other layouts, set the extraction task's `extractions_base_dir`
option explicitly (for example, `-o extractions_base_dir datasets/sfdmu/extractions`).
An explicit `output_dir` instead selects the complete output directory and takes
precedence over that base. See the [extraction task](../../tasks/rlm_sfdmu.py).

**Adding a new data shape (e.g. mfg):**

1. Create the directory tree: `datasets/sfdmu/mfg/en-US/<plan-name>/` (e.g. `mfg-pcm`).
2. Add `export.json` and CSV files following the same patterns as QB (single-pass with flat `objects`, or multi-pass with `objectSets`; see [qb-pcm](../../datasets/sfdmu/qb/en-US/qb-pcm/README.md) or [qb-rating](../../datasets/sfdmu/qb/en-US/qb-rating/README.md) as reference).
3. In `cumulusci.yml`, under **DATA PLAN NAMES AND PATHS**, add an anchor (e.g. `mfg_pcm_dataset: &mfg_pcm_dataset "datasets/sfdmu/mfg/en-US/mfg-pcm"`).
4. Add load, extract, and idempotency tasks that reference that anchor (`pathtoexportjson: *mfg_pcm_dataset`). Use the same task classes (`LoadSFDMUData`, `ExtractSFDMUData`, `TestSFDMUIdempotency`) and groups (Data Management - Extract / Idempotency) so extract runs post-process by default and output goes to `datasets/sfdmu/extractions/mfg-pcm/<timestamp>/processed/` for this layout.
5. Add a README in the plan directory and, if desired, list the plan in the table below.

#### QuantumBit (QB) Data Plans

| Data Plan | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| qb-pcm | `datasets/sfdmu/qb/en-US/qb-pcm/` | Product Catalog Management -- products, classifications, components, attributes | [README](../../datasets/sfdmu/qb/en-US/qb-pcm/README.md) |
| qb-product-images | `datasets/sfdmu/qb/en-US/qb-product-images/` | Product images and content document links | [README](../../datasets/sfdmu/qb/en-US/qb-product-images/README.md) |
| qb-pricing | `datasets/sfdmu/qb/en-US/qb-pricing/` | Pricing data (pricebook entries, price adjustments) | [README](../../datasets/sfdmu/qb/en-US/qb-pricing/README.md) |
| qb-tax | `datasets/sfdmu/qb/en-US/qb-tax/` | Tax engine data (tax treatments, policies) | [README](../../datasets/sfdmu/qb/en-US/qb-tax/README.md) |
| qb-billing | `datasets/sfdmu/qb/en-US/qb-billing/` | Billing data (billing terms, schedules) | [README](../../datasets/sfdmu/qb/en-US/qb-billing/README.md) |
| qb-dro | `datasets/sfdmu/qb/en-US/qb-dro/` | Dynamic Revenue Orchestration plans | [README](../../datasets/sfdmu/qb/en-US/qb-dro/README.md) |
| qb-transactionprocessingtypes | `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/` | Transaction Processing Type records | [README](../../datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md) |
| qb-rating | `datasets/sfdmu/qb/en-US/qb-rating/` | Rating design-time data | [README](../../datasets/sfdmu/qb/en-US/qb-rating/README.md) |
| qb-rates | `datasets/sfdmu/qb/en-US/qb-rates/` | Rates data | [README](../../datasets/sfdmu/qb/en-US/qb-rates/README.md) |
| qb-prm | `datasets/sfdmu/qb/en-US/qb-prm/` | Partner Relationship Management (channel programs, levels, members) | [README](../../datasets/sfdmu/qb/en-US/qb-prm/README.md) |
| qb-prm-pricing | `datasets/sfdmu/qb/en-US/qb-prm-pricing/` | PRM pricing overlay data (partner accounts, channel programs, member pricing, account self-lookups) | [README](../../datasets/sfdmu/qb/en-US/qb-prm-pricing/README.md) |
| qb-accounting | `datasets/sfdmu/qb/en-US/qb-accounting/` | General ledger and billing accounting reference data (not wired into CCI) | [README](../../datasets/sfdmu/qb/en-US/qb-accounting/README.md) |
| qb-approvals | `datasets/sfdmu/qb/en-US/qb-approvals/` | Advanced Approvals notification records | [README](../../datasets/sfdmu/qb/en-US/qb-approvals/README.md) |
| qb-clm | `datasets/sfdmu/qb/en-US/qb-clm/` | Contract clauses and lifecycle state definitions | [README](../../datasets/sfdmu/qb/en-US/qb-clm/README.md) |
| qb-guidedselling-products | `datasets/sfdmu/qb/en-US/qb-guidedselling-products/` | Guided-selling attributes for existing products | [README](../../datasets/sfdmu/qb/en-US/qb-guidedselling-products/README.md) |

#### Procedure Plans Data Plan

| Data Plan | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| procedure-plans | `datasets/sfdmu/procedure-plans/` | Procedure Plan sections and options with expression set links (2-pass upsert + Connect API + activation) | [README](../../datasets/sfdmu/procedure-plans/README.md) |

Procedure-plan overlays that require resolved parent IDs live under
`datasets/procedure_plan_overlays/` and are applied by dedicated CCI tasks
rather than SFDMU.

#### Removed Data Plans

The following historical constraint plans were removed from this checkout and
replaced by the CML utility. Their names are retained here for migration context;
there is no `datasets/sfdmu/_archived/` directory to browse:

- `qb-constraints-product` -- replaced by CML utility
- `qb-constraints-component` -- replaced by CML utility
- `qb-constraints-consolidated` -- replaced by CML utility
- `qb-constraints-prc-aisummit` -- replaced by CML utility

### Constraint Model Data Plans

Constraint model data is managed by the Python-based CML utility (`tasks/rlm_cml.py`) instead of SFDMU. These plans are stored under `datasets/constraints/` and include CSVs for Expression Sets, ESC associations, and the ConstraintModel blobs — which are **plain-text CML**, uploaded verbatim, not compiled binaries.

| Model | Directory | ESC Records | Active after `prepare_constraints`? |
|-------|-----------|-------------|-------------------------------------|
| QuantumBitBundle | `datasets/constraints/qb/QuantumBitBundle/` | 61 | **yes** — the active QuantumBit model |
| QuantumBitComplete | `datasets/constraints/qb/QuantumBitComplete/` | 57 | no — imported inactive, kept for A/B |
| QuantumBitPCM | `datasets/constraints/qb/QuantumBitPCM/` | 12 | no — imported inactive, kept for A/B |
| Server2 | `datasets/constraints/qb/Server2/` | 81 | **yes** — hardware model, not part of the QuantumBit family |

Exactly one QuantumBit model may be active at a time; `Server2` is a separate model and
is active alongside it.

For details on exporting new models, importing into target orgs, polymorphic ID resolution, and CCI integration, see the [Constraints Utility Guide](../../datasets/constraints/README.md).
