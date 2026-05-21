# Pricing Dependency and Layering Skill

Use this skill when adding or changing pricing behavior that spans:

- pricing recipes and recipe table mappings
- pricing procedures (Expression Set Definitions)
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

## DO NOT

- **DO NOT** wire feature-specific prerequisites into core bootstrap unless they are true global dependencies.
- **DO NOT** deploy pricing procedures whose lookup/PAS placeholders cannot resolve in target org.
- **DO NOT** mutate active procedure-plan versions without a controlled deactivate/reactivate sequence.
- **DO NOT** assume decision table existence implies recipe compatibility (mapping can still be missing).
- **DO NOT** reorder `prepare_rlm_org` or subflow steps without dependency analysis.
- **DO NOT** insert a procedure-plan section into an occupied sequence before moving the existing section out of that sequence.

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

### B) Pricing Procedures (Expression Sets)

Keep procedure metadata deploy-safe with placeholders and runtime transforms in
`cumulusci.yml`:

- lookup placeholders (e.g., `__LOOKUPID_*`)
- PAS placeholders (e.g., `__ATTRIBUTEPasID__`)

When altering calculation logic, prefer minimal additive deltas on top of stable
baseline structure.

### C) Procedure Plans and Overlays

Any overlay to active plan-driven behavior should follow:

1. deactivate plan version
2. insert/update overlay data in dependency-safe passes
3. verify overlay invariants
4. reactivate plan version

When an overlay changes section order and adds a new section into an existing
sequence, split the move and insert into separate SFDMU object sets:

1. move the existing section out of the target sequence
2. insert the new section into the freed sequence
3. wire child options
4. wire child criteria or other dependents

Do not rely on a single object set to update the existing row and insert the new
row in the right order. SFDMU may insert before update on a clean org, causing a
partial first run that appears fixed only because a rerun starts from the
partially moved state.

Repo examples:

- `tasks/rlm_create_procedure_plan_def.py`
- `tasks/rlm_verify_prm_procedure_plan_overlay.py`
- `datasets/sfdmu/procedure-plans-prm/`

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

### procedure-plan overlay succeeds only on rerun

Check for section sequence collisions. If the base plan already has a section at
the target sequence, move that section in an earlier object set before inserting
the overlay section. A first run that moves the existing section but fails to
insert the overlay can make the second run look healthy, masking the sequencing
bug.

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

- CCI orchestration skill: `.cursor/skills/cci-orchestration/SKILL.md`
- Repository integration skill: `.cursor/skills/repo-integration/SKILL.md`
- SFDMU data plans skill: `.cursor/skills/sfdmu-data-plans/SKILL.md`
- Dynamic UX assembly: `docs/features/dynamic-ux-assembly.md`
- SFDMU known matching constraints:
  - [SFDX-Data-Move-Utility issue #781](https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/781)
