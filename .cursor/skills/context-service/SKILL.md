# Context Service — Context Definitions, Mappings & Lifecycle

Use this skill when reading, extending, applying, deploying, or debugging a
Salesforce Revenue Cloud **Context Definition** — the canonical data layer that
pricing, BRE/expression sets, the configurator, DocGen, billing, and DRO bind to
at runtime. A context definition declares **nodes** (an object hierarchy) and
**attributes**, then **maps** those attributes to SObject fields; engines
**hydrate** an instance via SOQL (honoring FLS) and read/write attributes by
**ContextTag**. Tags are the shared vocabulary between a context and the
expression-set steps that consume it. This skill is consumable by any AI agent
(Cursor, Claude Code, Copilot, Codex, Windsurf, Aider).

> **Pinned to Release 262 / API v67.0.** Enums, limits, and API behavior are
> grounded in `tasks/rlm_context_service.py`, `tasks/rlm_extend_stdctx.py`, the
> repo's context plans, `docs/references/context-service-utility.md`, Core UDD,
> the Connect OAS, and Salesforce Help — re-verify edge behavior on the target
> release at merge time. The detailed reference lives in two sub-files:
> **`data-model-and-api.md`** (object model, enums, endpoints, plan format,
> limits, MDAPI) and **`authoring-and-lifecycle.md`** (definition types,
> activation, versioning, upgrade/Sync, standard contexts, gotchas).

## Quick Rules

1. **Route by task.** *Extend* a standard context → `extend_context_*` /
   `extend_standard_context`. *Apply an additive plan* → `apply_context_*` /
   `manage_context_definition`. *Deploy tracked metadata* →
   `deploy_context_definitions`. *Inspect / validate* → the helper scripts in
   `scripts/context_service/` (Deliverable of this skill). See the routing table below.
2. **Extend, don't clone.** An *extended* definition (custom layer on a standard
   base) auto-upgrades via Sync and preserves the base's mandatory mappings; a
   *cloned/custom* definition does not. Only create-new when no standard base
   fits (e.g. `RLM_QuoteDocGenContext`). See `authoring-and-lifecycle.md`.
3. **`IsActive` lives on the version, not the definition.** A definition holds a
   version list; each version holds nodes + mappings; only one version is active
   at a time. `manage_context_definition` and `apply_context_*` update **in place
   by default** (`deactivate_before: false`, verified at
   `rlm_context_service.py:160-162`) — additive attribute/tag/mapping changes do
   not require a deactivate cycle.
4. **Deactivation is blocked while an active consumer references the
   definition** (ExpressionSet, ContextRules, PricingActionParameters, decision
   table). Deactivating a definition a pricing procedure uses **breaks that
   procedure** — unlink consumers first.
5. **Connect API vs SObject REST split.** Connect covers
   definitions/nodes/attributes/tags and **basic SOBJECT/CONTEXT mappings**.
   **Relationship-traversal hydration, `MappedContextDefinition` (CONTEXT-type
   `mappedContextDefinitionName`), and `IsTransient`** require **SObject REST** —
   the Connect PATCH silently ignores or rejects them.
6. **Preflight before mutating.** `apply_context_*` default to
   execute + activate + verify — they are **not** inherently a dry run. Lint the
   plan offline first (`python scripts/context_service/validate_context_plan.py`), then
   `manage_context_definition -o validate_only true` (or `-o dry_run true`), then
   run with `verify` on.
7. **Plans live in `datasets/context_plans/<Name>/manifest.json`** →
   `contexts/<plan>.json`. The 6 active plans (`Billing`,
   `ConstraintEngineNodeStatus`, `DocGen`, `PartnerAccount`, `PrmPricing`,
   `RampMode`) are known-good; `archive/` is legacy — do not apply it.

## DO NOT

- **DO NOT** include `primaryDomainObject` / `primaryObject` on a create payload
  — the create endpoint rejects it (`JSON_PARSER_ERROR`). The offline validator
  flags either key as an error.
- **DO NOT** expect a Connect `PATCH /context-mappings` to set
  `mappedContextDefinitionName` (silently ignored) or to accept a
  relationship traversal (rejected). Use **SObject REST** for both. And beware:
  a Connect PATCH re-run **wipes existing hydration** —
  `isDeleteExistingHydrationDetail` defaults **true**.
- **DO NOT** change `TransactionType` (or other inherited) mappings — they are
  inherited from the standard base and the task skips them.
- **DO NOT** edit a **Standard** definition (`__stdctx` suffix). Extend it.
- **DO NOT** name a custom artifact without a **`__c`** suffix on a
  standard/extended base; **DO NOT** reuse a decision table's label/API name as a
  context tag; **DO NOT** use spaces or special characters in a definition
  `name` (alphanumeric only; use a separate DisplayName).
- **DO NOT** assume a metadata deploy can activate/deactivate a definition or set
  the default mapping — those are manual/API steps
  (`ContextDefinition` is a single atomic MDAPI unit, `childXmlNames: []`).
