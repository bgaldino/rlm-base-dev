---
name: pricing-procedures
description: >-
  Configure, verify, and troubleshoot Revenue Cloud pricing procedure elements
  (Aggregate Price, discounts, Price Revision, DDS, Proration, and others), their
  ordering, discovery procedures, and day-2 pricing operations. Use expression-sets
  for generic CRUD and overlays, pricing-wiring for build sequencing.
---

# Pricing Procedures — Element Configuration and Ongoing Management

Use this skill to **configure and maintain** a Revenue Cloud pricing procedure in a
real org: what each pricing element computes, how to fill in its Builder fields **and**
the matching metadata/Connect parameters, where it has to sit, which limits apply,
and how to tell whether it works. It is written for SEs, partners, and AI agents
working on customer procedures, not only for this repo's build. Any agent can read it
(Cursor, Claude Code, Copilot, Codex, Windsurf, Aider).

The neighbouring skills own the mechanics this one builds on:

| Concern | Owner |
|---|---|
| Export, import, overlay, activate, delete any Expression Set; labels; HTML-unescape; version-id rules | [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md) |
| Where pricing work slots into the build (recipes, recipe-table mappings, plan overlays, flow order, placeholders) | [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) |
| The decision tables that elements look up: definition, refresh, staleness | [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md) |
| Context definitions, tags, mappings, persistence | [`../context-service/SKILL.md`](../context-service/SKILL.md) |
| Rating procedures (usage) | [`../usage-consumption/SKILL.md`](../usage-consumption/SKILL.md) |
| Constraint (CML) procedures | [`../constraint-models/SKILL.md`](../constraint-models/SKILL.md) |

> **Pinned to Release 264 / API v68.0.** Each element file tags its claims with a
> source: **[Help]** (the 264 Help snapshot under `docs/salesforce/264/help/`),
> **[Dev guide]**, **[Repo]** (shipped XML in this repo), **[Core]** (Salesforce source
> behavior), **[Live]** (verified on an org). A live org of the target release beats
> every other source. Treat untagged or "inferred" claims as hypotheses until you
> have verified them.

## Quick Rules

1. **Find the procedure the org actually runs before touching anything.** It may not
   be `RLM_DefaultPricingProcedure`. See [Discovery](#discovery).
2. **Change a clone, then promote it.** Clone the procedure (or create a new version),
   configure it, Simulate, and only then activate it or point Revenue Settings at it.
   Never experiment on the active shipped procedure.
3. **Follow the ordering rules.** Pricing Setting comes first. Nothing goes after the
   DDS → Aggregate → Rounding closing block, and no `FormulaBasedPricing` step goes
   after it. Aggregate Price comes after Derived Price and DDS. See
   [`procedure-anatomy-and-ordering.md`](procedure-anatomy-and-ordering.md).
4. **Put line-scope logic in a List Group.** A filter (`AdvancedListFilter`) selects
   the lines, and the element runs only on them. Keep lanes mutually exclusive.
5. **Every reprice reloads written fields from the record.** Reset a conditionally
   written field on every line before the branches that set it. Don't read a value
   before the element that recalculates it.
6. **An element that reads a decision table needs its table active, refreshed and
   mapped in the procedure's pricing recipe.** A stale table prices wrongly **without
   an error**.
7. **Verify with Simulate JSON, not only the waterfall.** Aggregate Price, Pricing
   Setting, Price Tracking and Stop Pricing never appear in the waterfall. Then check
   the persisted field on a real quote.
8. **Capture the element from a working org rather than typing it by hand.** The
   parameter encoding (`section-N-…`, `condition-N-…`) is undocumented and strict.
   Slice it with the expression-sets toolkit, then edit it.

## DO NOT

- **DO NOT** mutate an active, shipped or customer procedure to experiment. Use a
  disposable clone (expression-sets Quick Rule 8).
- **DO NOT** add a `FormulaBasedPricing` step after the closing block, and don't move
  the aggregates above DDS to make room for it. The error blames DDS, and moving the
  aggregates breaks `TotalAmount`.
- **DO NOT** list an element's output variable (for example `section-N-output` on
  Aggregate Price) in an overlay's `addVariables`. The platform creates it and the
  apply fails with `A context variable with the name … already exists`.
