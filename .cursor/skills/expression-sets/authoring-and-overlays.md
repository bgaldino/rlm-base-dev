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

`apply_expression_set_overlay` (CCI) and `apply_overlay.py` (the standalone
toolkit) take a small overlay file rather than a full definition. Placement is
declared by **anchor**, not numeric sequence:

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

**Don't hand-author overlays — capture them.** GET a real, known-good element
from an org that already has it, then slice out the step(s). The
`export_overlay.py` toolkit CLI does exactly this and pre-classifies the three
dependency scopes for you:

```bash
python scripts/expression_sets/export_overlay.py --target-org <sf_alias> \
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
`→ declare in externalDependencies`); `export_overlay.py` bakes the result
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
- The standalone toolkit (`export_overlay` / `trace` / `apply_overlay` / …):
  `scripts/expression_sets/README.md`
- Exhaustive object/ID model, schema enums, every error + resolution:
  `docs/references/expression-set-connect-api-reference.md`
- Worked overlay examples (all three scopes): `SKILL.md` → *Examples*.
