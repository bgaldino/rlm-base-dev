# procedure-plans Data Plan

SFDMU data plan for Procedure Plan configuration. Creates the sections and options that define the pricing procedure execution order within a Procedure Plan Definition, linking each option to an Expression Set (pricing procedure).

## CCI Integration

### Flow: `prepare_procedureplans`

This data plan is executed as **step 4** of the `prepare_procedureplans` flow (when `procedureplans=true`).

| Step | Task                                    | Description                                                                  |
|------|-----------------------------------------|------------------------------------------------------------------------------|
| 1    | `deploy_post_procedureplans`            | Deploy expression set metadata (RLM_Price_Distribution_Procedure, RLM_Revenue_Management_Recalc_Procedure) + RevenueManagement.settings (`skipOrgSttPricing=false`) |
| 2    | `activate_procedure_plan_expression_sets` | Activate RLM_Price_Distribution_Procedure_V1 (idempotent)                   |
| 3    | `create_procedure_plan_definition`      | Create PPD + inactive PPDV via Connect API (idempotent)                      |
| 4    | `insert_procedure_plan_data`            | Run this SFDMU plan (2 passes — sections then options)                       |
| 5    | `activate_procedure_plan_version`       | Activate the ProcedurePlanDefinitionVersion (idempotent; only when `procedureplans_active=true`, default false) |

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
                                                                         only when
                                                                         procedureplans_active
