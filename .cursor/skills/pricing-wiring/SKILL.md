---
name: pricing-wiring
description: >-
  Wire Revenue Cloud pricing recipes, recipe-table mappings, procedure plans, and
  feature overlays in dependency order in this repo's build (CCI tasks, flows, datasets).
  Use when pricing changes span these layers; use pricing-setup for pricing setup in any org,
  expression-sets for procedure authoring, pricing-procedures for element configuration,
  and decision-tables for lookup definition or refresh work.
---

# Pricing Dependency and Layering Skill

Use this skill when adding or changing pricing behavior **in this repo's build** that spans:

- pricing recipes and recipe table mappings
- pricing procedures (Expression Set Definitions), authored via Metadata API
  (source-controlled) or CRUD'd at runtime via the Connect API (section E)
- procedure plans and plan overlays
- layered feature patches on top of core pricing

This guide is intentionally generic so future feature packs can reuse the same
pattern as PRM pricing without redesigning setup order each time. Pricing setup
that applies to any org (books, schedules, recipes as a concept, settings, multicurrency
rules) is [`pricing-setup`](../pricing-setup/SKILL.md).

## Quick Rules

1. Satisfy recipe-to-table prerequisites before deploying procedures that depend on them.
2. Split **core** prerequisites from **feature overlay** prerequisites.
3. Keep metadata org-agnostic (placeholders + transforms, never hardcoded record IDs).
4. Apply overlays with explicit sequencing (deactivate -> load -> verify -> restore the
   prior active state). The quote procedure plan is built **inactive** by default
   (`procedureplans_active: false`); see `datasets/sfdmu/procedure-plans/README.md` → *Activation*.
5. Validate on a clean org, then re-run for idempotency.
6. Prefer `LookUpApiName` for decision table references; add `LookUpId` only when
   a known org/runtime issue requires it.
7. Procedure authoring/CRUD: `expression-sets`; element configuration: `pricing-procedures`.
   Section E covers only where that work slots into the layering model.

## DO NOT

- **DO NOT** wire feature-specific prerequisites into core bootstrap unless they are true global dependencies.
- **DO NOT** deploy pricing procedures whose lookup/PAS placeholders cannot resolve in target org.
- **DO NOT** mutate active procedure-plan versions without a controlled deactivate/reactivate sequence.
- **DO NOT** assume decision table existence implies recipe compatibility (mapping can still be missing).
- **DO NOT** assume a pricing row created at runtime is visible to pricing. Decision
  tables are point-in-time snapshots of their source object, so a row written after the
  last refresh is invisible to lookups until that table re-syncs — and the miss is
  silent, not an error. See *Runtime-created pricing rows* below.
- **DO NOT** reorder `prepare_rlm_org` or subflow steps without dependency analysis.
- **DO NOT** insert a procedure-plan section into an occupied sequence before moving the existing section out of that sequence.
- **DO NOT** duplicate `LookUpId` parameters within a single expression-set step;
  this can produce a generic Metadata API "unexpected error" at deploy time.
- **DO NOT** mutate the shipped `RLM_DefaultPricingProcedure` to experiment; use a disposable clone.

---

## Reusable Layering Model

Use three explicit layers for any pricing customization:

1. **Core Layer**: global defaults needed by most orgs/features, for example the baseline
   recipe mapping for costbook list pricing.
2. **Feature Layer**: additive prerequisites and metadata for one feature pack, for example
   PRM-specific decision table mappings and procedures.
3. **Overlay Layer**: data/plan adjustments that alter behavior after metadata is deployed,
   for example procedure plan option/section overlays and context extensions.

Design goal: each layer can run independently where possible, and reruns should
be no-op safe.

---

## Dependency Contracts

### A) Pricing Recipe Table Mappings

A `ListPrice`/lookup-driven procedure step can fail even if the decision table
exists and is Active, if the recipe table mapping row is absent. Recipe concept,
subtype and the Setup UI: `.cursor/skills/pricing-setup/pricing-recipes.md`.

Typical failure: `Ensure that the lookup table in the ListPrice step is valid and try again.`

Repo implementation pattern:

