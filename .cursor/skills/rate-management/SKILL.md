---
name: rate-management
description: >-
  Design, set up, and verify Revenue Cloud Rate Management for usage products: rate cards
  and rate card entries (base and tier), tier and volume rate adjustments, negotiated and
  commitment rates, rating procedures and rating discovery procedures, the decision
  tables they read, permissions, the rating waterfall, and the rating APIs. Use when
  choosing how a usage resource is priced, mapping a price book to rate cards, cloning
  or activating a rating procedure, or asking why a rate is missing or wrong. Use
  usage-consumption to build, rate and verify metered demos, and expression-sets for
  generic procedure authoring.
---

# Rate Management — Rates, Adjustments and Rating Procedures

Rate Management defines what a usage resource costs and how that rate is adjusted. It is one of five
Usage Management capabilities (usage modeling, rate management, usage selling, consumption
management, wallets) [Help: `ind.um_usage_management`]. This skill covers the design and setup
decisions. Usage modeling is in
[`../usage-consumption/usage-setup.md`](../usage-consumption/usage-setup.md); building, rating and
verifying a metered demo is [`../usage-consumption/SKILL.md`](../usage-consumption/SKILL.md).

Labels: `[Help: id]` is a 264 Help article under `docs/salesforce/264/help/articles/`
(`ind.<id>.htm.md`); `[inferred]` is reasoning, not a measurement. Nothing here was
measured in a live org by this skill; "not measured" marks it. A live 264 org is ground
truth over the docs.

## Quick Rules

1. **Rates live on rate card entries, not on products.** A rate card (type Base or Tier)
   holds entries; each entry names a usage resource, a sellable product, a selling model
   and a rate unit of measure [Help: `ind.rm_create_a_base_rate_card_entry`].
2. **A rate card does nothing until a price book points at it.** Create a Price Book
   Rate Card per card type [Help: `ind.rm_create_price_book_rate_cards`].
3. **Use Base for a flat per-unit rate; use Tier for range-based adjustments** on that
   rate [Help: `ind.rm_create_a_rate_card`].
4. **Entries start Draft; activate them.** Active entries accept only limited edits, so
   finish the entry (and its tiers) while Draft [Help: `ind.rm_create_a_base_rate_card_entry`].
5. **Rating procedures are cloned, not hand-built.** Clone the Default or the Negotiable
   template, simulate, then activate [Help: `ind.rm_clone_the_default_rating_procedure`].
6. **Rating Setting is always the first element** of a rating procedure
   [Help: `ind.rm_element_rating_setting`].
7. **Rating reads decision tables.** After any rate-data change, refresh them; see
   [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md) and the refresh section below.
8. **Avoid attribute-based rate cards for usage.** Help says they are not supported in
   Usage Selling and Consumption Management [Help: `ind.rm_rate_mngmnt_limits`].

## DO NOT

- **DO NOT** treat an activated rate as editable. An Active entry takes limited changes
  (status), and a tier under it is locked on this repo's 264 loads [Help:
  `ind.rm_create_a_base_rate_card_entry`; repo plan notes in
  `datasets/sfdmu/qb/en-US/qb-rates/README.md`]. Correct a Draft, or deactivate first.
- **DO NOT** let tier ranges overlap. Bounds are inclusive and tiers cannot overlap
  [Help: `ind.rm_create_a_tier_rate_card_entry`].
- **DO NOT** mismatch a currency unit of measure code and the org currency ISO code. The
  Help warns a mismatch hides rate cards during selling with no error
  [Help: `ind.um_create_units_of_measure`].
- **DO NOT** skip the Negotiated Rate Card Entries element before a negotiated tier or volume
  element: its output feeds the next one [Help: `ind.rm_add_negotiated_tierbased_rate_adjustment`].
- **DO NOT** use CSV-based decision tables or decision matrices for rating; Help says
  Rate Management does not support them [Help: `ind.rm_rate_mngmnt_limits`].
- **DO NOT** assume a fresh decision table after a rate change. Refresh and wait; a stale
  table prices with the old rate and does not error [inferred from Help; see
  `../decision-tables/SKILL.md`].
- **DO NOT** reload rate plans into an org with live usage assets without reading
  [`../usage-consumption/SKILL.md`](../usage-consumption/SKILL.md) DO NOT list.

