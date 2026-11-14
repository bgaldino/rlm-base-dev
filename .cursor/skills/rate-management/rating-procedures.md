# Rating and Rating Discovery Procedures — Elements and Build Order

Read this when cloning, extending, simulating or debugging a rating or rating discovery
procedure. Parent skill: [SKILL.md](SKILL.md). Generic expression-set mechanics (Connect vs
Metadata API, overlays, activation): [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md).

Labels: `[Help: id]` = `docs/salesforce/264/help/articles/ind.<id>.htm.md`.
`[inferred]` = reasoning only. Nothing here was measured in a live org.

## Which template

| Template | Scenario | Source |
|----------|----------|--------|
| Default Rating Procedure | Non-negotiable rates; straightforward base, volume and tier pricing | [Help: `ind.rm_rating_procedures`] |
| Negotiable Rating Procedure | Rates negotiated per asset or binding target; reads asset-level tables | [Help: `ind.rm_rating_procedures`, `ind.rm_prereqs_to_build_rating_procedures`] |
| Default Rating Discovery Procedure | Fetch rate cards, entries and adjustments for quoting | [Help: `ind.rm_rating_discovery_procedures`] |

Clone from App Launcher, Expression Set Templates, open a version, Save As a new
procedure [Help: `ind.rm_clone_the_default_rating_procedure`]. The default discovery
procedure uses the Usage Ratable Summary object, which Help says is not generally
available: ask your account executive for access or map your own context definition
[Help: `ind.rm_clone_the_default_rating_discovery_procedure`].

## Prerequisites [Help: `ind.rm_prereqs_to_build_rating_procedures`]

1. Rate Management Design Time permission (context definitions, decision tables, procedures).
2. Lookup tables: the predefined ones, or custom. Non-negotiable: Rate Card Entries 2 and
   the Volume, Tier and Attribute adjustment Entries 2 tables. Negotiable adds the Asset,
   Binding Object, Commitment-based and by-Rate-Card-Entry-ID tables.
3. Transaction Management on, to see and invoke the asset-based tables.
4. Context definitions enabled. `RateManagementContext` maps Usage Ratable Summary;
   extend or clone it rather than editing the standard one.
5. A constant resource for variables with no context tag.

## Element catalog [Help: `ind.rm_rating_elements`]

| Element | Use | Lookup table / note |
|---------|-----|---------------------|
| Rating Setting | Map common variables to context tags; must be first | Later element tags win over it |
| Base Rate | Rate from the rate card entry | Rate Card Entries |
| Volume-Based Rate Discount | Flat discount to all units past a threshold | Rate Adjustment by Volume Entries 2; negotiable: by Rate Card Entry ID |
| Tier-Based Rate Discount | Range-based discount per band | Tier Entries 2 |
| Negotiated Rate Card Entries (+ Binding Object variant) | Rate card entry ID from asset ID or binding object entry | Asset / Binding Object Rate Card Entry |
| Negotiated Base Rate (+ Binding Object) | Negotiated rate, base rate if none negotiated | Asset Rate 2 / Binding Object Rate 2 |
| Negotiated Tier-Based Rate Adjustment (+ Binding Object) | Negotiated tier discount or surcharge | Asset Tier-based Rate Adjustment |
| Negotiated Volume-Based Rate Adjustment (+ Binding Object) | Uniform negotiated adjustment on all units | Asset Volume-based Rate Adjustment |
| Commitment Rate Adjustment | Rates for commitment products | Commitment-based Rate Adjustment |
| Map Line Item | Map variables on the line and its sub-lines | |
| Manual Rate Discount | Apply external discounts you enter | |
| Rate Adjustment Matrix | Custom conditions (for example region) | Custom matrix |
| Assignment | Set or change context tag values | |
| Formula-Based Rating | Functions and math for a rate | |
| List Group / List Operation | Filter a list, then operate on it | |
| Rounding Values | Rounding rules | |
| Stop Rating | Stop for a line; Waterfall shows where | |
| Get Rate Cards | Fetch the cards a procedure needs | |

Tier vs volume: both discount by consumed quantity; volume applies one standard flat
discount to all units, tier defines a discount per range
[Help: `ind.rm_element_tier_based_rate_discount`].

## Build order

1. Rating Setting first.
2. For negotiated tier or volume: Negotiated Rate Card Entries earlier than the
   adjustment element; its Rate Card Entry ID output is the adjustment's input
   [Help: `ind.rm_add_negotiated_tierbased_rate_adjustment`,
   `ind.rm_add_negotiated_volumebased_rate_adjustment_`].
3. Per element: pick the lookup table, map variables to context tags, set a rank, tick
   Include in Output, save.
4. Simulate: Simplified (fields) or Advanced (JSON) input; the Waterfall view shows each step. Take
   IDs for inputs from the record URLs [Help: `ind.rm_simulate_activate_rating_procedure`].
5. Activate the version once the simulation matches the hand-computed rate.

Designers need Rate Management Design Time User; runtime callers need Run Time User
[Help: `ind.rm_simulate_activate_rating_procedure`].

## Rating discovery procedure

Elements: Get Binding Object Rate Adjustment, Get Binding Object Rate Card Entries, Get
Rate Cards (Pricebook Rate Card Entries table), Get Rate Card Entries, Get Tier-Based Rate
Adjustments. Input is a Binding Object ID or a Price Book ID
[Help: `ind.rm_rating_discovery_procedure_elements`]. If a simulation supplies the output of
an element, that element is skipped when fetching, so test with an input that exercises
each step [Help: `ind.rm_rating_discovery_procedure_elements`]. Its resolution lookup tables
are listed in [Help: `ind.rm_rating_discovery_procedures`].

## Real-time data

Since Summer '25 an admin may choose real-time data over decision tables for some
elements (Get Binding Object Rate Adjustment and Rate Card Entries, and the Negotiated
elements, Commitment Rate Adjustment). Real-time is accurate but slower; tables are faster
but need refresh when rates change. Real-time does not support "not matches" or
"contains" [Help: `ind.rm_implementation_considerations`]. Which this repo uses on 264 is
not measured; check the org.

## Waterfall

Enable the rating waterfall for per-step reasons. Without persistence the steps are gone
once the transaction is final; with it, every transaction stores detailed logs at a
storage cost [Help: `ind.rm_enable_rating_waterfall_persistence`]. Read it through the API in
[SKILL.md](SKILL.md) (APIs).