- Task: `tasks/rlm_configure_pricing_recipe_table_mappings.py`
- Data payloads:
  - `datasets/tooling/PricingRecipeTableMappings/core_ngp_default.json`
  - `datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json`
- Core task: `configure_core_pricing_recipe_table_mappings`
  - Runs in `prepare_expression_sets` before `deploy_expression_sets`
  - Ensures `NGPDefaultRecipe` is mapped to `RLM_CostBookEntries` as `ListPrice`
- Feature task: `configure_pricing_recipe_table_mappings`
  - Runs in `deploy_post_prm_pricing` behind `prm` + `prm_pricing`
  - Ensures PRM-specific table mappings, plus idempotent coverage for shared
    cost-book mapping when the PRM pricing flow is run directly
  - `RLM_PRM_DISTI_Pricing_Procedure` runs only through the procedure plan, so
    distributor pricing also needs `procedureplans_active: true`

Mapping tasks fail fast when a required `DecisionTable` is missing. Keep
`skip_missing_tables: false` for flow usage; use `skip_missing_tables: true`
only for explicit diagnostic/manual runs.

### B) Pricing Procedures (Expression Sets)

Keep procedure metadata deploy-safe with placeholders and runtime transforms in
`cumulusci.yml`:

- lookup placeholders (e.g., `__LOOKUPID_*`)
- PAS placeholders (e.g., `__ATTRIBUTEPasID__`)

Lookup reference strategy:

- Default to `LookUpApiName` when the target `DecisionTable.DeveloperName` is
  stable and verified in setup/flows.
- Add `LookUpId` placeholders only when needed; do not add both casually. If both
  are present in a step, verify there is exactly one `LookUpId` parameter block per step.
- Keep source metadata org-agnostic: never commit real record IDs.

When altering calculation logic, prefer minimal additive deltas on top of stable
baseline structure.

### C) Procedure Plans and Overlays

Plan overlays are JSON-driven, and the JSON is the behavioral contract. The overlay task runs
deactivate, create/patch sections, resequence through a collision-safe range, create/patch options and
criteria, verify, and reactivate in a guarded `finally`. Placement is declared by anchor
(`placement.afterSubSectionType`), not by a hard-coded sequence. Contract, verification rules, ordering
between independent overlays, how to test your own Quote plan, and why an Order plan can fail every
Place order: [`procedure-plans-and-overlays.md`](procedure-plans-and-overlays.md).

Repo examples: `tasks/rlm_create_procedure_plan_def.py`, `tasks/rlm_apply_procedure_plan_overlay.py`,
`datasets/procedure_plan_overlays/`.

### D) Context Definitions and Context Plans

Pricing depends on context attributes/tags being present in the target context
definition at runtime. A pricing procedure can deploy successfully but still
fail during quote save or pricing execution if required context keys are missing.

Repo implementation pattern:

- Context plan assets under `datasets/context_plans/`
- Context application task: `tasks/rlm_context_service.py` (`manage_context_definition`)
- Feature-specific context apply tasks (example): `apply_context_prm_pricing`

Contract:

- If a pricing feature introduces or requires new context attributes, include a
  context plan update and wire its apply task in the same feature flow.
- Context updates should run before end-to-end pricing validation and before
  declaring the feature deploy complete.
- To create a node-level `ContextAttributeMapping` without source-field
  hydration, add an SObject `mappingRules` entry with `sObject` but no
  `sObjectField`. This is intentional for transient/runtime attributes such as
  `RLM_Transient_Distributor_Discount_Percent__c`; do not add a source field
  unless the target org behavior confirms a `ContextAttrHydrationDetail` should
  exist.

The failure signal `Invalid tag attribute name key: [<Attribute_API_Name>]` and its causes are in
[`../context-service/SKILL.md`](../context-service/SKILL.md) (also
[`../pricing-procedures/operations-and-troubleshooting.md`](../pricing-procedures/operations-and-troubleshooting.md)).

### E) Programmatic Procedure CRUD (Expression Sets)

A pricing procedure **is** an Expression Set; CRUD, overlays, dependency capture and the error register
are in [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md), element configuration in
[`../pricing-procedures/SKILL.md`](../pricing-procedures/SKILL.md). Pricing facts kept here:

