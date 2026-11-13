---
name: pricing-setup
description: >-
  Set up Salesforce Pricing in a Revenue Cloud org: enablement, permissions, price
  and cost books, price adjustment schedules, recipes, proration and selling models,
  price revision policies, pricing actions, data sync, and Help scenarios. Use
  pricing-procedures for elements, pricing-wiring for this repo's build order.
---

# Pricing Setup — Records and Settings Pricing Procedures Read

Use this skill to **configure Salesforce Pricing in any org**, not only this repo's build:
what has to be enabled and assigned, and the records a pricing procedure reads (price
books, cost books, adjustment schedules, recipes, selling models, proration and revision
policies, pricing actions). It is grounded in the Release 264 Help snapshot and written
for SEs, partners and AI agents. Any agent can read it (Cursor, Claude Code, Copilot,
Codex, Windsurf, Aider).

The neighbouring skills own the rest:

| Concern | Owner |
|---|---|
| Pricing elements: Builder fields, parameters, ordering, Simulate, which procedure runs | [`../pricing-procedures/SKILL.md`](../pricing-procedures/SKILL.md) |
| This repo's build: recipe-table mapping tasks, plan overlays, flow order, CPI data load | [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) |
| Decision-table authoring, refresh, staleness | [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md) |
| Expression Set CRUD, overlays, activation mechanics | [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md) |
| Context definitions, tags, mappings | [`../context-service/SKILL.md`](../context-service/SKILL.md) |
| SFDMU plan keys and operations for pricing data | [`../sfdmu-data-plans/SKILL.md`](../sfdmu-data-plans/SKILL.md) |
| Contract pricing | [`docs/guides/contract-pricing.md`](../../../docs/guides/contract-pricing.md) |

> **Pinned to Release 264 / API v68.0.** Claims are tagged **[Help]** (the 264 Help
> snapshot, `docs/salesforce/264/help/articles/ind.pricing_*`), **[Repo]** (shipped data or
> metadata), **[Core]** (Salesforce source behavior). Nothing here is live-verified yet beyond the measurements tagged [Repo, measured] (sync scope, schedule activation)
> and **[Measured]** (2026-11-11, a fresh 264 `ent-sb0` scratch org: cost lookup inputs, term-line cost, margin units,
> default term counts, partial-year proration, full-term values);
> a live org of the target release beats every other source. Treat "inferred" claims and
> unconfirmed API names as hypotheses and describe the object before you rely on them.

## Quick Rules

1. **Enable and assign before you build.** Salesforce Pricing on, Design Time for
   builders, Run Time for anyone (or any integration user) who prices. See
   [`org-enablement-and-permissions.md`](org-enablement-and-permissions.md).
2. **Sharing is a UI concern, permission sets an API concern.** A runtime user who prices
   through the API but sees no rows in the UI is missing sharing, not a permission set.
