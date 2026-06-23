# Pricing Dependency and Layering Skill

Use this skill when adding or changing pricing behavior that spans:

- pricing recipes and recipe table mappings
- pricing procedures (Expression Set Definitions) — authored via Metadata API
  (source-controlled) or CRUD'd at runtime via the Connect API (section E)
- procedure plans and plan overlays
- layered feature patches on top of core pricing

This guide is intentionally generic so future feature packs can reuse the same
pattern as PRM pricing without redesigning setup order each time.

## Quick Rules

1. Satisfy recipe-to-table prerequisites before deploying procedures that depend on them.
2. Split **core** prerequisites from **feature overlay** prerequisites.
3. Keep metadata org-agnostic (placeholders + transforms, never hardcoded record IDs).
4. Apply overlays with explicit sequencing (deactivate -> load -> verify -> reactivate).
5. Validate on a clean org, then re-run for idempotency.
6. Prefer `LookUpApiName` for decision table references; add `LookUpId` only when
   a known org/runtime issue requires it.
7. For **authoring or CRUD'ing pricing procedures themselves** (Connect vs
   Metadata API, overlays, dependency capture, the activation lifecycle), use the
   **Expression Sets skill** (`.cursor/skills/expression-sets/SKILL.md`). This
   skill (section E) covers only where that work slots into the pricing
   layering model.

## DO NOT

- **DO NOT** wire feature-specific prerequisites into core bootstrap unless they are true global dependencies.
- **DO NOT** deploy pricing procedures whose lookup/PAS placeholders cannot resolve in target org.
- **DO NOT** mutate active procedure-plan versions without a controlled deactivate/reactivate sequence.
- **DO NOT** assume decision table existence implies recipe compatibility (mapping can still be missing).
- **DO NOT** reorder `prepare_rlm_org` or subflow steps without dependency analysis.
- **DO NOT** insert a procedure-plan section into an occupied sequence before moving the existing section out of that sequence.
- **DO NOT** duplicate `LookUpId` parameters within a single expression-set step;
  this can produce a generic Metadata API "unexpected error" at deploy time.
- **DO NOT** mutate the real shipped `RLM_DefaultPricingProcedure` (or any shipped
  procedure) to experiment — test CRUD against a disposable clone, except for an
  intentional, approved change. (For the full set of Expression Set CRUD safety
  rules — HTML-entity normalization, version-id handling,
  `resourceInitializationType` immutability, structural-vs-functional removal,
  the three dependency scopes — see `.cursor/skills/expression-sets/SKILL.md`.)

---

## Reusable Layering Model

Use three explicit layers for any pricing customization:

1. **Core Layer**
   - Global defaults needed by most orgs/features.
   - Example: baseline recipe mapping for costbook list pricing.
2. **Feature Layer**
   - Additive prerequisites and metadata for one feature pack.
   - Example: PRM-specific decision table mappings and procedures.
3. **Overlay Layer**
   - Data/plan adjustments that alter behavior after metadata is deployed.
   - Example: procedure plan option/section overlays and context extensions.

Design goal: each layer can run independently where possible, and reruns should
be no-op safe.

---

## Dependency Contracts

### A) Pricing Recipe Table Mappings

A `ListPrice`/lookup-driven procedure step can fail even if the decision table
exists and is Active, if the recipe table mapping row is absent.

Typical failure:

- `Ensure that the lookup table in the ListPrice step is valid and try again.`

Repo implementation pattern:

- Task: `tasks/rlm_configure_pricing_recipe_table_mappings.py`
- Data payloads:
  - `datasets/tooling/PricingRecipeTableMappings/core_ngp_default.json`
  - `datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json`
- Core task: `configure_core_pricing_recipe_table_mappings`
  - Runs in `prepare_expression_sets` before `deploy_expression_sets`
  - Ensures `NGPDefaultRecipe` is mapped to `RLM_CostBookEntries` as
    `ListPrice`
- Feature task: `configure_pricing_recipe_table_mappings`
  - Runs in `deploy_post_prm_pricing` behind `prm` + `prm_pricing`
  - Ensures PRM-specific table mappings, plus idempotent coverage for shared
    cost-book mapping when the PRM pricing flow is run directly

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
- Add `LookUpId` placeholders only when needed; do not add both casually.
- If both are present in a step, verify there is exactly one `LookUpId`
  parameter block per step.
- Keep source metadata org-agnostic: never commit real record IDs.

When altering calculation logic, prefer minimal additive deltas on top of stable
baseline structure.

### C) Procedure Plans and Overlays

Procedure-plan overlays should be JSON-driven and reusable across feature
packs. Treat the JSON as the behavioral contract and keep the task generic.

Runtime contract:

