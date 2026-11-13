# Scenario: Cost and Margin on Quote Lines

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`, indexed in [README.md](README.md).
> Release 264. Unlike the other scenarios this one has no single Help example, because Help
> calls cost books tracking-only. It assembles the repo's shipped wiring end to end. Sources
> are tagged `[Help]`, `[Repo: <path>]`, `[inferred]` and `[Measured]` (measured 2026-11-11 on a
> fresh 264 `ent-sb0` scratch org, on a clone of `RLM_DefaultPricingProcedure`).

**Goal:** every quote line shows unit cost, total cost, margin % and margin amount, and the
quote shows a total cost. A source's costs (standard costs, loaded labour rates) become
cost book entries. For a full-term value, cost and margin next to the platform's quote
total, see [full-term-value.md](full-term-value.md).

## Wiring, in order

| # | Layer | What | Where it's documented |
|---|---|---|---|
| 1 | Data | `CostBook` + one `CostBookEntry` per product (and currency), with `Cost`, `EffectiveFrom` and `EffectiveTo`. The QuantumBit plan loads 623 entries (Upsert on `CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode`) [Repo: `datasets/sfdmu/qb/en-US/qb-pricing/`] | [../cost-books.md](../cost-books.md) |
| 2 | Lookup | Decision table `RLM_CostBookEntries` over `CostBookEntry`, mapped to `NGPDefaultRecipe`, then refreshed after every cost change. The shipped step looks up by product and currency only: no book, no date ([../cost-books.md → How pricing uses it](../cost-books.md#how-pricing-uses-it)) | `../../decision-tables/authoring-and-data-model.md`, `../../pricing-wiring/SKILL.md` |
| 3 | Unit cost | List Price step `Getunitcostfromcostbook` (top level, seq 6) writes the cost to `ItemUnitCost__std`, not to `ListPrice` [Repo: `force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml`] | `../../pricing-procedures/elements/list-price.md` |
| 4 | Line cost and margin | List Group `Calculatecostandmarginforpricedlines` filters lines with `ItemUnitCost__std` not null. Its formula step `Calculatetotalcostandmargin` writes `ItemTotalCost__std = ItemUnitCost__std * LineItemQuantity`, `ItemMargin__std = (ItemNetTotalPrice - total cost) / ItemNetTotalPrice` and `ItemMarginAmount__std`. That cost is **one pricing period**; term lines need the overlay [below](#term-lines-cost-one-period) | `../../pricing-procedures/elements/formula-based-pricing.md`, `../../pricing-procedures/elements/list-group-and-list-operation.md` |
| 5 | Persisted fields | `RLM_SalesTransactionContext` maps those tags to `QuoteLineItem.UnitCost`, `TotalCost`, `Margin` and `MarginAmount` (and the same on order products) [Repo: `docs/references/context-definitions/RLM_SalesTransactionContext.contextDefinition-meta.xml`]. `Margin` reads in **percent units** (below) | `../../context-service/SKILL.md` |
| 6 | Quote total | No shipped aggregate sums cost or margin onto the quote. Use a roll-up summary field on `QuoteLineItem.TotalCost`, as the manufacturing bundle does with `Quote.RLM_MFG_Total_Cost__c` [Repo: `unpackaged/post_manufacturing_core/objects/Quote/fields/`]. Derive quote margin from it and the quote total, or use the full-term roll-ups in [full-term-value.md](full-term-value.md) | `../../pricing-procedures/procedure-anatomy-and-ordering.md` (why a formula after the DDS tail is rejected or lags) |
| 7 | Visibility | Add the line fields to the line editor's Display Columns. Restrict unit cost to the users who may see it with field-level security | Help `ind.qocal_select_fields_for_the_line_editor.htm`, `../../apex-security-hardening/SKILL.md` (permission sets) |

## Modeling costs from a source

- **One entry per product and currency.** A cost that varies by configuration needs a
  product per variant, or a custom lookup keyed on the attribute.
- **Cost per pricing term.** Load the cost for one pricing term of the product's selling
  model (per year for an annual term line, per month for a monthly Evergreen line), so
  that it scales with `PricingTermCount` the way the price does. The lookup keys on product
  and currency only, so a product sold under two selling models with different terms
  (annual and monthly) can hold only one per-term cost; use a product per selling model, or
  one of the two line types gets the wrong cost `[inferred]`. Several entries for one product
  and currency are not resolved by book or date. In the discount lookup path a single-output lookup
  with several matches raises a duplicate-value error; the cost step's path was not separately
  traced and its mode is unknown, so if the table is single-output it raises ([../cost-books.md](../cost-books.md#how-pricing-uses-it)).
- **Services priced per hour or day:** load the loaded cost per unit, for example blended
  hourly cost × (1 + overhead), or × 8 for a day. Compute it before loading; the cost book
  holds only the result.
- **Pass-through items** such as travel: cost close to price, so a low margin by design.

## Check before relying on margins

### <a name="term-lines-cost-one-period"></a>Term lines cost one period

`[Measured]` The shipped formula multiplies unit cost by quantity only, while a term line's
`ItemNetTotalPrice` covers every term (`PricingTermCount`). On a three-year Term Defined
annual line (`SubscriptionTerm` 3, `SubscriptionTermUnit` `Annual`), the shipped procedure
wrote a `TotalCost` of exactly one year's cost, so cost was understated by a factor of three
and `Margin` overstated.

Fix it with an overlay on the formula step `Calculatetotalcostandmargin` in a clone of the
procedure (`../../expression-sets/SKILL.md` for overlays; `../../pricing-procedures/SKILL.md`
for cloning and pointing Revenue Settings at the clone):

| Output | Formula |
|---|---|
| `ItemTotalCost__std` | `ItemUnitCost__std * LineItemQuantity * IF(ISNULL(PricingTermCount), 1, IF(PricingTermCount > 0, PricingTermCount, 1))` |
| `ItemMargin__std` | `( ItemNetTotalPrice - ItemTotalCost__std ) / ItemNetTotalPrice` |
| `ItemMarginAmount__std` | `ItemNetTotalPrice - ItemTotalCost__std` |

`[Measured]` with this overlay:
- The term line's cost covered all three years and its margin matched a hand calculation.
- The margin formulas read `ItemTotalCost__std`, the first formula's output in the same
  element; this works.
- **The guard is needed.** One-Time lines carry `PricingTermCount` 0 (the procedure's
  `OneTimePricingTermCountConstant`), which would zero their cost. With the guard a One-Time line costs once.
- Evergreen lines without an end date carry `PricingTermCount` 1 (the procedure's
  `EvergreenPricingTermCountConstant`), so their cost stays per period, like their price.
- Each segment line of a yearly group ramp carries `PricingTermCount` 1, so each segment
  costs one year and the segments sum to the full term.

Example (neutral numbers): an annual line at 1,000 per year with a cost of 400 per year, 2
years (`SubscriptionTerm` 2 `Annual`), quantity 1. `TotalPrice` 2,000. Shipped: `TotalCost`
400, `Margin` 80. With the overlay: `TotalCost` 800, `Margin` 60.

`[Measured]` Carry a term line's term in the selling model's unit: on an annual model,
`SubscriptionTerm` 36 `Months` gave `PricingTermCount` 36 and priced 36 years, where 3
`Annual` gives 3. `[Platform behaviour, traced]` The count is the Proration step's multiplier,
read in the selling model's unit, falling back to the dates when no term is given; a One-Time line
carries 0 only where the procedure sets it (the shipped procedure's constant `[Repo]`).
A line given only start and end dates gets its term count from the dates, but Place does not derive `SubscriptionTerm` from dates `[Platform behaviour, traced]`. The trace shows Place filling a missing term context tag with the selling model's pricing term when the line's selling model option is Term Defined, but not that fill reaching the saved line. In the measured requests (price book entry only, no `ProductSellingModelId` in the request; the saved line's selling model was Term Defined) the saved unit was `Annual` but `SubscriptionTerm` stayed null: a dates-only Term Defined Annual line (System pricing, configuration method Force, rules on) priced from its dates (term count 3) and did not get the term-keyed discount step that the measured org's customised pricing procedure adds (not a shipped step) when a header switch is on (it was on), both standalone (net 17,100, vs 16,416 when the line was sent with `SubscriptionTerm` 3 and unit `Annual` instead of an end date) and as a bundle component (16,587 vs 15,923.52 on the same change) `[Measured: 2026-11-11, 264, scratch]`. Why the term was not filled was not established. A filter that reads `SubscriptionTerm` (such as a
commitment-term discount, `../../pricing-procedures/elements/commitment-term-discount.md`)
skips such a line; send the term explicitly.

### Margin units

`[Measured]` `QuoteLineItem.Margin` (and `ItemMargin__std`) reads in **percent units**:
a line with net total 2,000 and cost 800 reads 60, not 0.6, although the formula computes
a ratio. Divide by 100 before comparing it with a ratio, such as a quote-level margin
formula field.

### Other checks

- **Evergreen lines** without an end date are priced for one period: the shipped procedure
  assigns them `EvergreenPricingTermCountConstant` (1) [Repo], and the Evergreen default term
  count in Salesforce Pricing Setup also reads 1 on a fresh 264 org `[Measured]`
  ([../proration-and-selling-models.md](../proration-and-selling-models.md#default-term-counts)).
  `[Measured]` A $50/month line totals $50, and the quote total counts it for one period next
  to term lines at their full term. For a "full commitment" deal size or margin, such as
  monthly support counted over a comparison horizon, follow [full-term-value.md](full-term-value.md);
  don't change the Evergreen term count, which changes every Evergreen line's price.
- **Lines without a cost entry** are skipped by the filter, so they show no margin. They
  aren't zero-margin.
- **Table freshness:** a cost change without a refresh leaves the old cost. A quote priced
  while the refresh flow is still running gets empty lookups with no error; wait until
  the tables read Fresh (`../../decision-tables/SKILL.md`).

## Price from cost and a target margin

`[Measured]` A rule such as "price = unit cost ÷ (1 − target margin)", with the target
entered per line, works with:
- a custom Percent field on the line for the target margin, mapped into the context
  definition (`context-service`);
- a List Group whose filter admits lines with the target set and greater than 0 and
  `ItemUnitCost__std` not null, and a formula step under it writing
  `ROUND(ItemUnitCost__std / (1 - <target field> / 100), 2)` to `NetUnitPrice`. A Percent
  field reaches the formula in percent units, hence the `/ 100`;
- that group placed before Manual Discount (`pricing-procedures` →
  `procedure-anatomy-and-ordering.md`). The measured build placed it after the volume
  discount steps, so on a line with a target it replaces their result.

Example (neutral numbers): cost 60.00 at a 40% target → 100.00.

## Verify

```bash
sf data query -q "SELECT Product2.StockKeepingUnit, Quantity, PricingTermCount, TotalPrice, UnitCost, TotalCost, Margin, MarginAmount FROM QuoteLineItem WHERE QuoteId = '<quote>'" --target-org <sf_alias>
```

`UnitCost` equals the cost entry for that product and currency. `TotalCost` equals
`UnitCost × Quantity` with the shipped procedure, or `UnitCost × Quantity × PricingTermCount`
(1 when the count is null or 0) with the overlay. With no header discount, `Margin` equals
`(TotalPrice − TotalCost) / TotalPrice × 100`. The margin step runs before the header-discount
groups and Discount Distribution, so a distributed header discount isn't in `Margin`
`[inferred]`. Then repeat the query on the order.

## Open questions

- OPEN: how a cost-based target price (unit cost ÷ (1 − target margin), above) interacts
  with a later Manual Discount in the same procedure. Manual Discount reads the previous
  `NetUnitPrice` as its input (`../../pricing-procedures/elements/manual-discount.md`), so a
  rep discount after the target-price step may take the line below its target margin. Whether
  the target should act as a floor, or be re-applied after discounts, is untested.
