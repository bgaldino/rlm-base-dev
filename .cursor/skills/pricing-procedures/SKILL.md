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
| Org setup the elements read: enablement, permissions, price/cost books, adjustment schedules, recipes, selling models, revision policies, pricing actions | [`../pricing-setup/SKILL.md`](../pricing-setup/SKILL.md) |
| The decision tables that elements look up: definition, refresh, staleness | [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md) |
| Context definitions, tags, mappings, persistence | [`../context-service/SKILL.md`](../context-service/SKILL.md) |
| Rating procedures (usage): the `RatingProcedure` / `RatingDiscoveryProcedure` step graph is expression-sets territory; building, rating and verifying metered demos is usage-consumption, and rate cards and rating setup is rate-management | [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md), [`../usage-consumption/SKILL.md`](../usage-consumption/SKILL.md), [`../rate-management/SKILL.md`](../rate-management/SKILL.md) |
| Constraint (CML) procedures | [`../constraint-models/SKILL.md`](../constraint-models/SKILL.md) |

> **Pinned to Release 264 / API v68.0.** Each element file tags its claims with a
> source: **[Help]** (the 264 Help snapshot under `docs/salesforce/264/help/`),
> **[Dev guide]**, **[Repo]** (shipped XML in this repo), **[Core]** (Salesforce source
> behavior), **[Live]** (verified on an org). A qualifier narrows a tag, for example
> `[Repo, measured]` (a live measurement recorded in a repo README) or
> `[Live, repo owner]` (observed on an org by the repo owner, no recorded run).
> `[Measured: <date>, <release>]` is a live result with the run recorded in the file. A live org of the
> target release beats every other source. Treat untagged or "inferred" claims as
> hypotheses until you have verified them.

## Quick Rules