- **DO NOT** run an `Override` upgrade/Sync expecting it to be safe — Override is
  **destructive** (deletes custom artifacts). Prefer `Sync`.
- **DO NOT** treat `force-app/main/default/contextDefinitions/` as
  auto-generated — it is **tracked** metadata deployed by
  `deploy_context_definitions`. Prefer plans + tasks for additive changes.

## Entry Conditions

| I need to... | Do this |
|--------------|---------|
| Extend a standard context (add a custom layer) | `extend_context_*` task (or `extend_standard_context` with `name`/`baseReference`); see `authoring-and-lifecycle.md` → extend-vs-clone |
| Apply an additive attribute/tag/mapping plan | `apply_context_*` task, or `manage_context_definition -o plan_file <manifest>`; preflight first (Quick Rule 6) |
| Create a brand-new custom definition | Plan with `"create": true` + `developerName`/`label` (e.g. DocGen); `manage_context_definition` |
| Understand an org's mapping / hydration | `python scripts/context_service/describe_context.py --target-org <sf_alias> --developer-name <name>` |
| Trace how an SObject field links to a tag/attribute (hydration) or back (persistence), or find unmapped attributes | `python scripts/context_service/trace_context.py --target-org <sf_alias> --developer-name <name> --field <field> \| --tag <tag> \| --unmapped` |
| Compare a definition across orgs, or a plan vs an org (drift) | `python scripts/context_service/diff_context.py` (org-vs-org or `--plan-file`) |
| Extract that drift into an applicable patch (plan JSON) | `python scripts/context_service/patch_context.py` → lint → `manage_context_definition` |
| Snapshot a live definition into a repo plan | `python scripts/context_service/export_context.py --target-org <sf_alias> --developer-name <name> --custom-only` |
| List all definitions in an org | `python scripts/context_service/list_contexts.py --target-org <sf_alias>` |
| Validate a plan before applying | `python scripts/context_service/validate_context_plan.py` (offline) |
| Apply a plan **without** CCI (experimental sf-CLI mirror of `manage_context_definition`) | `python scripts/context_service/apply_context_plan.py --target-org <sf_alias> --plan-file <manifest> --dry-run` first; drop `--dry-run` to mutate. Prefer the CCI task for build work |
| Deactivate a definition, or hard-delete a definition / custom artifacts | `python scripts/context_service/delete_context.py --target-org <sf_alias> --developer-name <name>` (deactivate is the default); hard delete needs `--confirm-delete` (+ `--deactivate-first`, deletes are blocked while active). EXPERIMENTAL, destructive |
| Make one granular in-place edit to an existing definition (flip `isTransient`, re-point the default mapping, add/remove a tag) | `python scripts/context_service/mutate_context.py --target-org <sf_alias> --developer-name <name> --set-transient <Node.Attr> <bool> \| --set-default-mapping <name> \| --add-tag <Node.Attr> <tag__c> \| --remove-tag <tag>` — previews unless `--confirm`; modifies/deletes need `--deactivate-first --reactivate` (only `--add-tag` runs on an active version). EXPERIMENTAL |
| Deploy tracked `contextDefinitions/` metadata | `deploy_context_definitions` |
| Upgrade after a release (Sync) | `authoring-and-lifecycle.md` → upgrade/Sync (`upgradeMode` Sync/Preview/Override) |
| Understand the object model, enums, endpoints, plan format, limits | `data-model-and-api.md` |
| Debug a Connect API error (JSON_PARSER, hydration wipe, blocked deactivate) | DO NOT list above + `authoring-and-lifecycle.md` → gotchas table |
| Author a pricing procedure / expression set that reads a context | `.cursor/skills/expression-sets/SKILL.md`, `.cursor/skills/pricing-wiring/SKILL.md` |

## Task + script routing

CCI tasks (see `.cursor/skills/cci-orchestration/tasks-reference.md` for the
generated list; all in group *Revenue Lifecycle Management*):

| Task | Class | Purpose |
|------|-------|---------|
| `extend_context_*` (sales_transaction, product_discovery, cart, billing, asset, fulfillment_asset, collection_plan_segment, rate_management, rating_discovery, contracts, contracts_extraction) | `rlm_extend_stdctx.ExtendStandardContext` | Extend the named standard context; `activate: true` by default |
| `extend_standard_context` | `rlm_extend_stdctx.ExtendStandardContext` | Generic extend: `name`, `baseReference`, `defaultMapping`, `startDate`, `contextTtl`, optional `plan_file` |
| `apply_context_ramp_mode` / `_constraint_engine_node_status` / `_prm_pricing` / `_billing_order` / `_docgen` | `rlm_context_service.ManageContextDefinition` | Apply the named additive plan; `deactivate_before: false`, `activate: true` |
| `manage_context_definition` | `rlm_context_service.ManageContextDefinition` | Generic apply: `plan_file` (required), `developer_name`/`context_definition_id`, `activate`, `dry_run`, `deactivate_before`, `validate_only`, `verify` |
| `deploy_context_definitions` | `cumulusci.tasks.salesforce.Deploy` | Deploy `force-app/main/default/contextDefinitions/` |