## Entry Conditions

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Pick base vs tier vs volume, negotiable or not | Yes | Decision guide below. |
| Create or map rate cards, entries, price book rate cards | Yes | Model below. |
| Clone, edit, simulate, activate a rating or discovery procedure | Yes | [rating-procedures.md](rating-procedures.md). |
| A rate is missing, zero or stale at quote or rating time | Yes | Verification below, then `usage-consumption`. |
| Enable Usage/Rate Management, permissions | Yes | Setup below. |
| Units of measure, usage resources, policies, grants | No | [`usage-setup.md`](../usage-consumption/usage-setup.md). |
| Record usage, orchestrate, drawdown, verify rated summaries | No | `usage-consumption`. |
| Generic expression-set CRUD or overlays | No | `expression-sets`. |
| Pricing procedure elements (non-usage pricing) | No | `pricing-procedures`. |
| Rate object fields and relationships | Partly | [`rates.md`](../revenue-cloud-data-model/domains/rates.md). |

## Model

```
PriceBook --PriceBookRateCard--> RateCard (Base | Tier)
RateCard --> RateCardEntry (usage resource + product + selling model + rate UoM)
RateCardEntry --> RateAdjustmentByTier (lower/upper bound, adjustment type + value)
```

| Concept | What it is | Source |
|---------|------------|--------|
| Rate card | Group of rules that rate usage resources granted with a sold product; type Base or Tier; date range | [Help: `ind.rm_create_a_rate_card`] |
| Rate card entry | One rate (or tier set) for a resource, product and selling model; status Draft, Active, Inactive; negotiable flag; effective dates | [Help: `ind.rm_rate_card_entries`] |
| Price book rate card | Maps a price book to a rate card, one per card type | [Help: `ind.rm_create_price_book_rate_cards`] |
| Tier adjustment | Lower and upper bound plus a Percentage, Amount or Override adjustment | [Help: `ind.rm_create_a_tier_rate_card_entry`] |
| Rate unit | The entry's unit is a currency or a token unit; the product's usage resource setting decides which is used when selling | [Help: `ind.rm_rate_card_entries`] |

Token pricing needs two entries: usage to tokens (rate unit is the token unit) and tokens
to currency (rate unit is the currency) [Help: `ind.rm_rate_card_entries`]. An entry
uses the default unit of measure of its usage resource [Help:
`ind.rm_implementation_considerations`]. Objects and fields:
[`rates.md`](../revenue-cloud-data-model/domains/rates.md).

### Limits worth knowing [Help: `ind.rm_rate_mngmnt_limits`]

| Item | Default |
|------|---------|
| Rate card entries | 1,200 |
| Adjustment records on tier entries | 3,000 |
| Rating elements per procedure | 70 (max 100) |
| Active decision tables, rating procedures | 50 |
| Active decision tables, rating discovery | 40 |
| Procedure / element run time | 10,000 ms / 5,000 ms |

Quotes and orders cap at 200 lines, 200 line item rate card entries and 800 line item
rate adjustments [Help: `ind.um_usage_management_limits`].

## Decision guide

Ask the customer, then choose. Each row is what Help says each option does; the choice
rule is `[inferred from Help]` unless noted.

| Question to ask | If yes | If no / other |
|-----------------|--------|---------------|
| Is one flat per-unit rate enough? | Base card, one entry per resource | Add a Tier card for ranges |
| Does the price per unit fall as consumption grows, in bands? | Tier adjustments: each band gets its own discount, applied to the units in that band | See volume |
| Does one discount apply to all units once a threshold is met? | Volume adjustment: a standard flat discount to all units | Use tiers for banded |
| Is the price a fixed amount off, or a replacement rate? | Tier type Amount (flat discount) or Override (replaces the net unit rate) | Percentage |
| Does each customer get their own rates? | Mark entries negotiable; use the Negotiable Rating Procedure | Non-negotiable, Default procedure |
| Is the rate tied to a commitment? | Commitment product plus Commitment Rate Adjustment | No commitment element |
| Are rates quoted in tokens? | Two entries: usage to token, token to currency | Currency entry only |
| Do rates differ by region or another custom condition? | Rate Adjustment Matrix element on a custom matrix `[inferred]` | Standard elements |
| Must you explain a rate months later? | Enable waterfall persistence | Leave it off (the storage saving is `[inferred]`) |