1. deactivate plan version inside the same task that applies the overlay
2. create or patch declared sections
3. compute final section order from the current org state
4. resequence sections through a collision-safe temporary range
5. resolve parent IDs with SOQL instead of relying on traversal upsert keys
6. create or patch options, then criteria if present
7. verify exact overlay invariants
8. reactivate the plan version in a guarded `finally` path

When an overlay changes section order and adds a new section into an existing
sequence, declare placement by anchor (`placement.afterSubSectionType`) rather
than hard-coding the final numeric sequence:

```json
{
  "subSectionType": "MyFeatureSection",
  "placement": {
    "afterSubSectionType": "DefaultPricing"
  }
}
```

The task verifies dynamically from the JSON:

- sections: exactly one row per declared `subSectionType`
- placement: placed sections appear immediately after their declared anchor
- options: exactly one row per resolved section ID plus `priority`, with the
  expected expression set
- criteria: exactly one row per resolved option ID plus `sequence`, `fieldPath`,
  and `operator`

Criteria are optional. Omit the `criteria` array, or set it to `[]`, for
overlays that only add sections/options.

Avoid SFDMU relationship-traversal upserts for procedure-plan children unless
that exact traversal key has already been validated as idempotent in target
orgs.

Independent overlays that target the same anchor still need an ordering
convention if their relative order matters. Without a shared ordering key or a
single combined overlay declaration, run order is the only available signal.
If order matters across independently shipped overlays, add a stable ordering
model before relying on arbitrary execution order.

Repo examples:

- `tasks/rlm_create_procedure_plan_def.py`
- `tasks/rlm_apply_procedure_plan_overlay.py`
- `datasets/procedure_plan_overlays/`

### D) Context Definitions and Context Plans

Pricing depends on context attributes/tags being present in the target context
definition at runtime. A pricing procedure can deploy successfully but still
fail during quote save or pricing execution if required context keys are missing.

Repo implementation pattern:

- Context plan assets under `datasets/context_plans/`
- Context application task: `tasks/rlm_context_service.py` (`manage_context_definition`)
- Feature-specific context apply tasks (example): `apply_context_prm_pricing`

Runtime failure signal (example):

- `Invalid tag attribute name key: [<Attribute_API_Name>]`

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

### E) Programmatic Procedure CRUD (Expression Sets)

A pricing procedure **is** an Expression Set, so authoring or CRUD'ing the
procedure itself — Connect API vs Metadata API, overlays, dependency capture,
the deactivate→modify→reactivate lifecycle, HTML-entity normalization, version-id
rules — is owned by a dedicated skill:

> **Expression Sets skill:** `.cursor/skills/expression-sets/SKILL.md`
> (task-level entry point). **Exhaustive reference:**
> `docs/references/expression-set-connect-api-reference.md` (object/ID model,
> OAS-confirmed schema enums, every known error + resolution, verification
> checklist). Both pinned to **Release 262 / API v67.0**.

**What stays a pricing concern (this section):** *where* that CRUD slots into the
pricing layering and flow order, and the pricing-specific facts the Expression
Sets skill defers back here:

- **`usageType: DefaultPricing`** for a pricing procedure (vs `Bre`); a wrong
  value means the procedure won't surface in pricing UIs or be invocable.
- **Procedure-plan cascade.** A pricing procedure referenced by an active
  `ProcedurePlanDefinitionVersion` cannot have its ES version deactivated until
  the plan version is deactivated first (the cascade the tasks perform). This is
  the same lock described in **C) Procedure Plans and Overlays** above — keep
  plan-version deactivation paired with any procedure mutation.
- **Lookup placeholders.** Pricing-procedure steps carry `__LOOKUPID_*__` /
  `__ATTRIBUTEPasID__` placeholders resolved by `find_replace` transforms at
  deploy (see **B) Pricing Procedures** above) — keep source org-agnostic.
- **Recipe-table mappings + context definitions** (sections A and D) are
  pricing-procedure prerequisites the Expression Set engine does not know about;
  satisfy them before deploying/activating the procedure.

The shipped overlays under `datasets/expression_set_overlays/` are pricing
examples (`map_line_item`, `discount_distribution`, `facility_quantity`); the
Expression Sets skill walks through each. Always test procedure CRUD against a
**disposable clone**, never the shipped `RLM_DefaultPricingProcedure`.

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

In this repo today:

- Core mapping runs in `prepare_expression_sets` before core pricing procedure
  deploy.
- Feature mapping runs in `deploy_post_prm_pricing` before PRM pricing
  procedure deploy.

Future feature packs should mirror this split.

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

Expected idempotency:

- mapping task reports `No change` for existing rows
- procedure deploy path remains successful on rerun

---

## Troubleshooting Decision Tree

### `lookup table ... ListPrice ... valid`

Check in order:

1. placeholder resolution applied in deploy transforms
2. decision table exists
3. recipe-to-table mapping row exists for target recipe
4. mapping component type is correct

