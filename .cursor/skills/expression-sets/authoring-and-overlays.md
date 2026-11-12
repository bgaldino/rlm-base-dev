# Expression Sets — Authoring overlays & capturing dependencies

Progressive-disclosure sub-file of `.cursor/skills/expression-sets/SKILL.md`.
Read this when **building or applying a declarative overlay** (`addSteps` /
`removeSteps` / `updateSteps` / `reorderSteps` / `addVariables` /
`removeVariables`), capturing a known-good element from one org for another, or
removing a step safely. For the two authoring *paths* (Connect vs Metadata API),
the mutation lifecycle, verb-specific field rules, and GET serializer gotchas,
read the companion sub-file `metadata-vs-connect.md`.

Pinned to Release 264 / API v68.0.

---

## Authoring overlays (declarative add/remove/update/reorder)

An **expression set overlay** is a small JSON patch describing changes to a
definition's `steps` and `variables` (`addSteps` / `removeSteps` / `updateSteps` /
`reorderSteps` / `addVariables` / `removeVariables`) — applied without rewriting
the whole definition. (Not to be confused with a **procedure-plan overlay** in
`datasets/procedure_plan_overlays/`, applied by the `apply_procedure_plan_overlay`
task — a different object and tool.)

`apply_expression_set_overlay` (CCI) and `apply_expression_set_overlay.py` (the standalone
toolkit) take one of these overlay files rather than a full definition. Placement is
declared by **anchor**, not numeric sequence:

```json
{
  "expressionSetApiName": "RLM_DefaultPricingProcedure",
  "versionApiName": "RLM_DefaultPricingProcedure_V1",
  "addSteps": [
    { "name": "MyStep", "stepType": "BusinessKnowledgeModel",
      "placement": { "afterStep": "Get List Price" },
      "customElement": { "parameters": [ /* … */ ] } }
  ]
}
```

**Don't hand-author overlays — capture them.** GET a real, known-good element
from an org that already has it, then slice out the step(s). The
`export_expression_set_overlay.py` toolkit CLI does exactly this and pre-classifies the three
dependency scopes for you:

```bash
python scripts/expression_sets/export_expression_set_overlay.py --target-org <sf_alias> \
    --developer-name RLM_DefaultPricingProcedure \
    --step "Apply Discount" --after "Get List Price" \
    --out /tmp/apply_discount.overlay.json
```


### Existing steps and verification