Helper scripts (`scripts/context_service/` — the first block is offline/read-only, the
second **mutates/destroys** and is EXPERIMENTAL; see the directory `README.md`):

| Script | Org? | Purpose |
|--------|------|---------|
| `validate_context_plan.py` | No (offline) | Lint plan JSON: enums, required keys, limits, `__c` rule, `primaryDomainObject` |
| `list_contexts.py` | Read-only | One row per definition: name, active version, isActive, isUpgradeAvailable |
| `describe_context.py` | Read-only | Pretty-print one definition: version → nodes → attrs → mappings → hydration |
| `trace_context.py` | Read-only | Trace field↔tag↔attribute both directions (hydration/persistence, gated by intents + fieldType); `--field`/`--tag`/`--attribute`/`--unmapped` |
| `diff_context.py` | Read-only | Diff a definition org-vs-org or plan-vs-org (drift): added / removed / changed |
| `patch_context.py` | Read-only | Extract a diff into an applicable **plan-JSON patch** (adds & updates; never mutates the org) |
| `export_context.py` | Read-only | Serialize a live definition back into repo **plan JSON** (`--custom-only` for the authoring layer) |
| `apply_context_plan.py` | **Mutates** (EXPERIMENTAL) | sf-CLI mirror of `manage_context_definition` — apply an additive plan / create a definition without CCI. `--dry-run` previews. **Prefer the CCI task for build work**; never wire this into a flow |
| `delete_context.py` | **Destructive** (EXPERIMENTAL) | Deactivate (default) or hard-delete a definition / custom artifacts. Hard delete is opt-in (`--confirm-delete`); three pre-flight guards (inheritance / active-state / dependents) refuse a bad delete. Orchestration in `_delete.py`. No production delete task exists |
| `mutate_context.py` | **Mutates** (EXPERIMENTAL) | One granular in-place edit to an existing definition: `--set-transient` / `--set-default-mapping` / `--add-tag` / `--remove-tag`. Previews unless `--confirm`; op-specific inheritance + active-state guards (only `--add-tag`, a pure insert, runs on an active version). Orchestration in `_mutate.py`. Prefer a plan via `manage_context_definition` for build work |

## Examples

```bash
# Apply the ConstraintEngineNodeStatus plan to the Sales Transaction context
cci task run apply_context_constraint_engine_node_status --org beta

# Preflight a plan before applying: offline lint, then dry-run, then verify
python scripts/context_service/validate_context_plan.py \
  datasets/context_plans/PrmPricing/manifest.json
cci task run manage_context_definition --org beta \
  -o plan_file datasets/context_plans/PrmPricing/manifest.json \
  -o validate_only true
cci task run manage_context_definition --org beta \
  -o plan_file datasets/context_plans/PrmPricing/manifest.json -o verify true

# Extend a standard context (adds a custom, auto-upgradable layer)
cci task run extend_context_sales_transaction --org beta

# Inspect an org (SF CLI alias — NOT the CCI alias)
python scripts/context_service/list_contexts.py --target-org rlm-base__beta
python scripts/context_service/describe_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext
```

## Validation Checks

- **Offline, always:** `python scripts/context_service/validate_context_plan.py` — must
  report 0 errors on the 6 active plans before you apply any of them.
- **Before mutating an org:** `manage_context_definition -o validate_only true`
  (or `-o dry_run true`), then run with `-o verify true`.
- **After applying:** `describe_context.py --target-org <alias>
  --developer-name <name>` to confirm nodes/attrs/mappings/hydration landed as
  intended; `list_contexts.py` to confirm the active version and upgrade state.
- **Behavioral changes** to `tasks/rlm_context_service.py` /
  `tasks/rlm_extend_stdctx.py` must be run against a **live scratch org** — a
  plan applying cleanly on one org's inherited base is the real test, not a
  dry run alone.
- **After editing `cumulusci.yml`** context tasks: regenerate the CCI reference
  (`python scripts/ai/generate_cci_reference.py`) and update any docs that name
  the old task; if a plan's objects/counts change, update its plan README and run
  `python scripts/ai/check_plan_readme_consistency.py <plan_dir>`.

## Related Skills / references

- `data-model-and-api.md` — object model, canonical enums, Connect + SObject-REST
  endpoints, three mapping types, repo plan-file format, guardrail limits, MDAPI.
- `authoring-and-lifecycle.md` — three definition types, extend-vs-clone,
  activation/deactivation, versioning, upgrade/Sync, standard contexts, gotchas.
- `docs/references/context-service-utility.md` — `manage_context_definition`
  option reference.
- `.cursor/skills/expression-sets/SKILL.md` — expression sets that consume a
  context via tags.
- `.cursor/skills/pricing-wiring/SKILL.md` — where context definitions fit in the
  pricing layering model.
- `.cursor/skills/revenue-cloud-data-model/SKILL.md` — the mapped SObjects.