Tier arithmetic per Help [Help: `ind.rm_element_tier_based_rate_discount`]: at a unit
rate of 0.50, no discount for the first 10 units, 10% for the next 50 and 20% for the
last 40 gives 5.00 + 22.50 + 16.00 = 43.50. Volume: a 25% discount on 150 units once
100 or more are consumed over the grant [Help: `ind.rm_element_volume_based_rate_discount`].

Base rate vs negotiated rate card: Help's Negotiable procedure uses asset-level lookup
tables to check whether a rate was negotiated, and falls back to the base rate when not
[Help: `ind.rm_element_negotiated_base_rate`]. Choose Negotiable only when per-asset or
per-binding-target rates are a requirement; it needs more lookup tables and Transaction
Management [Help: `ind.rm_prereqs_to_build_rating_procedures`]. How the negotiated rate
is captured at quote time is not measured here.

Commitment rate behavior after the commitment is used (bounded object rate vs lowest
commitment rate) is a usage commitment policy choice, covered in
[`usage-setup.md`](../usage-consumption/usage-setup.md) and
[`usage-consumption`](../usage-consumption/SKILL.md) (How Drawdown Actually Works).

## Setup

Order [Help: `ind.rm_rate_management_setup`]:

1. Enable Usage Management, then Rate Management (Setup, Usage Management Settings;
   needs Customize Application) [Help: `ind.rm_enable_rate_management`,
   `ind.um_enable_usage_management`].
2. Enable Rating Waterfall; optionally enable waterfall persistence (Rate Management
   Admin) [Help: `ind.rm_enable_rating_waterfall_persistence`].
3. Create price book rate cards, rate cards and entries.
4. Clone a rating procedure; simulate; activate.
5. Clone and configure a rating discovery procedure.
6. Set up record sharing so runtime users can read the designers' data
   [Help: `ind.rm_rate_management_setup`].

Permissions [Help: `ind.rm_rate_management_psls`, `ind.rm_key_roles_in_rate_management`]:

| Permission set license | Gives | Personas |
|------------------------|-------|----------|
| Rate Management Design Time | CRUD on design-time objects | Admin, Design Time User |
| Rate Management Run Time | Read runtime data, call the APIs | Manager, Run Time User |

Building rating procedures also needs context definition and decision table access, and
cloning a discovery procedure needs Pricing Discovery as well
[Help: `ind.rm_prereqs_to_build_rating_procedures`,
`ind.rm_clone_the_default_rating_discovery_procedure`]. Rate Management is not supported
on mobile and its objects can't create records in Data Cloud
[Help: `ind.rm_rate_mngmnt_limits`]. Repo permission sets:
`docs/references/revenue-cloud-permissions.md`.

## Rating and discovery procedures

Detail in [rating-procedures.md](rating-procedures.md). Summary:

| Procedure | Job | Context definition |
|-----------|-----|--------------------|
| Rating procedure | Calculate the net rate of a usage resource; ordered rating elements | `RateManagementContext` (maps Usage Ratable Summary) |
| Rating discovery procedure | Fetch binding objects, rate cards, entries and adjustments for products and resources in a price book, for quoting | `RatingDiscoveryContext` |

Both are expression sets; authoring mechanics, overlays and activation are in
[`../expression-sets/SKILL.md`](../expression-sets/SKILL.md). Revenue Settings holds the
default usage rating discovery procedure the rating API needs
(`docs/api/rate-management-apis-reference.md`).

## Decision tables and refresh

Rating elements call lookup tables (decision tables): Rate Card Entries 2, Rate
Adjustment by Volume/Tier/Attribute Entries 2 for non-negotiable rates; asset and binding
object variants plus Commitment-based Rate Adjustment for negotiable rates
[Help: `ind.rm_prereqs_to_build_rating_procedures`]. Discovery uses resolution tables
[Help: `ind.rm_rating_discovery_procedures`]. Help offers real-time data as an
alternative to decision tables for some elements, trading performance for freshness;
real-time does not support "not matches" or "contains"
[Help: `ind.rm_implementation_considerations`].

