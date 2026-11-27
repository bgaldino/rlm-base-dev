# Ramped Quotes — Status polling, read-back and id discovery

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`. Used between and after the build steps in [build-sequence.md](build-sequence.md).

### <a name="status"></a>Poll `CalculationStatus` between calls

`Quote.CalculationStatus` is read-only and moves through tax/price/save states.
Match against the **live v68 enum** (from `scripts/erd/schema_diff/264-schema.json`),
not a suffix wildcard — several in-flight values are `QueuedFor…`-**prefixed** (they
do not *end* in `Queued`) and `TaxCalculationInProcess` is not `…InProgress`:

- **Settled — success:** `CompletedWithTax` (the org returns this where the describe
  lists `TaxCalculationSuccess` — treat both as success); `CompletedWithoutPricing`
  (settled, but pricing was **skipped** — not a priced result, so do not report
  prices from it; with `require_priced`, `E2ECommon.robot` treats it as failed and reprices once).
- **`CompletedWithPricing` — settled *when tax doesn't run*.** Pricing is done; on
  an org that calculates estimated tax, tax runs next. Which applies depends on the org:
  - **Foundations default build:** estimated tax on quotes and orders is **off**
    (`unpackaged/post_quote_est_tax_settings/`; the `quote_est_tax` flag, with `tax`,
    turns it on). Tax never
    runs, so `CompletedWithPricing` is **terminal**. Live 264.7, 2026-10-14: quotes
    stopped there with no `taxPref`.
  - **Estimated tax on and `taxPref` omitted:** `taxPref` defaults to running tax
    (`connect-requests-place-sales-transaction-input.md`), so `CompletedWithPricing`
    is **still in flight**; wait for `CompletedWithTax`.
  - **`taxPref: "Skip"`:** terminal on any org.
  - The platform also skips tax when any line has a **negative quantity**, so a
    quantity reduction (a negative-quantity line) is terminal at `CompletedWithPricing`
    even with estimated tax on. A price-lowering amendment instead fails with
    `AmountNegative` while estimated tax is on.
  - Robust pollers accept both values as settled; see `E2ECommon.robot`
    `@{QUOTE_CALC_PRICED}`.
- **Settled — failure (the poll stops):** any `…Failed` — `TaxCalculationFailed`,
  `PriceCalculationFailed`, `SaveFailedOrIncomplete`, `ConfigurationFailed`,
  `ReconciliationFailed`, `GroupRampConfigurationFailed`, `PstBaseStepFailed`,
  `ARCStepFailed`, `QuoteRequestFailed`, `CloneFailed`, `ImportQLIFailed`.
  No source says whether a failed status clears on its own; the repo pollers don't wait for it
  (`E2ECommon.robot`, `_Is Failed Calculation Status`).
  [Open: leave a failed quote untouched for several minutes and re-read `CalculationStatus`]
  `E2ECommon.robot` `Wait For Quote Calculation` reprices once
  (Place Sales Transaction, `pricingPref` Force) and fails the test if the second wait also fails.
  The large-deal reference, written for `Order.CalculationStatus` (Release 262), likewise allows a
  bounded reprice retry for `PstBaseStepFailed`, `ConfigurationFailed`, `GroupRampConfigurationFailed`,
  `PriceCalculationFailed`, `TaxCalculationFailed`, `SaveFailedOrIncomplete` and `ReconciliationFailed`
  (it also lists `OrderRequestFailed`, an Order-only value;
  `troubleshooting/large-deal-preprocess-reference.md`).
- **Settled partially, investigate (guide) vs. reprice once (repo poller):** `QuoteRequestPartiallySaved`, `PartialSaveSuccess`.
  Divergence: the repo poller puts both in `@{QUOTE_CALC_FAILED}`, so `_Is Failed Calculation Status`
  is true and `Wait For Quote Calculation` reprices once, like a failure (`E2ECommon.robot`). The large-deal
  reference (Order statuses) says investigate rather than retry for `OrderRequestPartiallySaved` and
  `PartialSaveSuccess` (`troubleshooting/large-deal-preprocess-reference.md`); it does not name
  `QuoteRequestPartiallySaved`, so that value follows the same rule by analogy `[inferred]`.
- **In-flight (keep polling):** `NotStarted`, `TaxCalculationWaiting`,
  `TaxCalculationInProcess`, `PriceCalculationQueued`, `PriceCalculationInProgress`,
  `Saving`, `ConfigurationInProgress`, `ReconciliationInProgress`,
  `ContextHydrationInProgress`, `ARCInProgress`, `CloneInProgress`, `ImportQLIInProgress`, `ImportQLISuccess`
  (the import is done but pricing may not have started; `E2ECommon.robot` retries it only when `require_priced` is set), and every
  `QueuedFor…` value (`QueuedForConfiguration`, `QueuedForPricing`,
  `QueuedForPricingAndSaving`, `QueuedForSaving`, `QueuedForARC`, `QueuedForClone`).

**A value in none of these = stop and look**, not "keep polling" or "assume done".

## Read-back → the ramp schedule

**Assert the groups first.** A clone after a failed `EditGroup` still returns `success:true`: it
copies a group that was never converted, leaving segments with `IsRamped` and `SortOrder` null that
look like a healthy ramp by count and name. Before reading prices, check:
- every segment group has `IsRamped = true`, a non-null `SortOrder` and a `SegmentType`;
- the segment count is the number of periods;
- in multi-schedule mode (repo default), exactly one group has `Type = 'RampScheduleGroup'`. It is
  the parent, not a segment (observed with `IsRamped = false` and `SortOrder` 0; leave it out of the
  segment checks), and it carries the expected `RampUpliftType`. Every segment's
  `ParentQuoteLineGroupId` must be the `RampScheduleGroup`'s Id. A segment with no parent prices correctly and passes the
  checks above, then fails at order activation with "Specify a ramp schedule group for ramp
  segment".

```bash
sf data query --target-org <sf_alias> -q "SELECT Id, Name, Type, ParentQuoteLineGroupId, \
  IsRamped, SortOrder, SegmentType, RampUpliftType \
  FROM QuoteLineGroup WHERE QuoteId='<QUOTE_ID>' ORDER BY StartDate NULLS FIRST"
