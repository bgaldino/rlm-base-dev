# Configurator behavior: what a rule does at runtime

Read this when a rule is correct in the model and the configurator does something
unexpected: a hidden choice keeps its value, a save raises a conflict, a rule seems to
ignore a field, or Place refuses a quote the configurator accepted.

Tags: `[Measured: 2026-11, 264 (USA796), ent-sb0 harness build]` means measured on a
264 build in the November 2026 batch; items tagged `[Open]` were not measured and must
not be taken as behavior.

## Clear a value when its controlling choice changes

A hide rule on attribute B hides B but **leaves its value**. To clear B when A is X:

1. Put `@(peelable = true)` on B. Without it, the save raises a conflict.
2. Give B a "None" picklist value.
3. Add the constraint "A is X implies B is None".

`B == ""` is refused on a picklist-backed attribute: "Enter an Attribute Picklist Value."
`[Measured: 2026-11, 264 (USA796), ent-sb0 harness build]`

## Hide or disable by a product field, or by the parent

- `@(productField = "<Field>")` loads a standard or custom Product2 field into a CML
  variable at activation: read-only, no null value, at most 50 fields and 20,000 products
  `[Help: cml-annotation-example-productfield]`.
- A multi-select picklist is `string[]`; `strcontain` and `strshare` test membership
  `[Help: cml-string-variable-functions-and-operators]`. Combining them with productField
  is not documented `[Open: not measured]`.
- Hide and disable name a relation or its types; there is no target "every component whose
  field is C". Condition the rule on the loaded value and list the types
  `[Help: cml-hide-disable-rule]`.
- `parent(attr)` reads a parent attribute inside a child rule
  `[Help: cml-best-practice-parent-products]`. A `filterExpression` relation annotation is
  not in the documented list, and it did not restrict which products a class relation
  offers when the products carry no attribute values in the model
  `[Open: filterExpression filtering of a class relation; not measured here]`.
- A hide rule on a component the user already selected: whether the line leaves the
  configuration, or stays because selected children are forced visible
  `[Open: not measured]`.
- A relation or type in more than one active model: a product belongs to one model; do
  not activate overlapping models (Quick Rule 7 in [SKILL.md](SKILL.md)).
- A disabled attribute displays as read-only, and inline attributes honour
  Is ReadOnly `[Open: not measured]`.

## What Place and PST do with configuration

Settings that decide whether defaults and messages are applied on a headless save
`[Measured: 2026-11, 264 (USA796), ent-sb0 harness build]`:

| Behavior | Setting |
|---|---|
| PCM attribute defaults are written | `addDefaultConfiguration=true` |
| `RequiredAttributeMissing` is checked, for Required attributes only | `validateProductCatalog=true` |
| Warning-severity configurator messages refuse Place | default `RunAndBlockErrors`; `RunAndAllowErrors` lets them through |
| An optional picklist with no default | no `QuoteLineItemAttribute` row and no message |

## Errors and logs

- `RevenueTransactionErrorLog` links to the quote through `PrimaryRecordId`, and the
  quote's related list shows it on 264. The `RunAndAllowErrors` path writes no log row.
  `[Measured: 2026-11, 264 (USA796), ent-sb0 harness build]`
- A configurator Error or Warning message raises the line's `ValidationResult`; quote
  `ValidationResult` values come from product code, not from CML
  `[Open: not measured here]`.

## Triggers and derived values

`QuoteLineRelationship` and `QuoteLineItemAttribute` do not allow Apex triggers. Place
writes relationships after the lines, so a value derived from the bundle needs a
line-level after-commit step ([computed-attribute-and-setup.md](computed-attribute-and-setup.md)).
`[Measured: 2026-11, 264 (USA796), ent-sb0 harness build]`

## Authoring surface

- The Metadata API carries a shell for a constraint model, not the CML body; the body is
  the `ConstraintModel` field and the constraint-version resource
  ([import-and-deploy.md](import-and-deploy.md)). `[Repo: tasks/rlm_cml.py]`
- Constraint Studio's own APIs are not in the 264 developer guide `[Open: not in the 264
  developer guide]`.
- Changing a model without deactivating it, and a no-downtime update, are not available:
  activation runs the checks and redeploys every active model
  ([import-and-deploy.md](import-and-deploy.md#active-models-and-downtime)).
- Summary component properties and adding a third-party component to the configurator UI
  `[Open: no repo guidance; configurator UI is outside this skill]`.
- Import Lines expands defaults but skips configuration rules `[Open: owned by
  transaction-line-editor]`.
- Recommend-rule results surface in Product Discovery, not in the configurator
  `[Open: not measured here]`.