- **`usageType: DefaultPricing`** (vs `Bre`); a wrong value hides the procedure from pricing UIs.
- **Plan cascade.** An ES version referenced by an active `ProcedurePlanDefinitionVersion` cannot be
  deactivated until the plan version is (section C).
- **Placeholders** (`__LOOKUPID_*__`, `__ATTRIBUTEPasID__`) resolve via `find_replace` at deploy (B).
- **Recipe mappings and context definitions** (A, D) are prerequisites the ES engine does not know about.

Shipped overlays: `datasets/expression_set_overlays/`; environment-specific:
`docs/references/expression-set-overlay-examples/`. Test CRUD against a **disposable clone**.

---

## Where to Wire in Flows

Use this generic sequencing rule:

1. activate/refresh lookup artifacts (decision tables, schedules)
2. ensure **core** recipe mappings
3. deploy core pricing procedures
4. ensure **feature** recipe mappings
5. deploy feature pricing procedures
6. apply context-definition updates required by pricing features
7. apply procedure-plan/data overlays
8. run verification tasks

In this repo today: core mapping runs in `prepare_expression_sets` before core pricing procedure
deploy; feature mapping runs in `deploy_post_prm_pricing` before PRM pricing procedure deploy. Future
feature packs should mirror this split.

---

## Runtime-created pricing rows

A decision table goes stale the moment its source object gains or changes a row, and pricing then
prices from the table as last refreshed, as if that row did not exist; the miss is silent. Most
pricing sources in this repo are loaded once at org build and never touched again. The ones that
bite are rows normal selling writes afterwards, above all `ContractItemPrice` and
`ContractItemPriceAdjTier`: `RLM_Contract_Activation_Refresh_Pricing_Tables` refreshes the three
`Contract_Pricing_*` tables when a contract becomes **Activated**, and a bulk load of contract
prices needs `cci task run refresh_dt_default_pricing` by hand.

