# Expression Set Programmatic Management — Reference

> **Release 262 / API v67.0.** Setup/admin reference for programmatically
> managing BRE Expression Sets / pricing procedures — **not** a runtime business
> API. Companion to `tasks/rlm_expression_set_connect.py` (the Connect CRUD
> tasks), `tasks/expression_set_schema.py` (the pre-flight validator), and the
> link index `docs/salesforce/262/dev-guide/expression-set-business-apis-links.md`.
> The Expression Sets skill (`.cursor/skills/expression-sets/SKILL.md`) is the
> task-level entry point; this file is the exhaustive detail behind it. For where
> Expression Set CRUD fits into the **pricing** layering model, see
> `.cursor/skills/pricing-wiring/SKILL.md`.
>
> Scope: programmatically reading and mutating pricing procedures during org
> setup/configuration. Two paths are available and both handle nested
> procedures: the **Connect API** for runtime/programmatic edits, and the
> **Metadata API** for source-controlled authoring. Use the verification
> checklist at the end before applying Connect mutations to a real target.

## Supported Management Paths

- **Connect API — full CRUD on expression sets, including nested pricing
  procedures.** GET (export), POST (create), PATCH (replace / declarative
  overlay), DELETE.
- **Mutations must normalize HTML entities first.** Connect GET escapes
  JSON-in-string values (`customElement.parameters[].value`,
  `advancedCondition.criteria[].value`, formula text) as `&quot;`/`&#39;`. The
  engine rejects those entities on input, so the mutation tasks `html.unescape`
  the payload before the Connect call (`normalize_html_entities`, default
  `true`). See [HTML-entity normalization](#html-entity-normalization).
- **Metadata API — source-controlled authoring.** Edit `expressionSetDefinition`
  metadata and deploy it (`cumulusci.tasks.salesforce.Deploy`). This is how all
  shipped procedures get into the org and gives specific, actionable
  validation errors. See [Metadata API authoring](#metadata-api-authoring).
- **Pre-flight schema validation** (`tasks/expression_set_schema.py`) runs before
  any Connect call, so a malformed payload fails locally with an actionable
  message. It also warns when a value still carries un-normalized HTML entities.
- **Choose by use case:** Connect for runtime/programmatic edits; Metadata for
  changes that should live in git. The step/param/variable shapes are identical
  between the two representations, so a step authored once works for both.

---

## The CCI tasks

| Task | Verb | Notes |
|---|---|---|
| `export_expression_set` | GET | Export a definition to JSON (export/inspect). |
| `import_expression_set` | POST (create) / PATCH (replace) | Create a new ES or replace an existing one. Handles nested graphs. |
| `apply_expression_set_overlay` | declarative PATCH | Add/remove/update/reorder steps & variables with a deactivate→modify→reactivate lifecycle. Handles nested graphs. |
| `delete_expression_set` | DELETE (whole) / sObject DELETE (one version) | Destructive — requires `confirm: true`. |
| `validate_expression_set` | — (org-less) | Run the pre-flight validator standalone on a definition or overlay JSON. |

The mutation tasks (`import`, `apply_overlay`) run the schema pre-flight (pass
`skip_validation: true` to bypass) and HTML-unescape the payload immediately
before the Connect call (`normalize_html_entities`, default `true`).

---

## Object / ID model

| Object | Key prefix | Role |
|---|---|---|
| `ExpressionSetDefinition` | `9QA` | Design-time definition; `DeveloperName` = the api name passed to tasks. |
| `ExpressionSet` (runtime) | `9QL` | **The `{id}` the Connect path expects.** |
| `ExpressionSetVersion` (runtime) | `9QM` | Carries `IsActive` (the activation toggle) + `ApiName`. sObject-deletable. |
| `ExpressionSetDefinitionVersion` | `9QB` | **Tooling object.** `FullName` + `Metadata` — the version-authoring route. |
| `ContextDefinition` | `11O` | Referenced by `{id, name}` (e.g. `RLM_SalesTransactionContext`). |
| `DecisionTable` | `0lD` | Expression-set dependency. |
| `ProcedurePlanOption` → `ProcedurePlanDefinitionVersion` | — | A procedure plan referencing the ES; blocks the ES version's deactivation until its plan version is deactivated (the reason for the cascade). |

**Resolution SOQL** (`ExpressionSetConnectBase`):
- api name → runtime expression set:
  `SELECT Id FROM ExpressionSet WHERE ExpressionSetDefinition.DeveloperName = '…'`
- runtime expression set → version (source of truth for identity / `IsActive`):
  `SELECT Id, ApiName, IsActive, VersionNumber FROM ExpressionSetVersion WHERE ExpressionSetId = '<ExpressionSetId>' ORDER BY IsActive DESC, VersionNumber DESC`
- referencing plans:
  `SELECT Id, ProcedurePlanSection.ProcedurePlanVersionId FROM ProcedurePlanOption WHERE ExpressionSetDefinitionId = '<ExpressionSetDefinitionId>'`

---

## Connect mutation lifecycle

The tasks encapsulate these rules; they matter when reading the code or
debugging a run.

1. **An enabled version cannot be modified or deleted.** A mutation runs
   **deactivate → PATCH → reactivate**.
2. **Reactivation is idempotent.** A full-graph PATCH whose body carries
   `enabled: true` re-activates the version itself, so the task checks the
   current `IsActive` and skips a redundant reactivation (which would otherwise
   hit the enabled-version guardrail). Handled by `_set_version_active`.
3. **PATCH is not atomic.** A failed (400) PATCH still commits the parts it
   accepted, so on failure the task **leaves the version deactivated** and raises
   loudly rather than re-enabling a half-mutated procedure.
4. **Version `id` handling differs by verb.** A PATCH (replace) body **must keep**
   the version-level `id` (from the `ExpressionSetVersion` sObject) so the server
   matches the version in place. A POST (create) of a new ES **must omit** the
   version `id`.
5. **Top-level `id`/`error` are output-only** and stripped before any
   PATCH/POST.
6. **Procedure-plan cascade.** If a procedure plan references the ES, its
   `ProcedurePlanDefinitionVersion` is deactivated before the ES version, then
   reactivated after.

---

## <a name="html-entity-normalization"></a>HTML-entity normalization

Connect GET escapes JSON-in-string values as `&quot;`/`&#39;` — e.g. a
`customElement.parameters[].value` comes back as `"{&quot;whereConditions&quot;:[]}"`
and an `advancedCondition.criteria[].value` as `"&#39;Evergreen&#39;"`.
`json.loads` returns those entity characters verbatim, so sending an
un-normalized payload back delivers literal `&quot;` to the engine's value
sub-parser, which rejects it.

**The mutation tasks `html.unescape` every string leaf before the Connect call**
(`_normalize_html_entities` / `_unescape_value`, toggled by
`normalize_html_entities`, default `true`). `html.unescape()` is the exact
inverse of one escape pass and a no-op on entity-free strings, so the recursive
walk is safe (the data contains no `&amp;`, so there is no double-escaping to
worry about).

**Why the Metadata API needs no equivalent step:** the shipped
`expressionSetDefinition` XML carries the *same* entities, but in XML `&quot;`/
`&apos;` are an entity layer the XML parser decodes (→ `"`/`'`) before the engine
sees the value. JSON has no such layer, so the Connect path unescapes explicitly.
The validator (`tasks/expression_set_schema.py`) emits a **warning** when a value
still contains HTML entities, flagging raw GET output before it reaches the org.

---

## POST-create vs. PATCH-replace

Both round-trip nested graphs; a few fields are handled differently:

| Concern | PATCH (replace existing) | POST (create new) |
|---|---|---|
| Version `id` | **Keep** (matches version in place) | **Omit** |
| `contextDefinitions[].id` | n/a | **Keep** — needed so context-node parameter data types resolve (omitting it yields `Specify a valid data type for the … variable`) |
| `resourceInitializationType` | Must equal the stored value (immutable — see below) | Set correctly up front (`Default` is common); cannot be changed later |
| `usageType` | unchanged | Set correctly (`DefaultPricing` for pricing, `Bre` for BRE); a wrong value (e.g. `sample`) means the ES won't surface in product UIs or be invocable |

---

## Known errors & conditions

A reference for the errors a mutation can surface and what each means. The tasks
handle the first three automatically.

| Error / condition | Meaning | Resolution |
|---|---|---|
| `An enabled Expression Set Version cannot be updated/deleted.` | The version is active; Connect won't modify or delete an active version. | Deactivate first (the tasks do this). |
| `The resourceInitializationType is set to null and cannot be changed.` | `ExpressionSet.ResourceInitializationType` is **immutable once set**, and the PATCH body's value must equal the stored value. GET reports `Off` even when the stored sObject field is `null` (common on seeded procedures), so copying GET output sends `Off` against a stored `null`. | Align the stored field once before PATCH (`_ensure_resource_initialization_type`). For a new ES, set it correctly at create time. *(Immutability observed empirically on 262.)* |
| `Specify a valid formula … Syntax error. Found '&'` (flat) / `INVALID_INPUT: Error processing JSON` (nested) | HTML-escaped values (`&quot;`/`&#39;`) reached the engine's value parser. The nested case surfaces as an opaque "Error processing JSON" because the failure is in a deeper parse path. | Normalize entities before sending (`normalize_html_entities`, default on). |
| `Specify a valid data type for the … variable` (on POST create) | A context-node parameter's data type can't resolve because `contextDefinitions[].id` was omitted from a create payload. | Keep `contextDefinitions[].id` on a POST. |
| `INVALID_ID_FIELD: Invalid identifier: 9QL…` (dependencies endpoint) | The dependencies endpoint expects an `ExpressionSetVersion` id (`9QM`), not an `ExpressionSet` id (`9QL`). | Call `/version/{9QM…}/dependencies`. |
| Transient version-apiName divergence | GET can briefly serve a stale clone version apiName disagreeing with the `ExpressionSetVersion` sObject (eventual-consistency in the GET serializer; not persistent). | Identity is resolved from the sObject (source of truth); `_check_version_name_consistency` logs a warning if GET disagrees. Re-GET / toggle activation until aligned. |
| Semantic rule-builder errors, e.g. `Select list filter as the first element in list group` | The step graph is genuinely invalid (ordering/shape). | Fix the graph; these messages are specific. The Metadata API surfaces the same class of message on deploy. |
| `FIELD_INTEGRITY_EXCEPTION` on a Tooling `Metadata` PATCH that appends a step | Appending a step to an existing version via Tooling PATCH is unreliable. | Prefer create-with-content (a new `ExpressionSetDefinitionVersion`) or the Metadata API deploy. |

> A real mutation failure can still be reported as an opaque server error by the
> PATCH/POST handler, so when a failure is opaque, **bisect the
> payload** — POST/Tooling *validation* messages are more specific than a PATCH's
> generic response. PATCH/CREATE/DELETE require
> `InteractionCalculation.userHasInteractionCalculationAdminAccess` (GET needs
> only user-level access); confirm the running user has it.

---

## Verified schema (OAS-confirmed)

Sourced from the generated Connect API OpenAPI spec (the closest published spec
to v67.0) and cross-checked against seeded procedure exports. These are the
enums the validator enforces.

**Top-level** (`ExpressionSetInputRepresentation`): `apiName`, `name`,
`description`, `usageType`, `interfaceSourceType`, `resourceInitializationType`,
`executionMode` (`Cloud|Local`), `executionScale` (`High|Low`), `usageSubtype`,
`contextDefinitions[]` (`{id, name}`), `versions[]`. Output-only: `id`, `error`.

- `interfaceSourceType`: `Constraint`, `DiscoveryProcedure`, `EventOrchestration`,
  `GpaCalculationProcedure`, `IntelligentDecisionStudio`, `ItServiceManagement`,
  `PricingProcedure`, `QualificationProcedure`, `RatingDiscoveryProcedure`,
  `RatingProcedure`, `Sample`.
- `resourceInitializationType`: `Default`, `Off`.

**Version** (`ExpressionSetVersionRepresentation`): `id` (**keep for PATCH**),
`apiName`, `name`, `description`, `versionNumber`, `rank`, `decimalScale`,
`enabled`, `startDate`, `endDate`, `showExplExternally`, `steps[]`, `variables[]`.

**Step** (`ExpressionSetVersionStepRepresentation`): `name`, `sequenceNumber`,
`stepType`, `actionType`, `parentStep` (**by name**), `resultIncluded`,
`description`, `customElement`, `assignment`, `conditionExpression`,
`subExpression`, `advancedCondition`, `aggregation`, `lookupTable`,
`hasNestedExplainability`, the three `*ExplainerTemplate`/`*MessageTokenMappings`
pairs, and the `should*` flags. **No `id`/`uniqueIdentifier` on steps.**

- `stepType` (complete, 9): `AdvancedCondition`, `AdvancedListFilter`, `Branch`,
  `BusinessKnowledgeModel`, `Condition`, `DefaultPath`, `ListFilter`, `ListGroup`,
  `SubExpression`.
- `actionType` (`BusinessKnowledgeModelEnumRepresentation`): **~130 values**, so
  the validator treats unknown values as a *warning*, not an error. Pricing-
  relevant ones include `PricingSettings`, `AssignmentElement`,
  `DiscountDistributionService`, `BreakdownLineMapping` (← Map Line Item),
  `ListPrice`, `DerivedPricing`, `PriceRevision`, `Proration`, `ManualDiscount`,
  `VolumeDiscount`, `AttributeDiscount`, `BundleDiscount`, `FormulaBasedPricing`,
  `SubscriptionPricing`, `GroupingAndAggregatePricing`.

**customElement.parameter** (`ExpressionSetCustomElementParameterRepresentation`):
`name`, `type`, `value`, `input`, `output`.
- `type` (complete, 5): `Formula`, `Literal`, `Lookup`, `Parameter`, `PickList`.

**Variable** (`ExpressionSetVersionVariableRepresentation`): `name`, `dataType`,
`type`, `collection`, `decimalPlaces`, `description`, `input`, `output`, `value`,
`lookupName`, `lookupType`, `objectName`, `resultStep`.
- `dataType` (complete, 14): `ActionOutput`, `Boolean`, `Context`, `ContextNode`,
  `Currency`, `Date`, `DateTime`, `DecisionMatrix`, `DecisionTable`, `Numeric`,
  `Percent`, `Sobject`, `SubExpression`, `Text`. **(NOT Number/Decimal/Double.)**
- `type` (5): `Constant`, `Formula`, `LocalListVariable`, `LocalNode`, `Variable`.
- `lookupType` (3): `DecisionMatrix`, `DecisionTable`, `SubExpression`.

**Serializer behaviors to know when reading GET output:**
- Top-level steps are returned **alphabetically by name**, NOT by
  `sequenceNumber`. Never infer execution order from the GET array index — read
  `sequenceNumber`.
- `sequenceNumber` is **scoped per parent**: child steps restart at 1 under each
  parent. The validator checks contiguity per scope.
- JSON-in-string values are **HTML-escaped** (see
  [HTML-entity normalization](#html-entity-normalization)).

---

## <a name="authoring-overlays"></a>Authoring overlays (`apply_expression_set_overlay`)

An overlay is a small JSON file with `expressionSetApiName`, `versionApiName`,
and any of `addSteps` / `removeSteps` / `updateSteps` / `reorderSteps` /
`addVariables` / `removeVariables`. The task GETs the live definition, applies
the overlay in memory, and PATCHes the result (deactivate → modify → reactivate).

**The reliable way to build `addSteps` is to capture from a live GET**, not to
hand-author (a hand-authored element is easy to get subtly wrong — wrong/missing
`actionType`, missing node params). GET a procedure that already has the element,
then slice the step(s) out. **A top-level step and a child step slice
differently:**

| | Top-level step | Child step |
|---|---|---|
| `sequenceNumber` | **drop it** — the task computes the final slot and renumbers siblings | **keep it** — scoped per parent, children start at 1 |
| `placement` | **add** (`afterStep` / `beforeStep` / `sequenceNumber`) | **omit** — children ride with their parent, not placed independently |
| `parentStep` | absent | **keep** (a step **name**) |

Because the step graph is **flat** (one `steps` array linked by `parentStep`, not
nested `steps` arrays), a nested subtree becomes one `addSteps` array: the parent
(with `placement`) immediately followed by each child (with `parentStep` + its
own `sequenceNumber`). List the parent before its children. Always HTML-unescape
captured values and run the validator before applying.

Shipped examples: `datasets/expression_set_overlays/map_line_item.json` (flat,
single step) and `discount_distribution.json` (nested — three `ListGroup` parents
each with an `AdvancedListFilter` + `AssignmentElement` child, followed by the
`DiscountDistributionService` element, **plus** 4 `Constant_DDS_*` version
constants in `addVariables`).

### Capture the steps' dependencies, not just the steps

An `addSteps` element references variables/fields by name — in
`customElement.parameters[]` where `type: Parameter` (the name is the `value`) or
`type: Formula` (field names appear **inside the expression string**), and in
`advancedCondition.criteria[].sourceFieldName`. Each reference resolves to one of
**three** scopes, handled differently:

| Scope | How to tell | Overlay action |
|---|---|---|
| **Version-level variable** | the name appears in the source version's `variables[]` (`type: Constant`/`Variable`/`LocalListVariable`/…) | if the **target** lacks it, ship it in `addVariables` |
| **Custom external dependency** | a custom field/relationship (`__c`/`__r`) or custom `ContextDefinition` node — **not** in `variables[]`, not standard | declare it in `externalDependencies` — the overlay can't create it; the target must already define it and map it into the bound context |
| **Standard context** | `__std` fields and no-suffix names — standard fields shipped with the standard context definitions, supplied by the bound `ContextDefinition` (e.g. `RLM_SalesTransactionContext`) | nothing — present wherever the standard context is bound |

The trap: the source org *has* the version variable / custom field, so the
captured element looks self-contained — but applied to a target lacking it, the
step references something undefined. To classify, collect every `Parameter`
value, `Formula` token, and `sourceFieldName` the extracted steps use; intersect
with the source version's `variables[]` (→ `addVariables`); of the rest, the
`__c`/`__r`/custom-node names are `externalDependencies` and the `__std`/no-suffix
names are standard context.

The validator emits two complementary warnings:
- the cross-check ([`validate_overlay_against_definition`](#authoring-overlays))
  warns when an added step references a **version-level variable** that is
  neither in `addVariables` nor in the target;
- `validate_overlay` warns when an added step consumes a **custom reference**
  (`__c`/`__r`) not declared in `externalDependencies` — so the requirement gets
  documented rather than failing only at apply time against a target that lacks
  the field.

#### The `externalDependencies` block

Declarative metadata for what the overlay does **not** create (in contrast to
`addVariables`, which it does) — what the target org must already have:

```json
"externalDependencies": {
  "customFields":  ["SalesTransaction_Hospitals__c (mapped into RLM_SalesTransactionContext)"],
  "contextNodes":  ["<custom ContextDefinition node>"],
  "contextFields": ["<custom context field, if any>"],
  "note": "why these are required and where they're mapped"
}
```

The apply task ignores it; the validator checks its shape and uses it to silence
the custom-reference warning. (`__std`/standard fields don't belong here — they
ship with the standard context.)

Shipped overlay examples:
- `discount_distribution.json` — references **19** names: **4** version-level
  constants (`Constant_DDS_Amount` = `"Amount"`, `_Percentage`, `_Override`,
  `_NetUnitPrice`, all `Constant`/`Text`) shipped in `addVariables`; the rest are
  standard context (`__std` discount fields + standard tags). No custom external
  dependency, so no `externalDependencies` block.
- `facility_quantity.json` — ships the `HospitalPrice` constant in
  `addVariables` and declares the **custom field
  `SalesTransaction_Hospitals__c` (mapped into `RLM_SalesTransactionContext`)**
  in `externalDependencies`. It references that field as a filter
  `sourceFieldName`, a `Parameter`, **and** inside a `Formula`
  (`SalesTransaction_Hospitals__c - ItemStartQuantity`). `ItemProductCode`,
  `ItemStartQuantity`, etc. are standard context.

### Removing steps — validation is structural, not functional

A `removeSteps` (or any PATCH) that passes validation and reactivates is **not**
proof it is correct. Connect/engine validation is **structural** (the graph shape
is legal; every variable still has *a* producer) — **not functional** (the
*right* producer feeds a given line subset). Removing a price-producing element
can leave a filter/`ListGroup` selecting that subset with no correct producer,
even if another step produces the same output variable elsewhere. Before
removing a step, check what consumes its outputs and whether a filter/`ListGroup`
selecting its target line subset is orphaned; do removals on a disposable clone
and verify with a test repricing, not by "it reactivated."

**Nested-child overlay rules:** Child steps carry `parentStep` and keep their
per-parent `sequenceNumber`; they do not use top-level `placement`. A later
`addSteps` entry may place itself after/before a sibling added earlier in the
same overlay, because `_add_steps` processes entries in array order. Forward
references to steps added later remain invalid.

---

## <a name="metadata-api-authoring"></a>Metadata API authoring (source-controlled path)

To author or modify a pricing procedure in git, edit `expressionSetDefinition`
metadata and deploy it via the repo's pipeline
(`cumulusci.tasks.salesforce.Deploy`, e.g. the `deploy_expression_sets` /
`deploy_post_prm_pricing_expression_sets` tasks). All 11 shipped procedures load
this way.

Characteristics:
- **Handles nested step graphs** — shipped metadata contains the full nested
  graph and deploys.
- **Validation errors are specific and actionable** — e.g. *"ListGroup can not be
  empty"*, *"a filter can't be the last or only step element in a group"*,
  *"Select list filter as the first element in list group"*, *"Local variables
  aren't supported when a business element is used in a list group; specify a
  list variable"*. Each names exactly what to fix.
- **No activation lifecycle** — no deactivate/reactivate, no version-id juggling,
  no entity normalization (the XML parser decodes entities), no procedure-plan
  cascade. You edit source XML and deploy.
- **Source-controlled and diffable.**
- **Shape parity with Connect:** the Metadata XML step/param/variable shapes are
  identical to the Connect JSON shapes (only diffs: XML adds `<label>`, uses the
  legacy-misspelled `<shouldExposExecPathMsgOnly>` — missing the second "e" — and
  omits the empty `*MessageTokenMappings`). The validator
  (`tasks/expression_set_schema.py`) covers both. A step authored once maps
  cleanly between representations.

Deploying to a scratch org skips the 75% Apex-coverage gate a production
`deploy validate` enforces; the `expressionSetDefinition` component validates
independently of that gate.

### Tooling / sObject versioning (alternative)

For new-version semantics rather than in-place edit:
1. Tooling-create a new `ExpressionSetDefinitionVersion` from the prior version's
   `Metadata` (bump `versionNumber` **and** `rank`, set `status`, drop the
   read-only `urls` key) — create-with-content.
2. Activate via `PATCH /sobjects/ExpressionSetVersion/{9QM…} {"IsActive":true}`.
3. Deactivate + `DELETE /sobjects/ExpressionSetVersion/{9QM…}` the old version.

Prefer create-with-content over create-then-PATCH (appending a step via a Tooling
`Metadata` PATCH returns `FIELD_INTEGRITY_EXCEPTION`). For most cases the
Metadata API deploy above is simpler.

---

## Map Line Item to Detail Item

Salesforce's **documented** method is the **UI**: open the Pricing Procedure, add
a Map Line Item element as the 2nd element (after Pricing Setting), and **paste a
JSON blob** into the element editor — there is no documented API path.

- The UI-paste blob is the **`lds-adapters-industries-rule-builder` LWC
  wire-adapter** shape (`componentName`, `businessKnowledgeModelName:
  "BreakdownLineMapping"`, `inputVariablesMappingText`,
  `outputVariablesMappingText`, `sectionJsonStringN`), **not** the Connect
  `ExpressionSetInputRepresentation`.
- The canonical mapping maps pricing variables → `ItemDetail*__std` outputs via
  BKM `BreakdownLineMapping` (`MapLineItemNodeInput: SalesTransactionItem`,
  `MapLineItemNodeOutput: SalesTransactionItemDetail`).
- The Connect overlay at `datasets/expression_set_overlays/map_line_item.json`
  is the supported programmatic form of the same element. It should be placed
  immediately after the pricing-settings step. Author the `sectionJsonStringN`
  values **unescaped** (`normalize_html_entities` leaves clean values as-is).
- **Automation options:** (a) the Connect overlay above, or (b) author the Map
  Line Item step as an `expressionSetDefinition` `<steps>` block and deploy via
  the Metadata API (see [above](#metadata-api-authoring)) — `BreakdownLineMapping`
  is a known-valid step and the metadata `customElement.parameters` shape is
  identical to the Connect shape. Fallbacks: Robot Framework driving the
  documented UI paste, or a Tooling create-with-content version.

---

## Endpoints & auth

- **Connect base:** `{instance}/services/data/v67.0/connect/business-rules/expression-set`
- **Dependencies** (GET): `/connect/business-rules/expression-set/version/{9QM…}/dependencies`
  → referenced `DecisionTable`s. Keyed by **version Id** (`9QM`); the `9QL`
  variant returns `INVALID_ID_FIELD`.
- **Tooling base:** `{instance}/services/data/v67.0/tooling/sobjects/ExpressionSetDefinitionVersion`
- **Token for manual API checks:** `yes | sf org auth show-access-token --target-org <sf_alias>`,
  or pull `instanceUrl`/`accessToken` from `sf org display --json`.
- **Validate a payload offline:** `python scripts/ai/validate_expression_set.py <file.json> [--overlay|--definition]`

Pinned to **262 / v67.0**. Re-verify on the target release at merge time —
platform behavior may change.

---

## Verification Checklist

Use this checklist before applying Connect mutations to a real target org.

1. Run the local validator on every definition or overlay payload.
2. Export the target expression set and confirm the overlay's anchors, update
   targets, removal targets, and required variables exist in that live shape.
3. For create/import testing, POST a uniquely named disposable clone and validate
   the exported clone before applying overlays.
4. Apply overlays to the disposable clone first, with `verify: true` and
   `normalize_html_entities` left at its default.
5. Re-export the clone and confirm the intended steps and variables landed.
6. Confirm the clone version and any cascaded procedure-plan versions are active
   after a successful run.
7. Delete disposable clones after inspection, unless the clone is intentionally
   retained for reviewer validation.
8. For removals, run a functional pricing test; structural validation alone is
   not sufficient.

### Docs note

Public enum listings can lag generated API schemas. Treat the generated OAS spec
and target-org behavior as the authority for enum support; the validator's enums
are OAS-sourced — see [Verified schema](#verified-schema-oas-confirmed).
