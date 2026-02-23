# procedure-plans Data Plan

SFDMU data plan for Procedure Plan configuration. Creates the sections and options that define the pricing procedure execution order within a Procedure Plan Definition, linking each option to an Expression Set (pricing procedure).

## CCI Integration

### Flow: `prepare_procedureplans`

This data plan is executed as **step 4** of the `prepare_procedureplans` flow (when `procedureplans=true`).

| Step | Task                                    | Description                                                                  |
|------|-----------------------------------------|------------------------------------------------------------------------------|
| 1    | `deploy_post_procedureplans`            | Deploy expression set metadata (RC_Price_Distribution_Procedure, RC_Revenue_Management_Recalc_Procedure) + RevenueManagement.settings (`skipOrgSttPricing=true`) |
| 2    | `activate_procedure_plan_expression_sets` | Activate RC_Price_Distribution_Procedure_V1 (idempotent)                   |
| 3    | `create_procedure_plan_definition`      | Create PPD + inactive PPDV via Connect API (idempotent)                      |
| 4    | `insert_procedure_plan_data`            | Run this SFDMU plan (2 passes — sections then options)                       |
| 5    | `activate_procedure_plan_version`       | Activate the ProcedurePlanDefinitionVersion (idempotent)                     |

### Task Definition

```yaml
insert_procedure_plan_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/procedure-plans"
```

## Data Plan Overview

The plan uses **2 SFDMU passes** with a **Connect API pre-step** and a **REST API post-step**:

```
Connect API             Pass 1 (SFDMU)          Pass 2 (SFDMU)          REST PATCH
──────────────          ─────────────────        ─────────────────       ──────────────
Create PPD +        ->  Upsert Procedure     ->  Upsert Procedure   ->  Activate PPDV
inactive PPDV           Plan Sections             Plan Options            (IsActive=true)
```

The ProcedurePlanDefinition and ProcedurePlanDefinitionVersion are created by the Connect API task (`create_procedure_plan_definition`) rather than SFDMU because the `ProcedurePlanDefinition` sObject type requires the Connect API endpoint `POST /connect/procedure-plan-definitions` for creation.

**Critical ordering:** The PPDV must be **inactive** during section/option insertion — Salesforce rejects DML on child records when the parent version is active ("You can't insert a procedure plan section with an active procedure plan definition version"). The activation step runs after all data is loaded.

### Pass 1 — Upsert ProcedurePlanSections

Sections define the phases of the pricing procedure plan. Each section references the parent `ProcedurePlanDefinitionVersion` (resolved via `Readonly` lookup by `DeveloperName`).

| # | Object                          | Operation | External ID                | Records |
|---|---------------------------------|-----------|----------------------------|---------|
| 1 | ProcedurePlanDefinition         | Readonly  | `DeveloperName`            | 1       |
| 2 | ProcedurePlanDefinitionVersion  | Readonly  | `DeveloperName`            | 1       |
| 3 | ProcedurePlanSection            | Upsert    | `SubSectionType;Sequence`  | 2       |

### Pass 2 — Upsert ProcedurePlanOptions with ExpressionSet Links

Options link each section to an Expression Set Definition (the pricing procedure to execute). Pass 2 resolves `ProcedurePlanSection` from the target org (inserted in Pass 1) and `ExpressionSetDefinition` records that are already present in the org.

| # | Object                     | Operation | External ID                              | Records |
|---|----------------------------|-----------|------------------------------------------|---------|
| 1 | ProcedurePlanSection       | Readonly  | `SubSectionType;Sequence`                | 2       |
| 2 | ExpressionSetDefinition    | Readonly  | `DeveloperName`                          | 2       |
| 3 | ProcedurePlanOption        | Upsert    | `ProcedurePlanSection.SubSectionType;Priority` | 2 |

## Connect API Task

**Module:** `tasks/rlm_create_procedure_plan_def.py`
**Class:** `CreateProcedurePlanDefinition`

Creates the ProcedurePlanDefinition and its initial ProcedurePlanDefinitionVersion atomically via the RLM Connect API (`POST /connect/procedure-plan-definitions`).

Key behaviors:
- **Idempotent:** Queries for existing PPD by `DeveloperName` before creating; skips if found
- **Context Definition Resolution:** Resolves the `ContextDefinition` ID by `MasterLabel` lookup (default: `RLM_SalesTransactionContext`) — the custom extended context, not `SalesTransactionContext__stdctx`
- **Inactive creation:** PPDV is created with `active: false` so sections and options can be inserted before activation

### Configuration (from `cumulusci.yml`)

| Option | Value | Description |
|--------|-------|-------------|
| `developerName` | `RC_Quote_Pricing_Procedure_Plan` | PPD DeveloperName |
| `name` | `RC Quote Pricing Procedure Plan` | PPD label |
| `primaryObject` | `Quote` | Target object |
| `processType` | `RevenueCloud` | Process type |
| `versionActive` | `false` | PPDV created inactive |
| `context_definition_label` | `RLM_SalesTransactionContext` | Context definition to resolve |
| `versionReadContextMapping` | `QuoteEntitiesMapping` | Read context mapping |
| `versionSaveContextMapping` | `QuoteEntitiesMapping` | Save context mapping |
| `versionEffectiveFrom` | `2026-01-01T00:00:00.000Z` | Version effective-from date |
| `versionRank` | `1` | Version rank |

## Activation Task

**Module:** `tasks/rlm_create_procedure_plan_def.py`
**Class:** `ActivateProcedurePlanVersion`