In this repo the lists are `dt_rating_decision_tables` and
`dt_rating_discovery_decision_tables` in `cumulusci.yml`. Rating tables have no runtime
refresh path of their own. At build time the `refresh_all_decision_tables` flow (run by
`prepare_rlm_org`) refreshes them via `refresh_dt_rating` and
`refresh_dt_rating_discovery`; `prepare_rating` itself does not. After that, use the
Decision Table Manager's stale-only refresh, and
`cci task run check_decision_table_freshness --org <cci_alias>` to confirm. See
[`../decision-tables/SKILL.md`](../decision-tables/SKILL.md) (`RateCardEntry` feeds
several tables; refresh after adding a rate).

## APIs

| API | Path (v68.0) | Notes |
|-----|--------------|-------|
| Get rate plan | `GET /connect/core-rating/rate-plan` | One price book and one product; needs `contextId` and `procedureApiName`; runtime permission and a default discovery procedure in Revenue Settings |
| Get rating waterfall | `GET /connect/core-pricing/waterfall/{lineItemId}/{executionId}?usageType=Rating` | Persisted waterfall; needs persistence enabled |

Reference:
[`docs/api/rate-management-apis-reference.md`](../../../docs/api/rate-management-apis-reference.md);
family index: [`../rlm-business-apis/SKILL.md`](../rlm-business-apis/SKILL.md).

## What this repo ships

Snapshot; discover with `rg -n -i "rate.?card|rating" cumulusci.yml` and `ls datasets/sfdmu`.

| Piece | Where |
|-------|-------|
| Rate card, entry, tier, price book rate card data | `datasets/sfdmu/qb/en-US/qb-rates`, `datasets/sfdmu/q3/en-US/q3-rates` (`insert_qb_rates_data`, `insert_q3_rates_data`) |
| Usage resources and PURs, policies and grants | `qb-rating`, `qb-rating-entitlements` (and `q3-` equivalents) |
| Flow | `prepare_rating`: load, `activate_rating_records`, `activate_rates` (REST; Apex DML path fails on 262) |
| Procedures | `RLM_DefaultRatingProcedure`, `Negotiable_Rating_Procedure`, `RLM_DefaultRatingDiscoveryProcedure` (see `expression-sets`) |
| Revenue Settings | `configure_revenue_settings` sets the usage rating discovery procedure |
| Extended context | `extend_context_rating_discovery` |

## Examples

### Example 1 — "Customer wants volume discounts on API calls"

1. Ask: bands (each band its own discount) or one discount past a threshold?
2. Bands: a Tier card, one entry for the resource and product, tiers with inclusive,
   non-overlapping bounds and a Percentage adjustment. Threshold: Volume adjustment.
3. Map the price book with a Price Book Rate Card; activate the entry.
4. Refresh decision tables; simulate the rating procedure with a known quantity and
   compare with the arithmetic above.

### Example 2 — "Rated amount ignores the new rate"

1. Is the entry Active and in its date range, on a card mapped to the price book?
2. `check_decision_table_freshness`: is a rating table Stale? Refresh and wait.
3. Simulate and read the waterfall to find the step that picked the old rate.
4. Still wrong: follow `usage-consumption` Example 1 (ordering) before blaming rates.

### Example 3 — "Per-customer negotiated rates"

1. Confirm entries are marked negotiable; use the Negotiable procedure clone.
2. Order elements: Rating Setting first, Negotiated Rate Card Entries before any
   negotiated tier or volume element.
3. Confirm Transaction Management is on, since asset-based tables need it.

## Validation Checks

- Every active entry has a price book rate card path; tiers do not overlap.
- The rating procedure simulates to the hand-computed rate, and the Waterfall shows
  each step [Help: `ind.rm_simulate_activate_rating_procedure`].
- `cci task run check_decision_table_freshness --org <cci_alias>` shows no Stale rating
  table after the last rate change.
- Usage product validator passes on the product [Help: `ind.um_run_validator`].
- Live rating of recorded usage: `usage-consumption` verification.
- Repo checks: `python scripts/ai/skill_manifest.py --check` and
  `python scripts/ai/analyze_agent_tooling.py check`.

## Related Skills

`usage-consumption`, `decision-tables`, `expression-sets`, `pricing-procedures`,
`pricing-setup`, `rlm-business-apis`, `revenue-cloud-data-model`, `revenue-cloud-docs`.