```

Then the lines:

```bash
sf data query --target-org <sf_alias> -q "SELECT Product2.Name, Product2.StockKeepingUnit, \
  SegmentName, IsPrimarySegment, RampIdentifier, StartDate, EndDate, Quantity, \
  UnitPrice, NetUnitPrice, TotalPrice, NetTotalPrice, UnitPriceUplift, \
  ApplUnitPriceUpliftPct, RampUpliftType, QuoteLineGroupId \
  FROM QuoteLineItem WHERE QuoteId='<QUOTE_ID>' ORDER BY StartDate NULLS FIRST"
```

Order by `StartDate` to find segment 1: `IsPrimarySegment` was false on **every** segment of a
UI-built ramp (measured 2026-11-11, fresh 264 `ent-sb0` scratch org), so it can't single out a segment.

Report: account, products, **TCV** (Σ all line totals across all segments),
per-period subtotal and **% of TCV**, and the ramp-by-product matrix (grouped on
`RampIdentifier`, labelled by `Product2.Name`/`StockKeepingUnit`). Sum the
platform-computed **`NetTotalPrice`** for TCV and subtotals — it is the
**post-discount, prorated** line total that propagates to the posted invoice
(`scripts/txn_data_harness/docs/contracts-sales-txn-quote.md`). Do **not** sum `TotalPrice`:
it isn't reliably the net total. In the 2026-11-11 UI ramps (fresh 264 `ent-sb0` scratch orgs) it
equalled quantity × net on Term lines but stayed at the un-uplifted price on One-Time and Evergreen
lines (Quick Rule 10). Do **not** derive totals from `Quantity × NetUnitPrice` either (unreliable for
term-priced/prorated lines). Both totals are read-only
(never *set* them) but queryable; all numbers come from the priced quote.

## <a name="discovering-ids"></a>Discovering ids

The ask won't give Salesforce ids — resolve them first. Map spoken product intent
("gen-AI licenses", "premium support") to real SKUs from the catalog; don't invent
SKUs.

```bash
# Account — SELECT CurrencyIsoCode: multicurrency is on (repo default), and it drives
# the Quote/PBE/BillingTreatment currency below.
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Name, CurrencyIsoCode FROM Account WHERE Name = '<name>'"
# PricebookEntry — a ramp needs BOTH Product2Id and this. Match the SKU on
# Product2.StockKeepingUnit (the repo's SKU field, per scripts/build_quote_to_asset.py
# and scripts/txn_data_harness/discovery.py — NOT ProductCode). Filter to the ACCOUNT
# currency and require BOTH the entry and the product active (IsActive = true AND
# Product2.IsActive = true), and read the selling model: a product can expose several
# (e.g. Evergreen / Term Monthly / Term Annual) and the model dictates which line
# fields are legal, so pick a TermDefined one deliberately (not the first row).
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Product2Id, Pricebook2Id, UnitPrice, \
     ProductSellingModel.Name, ProductSellingModel.SellingModelType \
   FROM PricebookEntry \
   WHERE Product2.StockKeepingUnit = '<SKU>' AND Pricebook2.IsStandard = true \
     AND IsActive = true AND Product2.IsActive = true \
     AND CurrencyIsoCode = '<ACCOUNT_CURRENCY>'"
# Group-ramp eligibility: no per-product ramp flag is required — any subscription
# (term-defined) product that meets the requirements is eligible by default (264
# Help). `Product2.CanRamp` is the LINE-ramp flag, not a group-ramp prerequisite.
# BillingTreatment for <TREATMENT_ID> — needed when the line's BillingFrequency differs from
# the selling model's term unit (billing-setup item 3). Then it must be Active, match the
# ACCOUNT currency, and have CanChangeBillingFrequency = true (when a treatment is needed,
# Place rejects one without it).
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Name, CanChangeBillingFrequency FROM BillingTreatment \
   WHERE Status = 'Active' AND CurrencyIsoCode = '<ACCOUNT_CURRENCY>' \
   AND CanChangeBillingFrequency = true ORDER BY Name"
```