3. **Table-backed pricing records reach the engine through a decision table.** After
   creating or editing price book entries, adjustment records, cost entries or index
   rates, refresh the tables that read them before you Simulate. Proration policies,
   selling-model options and revision-policy fields arrive through context tags instead
   (per the repo's context bindings; inferred for proration). A stale table prices
   wrongly without an error. See
   [`import-export-and-bulk-data.md` → After-load refresh rule](import-export-and-bulk-data.md#after-load-refresh-rule).
4. **A table an element cannot see is a recipe problem.** Element lookups list only tables
   mapped in the default recipe of the procedure's subtype. See
   [`pricing-recipes.md`](pricing-recipes.md).
5. **Product Selling Model on a price book entry is permanent.** To change it, deactivate
   the entry and create another. List-price tables key on it.
6. **Cost books are tracking data in Help.** Using them in pricing (as this repo does
   through a decision table read by List Price) is custom wiring. See
   [`cost-books.md`](cost-books.md).
7. **Check Help arithmetic before you copy a worked example.** Some Help proration and
   scenario examples do not add up; the sub-files call those out.

## DO NOT

- **DO NOT** bulk-load pricing records with a scheduled sync flow active. Deactivate it,
  load, then sync manually [Help].
- **DO NOT** assume a template procedure prices. A template is not executable; clone it
  and point the org at the clone (pricing-procedures → operations).
- **DO NOT** invent API names for objects Help names only by label (pricing action
  parameters, recipe subtype). Describe the object in the target org first.
- **DO NOT** copy repo build steps (CCI tasks, SFDMU plans) into a customer org's setup
  instructions. Point to [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) and
  the plan READMEs instead.
- **DO NOT** treat a saved record as working pricing. Refresh, Simulate, then re-price a
  real quote.

## Entry Conditions

| Situation | Read |
|---|---|
| New org; pricing pages missing; who needs which permission set; sharing | [`org-enablement-and-permissions.md`](org-enablement-and-permissions.md) |
| Price books, entries, currency, validity, selling model on an entry | [`price-books.md`](price-books.md) |
| Product cost, margin inputs, cost-based List Price | [`cost-books.md`](cost-books.md) |
| A full-term (commitment) value, cost or margin next to the quote total | [`scenarios/full-term-value.md`](scenarios/full-term-value.md) |
| Volume, tier, attribute or bundle adjustments; tiers; schedule migration | [`price-adjustment-schedules.md`](price-adjustment-schedules.md) |
| Viewing, syncing, exporting/importing or bulk-loading pricing data | [`import-export-and-bulk-data.md`](import-export-and-bulk-data.md) |
| Adding a second currency: what to enable, which records need a row per currency | [`import-export-and-bulk-data.md` → Adding a currency](import-export-and-bulk-data.md#adding-a-currency) |
| Recipes: which tables a procedure may read; subtype; sync | [`pricing-recipes.md`](pricing-recipes.md) |
| One-time / term / evergreen selling models; proration settings and policies | [`proration-and-selling-models.md`](proration-and-selling-models.md) |
| Uplift and CPI: revision policies, index rates, regions, renewal math | [`price-revision-policies.md`](price-revision-policies.md) |
| A Calculate Price button; action parameters; constant resources | [`pricing-actions.md`](pricing-actions.md) |
| An end-to-end Help example to follow | [`scenarios/README.md`](scenarios/README.md) |
| An element's fields, ordering, errors | [`../pricing-procedures/SKILL.md`](../pricing-procedures/SKILL.md) |
| How this repo builds recipes, plans and pricing data | [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) |

## <a name="discovery"></a>Discovery

Find out what the org already has before you create anything:

```bash
# Settings: Salesforce Pricing on, waterfall, logs, parallel execution
sf project retrieve start --target-org <sf_alias> -m Settings:IndustriesPricing

# Who holds the pricing permission sets
sf data query --target-org <sf_alias> -q "SELECT PermissionSet.Name, Assignee.Username FROM PermissionSetAssignment WHERE PermissionSet.Name LIKE 'CorePricing%'"

# Price books and entry counts
sf data query --target-org <sf_alias> -q "SELECT Pricebook2.Name, COUNT(Id) FROM PricebookEntry GROUP BY Pricebook2.Name"

# Adjustment schedules
sf data query --target-org <sf_alias> -q "SELECT Name, ScheduleType, IsActive, EffectiveFrom, EffectiveTo FROM PriceAdjustmentSchedule"

# Decision-table freshness (repo task; any org it can authenticate to)
cci task run check_decision_table_freshness --org <cci_alias>
```

Then find the procedure the org runs with
[`../pricing-procedures/SKILL.md` → Discovery](../pricing-procedures/SKILL.md#discovery).

## Setup order

The Help basic setup, with the owner of each step:

1. Turn on Salesforce Pricing; assign licenses and permission sets
   ([`org-enablement-and-permissions.md`](org-enablement-and-permissions.md)).
2. Selling models, price books and entries; cost books if used
   ([`proration-and-selling-models.md`](proration-and-selling-models.md),
   [`price-books.md`](price-books.md), [`cost-books.md`](cost-books.md)).
3. Adjustment schedules and revision policies as needed
   ([`price-adjustment-schedules.md`](price-adjustment-schedules.md),
   [`price-revision-policies.md`](price-revision-policies.md)).
4. Decision tables active and refreshed ([`../decision-tables/SKILL.md`](../decision-tables/SKILL.md)),
   mapped in the recipe ([`pricing-recipes.md`](pricing-recipes.md)).
5. Context definition and tags ([`../context-service/SKILL.md`](../context-service/SKILL.md)).
6. Clone a procedure, configure its elements, Simulate, activate, point Revenue Settings at
   it ([`../pricing-procedures/SKILL.md`](../pricing-procedures/SKILL.md)).
7. Waterfall, price logs, page layouts, sharing, pricing actions
   ([`../pricing-procedures/runtime-and-observability.md`](../pricing-procedures/runtime-and-observability.md),
   [`org-enablement-and-permissions.md`](org-enablement-and-permissions.md),
   [`pricing-actions.md`](pricing-actions.md)).

## Examples

**Runtime user prices nothing in the UI.** Check the Run Time permission set, then the
org-wide defaults for Price Book, Expression Set and Price Adjustment Schedule
([`org-enablement-and-permissions.md` → Record sharing](org-enablement-and-permissions.md#record-sharing)).

**New volume discount is ignored.** Confirm the tiers are in date (an inactive schedule still prices on 264)
([`price-adjustment-schedules.md`](price-adjustment-schedules.md)), refresh the adjustment
tier table, then check the Volume Discount element
([`../pricing-procedures/elements/volume-and-tier-discount.md`](../pricing-procedures/elements/volume-and-tier-discount.md)).

**A custom decision table is not offered in the Builder.** Map it in the recipe for the
procedure's subtype and sync ([`pricing-recipes.md`](pricing-recipes.md)).

**Renewal uplift by CPI.** Create the index rates and revision policy
([`price-revision-policies.md`](price-revision-policies.md)), then configure the Price
Revision element ([`../pricing-procedures/elements/price-revision.md`](../pricing-procedures/elements/price-revision.md)).
This repo's CPI data load is in [`../pricing-wiring/price-revision-cpi.md`](../pricing-wiring/price-revision-cpi.md).

## Validation Checks

Before calling a setup change done:

- [ ] Salesforce Pricing is on and the right users hold Design Time / Run Time.
- [ ] The records you created are active and within their validity dates.
- [ ] Every decision table that reads them was refreshed after the change.
- [ ] The tables the procedure needs are mapped in the default recipe of its subtype.
- [ ] Simulate returns the expected values, and a real quote re-prices to them.

For edits to this skill, run with the gate interpreter (`.venv`, Python 3.13 to match CI; see
`docs/guides/local-installation.md`). Activate it first, or call `.venv/bin/python` (in a
worktree, `.venv` lives in the main checkout):

```bash
.venv/bin/python scripts/ai/analyze_agent_tooling.py check
.venv/bin/python scripts/ai/skill_manifest.py --check
```

## Sub-files

- [`org-enablement-and-permissions.md`](org-enablement-and-permissions.md) — turn on
  Salesforce Pricing, basic and advanced setup, settings, page layouts, permission sets and
  personas, record sharing, Einstein tag suggestions, a pre-build checklist.
- [`price-books.md`](price-books.md) — price books and entries: selling model, currency,
  validity, and how List Price reads them.
- [`cost-books.md`](cost-books.md) — cost books and entries, and the Help-vs-repo note on
  cost-based pricing.
- [`price-adjustment-schedules.md`](price-adjustment-schedules.md) — volume, tier,
  attribute and bundle adjustment schedules, tiers, and migration.
- [`import-export-and-bulk-data.md`](import-export-and-bulk-data.md) — viewing and syncing
  pricing data, the after-load refresh rule, packaged export/import, bulk loads and edits.
- [`pricing-recipes.md`](pricing-recipes.md) — recipe concept, the active recipe, subtype,
  table mappings, sync paths, scheduled refresh flows.
- [`proration-and-selling-models.md`](proration-and-selling-models.md) — selling models,
  term settings, proration policies, worked period examples.
- [`price-revision-policies.md`](price-revision-policies.md) — flat and price-index
  policies, index rates, regions, overlap rules, renewal math.
- [`pricing-actions.md`](pricing-actions.md) — Calculate Price actions, action parameters,
  button or LWC placement, constant resources, how an action picks its procedure.
- [`scenarios/README.md`](scenarios/README.md) — index of Help end-to-end walkthroughs:
  - [`scenarios/simple-pricing-procedure.md`](scenarios/simple-pricing-procedure.md) — list
    price, volume and manual discount, aggregate.
  - [`scenarios/lowest-price-across-price-books.md`](scenarios/lowest-price-across-price-books.md)
    — minimum list price with output resolution.
  - [`scenarios/sequential-discounts.md`](scenarios/sequential-discounts.md) — discounts
    applied one after another.
  - [`scenarios/pricing-action-button.md`](scenarios/pricing-action-button.md) — Calculate
    Price on an Opportunity.
  - [`scenarios/cost-and-margin.md`](scenarios/cost-and-margin.md) — unit cost, line
    cost and margin, and a quote total cost, from cost book entries (repo wiring, not a
    Help example); term-line cost × `PricingTermCount`; `Margin` in percent units.
  - [`scenarios/full-term-value.md`](scenarios/full-term-value.md) — a full-term value,
    cost and margin next to the platform's one-period total: per-line fields written by the
    procedure, quote roll-ups and formulas, a fee on a product subset; the months left on
    an amendment and the segment's months in a group ramp.
