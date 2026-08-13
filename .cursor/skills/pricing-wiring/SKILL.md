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
- **DO NOT** assume a pricing row created at runtime is visible to pricing. Decision
  tables are point-in-time snapshots of their source object, so a row written after the
  last refresh is invisible to lookups until that table re-syncs — and the miss is
  silent, not an error. See *Runtime-created pricing rows* below.
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
> checklist). Both pinned to **Release 264 / API v68.0**.

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

The shipped overlays under `datasets/expression_set_overlays/` are generally
applicable pricing examples (`map_line_item`, `discount_distribution`). More
environment-specific reference overlays live under
`docs/references/expression-set-overlay-examples/`; the Expression Sets skill
walks through both categories. Always test procedure CRUD against a
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

## Runtime-created pricing rows

A decision table goes stale the moment its source object gains or changes a row, and
pricing then silently prices as if that row did not exist — no error, no warning. Most
pricing sources in this repo are loaded once at org build and never touched again, so in
practice the tables stay correct. The ones that bite are the sources normal selling
writes to *after* the build.

`ContractItemPrice` / `ContractItemPriceAdjTier` are the case that bites: selling a contract
with contract prices writes rows that the three `Contract_Pricing_*` tables have not seen.
`RLM_Contract_Activation_Refresh_Pricing_Tables` (record-triggered on `Contract`) refreshes
all three when a contract becomes **Activated**, which covers every path — the UI Activate
button, REST/SOAP, Apex, another flow — because they all end in the same status change.

**Refresh on activation, not on creation.** The two tier tables filter their source on
`ContractItemPriceId.ContractId.StatusCode = 'Activated'` (inspect any table's filter via
`DecisionTableSourceCriteria`). A contract is created **Draft**, so a refresh fired at
creation time excludes that contract's tier rows and *still* stamps `LastSyncDate` — leaving
a table that reads fresh while holding nothing, which is worse than leaving it visibly stale.
`Contract_Pricing_Entries_Decision_Table` has no such filter, so only two of the three tables
show the symptom, which makes it easy to half-test and conclude the wrong thing.

A refresh is still needed by hand after a **bulk data load** of contract prices that does not
end in an activation:

```bash
cci task run refresh_dt_default_pricing
```

