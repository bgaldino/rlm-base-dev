# Expression Sets — Programmatic CRUD & Overlay Authoring

Use this skill when reading or mutating a BRE **Expression Set** (pricing
procedure, constraint procedure, qualification/discovery/rating procedure, …)
programmatically — via the **Connect API** (runtime/programmatic CRUD) or the
**Metadata API** (source-controlled authoring) — including building declarative
overlays that add/remove/update steps and variables. It is consumable by any AI
agent (Cursor, Claude Code, Copilot, Codex, Windsurf, Aider).

Expression Sets back more than pricing — the `interfaceSourceType` enum covers
`Constraint`, `DiscoveryProcedure`, `EventOrchestration`,
`QualificationProcedure`, `RatingProcedure`, and more — so this skill is generic
to the Expression Set engine. For where Expression Set CRUD fits into the
**pricing** layering model (recipes, recipe-table mappings, procedure plans,
context definitions), read `.cursor/skills/pricing-wiring/SKILL.md`.

> **Pinned to Release 262 / API v67.0.** Re-verify enums and behavior on the
> target release at merge time. The exhaustive detail — object/ID model,
> OAS-confirmed schema enums, every known error + resolution, and the
> verification checklist — lives in the detail file
> **`docs/references/expression-set-connect-api-reference.md`**. This skill is
> the task-level entry point.

## Quick Rules

1. **Choose the path by use case.** **Metadata API** (`expressionSetDefinition`
   XML + deploy) for source-controlled, git-tracked changes; **Connect API**
   (`tasks/rlm_expression_set_connect.py`) for runtime/programmatic CRUD. The
   step/param/variable shapes are identical, so a step authored once works for
   both.
2. **Every Connect mutation must HTML-unescape the payload before sending**
   (`normalize_html_entities`, default on). Raw GET output is HTML-escaped
   (`&quot;`/`&#39;`) and the engine rejects the entities. The Metadata path
   needs no equivalent — the XML parser decodes entities before the engine sees
   them.
3. **Run the pre-flight validator on any payload before a Connect call**
   (`validate_expression_set`, or `python scripts/ai/validate_expression_set.py`).
4. **The step graph is flat.** One `steps[]` array; hierarchy is encoded by
   `parentStep` (a step **name**), not nested arrays. Read `sequenceNumber` for
   execution order — GET returns top-level steps **alphabetically by name**, and
   `sequenceNumber` is **scoped per parent** (children restart at 1).