1. **Find the procedure the org actually runs before touching anything.** It may not
   be `RLM_DefaultPricingProcedure`. See [Discovery](#discovery).
2. **Change a clone, then promote it.** Clone the procedure (or create a new version),
   configure it, Simulate, and only then activate it or point Revenue Settings at it.
   Never experiment on the active shipped procedure.
3. **Follow the ordering rules.** Pricing Setting comes first, once. After DDS only
   Aggregate Price and Rounding Values may follow, so no `FormulaBasedPricing` step goes
   there. Aggregate Price comes after DDS in a procedure with a DDS, and after Derived
   Price (filtered to the contributing lines) in one with Derived Price; the two never
   share a procedure. Save rejects some combinations (Derived Price with DDS or Promotion
   Execution; Price Propagation with Derived Price, Promotion Execution or Map Line Item). See
   [`procedure-anatomy-and-ordering.md`](procedure-anatomy-and-ordering.md).
4. **Use a List Group to act on a subset of lines.** A top-level element runs for every
   line; a filter (`AdvancedListFilter`) narrows it to the lines it selects. Keep lanes
   mutually exclusive.
5. **Every reprice reloads written fields from the record.** Reset a conditionally
   written field on every line before the branches that set it. Don't read a value
   before the element that recalculates it.
6. **An element that reads a decision table needs its table active, refreshed and
   mapped in the procedure's pricing recipe.** A stale table prices wrongly **without
   an error**.
7. **Verify with Simulate JSON, not only the waterfall.** Aggregate Price and Price
   Tracking results are not in the waterfall [Help]; Stop Pricing is (it shows where
   pricing ended). Then check
   the persisted field on a real quote.
8. **Capture the element from a working org rather than typing it by hand.** The
   parameter encoding (`section-N-…`, `condition-N-…`) is undocumented and strict.
   Slice it with the expression-sets toolkit, then edit it.

## DO NOT

- **DO NOT** mutate an active, shipped or customer procedure to experiment. Use a
  disposable clone (expression-sets Quick Rule 8).
- **DO NOT** add a `FormulaBasedPricing` step after DDS (in a procedure that has one), and don't move
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
| Which procedure is configured, Simulate/activate, procedure plans, output resolution, symptoms without an error. Which procedure actually executed: the Operations Console log in [`runtime-and-observability.md`](runtime-and-observability.md) | [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) |
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

# The step tree in execution order (each step's actionType, no parameters: small).
# Add --params only to read parameters; it prints every step's, about 5x the output.
python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> \
    --developer-name <PRICING_PROCEDURE>

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
| Attribute Adjustment Price (undocumented in Help) | `AttributeAdjustmentMatrix` | [`elements/attribute-adjustment-matrix.md`](elements/attribute-adjustment-matrix.md) | no |
| Formula-Based Pricing (commitment-term discount pattern: [`commitment-term-discount.md`](elements/commitment-term-discount.md)) | `FormulaBasedPricing` | [`elements/formula-based-pricing.md`](elements/formula-based-pricing.md) | yes |
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
[`discovery-procedures.md`](discovery-procedures.md). No element file yet: `PriceGuidance`
(pilot-gated; see [`price-tracking.md`](elements/price-tracking.md)) and `CommercePricing`
(must stand alone; see the anatomy save-time table). Qualification elements such as
`EvaluateQualification` belong to qualification procedures, not pricing.

## How a custom element is encoded

Most pricing elements are `stepType: BusinessKnowledgeModel` steps with an `actionType`
and a flat list of `customElement.parameters` (`customElement` is the nested payload, not
the step type). Each parameter has a `name`, a `type`
(`Literal` = a fixed value, `Parameter` = a context tag or variable, `Formula`,
`Lookup`, `PickList`), a `value`, and `input`/`output` flags [Dev guide, Repo]. Repeating
structures differ per element, so copy the element file's shape [Repo]:

- Aggregate Price: zero-based `section-0-…` with a hyphenated `section-count`, and
  `condition-0-…` with `where-condition-count`.
- Most others (Assignment, Map Line Item and the lookup elements): camel-case `sectionCount`.
- Map Line Item and Assignment read one-based `sectionJsonString1`, `2`, … until the
  first missing number, so a gap silently drops every later part; `sectionCount` does not
  drive that read [Core].
- Formula-Based Pricing counts its formulas in `formulaSectionCount`.

Keep counts and indexes consistent anyway. List Group and List Operation are step types
with no custom-element parameters [Repo].

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
6. **Activate** the version, or point Revenue Settings at the clone (that changes pricing
   for every transaction in the org, not only the test quote; note the old value to roll
   back). Don't activate the procedure plan as part of this: this repo leaves it inactive
   because an active plan re-runs pricing (doubled price revision or header discount) and
   truncates the waterfall [Repo]; see
   [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) section 3.
7. **Re-price a real quote** and query the persisted fields. Keep the clone and the test
   quote for the record.

## Examples

**Partner can't get Aggregate Price to work.** Read
[`elements/aggregate-price.md`](elements/aggregate-price.md) → *Troubleshooting*. Check
that the Output and GroupBy tags are at the same context level, that the step sits
after DDS in a procedure with one, or after Derived Price otherwise (a procedure with DDS rejects any other step after it except Aggregate or Rounding), that derived-price
lines are excluded with the Where conditions on `DerivedPricingAttribute` (keep them even when
Pricing Setting maps `IsDerived`, which also makes the engine drop derived lines [Core]), that Write Back (a filter on which lines receive the
result) isn't combined with Roll Up, which ignores it, and that the result is read from Simulate
JSON (it is not in the waterfall).

**Add a header margin percent.** Don't add a trailing formula step: in a procedure with DDS it is
rejected after DDS and stale before the aggregates. Use a record formula field over the aggregated
cost and margin. See [`procedure-anatomy-and-ordering.md`](procedure-anatomy-and-ordering.md)
→ *Rule 1* and the margin caveat.

**Quantity discount by bands.** Choose Volume Discount (the whole quantity priced at the
band it reaches) or Tier Discount (each band priced separately) with
[`elements/volume-and-tier-discount.md`](elements/volume-and-tier-discount.md). Then
refresh the adjustment-tier decision table before you Simulate. Units added on an amendment
don't re-band as shipped; that file has the measured overlay that makes them.

**Extra discount for a long commitment term.** No pricing element is built for term-based discounts.
Use a List Group whose filter selects the long-term lines and whose Formula-Based Pricing step
rewrites `NetUnitPrice`, placed before the term pricing groups. The filter, formula and placement
are in [`elements/commitment-term-discount.md`](elements/commitment-term-discount.md), measured
live on 264.

**Compound ramp uplift is flat.** Read [`elements/price-revision-compound-uplift.md`](elements/price-revision-compound-uplift.md)
→ prerequisites. A blank Uplift Method silently gives a standard (non-compound) uplift.

## Validation Checks

Before calling a pricing-procedure change done, or before opening a PR that changes a
procedure or this skill:

```bash
# Offline pre-flight of a definition or overlay JSON. It errors unless the first top-level
# step of a DefaultPricing or PricingDiscovery definition is PricingSettings, so it rejects
# a derived-pricing discovery procedure (starts with Discovery Settings or Fetch Pricing
# Rules) and a DDS-only or lone Commerce procedure that core saves. It also checks none of
# the ordering rules below (formula after DDS, two DDS, DDS plus Derived Price and two
# Pricing Settings all pass), so check those by hand or by Simulate. An unknown actionType
# is only a warning (--strict fails on every warning, that one included).
python scripts/ai/validate_expression_set.py <path> --overlay   # or --definition

# For skill edits: the full PR gate (it runs the skill and registry checks it selects)
python scripts/ai/pr_gate.py --base origin/main
```

Only for a change to the tracked `force-app` procedure XML, on a disposable or freshly
built org: `cci task run deploy_expression_sets --org <cci_alias>`. It deploys the TRACKED
XML (not your clone) with placeholders resolved, so it cannot validate a clone or new
version. It overwrites the org's copy, and an active version blocks the deploy: the
`prepare_expression_sets` flow deactivates versions first and
`activate_and_deploy_expression_sets` flips the tracked Drafts back to Active. Never run it
to "check" a working org.

Checklist:

- [ ] The active procedure was discovered, not assumed.
- [ ] The change was made on a clone or new version, Simulated, then activated.
- [ ] The ordering rules hold (in a procedure with DDS: only Aggregate Price or Rounding Values after it, aggregates after it; without DDS, aggregates after Derived Price).
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
  metadata shape (where one is known), shipped snapshot, how to verify, troubleshooting,
  open questions.
- [`elements/commitment-term-discount.md`](elements/commitment-term-discount.md) — a
  commitment-term discount (annual Term Defined lines committed 48+ months get a further
  percentage off) built from a List Group filter and Formula-Based Pricing: tags, filter logic,
  rounding, placement before term pricing, the overlay, a measured headless-pricing result, what
  real quote lines must carry (term in the selling model's unit, ramp lines, a header switch), and
  the Price Adjustment Matrix alternative, plus rounding before a negotiated discount. Read it when
  a discount depends on the subscription term.
- [`elements/root-answer-child-price.md`](elements/root-answer-child-price.md) — a child line's
  price driven by an answer on the bundle root (for example a regional uplift on some children):
  the documented routes (CML `parent()` into a price-impacting child attribute, Formula-Based
  Pricing over a header tag, a Price Adjustment Matrix), each cited; route 1 measured end to end.
- [`elements/price-revision-compound-uplift.md`](elements/price-revision-compound-uplift.md)
  — compound ramp uplift on Price Revision: prerequisites, ramp-path bindings, tracked
  default vs the 264 template, the compounding arithmetic, rounding after the uplift, and what
  can't compound.