Activates the ProcedurePlanDefinitionVersion after all sections and options have been inserted.

- **Idempotent:** Checks `IsActive` before patching; skips if already active
- Queries PPDV by parent `ProcedurePlanDefinition.DeveloperName`
- Patches `IsActive = true` via sObject REST API

## Procedure Plan Structure

### RC Quote Pricing Procedure Plan

| Section | SubSectionType | Sequence | Expression Set | Priority |
|---------|----------------|----------|----------------|----------|
| Default Pricing | `DefaultPricing` | 1 | `RLM_DefaultPricingProcedure` | 1 |
| Header Distribution | `HeaderDistribution` | 2 | `RC_Price_Distribution_Procedure` | 1 |

The plan executes two pricing procedures in order:
1. **Default Pricing** (Seq 1): Runs `RLM_DefaultPricingProcedure` — the main pricing expression set (deployed by the core flow, not this plan)
2. **Header Distribution** (Seq 2): Runs `RC_Price_Distribution_Procedure` — distributes header-level adjustments to line items (deployed by `deploy_post_procedureplans`)

## Expression Set Metadata

Two expression sets are deployed by `deploy_post_procedureplans` (step 1 of the flow):

| Expression Set | Description | Deployed By |
|----------------|-------------|-------------|
| `RC_Price_Distribution_Procedure` | Price distribution procedure for header-to-line allocation | `post_procedureplans` |
| `RC_Revenue_Management_Recalc_Procedure` | Revenue management recalculation procedure | `post_procedureplans` |

`RLM_DefaultPricingProcedure` is deployed and activated by the core expression set flow (`activate_and_deploy_expression_sets`) earlier in the `prepare_rlm_org` pipeline. It is referenced by the data plan but not deployed or managed by this flow.

## File Structure

```
procedure-plans/
├── export.json                          # SFDMU data plan (2 passes)
├── README.md                            # This file
│
│  Source CSVs (Pass 1 — Sections)
├── ProcedurePlanDefinition.csv          # 1 record (Readonly)
├── ProcedurePlanDefinitionVersion.csv   # 1 record (Readonly)
├── ProcedurePlanSection.csv             # 2 records (Upsert)
│
│  Source CSVs (Pass 2 — Options)
├── objectset_source/
│   └── object-set-2/
│       └── ProcedurePlanOption.csv      # 2 records (Upsert)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
├── target/                              # SFDMU-generated target snapshots
└── reports/                             # SFDMU missing-parent reports
```

## Composite Key Design

### ProcedurePlanSection

**External ID:** `SubSectionType;Sequence`

Each section is uniquely identified by its `SubSectionType` and `Sequence` within the parent PPDV. The `$$SubSectionType$Sequence` column in the CSV provides the composite key value for SFDMU upsert matching.

### ProcedurePlanOption

**External ID:** `ProcedurePlanSection.SubSectionType;Priority`

Each option is uniquely identified by its parent section's `SubSectionType` and the option's `Priority`. The `$$ProcedurePlanSection.SubSectionType$Priority` column in the CSV provides the composite key. The parent section is resolved via `ProcedurePlanSection.$$SubSectionType$Sequence` lookup.

## Idempotency

This plan is **fully idempotent** at every step:

1. **Connect API task** — skips if PPD already exists
2. **Expression set activation** — skips if already active
3. **SFDMU Upsert** — matches existing records via composite external IDs; "Nothing was updated" on re-run
4. **PPDV activation** — skips if already active

Verified on API 260 against `dev-sb0` with all records present.

## Dependencies

This plan depends on the following having been loaded/deployed first:

- **Core expression sets** — `RLM_DefaultPricingProcedure` must exist (deployed by `activate_and_deploy_expression_sets` in step 19 of `prepare_rlm_org`)
- **Context definitions** — `RLM_SalesTransactionContext` must exist for Connect API context resolution (deployed by `extend_context_definitions` in `prepare_core`)

This plan deploys its own prerequisite expression sets (`RC_Price_Distribution_Procedure`, `RC_Revenue_Management_Recalc_Procedure`) in step 1 of the flow.

## Simulation Mode

The SFDMU data plan supports simulation (dry run) mode via the CCI task:

```bash
# Simulate the full data plan (no writes to org)
cci task run insert_procedure_plan_data -o simulation true

# Simulate a specific pass
cci task run insert_procedure_plan_data -o object_sets "[0]" -o simulation true
```

## Known Issues

### PPDV Must Be Inactive During Data Load

Salesforce rejects `INSERT` and `UPSERT` operations on `ProcedurePlanSection` when the parent `ProcedurePlanDefinitionVersion` is active. The flow handles this by creating the PPDV with `versionActive: false` and activating it in the final step after all sections and options are loaded.

### ProcedurePlanDefinition Requires Connect API

The `ProcedurePlanDefinition` metadata type is not supported by the Salesforce CLI source-deploy-retrieve registry (`RegistryError: Missing metadata type definition`). While it is listed as a metadata type in the org, direct metadata deployment is not possible. The Connect API provides an atomic create-with-version operation that works reliably.

### Object Set Filtering with `useSeparatedCSVFiles`

When using the `object_sets` option to run a single pass from a multi-pass plan, SFDMU reindexes the filtered object set to position 0 and looks for CSVs in the root directory instead of the expected `objectset_source/object-set-N/` directory. For pass-by-pass execution, use the `sync_objectset_source_to_source` option or run the full plan (the `Upsert` operation ensures idempotency).