The full section (refresh on activation, not creation; which sync date to read; the two failure
shapes of `refreshDecisionTable`; the per-table staleness query) is in
[`../decision-tables/lifecycle-and-refresh.md`](../decision-tables/lifecycle-and-refresh.md#runtime-created-pricing-rows) →
*Runtime-created pricing rows*.

---

## Pattern for New Pricing Patch Packs

When introducing a new pricing patch/feature:

1. Create a feature payload under `datasets/tooling/PricingRecipeTableMappings/`.
2. Add a dedicated `configure_*_pricing_recipe_table_mappings` task in `cumulusci.yml`.
3. Wire the task in the feature subflow before the feature's expression set deploy.
4. Keep core mapping task unchanged unless the prerequisite is universally required.
5. Add verification task(s) for overlay semantics and mapping presence.

This avoids coupling and prevents cross-feature regressions.

---

## Validation Playbook

Use these checks after wiring changes:

```bash
# Core path
cci flow run prepare_expression_sets --org <cci_alias>

# Verify core mapping prerequisites (Tooling API)
sf data query --use-tooling-api -q "SELECT Id, PricingComponentType FROM PricingRecipeTableMapping WHERE PricingRecipeId IN (SELECT Id FROM PricingRecipe WHERE DeveloperName = 'NGPDefaultRecipe') AND LookupTableId IN (SELECT Id FROM DecisionTable WHERE DeveloperName = 'RLM_CostBookEntries')" --target-org rlm-base__<cci_alias>

# Feature path
cci flow run prepare_prm_pricing --org <cci_alias>

# Idempotency rerun
cci flow run prepare_expression_sets --org <cci_alias>

# Targeted expression-set parse/deploy check (fast failure signal)
sf project deploy start --metadata ExpressionSetDefinition:RLM_DefaultPricingProcedure --target-org rlm-base__<cci_alias> --dry-run --test-level NoTestRun --json
```

Expected idempotency: the mapping task reports `No change` for existing rows, and the procedure
deploy path remains successful on rerun.

---

## Troubleshooting Decision Tree

### `lookup table ... ListPrice ... valid`

Check in order:

1. placeholder resolution applied in deploy transforms
2. decision table exists
3. recipe-to-table mapping row exists for target recipe
4. mapping component type is correct

### Wrong-currency price returned (multicurrency orgs)

Cause (a lookup step that does not pass `CurrencyIsoCode`), symptoms and the fix:
[`../pricing-setup/multicurrency.md`](../pricing-setup/multicurrency.md). This repo's currency
inheritance flows and the exchange-rate refresh: [`multicurrency-build.md`](multicurrency-build.md).

### Active version update failures

Confirm the deactivate step runs before deploy and targets the correct versions. There are two
distinct deactivation gates:

1. **ExpressionSetVersion**: the `deactivate_expression_sets` task handles this.
2. **ProcedurePlanDefinitionVersion**: if the expression set is referenced by an active plan
   version, that plan version must also be deactivated before deploy. The plan version lock
   produces a generic "unexpected error" distinct from the expression set version lock.

### Connect API mutation errors (`Error processing JSON`, `resourceInitializationType`, version-id)

These are Expression Set CRUD mechanics, not layering issues; the error register is in
[`../expression-sets/SKILL.md`](../expression-sets/SKILL.md) and the reference's *Known errors &
conditions* table.

### `ExpressionSetDefinition ... unexpected error occurred`

When the deploy error is generic and points at a single expression set:

1. check whether an active `ProcedurePlanDefinitionVersion` references the expression set — an
   active plan version locks the expression set from metadata API updates. Deactivate the plan
   version first, deploy, then reactivate.
2. run a targeted dry-run deploy for that expression set only
3. diff against last known-good version
4. inspect changed steps for duplicate parameter names (especially `LookUpId`)
5. confirm lookup strategy is coherent (`LookUpApiName` baseline, `LookUpId` only when intentional)

### Expression sets fail deploy via raw `sf project deploy`

Expression sets containing `__LOOKUPID_*__` placeholder tokens cannot deploy via
`sf project deploy start`: the placeholders are not valid record IDs and the metadata API rejects
them. Use `cci task run deploy_expression_sets` (or `activate_and_deploy_expression_sets`), which
applies `find_replace` transforms from `cumulusci.yml` to resolve placeholders to real DecisionTable
IDs via SOQL before deploying.

### Procedure-plan overlay succeeds only on rerun

The overlay still uses fixed sequences or manual move steps; use `placement.afterSubSectionType` so the
task owns sequencing (see `procedure-plans-and-overlays.md`).

### Every Place order fails once a custom Order plan is active

See *An Order plan* in [`procedure-plans-and-overlays.md`](procedure-plans-and-overlays.md).

---

## Context and Best Practices

When pricing adds or consumes context keys, capture them in `datasets/context_plans/<Feature>/`, wire the
apply task in the feature flow before pricing validation, verify the keys exist, and keep it idempotent.
Keep mapping payloads data-driven, setup additive; verify clean-org and rerun behavior. After
`cumulusci.yml` edits run `python scripts/ai/generate_cci_reference.py`.

---

## Sub-files

- [`procedure-plans-and-overlays.md`](procedure-plans-and-overlays.md): the overlay task contract and
  verification, how to test your own Quote plan, and the Order-plan hydration rule. Read it when
  adding or changing a plan overlay.
- [`multicurrency-build.md`](multicurrency-build.md): the repo's currency inheritance flows and the
  exchange-rate refresh across the data plans. Read it when adding a currency to a plan.
- [`price-revision-cpi.md`](price-revision-cpi.md): this repo's CPI (Price Index) data load, how to
  run and verify a renewal revision, and the build gotchas. Read it when setting up or checking a
  price revision on a renewal or ramp.

## Related References

- Skills (`.cursor/skills/`): `expression-sets`, `pricing-procedures`, `pricing-setup`, `cci-orchestration`, `repo-integration`, `sfdmu-data-plans`.
- Expression Set reference: `docs/references/expression-set-connect-api-reference.md`; Connect CRUD
  tasks `tasks/rlm_expression_set_connect.py`.
- Dynamic UX assembly: `docs/features/dynamic-ux-assembly.md`; SFDMU matching constraints: [SFDX-Data-Move-Utility issue #781](https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/781)
