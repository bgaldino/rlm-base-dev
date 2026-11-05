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

**Pricing remembers the contract price it put into Sales Price.** It records it
in `QuoteLineItem.RLM_Contract_Applied_Unit_Price__c`. While Sales Price still
equals that value, a changed contract price, or a switch to another contract,
replaces it on the next reprice, and on a new-sale line a removed contract
returns it to List Price. A new-sale line with no contract price has its
recorded value cleared. A Sales Price the rep typed differs from the recorded
value, so it is kept, including an old contract price typed back in after the
contract is gone. Amendment lines are the exception when the contract goes away
(see [Changing the contract on a priced quote](#changing-the-contract-on-a-priced-quote)).

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
`StartDate`/`EndDate`. Price and discount rows are matched on each line's own
`StartDate`, so one quote can carry lines in different contract years. Volume
tiers are dated differently (see [Known limits](#known-limits)).

## How a line gets its contract price

1. **Quote.** `RLM_Set_Pricing_Contract_On_Quote` sets `PricingContractId` from
   `ContractId` when it is blank, and again whenever `ContractId` changes,
   including when it is cleared. A different value set by hand is kept until
   `ContractId` changes. When `PricingContractId` changes on an existing quote,
   `RLM_Cascade_Pricing_Contract_To_Quote_Lines` copies it to every line in the
   same save; if a line cannot be updated, the quote change is rolled back with
   the reason.
2. **Lines.** *Pass Pricing Contract ID from Quote to Quote Lines* copies the
   quote's pricing contract to every line (`QuoteLineItem.PricingContractId`)
   on every pricing run.
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
   the date of the pricing run. Both lookups skip lines with a quantity of 0 or
   less, so a credit keeps the prices the units were sold at.
4. **Sales Price.** *Set input unit price for lines with contract pricing*
   copies the contract price into Sales Price when Sales Price is empty, still
   equals List Price, or still equals the contract price it last applied. On
   lines still tagged `LastTransaction` (amendment and renewal lines) it always
   does. Each time, it records the price in
   `RLM_Contract_Applied_Unit_Price__c`. When a new-sale line no longer has a
   contract price but its Sales Price still equals the recorded one,
   *Set input unit price for lines without derived pricing or last-trxn
   pricing* returns Sales Price to List Price. Then *Clear
   contract applied unit price for lines without contract pricing* clears the
   recorded price on every new-sale line that has no contract price.
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

These were run live on quotes created with the
`/connect/revenue-management/assets/actions/amend`, `…/cancel` and `…/renew`
APIs. Most assets were sold at list price (12000) with no contract. One was
sold at 12000 and then increased by 1 at a contract price of 10000, under a
contract that prices it at 9000 from the credit and renewal dates.

| Situation | Result |
|---|---|
| Amended without a contract | Asset price (12000) |
| Contract linked to the amendment quote, then repriced | Contract price (1000) where the contract has a price for the product; asset price where it only has a discount |
| Amended with `contractId` set to the contract the assets belong to | Contract price on the first pricing |
| Assets linked to a contract, but amended without `contractId` | Asset price: the contract is not carried onto the quote |
| Never-priced amendment quote linked to a second contract | That contract's price |
| Quantity reduced, or the asset cancelled, with or without `contractId` | Credit at the prices the units were sold at, latest sale first: 10000 for one unit, 10000 and 12000 for two. The contract price (9000) is not used |
| Renewed with `contractId`, asset sold without a contract | Asset price (12000) when the quote is created; the contract price (9000) from its first pricing, standard or forced |
| Renewed with `contractId`, asset last sold under that contract | Contract price (9000) |
| Renewed without `contractId`, asset last sold under a contract | Contract price (9000) when created, carried from the asset; last sale price (10000) from the first pricing, because the quote has no contract. Renew with `contractId` to keep the contract price |

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

Each change takes effect on the next reprice.

| Change | Result | To re-derive |
|---|---|---|
| Contract price edited on a draft contract | New contract price | Refresh the contract pricing tables first (see the [setup checklist](#setup-checklist)). The platform rejects a `Price` edit once the contract is activated |
| Quote switched to another contract | That contract's price; on a new-sale line with no price in it, List Price | — |
| Contract removed from a new-sale line | List Price | — |
| Contract removed from a contract-priced amendment line | Contract price stays | Clear Sales Price and reprice: the asset price returns |
| Quote switched, on an amendment line the new contract has no price for | Previous contract's price stays | Clear Sales Price and reprice: the asset price returns |
| Sales Price set by hand on a contracted line | Hand-set price stays | Clear Sales Price and reprice |

Amendment lines keep the old price because their fallback is the asset's last
price, which only the platform supplies, and only once Sales Price is cleared.

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
   Rows added to an activated contract, or edited on a draft one, need a
   refresh too.
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
- **The volume-tier lookup is dated by `PricingDate`**, not each line's
  `StartDate`. The procedure sets `PricingDate` from `EffectiveFrom` (step 7),
  and from `EffectiveDate` on contracted lines where it is still empty (step 9),
  so on a multi-year quote the tier rows may not follow each line's contract
  year. In the TAT-264 org a contract with no tiers also
  reset `IsContracted` to false. Neither is verified in this repository yet.
- **Lines contract-priced before `RLM_Contract_Applied_Unit_Price__c` existed
  are not tracked.** On an org upgraded from an earlier build, their contract
  price stays put when the contract changes. Clear Sales Price and reprice once.
- **There is no `Order.PricingContractId` sync**, and applied contract prices
  are tracked on quote lines only. Orders use the same procedure, so on an
  order reprice *Pass Pricing Contract ID from Quote to Quote Lines* copies the
  order's `PricingContractId` (normally blank) to its lines, overwriting any
  line value.
- **Only `RLM_DefaultPricingProcedure` reads `PricingContractId`.**
  `RLM_Revenue_Management_Recalc_Procedure` and
  `RLM_PRM_DISTI_Pricing_Procedure` look up contract prices only from the
  line's `ItemContract`, which on quotes normally has no value. On a PRM
  distributor quote, when the quote procedure plan is active (it is built
  inactive), the DISTI procedure runs after the default one, keeps the contract
  Sales Price and takes the partner discount off it.
- **An org built before this procedure needs the field and the context
  attribute before the procedure is redeployed.** Deploy
  `unpackaged/pre/6_fields` (for `RLM_Contract_Applied_Unit_Price__c`) and run
  `apply_context_contract_pricing`, then redeploy the expression sets.
  `prepare_rlm_org` runs them in that order.
- **Not exercised live in this repository:** amount discounts, volume tiers,
  bundle children, and amendment lines with no quantity change. The contract
  lookups skip quantity 0, so those lines should keep the asset price.

## Coming from the TAT-264 reference org

That org applied the V2 migration runbook as a second procedure version. This
repository folds the same intent into `RLM_DefaultPricingProcedure_V1`, with
these differences:

| Reference org | This repository | Why |
|---|---|---|
| Lookup dated by `DerivedStartDateTime__std` | Price and discount lookups dated by the line's `StartDate` | `DerivedStartDateTime__std` is empty until the line is saved, so first pricing of a multi-window contract failed with `DUPLICATE_VALUE_FOUND_IN_LOOKUP` |
| Undated lines skipped | Priced on the run date | One-time services priced from the contract (the reference org's "one-time products skip contract pricing" gap) |
| Lookup writes Sales Price directly | Sales Price set only while it is empty, still list, or still the contract price last applied | A hand-set Sales Price survives a reprice, while contract changes still flow through |
| Contracted lines excluded from the list-price fallback | Kept in it | Discount-only rows have no price, and excluding them left Sales Price at 0 |
| Flow sets `PricingContractId = ContractId` on every save, with `ISNULL` | Fills it when blank and follows `ContractId` changes, with `ISBLANK` | `ISNULL` misses a blank lookup, and a hand-set value was overwritten |
| Last-transaction override on any contract-linked line | Only on lines that get a contract price | Contract-linked amendment lines with no contract price keep renewal revision and ramp uplift |
| Contract price looked up for every line | Only for lines with a positive quantity | On an asset sold under a contract, credits otherwise took the contract's current price instead of the price the units were sold at |
| Field access through 75 partial profiles | `RLM_QuantumBit` (and its TSO copy in `unpackaged/post_tso`), `RLM_QuantumBit_Sales_Representative` and `RLM_Partner_Community_User_Perm_Set` permission sets | Profiles in `force-app/` carry class access only, and a TSO build replaces `RLM_QuantumBit` with its TSO copy |
| Line `PricingContractId` editable on the layout | Read-only | The procedure overwrites it on every pricing |
