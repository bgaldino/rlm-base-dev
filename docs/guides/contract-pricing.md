# Contract Pricing

How negotiated prices stored on a Contract reach quote lines through
`RLM_DefaultPricingProcedure`, how amendments behave, and what to check when a
contract price does not appear. Written for SEs and builders setting up or
demonstrating contract pricing on QuantumBit.

Adapted from the contract-pricing reference built in the TAT-264 org, and
updated to what this repository deploys. Where the two differ, see
[Coming from the TAT-264 reference org](#coming-from-the-tat-264-reference-org).

## The two things to know first

**Pricing reads `Quote.PricingContractId`, not `Quote.ContractId`.** The
before-save flow `RLM_Set_Pricing_Contract_On_Quote` fills it from `ContractId`,
so in practice you set the contract on the quote and reprice.

**Once a line holds a contract price, it behaves like a Sales Price the rep
typed.** Removing the contract, or switching the quote to another contract,
does not take that price off the line. Clear the line's Sales Price and reprice
to re-derive it (see [Changing the contract on a priced quote](#changing-the-contract-on-a-priced-quote)).
This is the platform's default rule, and it is also what keeps a hand-set
Sales Price from being overwritten on the next reprice.

## What a contract can carry

Each `ContractItemPrice` row applies to one product and one selling model over
one date window.

| Contract price type | Fields on `ContractItemPrice` | Effect on the line | Waterfall element |
|---|---|---|---|
| Fixed price | `Price` | Sales Price becomes the contract price | *Assigned From Pricing Contract*, or *… for undated lines* |
| Percentage discount | `DiscountType = AdjustmentPercentage`, `DiscountValue` | Sales Price stays at list; Net Unit Price is discounted | *Discount Assigned From Pricing Contract* |
| Amount discount | `DiscountType = AdjustmentAmount`, `DiscountValue` | Same element as the percentage discount | *Discount Assigned From Pricing Contract* |
| Volume tiers | `AdjustmentMethod = Range`, plus `ContractItemPriceAdjTier` rows | Tier bracket picked by quantity | *Calculate net unit, net total, and contract prices after volume-based discounts* |

For year-by-year pricing, add one row per year with non-overlapping
`StartDate`/`EndDate`. Each line picks the window that contains its own
`StartDate`, so one quote can carry lines in different contract years.

## How a line gets its contract price

1. **Quote.** `RLM_Set_Pricing_Contract_On_Quote` sets `PricingContractId` from
   `ContractId` when it is blank, and again whenever `ContractId` changes,
   including when it is cleared. A different value set by hand is kept until
   `ContractId` changes.
2. **Lines.** *Pass Pricing Contract ID from Quote to Quote Lines* copies the
   quote's pricing contract to every line (`QuoteLineItem.PricingContractId`).
   *Default pricing contract for amendment and renewal lines* falls back to the
   line's platform `ItemContract` when the engine supplies one. On quotes that
   tag has no field behind it, so the contract normally arrives through the
   quote.
3. **Lookup.** *Assigned From Pricing Contract* reads the
   **Contract Pricing Entries** decision table:

   | Input | Match |
   |---|---|
   | Contract, product, selling model, currency | equals (required) |
   | Selling model type | equals (optional) |
   | Line `StartDate` | on or after the row's `StartDate` |
   | Line `StartDate` | on or before the row's `EndDate` (optional) |

   Lines with no `StartDate`, such as an undated one-time service, run
   *Assigned From Pricing Contract for undated lines* instead, which matches on
   the date of the pricing run.
4. **Sales Price.** *Set input unit price for lines with contract pricing*
   copies the contract price into Sales Price when Sales Price is empty or
   still equals List Price. On lines still tagged `LastTransaction`
   (amendment and renewal lines) it always does.
5. **Discounts.** *Discount Assigned From Pricing Contract* applies a
   percentage or amount contract discount to Net Unit Price. It skips
   last-transaction lines, because the asset price they carry already includes
   the original deal's discount.
6. **Last-transaction lines with a contract price.** *Set net unit price for
   contracted last-transaction lines* sets Net Unit Price to the contract price
   after renewal price revision and ramp uplift have run. A negotiated price is
   not uplifted on top.

A line with no matching row prices as it would without a contract.

## Amendments and renewals

Amendment and renewal lines carry `PricingSource = LastTransaction`: they start
from the asset's last price. A contract price for the line overrides it; a
discount-only row, or no row at all, leaves the asset price in place.

These were run live on amendment quotes created with the
`/connect/revenue-management/assets/actions/amend` API, from assets sold at
list price (12000) with no contract. Renewals take the same last-transaction
path but were not run.

| Situation | Result |
|---|---|
| Amended without a contract | Asset price (12000) |
| Contract linked to the amendment quote, then repriced | Contract price (1000) where the contract has a price for the product; asset price where it only has a discount |
| Amended with `contractId` set to the contract the assets belong to | Contract price on the first pricing |
| Assets linked to a contract, but amended without `contractId` | Asset price: the contract is not carried onto the quote |
| Never-priced amendment quote linked to a second contract | That contract's price |

Two platform behaviors to expect:

- **The amend API only accepts a `contractId` the assets belong to**, through
  `AssetContractRelationship`. A contract you create by hand needs a
  `RevenueLifecycleManagement` `AppUsageAssignment` before assets can be
  linked to it.
- **The platform re-tags a contract-priced amendment line** from
  `LastTransaction` to `PriceBookListPrice` on the next pricing, because its
  price no longer matches the asset. Contract pricing applies to both values,
  so the price holds.

## Changing the contract on a priced quote

| Change | Result | To re-derive |
|---|---|---|
| Contract removed from a contract-priced amendment line | Contract price stays | Clear Sales Price and reprice: the asset price returns |
| Quote switched to another contract | Previous contract's price stays | Clear Sales Price and reprice: the new contract's price applies |
| Sales Price set by hand on a contracted line | Hand-set price stays | Clear Sales Price and reprice |

On new-sale lines the place API ignores a null `UnitPrice`, so clearing it
through the API does not trigger a new lookup. Delete and re-add the line
instead.

## Setup checklist

1. **Activate the contract.** Activation runs
   `RLM_Contract_Activation_Refresh_Pricing_Tables`, which refreshes the three
   contract pricing tables. The two tier tables only include activated
   contracts.
2. **Check the refresh landed before testing.** The refresh is asynchronous,
   and the flow absorbs refresh failures so that activation never rolls back.
   Compare the table's `LastSyncDate` and `LastIncrementalSyncDate` with your
   last `ContractItemPrice` change: a refresh can land as an incremental sync
   that leaves `LastSyncDate` unchanged. The per-table source queries are in
   the pricing-wiring skill, under
   [Runtime-created pricing rows](../../.cursor/skills/pricing-wiring/SKILL.md#runtime-created-pricing-rows).
   Refresh by hand with `scripts/decision_tables/refresh_decision_table.py`.
   Rows added to an already-active contract need a refresh too.
3. **Match product, selling model and currency exactly.** A row for a product's
   Term Annual selling model does not match a Term Monthly line, and there is
   no wildcard.
4. **Keep each row's dates inside the contract term, and windows for the same
   product and selling model from overlapping.** Overlapping windows make one
   line match more than one row.
5. **Use realistic demo prices.** The line's Margin field holds at most 999.99
   in either direction. A contract price far below the cost-book cost, over a
   short prorated term, fails pricing with `NUMBER_OUTSIDE_VALID_RANGE` on
   `Margin`.

## Creating a contract from a quote

`RLM CreateContractFromQuote` (in `unpackaged/post_utils`) offers three options:

| Option | Creates |
|---|---|
| None | Contract header only |
| Discount | Header plus one contract discount per quote line |
| Net Unit Price | Header plus one contract price per quote line, from its Net Unit Price |

It also sets `Contract.PricingSource = LastTransaction`. A Net Unit Price
contract captures the price each line had on that quote: volume tiers on the
source quote are not carried over as tier rows.

## Known limits

- **No category-level prices.** The entries table requires the selling model as
  an exact match, so a row without one never matches. Generate one row per
  product and selling model instead.
- **Volume tier rows are not generated** when a contract is created from a
  quote (observed in the TAT-264 org). Create `ContractItemPriceAdjTier` rows
  yourself.
- **The volume-tier lookup still uses the quote-level `PricingDate`**, not each
  line's start date, so on a multi-year quote every line's tier lookup uses
  one date. When a contract has no tiers, that lookup also resets
  `IsContracted` to false.
- **An applied contract price does not follow a change of window.** Moving a
  priced line's start date into another year keeps the old price, for the same
  reason as [Changing the contract on a priced quote](#changing-the-contract-on-a-priced-quote).
- **There is no `Order.PricingContractId` sync.**
- **Not exercised live in this repository:** amount discounts, volume tiers,
  bundle children, renewals, and amendment lines with no quantity change.

## Coming from the TAT-264 reference org

That org applied the V2 migration runbook as a second procedure version. This
repository folds the same intent into `RLM_DefaultPricingProcedure_V1`, with
these differences:

| Reference org | This repository | Why |
|---|---|---|
| Lookup dated by `DerivedStartDateTime__std` | Dated by the line's `StartDate` | `DerivedStartDateTime__std` is empty until the line is saved, so first pricing of a multi-window contract failed with `DUPLICATE_VALUE_FOUND_IN_LOOKUP` |
| Undated lines skipped | Priced on the run date | One-time services priced from the contract (the reference org's "one-time products skip contract pricing" gap) |
| Lookup writes Sales Price directly | Sales Price set only while it is empty or still list | A hand-set Sales Price survives a reprice |
| Contracted lines excluded from the list-price fallback | Kept in it | Discount-only rows have no price, and excluding them left Sales Price at 0 |
| Flow sets `PricingContractId = ContractId` on every save, with `ISNULL` | Fills it when blank and follows `ContractId` changes, with `ISBLANK` | `ISNULL` misses a blank lookup, and a hand-set value was overwritten |
| Last-transaction override on any contract-linked line | Only on lines that get a contract price | Contract-linked amendment lines with no contract price keep renewal revision and ramp uplift |
| Field access through 75 partial profiles | `RLM_QuantumBit` and `RLM_QuantumBit_Sales_Representative` permission sets | Profiles in `force-app/` carry class access only |
| Line `PricingContractId` editable on the layout | Read-only | The procedure overwrites it on every pricing |