See the toolkit guide’s [existing-step and read-back rules](../../../scripts/expression_sets/README.md#existing-steps-and-verification)
for `addSteps` replay, `updateSteps` edits, and verification shared by the CLI and CCI task.

### Several overlays on one procedure: merge locally, import once

Applying overlays one after another to the same procedure is not reliable. On a clone of the
default pricing procedure that already carried one applied overlay, applying a second with
`apply_expression_set_overlay.py --confirm` failed at the Connect PATCH with
`JSON_PARSER_ERROR: Unexpected end-of-input in null at [line:1, column:3]`. As designed for a
failed PATCH, the tool left the version **deactivated** (see SKILL.md → *Mutation lifecycle*)
[Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. The cause was not isolated: the
tool's simulated merge reported no errors, and the same overlays merged locally imported cleanly.

What worked on every run, in two orgs [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]:

1. Export the procedure import-ready (`export_expression_set.py --for-import --out <file>`).
2. Apply every overlay to that JSON locally, in order, with `apply_overlay()` from
   `scripts/expression_sets/_overlay.py` (the merge the CLI and CCI task use), passing the
   version API name.
3. Validate the merged definition (`python scripts/ai/validate_expression_set.py <file>`).
4. Import it once with `import_expression_set.py --input-file <file>` (preview, then `--confirm`),
   which replaces the existing procedure in place, or creates it under a new name.

This also recovers a version a failed PATCH left inactive: re-import a known-good merged
definition before reactivating it.

### Top-level vs child steps are sliced differently

| | Top-level step | Child step |
|---|---|---|
| `sequenceNumber` | **drop it** — the task computes the final slot and renumbers siblings | **keep it** — scoped per parent, children start at 1 |
| `placement` | **add** (`afterStep` / `beforeStep` / `sequenceNumber`) | **omit** — children ride with their parent, not placed independently |
| `parentStep` | absent | **keep** (a step **name**) |

Because the step graph is **flat** (one `steps` array linked by `parentStep`,
not nested `steps` arrays — see `metadata-vs-connect.md` → *Reading GET output*),
a nested subtree (e.g. a `ListGroup` parent + its `AdvancedListFilter` and
`AssignmentElement` children) becomes one `addSteps` array: the parent (with
`placement`) immediately followed by each child carrying `parentStep` + its own
`sequenceNumber`. Order the parent before its children in the array. Always
HTML-unescape captured values and run the validator before applying.

---

## Capture the steps' dependencies, not just the steps

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

**`trace_expression_set.py --step "<name>"` does this classification for you**
and prints the per-scope capture guidance (`→ ship in addVariables`,
`→ declare in externalDependencies`); `export_expression_set_overlay.py` bakes the result
straight into the emitted overlay.

The validator emits two complementary warnings:
- the overlay↔definition cross-check warns when an added step references a
  **version-level variable** that is neither in `addVariables` nor in the target;
- `validate_overlay` warns when an added step consumes a **custom reference**
  (`__c`/`__r`) not declared in `externalDependencies` — so the requirement gets
  documented rather than failing only at apply time against a target that lacks
  the field.

### The `externalDependencies` block

Declarative metadata for what the overlay does **not** create (in contrast to
`addVariables`, which it does) — what the target org must already have. It is an
**object** (not a list); all keys optional. The apply task ignores the block; the
validator checks its shape and uses it to silence the custom-reference warning:

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

### `addVariables` is for INPUT Constants only — never a step's output

A step's **output** variable is materialized **implicitly** by the platform from
the step's own output param (`section-N-output` on aggregate steps,
`formula-section-N-output` on formula steps). Do **not** also list that output
name in `addVariables`. Declaring it in both places registers the same variable
twice and the apply fails at POST time with:

```
INVALID_INPUT: A context variable with the name '<Name>' already exists.
```

`addVariables` is exclusively for **input** version variables the new steps
*consume* — `type: Constant` (e.g. a markup factor) or a `Variable`/
`LocalListVariable` scratch value — that the target version doesn't already
carry. Rule of thumb: if a name appears as a step's `output` param, it belongs
**only** to that step, not to `addVariables`.

`validate_overlay` now enforces this: any `addVariables[].name` that collides
with an `addSteps` step-output variable is a hard error, caught at authoring
time instead of at apply. (This is one of the deliberate divergences the toolkit
copy of the validator, `scripts/expression_sets/_schema.py`, carries over the
frozen `tasks/` copy.)

---

## Pricing procedures — element ordering lives in the pricing-procedures skill

Overlays on a **pricing** procedure must respect cross-element ordering rules the
engine enforces or depends on: no step other than Aggregate Price or Rounding Values
after DDS, in a procedure that has one (rejected with a misleading DDS error), aggregates
pinned after `DiscountDistributionService`, stale hydrated operands before the
tail, the pre-DDS line margin vs post-DDS header total caveat, and dropped
producer steps leaving their context mapping inert. Those rules, with the
evidence, live in
[`../pricing-procedures/procedure-anatomy-and-ordering.md`](../pricing-procedures/procedure-anatomy-and-ordering.md);
per-element configuration lives in `../pricing-procedures/elements/`.

---

## Conditional assignments — reset every line first

Each reprice hydrates a written field's **prior value from the record** before
the procedure runs. An overlay that assigns a field only inside filtered
branches (e.g. "discount above X → flag") therefore never clears it: a line
that stops matching every branch keeps its stale value. Start with an
unconditional step that resets the field on **every** line, then let the
branches overwrite it. Order matters — the reset must come before the branches.

- An empty-string `Constant` assigned to a Text field persists as **null**, so a
  `""` reset is a real clear, not a blank string.
- Add the overlay to a shipped procedure in a flow step **after**
  `activate_and_deploy_expression_sets` and **before** `prepare_procedureplans`.
  The apply deactivates and reactivates the procedure; doing it before
  procedure plans are wired to it avoids cascading through those plans.

Worked example: `datasets/expression_set_overlays/approval_flags.json`
(applied by `prepare_approvals_pricing`). The `RLMApprovalFlagsReset`
`ListGroup` clears both flag fields on every line, then one `ListGroup` per
band sets them. That overlay selects "every line" with an
`IsNull OR IsNotNull` filter on the same field; that is how this example does
it, not a platform requirement.

---

## Removing steps — validation is structural, not functional

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
remove or rewire those too. `trace_expression_set.py --variable <output>` shows
every consumer of a step's output (the safe-removal view), and `--orphans`
surfaces consumed-with-no-producer names left behind. Always do removals on a
**disposable clone** first and inspect the re-exported graph + a functional test
(e.g. a test repricing) — never judge a removal by "it reactivated."
For pricing procedures, the removed step's context mapping also goes inert:
[`../pricing-procedures/procedure-anatomy-and-ordering.md`](../pricing-procedures/procedure-anatomy-and-ordering.md)
→ *Removing a step leaves its context mapping inert*.

---

## Related

- Authoring paths, mutation lifecycle, verb-specific field rules, GET serializer
  gotchas, Metadata API authoring, create-with-content:
  `.cursor/skills/expression-sets/metadata-vs-connect.md`
- The standalone toolkit (`export_expression_set_overlay` / `trace` / `apply_expression_set_overlay` / …):
  `scripts/expression_sets/README.md`
- Exhaustive object/ID model, schema enums, every error + resolution:
  `docs/references/expression-set-connect-api-reference.md`
- Worked overlay examples (all three scopes): `SKILL.md` → *Examples*.
- The shipped overlays, which of them run in the build, and the file format:
  `datasets/expression_set_overlays/README.md`
