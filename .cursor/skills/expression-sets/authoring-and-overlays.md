# Expression Sets — Authoring overlays & capturing dependencies

Progressive-disclosure sub-file of `.cursor/skills/expression-sets/SKILL.md`.
Read this when **building or applying a declarative overlay** (`addSteps` /
`removeSteps` / `updateSteps` / `reorderSteps` / `addVariables` /
`removeVariables`), capturing a known-good element from one org for another, or
removing a step safely. For the two authoring *paths* (Connect vs Metadata API),
the mutation lifecycle, verb-specific field rules, and GET serializer gotchas,
read the companion sub-file `metadata-vs-connect.md`.

Pinned to Release 262 / API v67.0.

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

## Step ordering — no `FormulaBasedPricing` after the aggregate/DDS/rounding tail

The pricing procedure ends with a fixed tail block — Discount Distribution
Service (`DiscountDistributionService`), the `GroupingAndAggregatePricing`
aggregate steps, and Rounding Rules. A `FormulaBasedPricing` step placed **after**
that block is rejected, and the error message is **misleading** — it names DDS,
not your formula step:

```
INVALID_INPUT: You can add the Discount Distribution Service element only
before the Rounding Rules and Aggregate elements …
```

The real cause is ordering: a header-scope formula that depends on aggregate
outputs cannot sit after the aggregate/rounding tail. Two consequences for
authoring an overlay that adds a formula computed *from* aggregate results:

- Place `GroupingAndAggregatePricing` (SUM) steps with `afterStep` anchored to
  the **last existing aggregation** — they slot into the aggregate band cleanly.
- A `FormulaBasedPricing` step that consumes those aggregate outputs has **no
  slot that is both accepted *and* fed fresh operands**. This is subtler than
  "can't add a header-scope formula step" — you **can**: a top-level (no
  `parentStep`) `FormulaBasedPricing` step placed **before** the DDS/aggregate
  tail is accepted and does write to the record (live-proven with a manual
  `TotalMarginAmount__c / TotalAmount → TotalMarginPercent__c` step positioned
  just before DDS). But **before** the aggregates its operands still hold the
  values **hydrated from the record at the start of the reprice** — i.e. *last*
  reprice's numbers — so the formula lags one full reprice cycle (looks
  ~right on an unchanged quote, visibly off after any change). **After** the
  aggregates, where the operands are fresh, the tail barrier rejects it. So an
  in-engine header-scope formula rollup on top of aggregates is effectively
  unusable: compute that value another way (an additional aggregate/derivation
  step earlier in the graph, or a Salesforce formula field on the record) rather
  than a trailing formula step.

**"Can't I just move the aggregates (and the formula) higher?" — no.** The
aggregate band is pinned *after* `DiscountDistributionService` (DDS) by a real
data dependency, not merely by convention: DDS **rewrites** the per-line
`NetUnitPrice` / `ItemNetTotalPrice` that `TotalAmount` sums. Moving the SUM
above DDS would sum *pre-header-discount* prices → wrong total. And the barrier
is relative to the aggregate elements, not an absolute position — dragging the
aggregates up just drags the "no formula after aggregates" barrier up with them.
So a formula whose operands are post-aggregate header values genuinely has
nowhere legal to sit *with fresh operands*. (Grounding facts from the 262
`RLM_DefaultPricingProcedure`: every *shipped* `FormulaBasedPricing` step in it
is **line-scope** — each has a `parentStep` and runs *before* DDS; every
`GroupingAndAggregatePricing` step is **SUM-only** on a single line field; and
there are **no `RoundingValues` steps** at all, despite the error message naming
Rounding Rules. A **top-level** header-scope `FormulaBasedPricing` step is
nonetheless *permitted* before the tail — it just reads stale operands there, per
the point above; the "line-scope only" observation describes what ships, not a
hard platform constraint.)

### Caveat: pre-DDS line margin vs. post-DDS header total

A header cost/margin rollup built from the standard line fields carries a subtle
base mismatch worth flagging to whoever consumes the numbers. In
`RLM_DefaultPricingProcedure`, per-line **cost and margin** (`ItemTotalCost__std`,
`ItemMarginAmount__std`) are computed **before** DDS (in the
`Calculatecostandmarginforpricedlines` ListGroup), while `TotalAmount` is a
**post-DDS** aggregate. Consequences for a SUM rollup like this one:

- `SUM(ItemTotalCost__std)` → header total cost is unaffected by DDS (cost isn't
  touched), so it's always correct.
- `SUM(ItemMarginAmount__std)` → header total margin **amount** sums *pre-header-
  discount* line margins. On a quote with a **header discount**, that margin sits
  on a different base than `TotalAmount` / the booked prices, so a margin **percent**
  derived from the two would be internally inconsistent. On a quote with **no**
  header discount the bases coincide and everything ties out.

If a header margin percent is required, prefer a record-level formula field over
an in-engine step (see the ordering rule above), and be explicit about which base
it uses.

### Dropping an overlay step leaves its context mapping inert

If you remove a step that *produced* a value which a Context Definition mapping
persists (as we did with the blocked margin-percent step), the context mapping
does **not** error — it simply has nothing feeding it, so the field persists as
**null** on every reprice. Field + FLS + persist binding can all be present and
the field still never populates. When you drop a producing step, also remove (or
knowingly accept as inert) the field's context mapping so the schema doesn't
imply a value that never arrives.

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