- **DO NOT** read a tag in a way that writes back into its own input, for example
  `NetUnitPrice → aggregate → InputUnitPrice → NetUnitPrice`. That is a pricing loop.
- **DO NOT** assume `SUM`-only, line-scope-only or rounding-free behavior is a platform
  limit because the shipped procedure looks that way. It describes what ships.
- **DO NOT** activate a procedure right after changing its decision tables. Make a
  small edit, save, then activate it [Help].
- **DO NOT** claim an element change works because the procedure saved or reactivated.
  Validation is structural, not functional. Simulate and re-price a real quote.

## Entry Conditions

| Situation | Read |
|---|---|
| Configure or fix one element (fields, parameters, limits, errors) | Its file in [Element catalog](#element-catalog) |
| Add, move or remove elements; any ordering error; stale or lagging values | [`procedure-anatomy-and-ordering.md`](procedure-anatomy-and-ordering.md) |
| Which procedure runs, Simulate/activate, procedure plans, output resolution, symptoms without an error | [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) |
| Waterfall, price logs, Operations Console, execution messages, PST order, parallel execution, Apex hooks, limits | [`runtime-and-observability.md`](runtime-and-observability.md) |
| Prices shown while browsing products (Product Discovery) | [`discovery-procedures.md`](discovery-procedures.md) |
| Export/import/overlay/activate mechanics, Connect errors | [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md) |
| Recipe-table mappings, procedure-plan overlays, build flow order | [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) |
| Building ramp quotes end to end | [`../ramped-quotes/SKILL.md`](../ramped-quotes/SKILL.md) |

## <a name="discovery"></a>Discovery

Find out what the org runs and what the procedure contains before you plan a change:

```bash
# Every pricing procedure and its ACTIVE version (--versions marks [ACTIVE]).
python scripts/expression_sets/list_expression_sets.py --target-org <sf_alias> \
    --type PricingProcedure --versions

# The step tree in execution order, with each step's parameters.
python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> \
    --developer-name <PRICING_PROCEDURE> --params

# Who writes and who reads a tag (before you add a writer or reader).
python scripts/expression_sets/trace_expression_set.py --target-org <sf_alias> \
    --developer-name <PRICING_PROCEDURE> --variable <Tag>
```

Then confirm which procedure Revenue Settings actually uses and whether a procedure plan
calls it (see [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md)).
To copy a known-good element between orgs, slice it into an overlay with
`export_expression_set_overlay.py` (expression-sets → script routing).

## <a name="element-catalog"></a>Element catalog

Builder element → `actionType` in metadata/Connect → sub-file. "Shipped" is a
snapshot of the procedures this repo deploys; check it again with the discovery commands.

| Builder element | `actionType` | Sub-file | Shipped here |
|---|---|---|---|
| Pricing Setting | `PricingSettings` | [`elements/pricing-setting.md`](elements/pricing-setting.md) | yes |
| Map Line Item | `BreakdownLineMapping` | [`elements/map-line-item.md`](elements/map-line-item.md) | yes |
| List Price (incl. contract pricing) | `ListPrice` | [`elements/list-price.md`](elements/list-price.md) | yes |
| Derived Price | `DerivedPricing` | [`elements/derived-price.md`](elements/derived-price.md) | PRM, Recalc |
| Decision table / matrix lookup | `GetOutputsFromDecisionTable`, `GetOutputsFromDecisionMatrix` | [`elements/decision-table-lookups.md`](elements/decision-table-lookups.md) | no |
| Volume Discount, Tier Discount | `VolumeDiscount`, `VolumeTierDiscount` | [`elements/volume-and-tier-discount.md`](elements/volume-and-tier-discount.md) | volume |
| Manual Discount | `ManualDiscount` | [`elements/manual-discount.md`](elements/manual-discount.md) | yes |
| Attribute-Based Price | `AttributeDiscount` | [`elements/attribute-based-price.md`](elements/attribute-based-price.md) | yes |
| Bundle-Based Price | `BundleDiscount` | [`elements/bundle-based-price.md`](elements/bundle-based-price.md) | yes |
| Price Adjustment Matrix | `PriceAdjustmentMatrix` | [`elements/price-adjustment-matrix.md`](elements/price-adjustment-matrix.md) | PRM |
| Formula-Based Pricing | `FormulaBasedPricing` | [`elements/formula-based-pricing.md`](elements/formula-based-pricing.md) | yes |
| List Group / List Operation | `ListGroup` / `AdvancedListFilter` (step types) | [`elements/list-group-and-list-operation.md`](elements/list-group-and-list-operation.md) | yes |
| Assignment | `AssignmentElement` | [`elements/assignment.md`](elements/assignment.md) | yes |
| Aggregate Price | `GroupingAndAggregatePricing` | [`elements/aggregate-price.md`](elements/aggregate-price.md) | yes (SUM) |
| Price Propagation | `PricingPropagation` | [`elements/price-propagation.md`](elements/price-propagation.md) | no |
| Discount Distribution Service | `DiscountDistributionService` | [`elements/discount-distribution-service.md`](elements/discount-distribution-service.md) | yes |
| Price Revision (compound ramp uplift: [`price-revision-compound-uplift.md`](elements/price-revision-compound-uplift.md)) | `PriceRevision` | [`elements/price-revision.md`](elements/price-revision.md) | yes |
| Proration, Subscription Price | `Proration`, `SubscriptionPricing` | [`elements/proration-and-subscription.md`](elements/proration-and-subscription.md) | yes |
| Rounding Values | `RoundingValues` | [`elements/rounding-values.md`](elements/rounding-values.md) | no |
| Stop Pricing | `StopPricing` | [`elements/stop-pricing.md`](elements/stop-pricing.md) | no |
| Price Tracking | `MinimumPrice` | [`elements/price-tracking.md`](elements/price-tracking.md) | no |
| Promotion Execution | `PromotionExecution` (or `AdvancedPromotionExecution` / `GPMPromotionExecution`, by org enablement) | [`elements/promotion-execution.md`](elements/promotion-execution.md) | no |

Discovery-only elements (`MapProduct`, `RuleFetch`, `AssetDiscovery`) are covered in
[`discovery-procedures.md`](discovery-procedures.md).

## How a custom element is encoded

Most pricing elements are `stepType: BusinessKnowledgeModel` steps with an `actionType`
and a flat list of `customElement.parameters` (`customElement` is the nested payload, not
the step type). Each parameter has a `name`, a `type`
(`Literal` = a fixed value, `Parameter` = a context tag or variable, `Formula`,
`Lookup`, `PickList`), a `value`, and `input`/`output` flags [Dev guide, Repo]. Repeating
structures are numbered with zero-based indexes and an explicit count, for example
`section-count` with `section-0-…`, or `where-condition-count` with `condition-0-…`
[Repo]. Keep counts and indexes consistent when you add or remove an entry (inferred:
the counts drive iteration). List Group and List Operation are step types with no
custom-element parameters [Repo].

The parameter **names** are what the element files document. The step envelope
(`name`, `label`, `sequenceNumber`, `parentStep`, `shouldExposeConditionDetails`, …) and
how to round-trip it are expression-sets territory.

## Change workflow

1. **Discover** the active procedure and its plan ([Discovery](#discovery)).
2. **Clone** it, or create a new version. In the UI use *Save As*. With the API, follow
   expression-sets → disposable clone: change the top-level `apiName`, `name` and the
   version `apiName`.
3. **Configure** the element in Pricing Procedure Builder, or as metadata/overlay using
   the element file's *Metadata shape*. Map new tags in the context definition first
   (context-service).
4. **Check prerequisites**: the decision table is active and refreshed, the recipe
   mapping exists (pricing-wiring §A), and the context tags exist (pricing-wiring §D).
5. **Simulate** with representative lines and read the JSON output for the element's
   output tags.
6. **Activate** the version (and its procedure plan), or point Revenue Settings at the
   clone.
7. **Re-price a real quote** and query the persisted fields. Keep the clone and the test
   quote for the record.

## Examples

**Partner can't get Aggregate Price to work.** Read
[`elements/aggregate-price.md`](elements/aggregate-price.md) → *Troubleshooting*. Check
that the Output and GroupBy tags are at the same context level, that the step sits
after DDS, that its Where conditions exclude derived-price lines, that Write Back (a filter on
which lines receive the result) isn't combined with Roll Up, and that the result is read from Simulate JSON (it is not in the
waterfall).

**Add a header margin percent.** Don't add a trailing formula step: it is rejected after
the closing block and stale before it. Use a record formula field over the aggregated
cost and margin. See [`procedure-anatomy-and-ordering.md`](procedure-anatomy-and-ordering.md)
→ *Rule 1* and the margin caveat.

**Quantity discount by bands.** Choose Volume Discount (the whole quantity priced at the
band it reaches) or Tier Discount (each band priced separately) with
[`elements/volume-and-tier-discount.md`](elements/volume-and-tier-discount.md). Then
refresh the adjustment-tier decision table before you Simulate.

**Compound ramp uplift is flat.** Read [`elements/price-revision-compound-uplift.md`](elements/price-revision-compound-uplift.md)
→ prerequisites. A blank Uplift Method silently gives a standard (non-compound) uplift.

## Validation Checks

Before calling a pricing-procedure change done, or before opening a PR that changes a
procedure or this skill:

```bash
# Offline pre-flight of a definition or overlay JSON
python scripts/ai/validate_expression_set.py <path> --overlay   # or --definition

# Deploy of the TRACKED procedures (placeholders need the CCI task to resolve).
# This overwrites the org's procedures with the repo versions, including active shipped
# ones: run it only on a disposable or freshly built org, never to "check" a working one.
cci task run deploy_expression_sets --org <cci_alias>

# Skill/registry gates for skill edits
python scripts/ai/analyze_agent_tooling.py check
python scripts/ai/skill_manifest.py --check
```

Checklist:

- [ ] The active procedure was discovered, not assumed.
- [ ] The change was made on a clone or new version, Simulated, then activated.
- [ ] The ordering rules hold (no step after the closing block, aggregates after DDS).
- [ ] Decision tables used by the changed element are refreshed and mapped in the recipe.
- [ ] New output tags are mapped in the context definition if they must persist.
- [ ] A real quote re-priced as expected, checked by querying the persisted fields.

## Sub-files

- [`procedure-anatomy-and-ordering.md`](procedure-anatomy-and-ordering.md) — procedure
  shape, phase order of the shipped default, and the cross-element ordering rules (the
  closing block, DDS → aggregates, reload from the record, pricing loops). Read it before
  adding, moving or removing any element.
- [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) — default
  procedure and Revenue Settings, Simulate/activate/versions, procedure plans (summary),
  output resolution, context tag mapping, decision-table sync, and a symptom table for
  cases with no error.
- [`runtime-and-observability.md`](runtime-and-observability.md) — headless API check,
  waterfall/logs/decision explainer, Operations Console, batch jobs, execution messages,
  Place Sales Transaction order, parallel execution, Apex hooks, runtime guardrails, limits.
- [`discovery-procedures.md`](discovery-procedures.md) — Product Discovery pricing
  procedures and the discovery-only elements.
- `elements/*.md` — one file per pricing element (see the [Element catalog](#element-catalog)):
  what it computes, Builder field → parameter mapping, placement, rules and limits,
  metadata shape, shipped snapshot, how to verify, troubleshooting, open questions.
- [`elements/price-revision-compound-uplift.md`](elements/price-revision-compound-uplift.md)
  — compound ramp uplift on Price Revision: prerequisites, ramp-path bindings, tracked
  default vs the 264 template, the compounding arithmetic, and what can't compound.