### active version update failures

Confirm deactivate step runs before deploy and targets correct versions.
Note: there are two distinct deactivation gates:

1. **ExpressionSetVersion** — the `deactivate_expression_sets` task handles this
2. **ProcedurePlanDefinitionVersion** — if the expression set is referenced by an
   active plan version, that plan version must also be deactivated before deploy.
   The plan version lock produces a generic "unexpected error" distinct from the
   expression set version lock.

### Connect API mutation errors (`Error processing JSON`, `resourceInitializationType`, version-id)

These are Expression Set CRUD mechanics, not pricing-layering issues — the full
error register (HTML-entity parsing failures, opaque-error bisection, immutable
`resourceInitializationType`, version-id handling, `contextDefinitions[].id`,
admin permission) lives in **`.cursor/skills/expression-sets/SKILL.md`** and its
reference's *Known errors & conditions* table. Come back here for the
pricing-specific deploy error below.

### `ExpressionSetDefinition ... unexpected error occurred`

When the deploy error is generic and points at a single expression set:

1. check whether an active `ProcedurePlanDefinitionVersion` references the
   expression set — an active plan version locks the expression set from
   metadata API updates. Deactivate the plan version first, deploy, then
   reactivate.
2. run a targeted dry-run deploy for that expression set only
3. diff against last known-good version
4. inspect changed steps for duplicate parameter names (especially `LookUpId`)
5. confirm lookup strategy is coherent (`LookUpApiName` baseline, `LookUpId` only when intentional)

### Expression sets fail deploy via raw `sf project deploy`

Expression sets containing `__LOOKUPID_*__` placeholder tokens cannot deploy
via `sf project deploy start` — placeholders are not valid Salesforce record
IDs and the metadata API rejects them. Always use `cci task run
deploy_expression_sets` (or `activate_and_deploy_expression_sets`), which
applies `find_replace` transforms from `cumulusci.yml` to resolve placeholders
to real DecisionTable IDs via SOQL before deploying.

### procedure-plan overlay succeeds only on rerun

Check whether the overlay is still using fixed numeric sequences or separate
manual move steps. Rework it to use `placement.afterSubSectionType` so the task
creates/patches sections first, computes the full target order from the org, and
resequences with a temporary high-sequence pass. A first run that partially moves
sections and only succeeds on rerun usually means sequencing is not owned by the
overlay task.

### feature flow fails before mapping step

Treat as unrelated until proven otherwise (missing metadata/field dependencies can
mask mapping validation).

### `Invalid tag attribute name key`

Usually indicates context definition drift:

1. required context attribute/tag was not applied in target org
2. feature context plan was not wired/run in the flow
3. context plan points to wrong context definition/mapping

---

## Context Update Checklist

Use this quick checklist whenever pricing changes add or consume new context keys:

- [ ] Context attribute/tag additions are captured in `datasets/context_plans/<Feature>/`.
- [ ] A context apply task is wired in the corresponding feature flow (not only in ad hoc/manual runs).
- [ ] Context apply runs before pricing validation and quote/pricing runtime tests.
- [ ] At least one verification step confirms required context keys are present in the target context definition.
- [ ] Re-run is idempotent (no duplicate nodes, no destructive replacement unless explicitly intended).

---

## Best Practices

- Use data-driven JSON payloads for mapping declarations.
- Separate core vs feature mapping payloads.
- Keep setup additive; avoid replacing stable baseline wiring.
- Verify clean-org behavior and rerun behavior before merge.
- After `cumulusci.yml` updates, regenerate references:
  - `python scripts/ai/generate_cci_reference.py`

---

## Related References

- **Expression Sets skill (CRUD, overlays, dependency capture):**
  `.cursor/skills/expression-sets/SKILL.md` — the task-level entry point for
  authoring/mutating procedures themselves (the work §E points to).
- **Expression Set reference (exhaustive):**
  `docs/references/expression-set-connect-api-reference.md` — object/ID model,
  OAS-confirmed schema enums, every known error + resolution, Metadata API
  authoring path, and the verification checklist.
- **Connect CRUD tasks:** `tasks/rlm_expression_set_connect.py`; pre-flight
  validator `tasks/expression_set_schema.py`; tests `tests/test_expression_set_schema.py`.
- **External doc link index:** `docs/salesforce/262/dev-guide/expression-set-business-apis-links.md`.
- CCI orchestration skill: `.cursor/skills/cci-orchestration/SKILL.md`
- Repository integration skill: `.cursor/skills/repo-integration/SKILL.md`
- SFDMU data plans skill: `.cursor/skills/sfdmu-data-plans/SKILL.md`
- Dynamic UX assembly: `docs/features/dynamic-ux-assembly.md`
- SFDMU known matching constraints:
  - [SFDX-Data-Move-Utility issue #781](https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/781)