5. **Build `addSteps` overlays by capturing from a live GET**, not hand-authoring.
   Slice top-level steps and child steps differently (see [Authoring overlays](#authoring-overlays)).
6. **Capture a step's dependencies, not just the step** — classify every
   referenced name into one of three scopes (version variable → `addVariables`;
   custom external dep → `externalDependencies`; standard context → nothing).
7. **Mutations run deactivate → modify → reactivate**, in a guarded `finally`;
   the tasks enforce this, including the procedure-plan cascade.
8. **Test Connect CRUD on a disposable clone** (POST-create a renamed copy),
   never the shipped procedure — except for an intentional, approved change.

## DO NOT

- **DO NOT** send raw Connect GET output back in a PATCH/POST without
  HTML-unescaping it first — the escaped `&quot;`/`&#39;` values make engine parsing fail
  (flat: `Syntax error. Found '&'`; nested: opaque `INVALID_INPUT: Error
  processing JSON`). The mutation tasks do this automatically; only set
  `normalize_html_entities: false` to reproduce the failure.
- **DO NOT** keep the version-level `id` on a POST-create payload, and DO NOT
  drop it on a PATCH-replace. Create omits it; replace keeps it (the tasks
  handle this — `import_expression_set` strips it on create).
- **DO NOT** drop `contextDefinitions[].id` on a POST-create — context-node
  parameter data types fail to resolve without it (`Specify a valid data type
  for the … variable`).
- **DO NOT** change `resourceInitializationType` on an existing ES — it is
  **immutable once set**. Set it correctly at POST-create time (`Default` is
  common).
- **DO NOT** mutate a shipped/production Expression Set to experiment — test
  Connect CRUD against a disposable clone, except for an intentional, approved
  change.
- **DO NOT** treat a `removeSteps` (or any PATCH) that reactivates as proof it
  is correct — engine validation is **structural, not functional**. Removing a
  producer element can leave its consumers/filters orphaned and **silently
  misbehave** with no error. See [Removing steps](#removing-steps).
- **DO NOT** ship an `addSteps` overlay without accounting for **all three**
  dependency scopes (see [Capture dependencies](#capture-dependencies)). The
  validator warns on an undeclared **custom** (`__c`/`__r`) reference — declare
  it rather than suppressing the signal. Don't put `__std`/standard fields in
  `externalDependencies`; they aren't custom.
- **DO NOT** append a step to an existing version via a Tooling `Metadata`
  PATCH — it returns `FIELD_INTEGRITY_EXCEPTION`. Use create-with-content or a
  Metadata API deploy.

## Entry Conditions

| Situation | Use |
|---|---|
| Export, create, replace, overlay, or delete an Expression Set at runtime | This skill → Connect API tasks |
| Author/modify a procedure in git (source-controlled) | This skill → [Metadata API authoring](#metadata-api-authoring) |
| Capture a known-good element from one org and add it to another | This skill → [Authoring overlays](#authoring-overlays) |
| Where ES CRUD fits in the **pricing** setup order (recipes, plans, context) | `.cursor/skills/pricing-wiring/SKILL.md` |
| Object/ID model, full schema enums, every error + resolution, verification checklist | Detail file: `docs/references/expression-set-connect-api-reference.md` |
| Writing the Python task class itself | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |

---

## The CCI tasks

`tasks/rlm_expression_set_connect.py` wraps
`/connect/business-rules/expression-set` and handles the activation lifecycle,
HTML-entity normalization, version-id rules, and the procedure-plan cascade.

| Task | Verb | Use |
|---|---|---|
| `export_expression_set` | GET | Export a definition to JSON (`-o expression_set_api_name <DevName> -o output_file <path>`). |
| `import_expression_set` | POST create / PATCH replace | Create a new ES or replace an existing one whole (`-o input_file <path>`). Auto-detects create vs replace from whether the ES already exists. |
| `apply_expression_set_overlay` | declarative PATCH | Add/remove/update/reorder steps & variables without rewriting the whole definition (`-o overlay_file <path>`). |
| `delete_expression_set` | DELETE | Destructive; requires `-o confirm true`. Whole ES, or one version via `-o version_api_name`. |
| `validate_expression_set` | — (org-less) | Pre-flight a JSON file offline: `-o file <path> -o kind definition\|overlay`. CLI form: `python scripts/ai/validate_expression_set.py <file> [--definition\|--overlay]`. |

Common options on the mutation tasks: `dry_run` (log without mutating),
`skip_validation` (bypass the pre-flight — avoid), `normalize_html_entities`
(default true — leave on), `activate_after_import`/`activate_after_apply`,
`cascade_deactivate_procedure_plan`, `max_wait_seconds`/`poll_interval_seconds`.

---

## Mutation lifecycle (the tasks enforce this)

An **enabled version cannot be modified or deleted**, so every mutation runs
**deactivate → PATCH/POST → reactivate**, in a guarded `finally`:

1. If a `ProcedurePlanDefinitionVersion` references the ES, deactivate it first
   (the cascade) — an active plan version locks the ES version.
2. Deactivate the `ExpressionSetVersion`.
3. HTML-unescape the payload, then PATCH/POST.
4. On success, reactivate (idempotent — a PATCH body with `enabled:true` already
   reactivates the version). On failure, **leave it deactivated and raise** —
   PATCH is non-atomic, so a half-applied mutation must not be re-enabled.

Pre-flight ordering is **validate (still-escaped) → strip read-only fields →
normalize entities → Connect call**. The overlay task runs its
overlay↔definition cross-check (placement/update/reorder/remove targets must
exist) **before** any deactivation, so a typo'd target fails while the version
is still active.

### Verb-specific field handling

| Concern | POST (create new) | PATCH (replace existing) |
|---|---|---|
| version-level `id` | **omit** (task strips it on create) | **keep** (matches version in place) |
| top-level `id`/`error` | strip (output-only) | strip (output-only) |
| `contextDefinitions[].id` | **keep** — else context-node param data types fail (`Specify a valid data type for the … variable`) | n/a |
| `resourceInitializationType` | set correctly up front (`Default` common); **immutable after** | must equal stored value (task aligns it once) |
| `usageType` | set correctly (`DefaultPricing` for pricing, `Bre` for BRE; a wrong value like `sample` means the ES won't surface in UI / be invocable) | unchanged |

### Reading GET output — serializer gotchas

- Top-level steps come back **alphabetically by name**, NOT by `sequenceNumber`.
  Always read `sequenceNumber` for execution order; never trust the array index.
- `sequenceNumber` is **scoped per parent** — child steps restart at 1 under
  each parent.
- JSON-in-string values (`customElement.parameters[].value`,
  `advancedCondition.criteria[].value`, formula text) are **HTML-escaped**.
- Version identity is resolved from the `ExpressionSetVersion` sObject (source of
  truth), not the GET body — GET can transiently serve a stale version apiName.

---

## <a name="authoring-overlays"></a>Authoring overlays (declarative add/remove/update/reorder)

`apply_expression_set_overlay` takes a small overlay file rather than a full
definition. Placement is declared by anchor, not numeric sequence:

```json
{
  "expressionSetApiName": "RLM_DefaultPricingProcedure",
  "versionApiName": "RLM_DefaultPricingProcedure_V1",
  "addSteps": [
    { "name": "MyStep", "stepType": "BusinessKnowledgeModel",
      "placement": { "afterStep": "Mapcontexttagstocommonpricingvariables" },
      "customElement": { "parameters": [ /* … */ ] } }
  ]
}
```

To capture a real, known-good element: GET it from an org that already has it,
then slice out the step(s) into an `addSteps` overlay. **A top-level step and a
child step are sliced differently:**

| | Top-level step | Child step |
|---|---|---|
| `sequenceNumber` | **drop it** — the task computes the final slot and renumbers siblings | **keep it** — scoped per parent, children start at 1 |
| `placement` | **add** (`afterStep` / `beforeStep` / `sequenceNumber`) | **omit** — children ride with their parent, not placed independently |
| `parentStep` | absent | **keep** (a step **name**) |

Because the step graph is **flat** (one `steps` array linked by `parentStep`,
not nested `steps` arrays), a nested subtree (e.g. a `ListGroup` parent + its
`AdvancedListFilter` and `AssignmentElement` children) becomes one `addSteps`
array: the parent (with `placement`) immediately followed by each child carrying
`parentStep` + its own `sequenceNumber`. Order the parent before its children in
the array. Always HTML-unescape captured values and run the validator before
applying.

### <a name="capture-dependencies"></a>Capture the steps' dependencies, not just the steps

An `addSteps` element references variables/fields by name — in
`customElement.parameters[]` where `type: Parameter` (the name is the `value`) or
`type: Formula` (field names appear **inside the expression string**), and in
`advancedCondition.criteria[].sourceFieldName`. Each reference resolves to one of
**three** scopes, handled differently:

| Scope | How to tell | Overlay action |
|---|---|---|
| **Version-level variable** | the name appears in the source version's `variables[]` (`type: Constant`/`Variable`/`LocalListVariable`/…) | if the **target** lacks it, ship it in `addVariables` |
| **Custom external dependency** | a custom field/relationship (`__c`/`__r`) or custom `ContextDefinition` node — **not** in `variables[]`, not standard | declare it in `externalDependencies` — the overlay can't create it; the target must already define it and map it into the bound context |
| **Standard context** | `__std` fields **and no-suffix names** — standard fields shipped with the standard context definitions, supplied by the bound `ContextDefinition` (e.g. `NetUnitPrice`, `ItemDetailListPrice__std`) | nothing — present wherever the standard context is bound |

The trap: the source org *has* the version variable / custom field, so the
captured element looks self-contained — but applied to a target lacking it, the
step references something undefined. **To classify:** collect every `Parameter`
value, `Formula` token, and `sourceFieldName` the extracted steps use; intersect
with the source version's `variables[]` (→ those, used only by your new steps,
are `addVariables`); of the rest, the `__c`/`__r`/custom-node names are
`externalDependencies` and the `__std`/no-suffix names are standard context.

The validator emits two complementary warnings:
- the overlay↔definition cross-check warns when an added step references a
  **version-level variable** that is neither in `addVariables` nor in the target;
- `validate_overlay` warns when an added step consumes a **custom reference**
  (`__c`/`__r`) not declared in `externalDependencies` — so the requirement gets
  documented rather than failing only at apply time against a target that lacks
  the field.

#### The `externalDependencies` block

Declarative metadata for what the overlay does **not** create (in contrast to
`addVariables`, which it does) — what the target org must already have. All keys
optional; the apply task ignores the block, the validator checks its shape and
uses it to silence the custom-reference warning:

```json
"externalDependencies": {
  "customFields":  ["SalesTransaction_Hospitals__c (mapped into RLM_SalesTransactionContext)"],
  "contextNodes":  ["<custom ContextDefinition node>"],
  "contextFields": ["<custom context field, if any>"],
  "note": "why these are required and where they're mapped"
}
```

(`__std`/standard fields don't belong here — they ship with the standard
context.)

### <a name="removing-steps"></a>Removing steps — validation is structural, not functional

A `removeSteps` (or any PATCH) that passes validation and reactivates is **not**
proof it is correct. Connect/engine validation is **structural** (the graph
shape is legal; every variable still has *a* producer somewhere) — **not
functional** (the *right* producer feeds a given line subset). Removing a
producer element while leaving its consumers/filters in place can yield a
procedure that activates and runs but **silently misbehaves** — for example,
removing a price-producing element whose output variable is also produced by
other steps keeps the graph structurally valid, but a `ListGroup`/filter that
selected that element's target subset is now left with nothing computing its
result, mispricing that scenario with no error.

Before removing a step: check what consumes its **outputs** and whether any
**filter/`ListGroup` selecting its target subset** is left orphaned; if so,
remove or rewire those too. Always do removals on a **disposable clone** first
and inspect the re-exported graph + a functional test (e.g. a test repricing) —
never judge a removal by "it reactivated."

---

## <a name="metadata-api-authoring"></a>Metadata API authoring (source-controlled path)

To author or modify a procedure in git, edit `expressionSetDefinition` metadata
and deploy it via the repo's pipeline (`cumulusci.tasks.salesforce.Deploy`, e.g.
the `deploy_expression_sets` / `deploy_post_prm_pricing_expression_sets` tasks).
All shipped procedures load this way.

Characteristics:

- **Handles nested step graphs** — shipped metadata contains the full nested
  graph and deploys.
- **Validation errors are specific and actionable** — e.g. *"ListGroup can not
  be empty"*, *"Select list filter as the first element in list group"*,
  *"Local variables aren't supported when a business element is used in a list
  group; specify a list variable"*. Each names exactly what to fix.
- **No activation lifecycle** — no deactivate/reactivate, no version-id juggling,
  no entity normalization (the XML parser decodes entities), no procedure-plan
  cascade. Edit source XML and deploy.
- **Source-controlled and diffable.**
- **Shape parity with Connect:** the Metadata XML step/param/variable shapes are
  identical to the Connect JSON shapes (only diffs: XML adds `<label>`, uses the
  legacy-misspelled `<shouldExposExecPathMsgOnly>`, and omits empty
  `*MessageTokenMappings`). A step authored once maps cleanly between
  representations.

For new-version semantics rather than in-place edit, prefer **create-with-content**
(Tooling-create a new `ExpressionSetDefinitionVersion` from the prior version's
`Metadata`) over create-then-PATCH — see the detail file.

---

## Examples

Shipped overlays in `datasets/expression_set_overlays/` are generally
applicable examples. Environment-specific examples live under
`docs/references/expression-set-overlay-examples/` so they remain available for
study without looking like safe default overlays. Capture each from a live GET,
HTML-unescape, validate, cross-check, then apply to a **disposable clone** before
any real target.

| Overlay | Shape | Dependency scopes demonstrated |
|---|---|---|
| `map_line_item.json` | flat, single step (`actionType: BreakdownLineMapping`; maps `SalesTransactionItem` → `SalesTransactionItemDetail`, 18 `sectionJsonStringN` field-mappings) | standard context only — no `addVariables`, no `externalDependencies` |
| `discount_distribution.json` | **nested** — 3 `ListGroup` parents (each with an `AdvancedListFilter` + `AssignmentElement` child) feeding a `DiscountDistributionService` element | ships 4 `Constant_DDS_*` constants in `addVariables`; rest standard context (incl. `__std` discount fields) → no `externalDependencies` |
| `docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json` | **Environment-specific reference** — 2 `ListGroup` blocks, incl. a `FormulaBasedPricing` child computing `SalesTransaction_Hospitals__c - ItemStartQuantity` | **all three scopes**: `HospitalPrice` in `addVariables`; the custom field `SalesTransaction_Hospitals__c` (mapped into `RLM_SalesTransactionContext`) in `externalDependencies`; `ItemProductCode`/`ItemStartQuantity`/etc. standard context |

The facility-quantity example is intentionally not in
`datasets/expression_set_overlays/`: it depends on an org-specific custom field,
context mapping, and procedure-shape anchor. It also shows that a custom field
can be referenced inside a `Formula` string, not just a `Parameter`, so the
dependency scan must tokenize formula text, which the validator does.

### Map Line Item — special case

Salesforce's **documented** authoring path is the **UI paste** (the
`lds-adapters-industries-rule-builder` BKM `BreakdownLineMapping` blob). The
Connect overlay at `map_line_item.json` is the supported programmatic form and
should place the Map Line Item element right after Pricing Setting. Author the
`sectionJsonStringN` values **unescaped**.
Alternative: author it as an `expressionSetDefinition` `<steps>` block and deploy
via the Metadata API (identical shape).

---

## Validation Checks

Run before any Connect mutation and before a PR that touches overlays, the
tasks, or the validator:

```bash
# Pre-flight a payload offline (definition or overlay)
cci task run validate_expression_set -o file <path> -o kind overlay
python scripts/ai/validate_expression_set.py <path> --overlay   # CLI form

# Validator/schema unit tests (self-contained check() runner, no pytest)
python tests/test_expression_set_schema.py        # expect: all pass

# Token for manual API checks
yes | sf org auth show-access-token --target-org <sf_alias>
```

Checklist:

- [ ] Payload HTML-unescaped (or `normalize_html_entities` left on).
- [ ] Validator reports 0 errors; resolve or consciously accept warnings.
- [ ] Overlay `addSteps` account for all three dependency scopes; custom
      (`__c`/`__r`) refs declared in `externalDependencies`.
- [ ] Top-level vs child steps sliced correctly (placement vs `parentStep` +
      `sequenceNumber`).
- [ ] POST omits version `id` and keeps `contextDefinitions[].id`; PATCH keeps
      version `id`.
- [ ] `resourceInitializationType` matches the stored value (or set correctly at
      create).
- [ ] Applied + verified on a **disposable clone** before any real target; for a
      removal, verified functionally (test run), not just "it reactivated."
- [ ] After `cumulusci.yml` task/option edits:
      `python scripts/ai/generate_cci_reference.py` and commit the regenerated
      reference.

---

## Related References

- **Exhaustive detail (object/ID model, OAS schema enums, every error +
  resolution, Metadata authoring, verification checklist):**
  `docs/references/expression-set-connect-api-reference.md`
- **Pricing layering model (recipes, recipe-table mappings, procedure plans,
  context definitions) — where ES CRUD fits in pricing setup:**
  `.cursor/skills/pricing-wiring/SKILL.md`
- **Connect CRUD tasks:** `tasks/rlm_expression_set_connect.py`; pre-flight
  validator `tasks/expression_set_schema.py`; tests
  `tests/test_expression_set_schema.py`.
- **External doc link index:**
  `docs/salesforce/262/dev-guide/expression-set-business-apis-links.md`.
- **Writing the Python task class:**
  `.cursor/skills/cci-orchestration/custom-task-authoring.md`.