```

The ProcedurePlanDefinition and ProcedurePlanDefinitionVersion are created by the Connect API task (`create_procedure_plan_definition`) rather than SFDMU because the `ProcedurePlanDefinition` sObject type requires the Connect API endpoint `POST /connect/procedure-plan-definitions` for creation.

**Critical ordering:** The PPDV must be **inactive** during section/option insertion — Salesforce rejects DML on child records when the parent version is active ("You can't insert a procedure plan section with an active procedure plan definition version"). The activation step, when enabled (see *Activation*), runs after all data is loaded.

### Pass 1 — Upsert ProcedurePlanSections

Sections define the phases of the pricing procedure plan. Each section references the parent `ProcedurePlanDefinitionVersion` (resolved via `Readonly` lookup by `DeveloperName`).

| # | Object                          | Operation | External ID                | Records |
|---|---------------------------------|-----------|----------------------------|---------|
| 1 | ProcedurePlanDefinition         | Readonly  | `DeveloperName`            | 1       |
| 2 | ProcedurePlanDefinitionVersion  | Readonly  | `DeveloperName`            | 1       |
| 3 | ProcedurePlanSection            | Upsert (`skipExistingRecords`) | `SectionType;SubSectionType` | 2 |

### Pass 2 — Upsert ProcedurePlanOptions with ExpressionSet Links

Options link each section to an Expression Set Definition (the pricing procedure to execute). Pass 2 resolves `ProcedurePlanSection` from the target org (inserted in Pass 1) and `ExpressionSetDefinition` records that are already present in the org.

| # | Object                     | Operation | External ID                              | Records |
|---|----------------------------|-----------|------------------------------------------|---------|
| 1 | ProcedurePlanSection       | Readonly  | `SubSectionType`                         | 2       |
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
| `developerName` | `RLM_Quote_Pricing_Procedure_Plan` | PPD DeveloperName |
| `name` | `RLM_Quote_Pricing_Procedure_Plan` | PPD label |
| `primaryObject` | `Quote` | Target object |
| `processType` | `Default` | Process type — see the 264 note below |
| `subType` | `RevenueCloud` | Revenue Cloud identity (new in 264) |
| `versionActive` | `false` | PPDV created inactive |
| `context_definition_label` | `RLM_SalesTransactionContext` | Context definition to resolve |
| `versionReadContextMapping` | `QuoteEntitiesMapping` | Read context mapping |
| `versionSaveContextMapping` | `QuoteEntitiesMapping` | Save context mapping |
| `versionEffectiveFrom` | `2026-01-01T00:00:00.000Z` | Version effective-from date |
| `versionRank` | `1` | Version rank |

> **Release 264 — `processType` / `subType` pairing.** Through 262 a Revenue Cloud
> procedure plan was identified by `ProcessType: RevenueCloud` with no subtype. 264 moved
> that identity into the new `SubType` field and rejects the 262 shape outright with
> *"Specify a valid subtype"*. The accepted pair is **`processType: Default` +
> `subType: RevenueCloud`**.
>
> Note the platform's own remediation text contradicts itself here — it offers
> *"Process Type to Revenue Cloud with no Subtype"* as an alternative, but that is the
> 262 shape and it still fails. Do not restore `processType: RevenueCloud` on the strength
> of that message.
>
> `ProcedurePlanDefinition.csv` is a `Readonly` snapshot — SFDMU queries the target org and
> never writes this object — so its `ProcessType` column is descriptive only and cannot
> affect a load. It nonetheless carried the stale `RevenueCloud` extract, which read as a
> contradiction of the pairing above; it now reads `Default`. `SubType` is deliberately
> **not** added to the `Readonly` query: the field does not exist before 264, and adding it
> would break this plan's extract against a 262 org on the way back to `main`.

## Activation Task

**Module:** `tasks/rlm_create_procedure_plan_def.py`
**Class:** `ActivateProcedurePlanVersion`

Activates the ProcedurePlanDefinitionVersion after all sections and options have been inserted.

- **Idempotent:** Checks `IsActive` before patching; skips if already active
- Queries PPDV by parent `ProcedurePlanDefinition.DeveloperName`
- Patches `IsActive = true` via sObject REST API

## Activation (off by default)

`prepare_procedureplans` builds the plan, but activates it (step 5) only when `procedureplans_active`
is true. The default is false. `apply_procedure_plan_overlay` (the PRM section) leaves the version as
it found it.

Measured on a fresh 264 build (todo 314):

- **Plan active, `skipOrgSttPricing=false`** (the repo setting). The Revenue Settings default procedure
  runs again after the plan. A price revision on an as-is renewal is applied twice: CPI 4% + 2 on
  2,400 gave 2,696.64 instead of 2,544. The stored waterfall is the re-run's.
- **Plan active, `skipOrgSttPricing=true`.** The CPI renewal is right, but a header discount is applied
  twice: `RLM_DefaultPricingProcedure` already distributes it, then `RLM_Price_Distribution_Procedure`
  does it again (10% on 5,240 gave 4,244.40 instead of 4,716). The stored waterfall is one step.
- **Plan inactive.** CPI 2,544, header discount 4,716, and amendments, renewals and group ramps
  unchanged. The waterfall is the full default procedure.

Help (*Pricing Procedure Plan Limits*): "The Price Waterfall displays execution results for only the
last pricing procedure in the sequence" and "Don't stitch multiple pricing procedures together within
a single procedure plan". Waterfall chaining across procedures is planned for 266 (GUS W-24674830).

To use the plan anyway (for example for PRM distributor pricing), set `procedureplans_active: true`,
or activate the version in Setup after the build.

## Procedure Plan Structure

### RC Quote Pricing Procedure Plan

| Section | SubSectionType | Sequence | Expression Set | Priority |
|---------|----------------|----------|----------------|----------|
| Default Pricing | `DefaultPricing` | 1 | `RLM_DefaultPricingProcedure` | 1 |
| Header Distribution | `HeaderDistribution` | 2 | `RLM_Price_Distribution_Procedure` | 1 |

When active, the plan executes these pricing procedures in order (the PRM overlay inserts `IFPartnerDistributorOnQuote` at sequence 2 and moves Header Distribution to 3):
1. **Default Pricing** (Seq 1): Runs `RLM_DefaultPricingProcedure` — the main pricing expression set (deployed by the core flow, not this plan)
2. **Header Distribution** (Seq 2): Runs `RLM_Price_Distribution_Procedure` — distributes header-level adjustments to line items (deployed by `deploy_post_procedureplans`)

## Expression Set Metadata

Two expression sets are deployed by `deploy_post_procedureplans` (step 1 of the flow):

| Expression Set | Description | Deployed By |
|----------------|-------------|-------------|
| `RLM_Price_Distribution_Procedure` | Price distribution procedure for header-to-line allocation | `post_procedureplans` |
| `RLM_Revenue_Management_Recalc_Procedure` | Revenue management recalculation procedure | `post_procedureplans` |

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

**External ID:** `SectionType;SubSectionType`

This is the platform's own uniqueness rule: SectionType + SubSectionType must be unique per
version. Every query in the plan is scoped to `RLM_Quote_Pricing_Procedure_Plan`'s version, so
another plan in the org can't match. The `$$SectionType$SubSectionType` column in the CSV holds the
composite key. `Sequence` isn't part of the key, because `apply_procedure_plan_overlay` (PRM)
resequences sections. The platform also requires `Sequence` to be unique per version ("This
sequence already exists").

**`skipExistingRecords: true`.** A rerun never rewrites an existing section, so the PRM order
(`HeaderDistribution` at 3) survives. A missing section is inserted at its CSV `Sequence`, but
only if that slot is free:
- On a PRM org, `IFPartnerDistributorOnQuote` holds slot 2, so a missing `HeaderDistribution` is
  rejected, and the overlay doesn't recreate it (measured 2026-10-29).
- With every section gone, including the PRM one, the load inserts its two CSV sections, and the
  PRM overlay then re-adds `IFPartnerDistributorOnQuote` and resequences them.

**Recovery.** The version must be inactive for the reload, which is the default. With
`procedureplans_active: true`, deactivate it first.
1. Delete the plan's sections and options.
2. Rerun `insert_procedure_plan_data`.
3. Run `apply_procedure_plan_overlay`.
4. Reactivate the version if you deactivated it.

**Consequences:**
- **CSV edits don't reach existing rows.** Edits to an existing row in `ProcedurePlanSection.csv`
  (`Phase`, `ResolutionType`, `Description`) don't propagate to an org that already has the
  section. Change it in the org, or delete and reload.
- **Why not `excludedFromUpdateFields: [Sequence]`:** SFDMU 5.8.0 drops excluded fields from
  inserts too, so new sections would have no Sequence.

### ProcedurePlanOption

**External ID:** `ProcedurePlanSection.SubSectionType;Priority`

Each option is uniquely identified by its parent section's `SubSectionType` and the option's `Priority`. The `$$ProcedurePlanSection.SubSectionType$Priority` column in the CSV provides the composite key. The parent section is resolved with a single-field `ProcedurePlanSection.SubSectionType` lookup.
`SubSectionType` is unique within this plan's version, which the queries are scoped to. The
single-field lookup avoids SFDMU Bug 4 (`$$` composite notation on lookup columns).

## Idempotency

An unchanged rerun is a no-op at every step. If sections were partly deleted, use the recovery in
[Composite Key Design](#composite-key-design).

1. **Connect API task** — skips if PPD already exists
2. **Expression set activation** — skips if already active
3. **SFDMU Upsert** — matches existing records on the keys above; "Nothing was updated" on rerun, including after the PRM overlay has resequenced the sections
4. **PPDV activation** — skips if already active (and is skipped entirely unless `procedureplans_active`)

Verified 2026-10-29 on r1-306 (fresh 264 build with the PRM overlay applied, todo 316):
- two `prepare_procedureplans` reruns with no ignore options were both no-ops;
- the sections stayed at DefaultPricing=1, IFPartnerDistributorOnQuote=2, HeaderDistribution=3;
- with the plan's sections and options deleted, a load re-inserted them, and the overlay then
  resequenced them as before;
- with only `HeaderDistribution` deleted, the rerun was rejected on its Sequence slot (see
  *Composite Key Design* for recovery).

## Dependencies

This plan depends on the following having been loaded/deployed first:

- **Core expression sets** — `RLM_DefaultPricingProcedure` must exist (deployed by `activate_and_deploy_expression_sets` in step 18 of `prepare_rlm_org`)
- **Context definitions** — `RLM_SalesTransactionContext` must exist for Connect API context resolution (deployed by `extend_context_definitions` in `prepare_core`)

This plan deploys its own prerequisite expression sets (`RLM_Price_Distribution_Procedure`, `RLM_Revenue_Management_Recalc_Procedure`) in step 1 of the flow.

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

Salesforce rejects `INSERT` and `UPSERT` operations on `ProcedurePlanSection` when the parent `ProcedurePlanDefinitionVersion` is active. The flow handles this by creating the PPDV with `versionActive: false` and, when `procedureplans_active` is true, activating it in the final step after all sections and options are loaded.

### ProcedurePlanDefinition Requires Connect API

The `ProcedurePlanDefinition` metadata type is not supported by the Salesforce CLI source-deploy-retrieve registry (`RegistryError: Missing metadata type definition`). While it is listed as a metadata type in the org, direct metadata deployment is not possible. The Connect API provides an atomic create-with-version operation that works reliably.

### Object Set Filtering with `useSeparatedCSVFiles`

When using the `object_sets` option to run a single pass from a multi-pass plan, SFDMU reindexes the filtered object set to position 0 and looks for CSVs in the root directory instead of the expected `objectset_source/object-set-N/` directory. For pass-by-pass execution, use the `sync_objectset_source_to_source` option or run the full plan (the `Upsert` operation ensures idempotency).