(`refresh_dt_*` tasks accept `--org` as of 2026-07-27 — `RefreshDecisionTable` now sets
`salesforce_task = True`. Before that they silently ran against the CCI **default** org.
`manage_expression_sets` and most other custom tasks still reject it; see issue #320.)

**Use `LastSyncDate` to decide whether a refresh happened.** It only advances on a refresh
that actually ran, so the staleness comparison above is the one check that holds for every
failure shape. Do not rely on `DecisionTable.RefreshStatus` / `RefreshFailureReason` as the
detector: they live *on a table record*, so they only tell you anything once a refresh has
been accepted for a table that exists.

Two failure shapes, measured against a live org — the difference matters before you add
error handling to a flow that calls `refreshDecisionTable`:

| Shape | What you get | Where it shows |
|---|---|---|
| Invalid or inactive `DecisionTableApiName` | **A Flow fault** (*"The decision table API Name is invalid…"*), not a `Failed` status | Nowhere on `DecisionTable` — an unresolvable name identifies no table record to stamp. Only the flow's own fault handling sees it. |
| Accepted refresh that then fails | `status = Queued`, async job result | `RefreshStatus` (observed cycling `Initiated` → `Completed`) and `RefreshFailureReason` |

Consequences:

- A flow calling this action needs a `faultConnector`, and in a **record-triggered
  after-save** flow it needs one urgently: an unhandled fault rolls back the triggering DML,
  so a refresh problem would block the very save that should have caused the refresh.
- The documented `status = Failed` output could not be provoked — a valid table returned
  `Queued` on every attempt, including five back-to-back refreshes of the same table.
- Because the fault case leaves no trace on the table, a flow that swallows the fault leaves
  `LastSyncDate` as the *only* evidence. That is by design, but it means the staleness check
  above is the monitoring story, not an afterthought.

To tell whether a table is stale, compare **each** table against **its own** source object's
newest `LastModifiedDate`. Two things make this easy to get wrong:

- The three tables do **not** share one source, so a single source query proves nothing about
  the other two: `Contract_Pricing_Entries_Decision_Table` ← `ContractItemPrice`, while
  `Contract_Pricing_Adjustment_Tiers` and `Contract_Pricing_Volume_Tiers` ←
  `ContractItemPriceAdjTier`.
- Use `LastModifiedDate`, not `CreatedDate`. An **edited** price row invalidates the table
  exactly as a new one does, and `CreatedDate` cannot see it.

The source query must also **reproduce the table's own source criteria**, or it reports rows
the table deliberately excludes. The tier tables only admit rows whose contract is Activated,
so an unfiltered `MAX` over a Draft contract's tiers would report them stale forever:

```bash
sf data query -q "SELECT DeveloperName, LastSyncDate FROM DecisionTable WHERE DeveloperName LIKE 'Contract_Pricing%' ORDER BY DeveloperName" --target-org <sf_alias>

# Entries <- ContractItemPrice, which has NO source criteria: no filter here.
sf data query -q "SELECT MAX(LastModifiedDate) newest FROM ContractItemPrice" --target-org <sf_alias>

# Both tier tables <- ContractItemPriceAdjTier, filtered to activated contracts.
# Note the SOQL relationship names differ from the criteria field path stored in
# DecisionTableSourceCriteria: ContractItemPriceId.ContractId -> ContractItemPrice.Contract
sf data query -q "SELECT MAX(LastModifiedDate) newest FROM ContractItemPriceAdjTier WHERE ContractItemPrice.Contract.StatusCode = 'Activated'" --target-org <sf_alias>
```

A table whose `LastSyncDate` is **earlier** than its own source's `newest` is stale, and the
contract's negotiated price is not being applied. A `null` `newest` means that source has no
qualifying rows, so its tables cannot be stale.

Generalising: read the table's real filter out of the org rather than assuming it has none —

```bash
sf data query -q "SELECT DecisionTable.DeveloperName, SourceFieldName, Operator, Value FROM DecisionTableSourceCriteria WHERE DecisionTable.DeveloperName = '<table>'" --target-org <sf_alias>
```

Never generalise one source's timestamp to a sibling table, and never compare against rows the
table would have excluded anyway.

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

### Wrong-currency price returned (multicurrency orgs)

A lookup step that does **not** pass `CurrencyIsoCode` matches the first row for the
product regardless of currency — so every currency silently prices at whichever row
the table returns first. The symptom is a *plausible* price, not an error.

**Fix:** add `CurrencyIsoCode` as an input on **every** lookup step that resolves a
currency-denominated value — list price, adjustment schedule, and adjustment tier
lookups alike. Missing it on the tier step alone still yields wrong discounts.

Currency must also *reach* the record for the step to filter on it. Records created
by quick actions and flows default to the **running user's** currency, not the
account's, so wire currency inheritance explicitly. Two before-save flows show the
pattern — note their **placement differs by scope**:

| Flow | Lives in | Why |
|------|----------|-----|
| `RLM_Default_AssetRateCard_Currency` | `force-app/main/default/flows/` | Foundational. An `AssetRateCardEntry` whose currency differs from its Asset is *always* wrong; the platform defaults it to USD and never inherits (262, no config remedy). Every multicurrency build needs this. |
| `RLM_Default_Opportunity_Currency` | `unpackaged/post_quantumbit/flows/` | Feature-specific. It **enforces** account currency, so a deliberately cross-currency Opportunity cannot be created while it is active — acceptable for the QB demo, not something to impose on every build. Gated behind the `quantumbit` flag. |

The distinction generalises: a flow that corrects an always-wrong platform default is
foundational; one that removes a legitimate user choice to suit a demo belongs in
that demo's feature bundle.

Offline guard: `python tests/test_qb_multicurrency_data.py`.
Live guard: `cci task run validate_multicurrency_rates`.

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
