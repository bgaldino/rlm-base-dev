# Verifying a Change End to End

Read this when testing an amendment, swap, cancellation or renewal. Parent:
[asset-lifecycle-changes](SKILL.md).

## The test

For each change, record the state after every step:

1. **Initiate** with the change's invocable action:
   `POST /services/data/v68.0/actions/standard/<action>` with `{"inputs":[{...}]}`, where
   the action is `initiateAmendment`, `initiateCancellation` or `initiateRenewal`. Use
   output type `Quote` to inspect before committing. The inputs are in
   `rlm-business-apis` → `backdated-asset-lifecycle.md` → API path. The 2026-11-11 runs
   amended through Connect instead (`POST /connect/revenue-management/assets/actions/amend`
   on the top-level asset, `quantityChange` 0, Quote output), then made the change with a
   Place request.
2. **Make the change and read the quote.** Edit an amendment line or answer through Place
   with `configurationMethod: Force` (and `configurationPref.configurationOptions.executeConfigurationRules: true` for rules on), as in
   the measured runs. On a No Change line, `Skip` refused a non-zero quantity ("Specify 0 in
   Quantity...") and `Force` accepted it, turning the line's `QuoteAction.Type` to Amend, even
   at quantity 0 [Measured: 2026-11-12, 264, scratch; one standalone asset, System pricing]
   (SKILL.md Quick Rule 7). Then read:
    - each line's `Quantity`, `UnitPrice` and `TotalPrice`. On an amendment quote
      `Quantity` is the delta, and `StartQuantity` and `EndQuantity` the totals before and
      after. A line's source asset is on `QuoteAction.SourceAssetId`; `QuoteLineItem` has
      no `AssetId`. An amendment quote has no contract or related-quote link, and its lines
      reach the asset only through the quote action (change-policy-mapping.md → Questions to
      settle in the plan);
    - its `QuoteLineDetail` rows (dated by `EffectiveFrom` and `EffectiveTo`);
    - `QuoteLineItemAttribute` for configured products;
    - the header `Subtotal`, `Discount` and `TotalPrice`.
3. **Reprice** and read again: nothing should move. Use Reprice All or a Place request
   with Force pricing, or a Place request that includes a line record. A Place request
   that patches only the quote header isn't priced under System pricing: it is priced
   only when it carries at least one quote or order line (or line attribute) record, so a
   header-only PATCH leaves the lines untouched and "nothing moved" proves nothing. A
   request that carries a context id is priced whenever the transaction has lines (not
   measured). Force always prices [Platform behaviour, traced].
4. **Create the order** (`createOrdersFromQuote`), reprice it, and read `OrderItem`,
   `OrderItemDetail` and `OrderItemAttribute`. Read the order's `EffectiveDate` back: it is
   set to the earlier of the day the order is created and the earliest line start date on
   the quote, and nothing in the call sets it. A quote that starts in the future therefore
   gives an order dated today, and a past start gives an order dated at the earliest start.
   For a dated replay set the line start dates (in the past to backdate) before creating
   the order [Measured: 2026-11-12, 264, a 2027-01-01 start gave an order dated the run
   date] [Platform behaviour, traced]. Lines with no start date are ignored. This is the standard advanced quote-to-order path only; industry processors and time-zone conversion weren't checked (`quote-negotiation-rounds` has the order-creation detail). Whether each
   order of a split gets its own minimum, and where the order item's service date comes
   from on amendment lines, wasn't established: read each created order back [Platform
   behaviour, traced in part].
5. **Activate the order.** Fill its bill-to contact and addresses first: backdated-change
   orders were refused without them [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`
   → Activating the order]. Amendment and renewal quotes had `AccountId` null and `QuoteAccountId` set
   [Measured: 2026-11-11 (amendment) and 2026-11-12 (amendment and renewal), 264,
   scratch org]. They carry the account in `QuoteAccountId` when the org allows quotes without an
   opportunity [Platform behaviour, traced]; this repo's scratch org definitions enable it
   [Repo: `config/project-scratch-def.json`]. With that setting off, they get an opportunity
   and `AccountId` comes from it [Platform behaviour, traced; not measured], so a lookup that
   must work on both kinds of org reads `QuoteAccountId` and falls back to `AccountId`.
   Cancellation quotes weren't measured; the same code path builds them
   [Platform behaviour, traced].
6. **Read the asset:**
    - `AssetStatePeriod` (`StartDate`, `EndDate`, `Quantity`, `Amount`, `Mrr`);
    - `AssetStatePeriodAttribute`;
    - `AssetAction` (`Type`, `CategoryEnum`, `QuantityChange`, `Amount`), which links to
      the order lines through `AssetActionSource.ReferenceEntityItemId`: the order line's
      Id, or its `OrderItemDetail` Id when the line has detail rows (SKILL.md Quick Rule 2)
      [Platform behaviour, traced].
    - For a CML bundle that will be amended again, the root's latest asset action source
      rows must carry the node status (SKILL.md Quick Rule 2). `AssetAction.ActionDate` is
      the activation time, so the latest action is the last one activated. The field is
      long text, so read it rather than filtering on it:
      `SELECT Id, ReferenceEntityItemId, RLM_ConstraintEngineNodeStatus__c, AssetAction.ActionDate FROM AssetActionSource WHERE AssetAction.AssetId = '<root asset>' ORDER BY AssetAction.ActionDate DESC`.

## Measured results (QuantumBit builds, release 264, 2026-11-05)

On a configured bundle (a device with a one-time selling model, an evergreen annual
service component and a one-time accessory). The assets' `PricingSource` was not recorded:

| Change | Quote | After reprice, order, order reprice, activation |
|---|---|---|
| Amend +1 (API `quantityChange: 1`) | +1 × net unit on the root; components at quantity 0 | Unchanged; new state period with quantity 2; asset action "Change / Upsells" for the net unit |
| Amend −1 (API) | −1 × net unit; parent `UnitPrice` null, detail row carries it | Unchanged; state period back to 1; "Change / Downsells" |
| Cancel the top-level asset | Every line −1; prices in detail rows | Unchanged; state periods end at the cancel date; "Cancel / Cancellations" |
| Cancel or renew a component alone | Refused: "the asset is a bundle component. Provide the top-level asset" | — |
| Renew | $0; quantity 0 on every line (no Term Defined line) | — |
| Amend in the UI, inline quantity edit, rules on | Total right; parent prices blank (details +2 and −1); **attributes reset to product defaults** | The asset's new state period carries the defaults |

The action history netted to zero over add, add, remove and cancel (+, +, −, −). The
attributes stayed unchanged after an `initiateAmendment` with `quantityChange`, a quantity change
with configuration rules off, a reprice with rules on and **no** quantity change, and a
cancellation. The attribute reset also reproduced on a product
outside any custom model: one attribute went from its chosen value to its default. That
points to platform or base-build behaviour rather than a particular catalog.

Cancellation credits on the quote, by selling model, at +1, +30, +180, +300 and +400 days:
- one-time: the full price every time;
- evergreen annual: one annual period every time;
- evergreen monthly: one monthly period every time.

The Standard price book gave the same results.

## Measured results (fresh 264 `ent-sb0` scratch orgs, 2026-11-11)

On a Term Defined bundle sized by CML root answers (locations, seats), with Term Defined, evergreen
monthly and one-time components, three annual periods, configuration rules on, and every
asset's `PricingSource` `LastTransaction`. The ordered changes ran in date order, each
through activation before the next; a reprice moved nothing at any step:

| Change | Quote | After order and activation |
|---|---|---|
| Root answer changed (more locations), mid-period | Each CML-sized child as a delta line at its price; other children 0; root a −1 / +1 detail pair at 0.00. Term Defined lines at 2 + 275/365 terms (day counts illustrative; the rule is what was measured) | New state periods from the amendment date; "Change / Upsells" per delta, amounts equal to the line totals |
| Second answer changed (more seats) on a later amendment | The first answer reset to its CML default and its children came back negative, until restated in a second Place request (SKILL.md Quick Rule 2) | Ordered after the restatement; state periods carry both answers |
| Added units on a `LastTransaction` asset | A plain delta line at the asset's last net price; no volume-band step; existing units unchanged | State period at the new total, MRR at the last price |
| The same, with a re-band overlay on the procedure ([change-policy-mapping.md](change-policy-mapping.md) → volume-band row) | The added units at the band for the new total | MRR = existing units at their old price + added units at the new band |
| Term Defined component to 0 on an anniversary | −qty × net unit × 1 term, in two last-in-first-out detail rows | Component asset kept; state period 0 from the date; "Change / Downsells" for the credit |
| The same, with 275 days left in the current period (quote only) | Term count 1 + 275/366 (leap year), not 1.75 (day counts illustrative; the rule is what was measured) | Not ordered |
| Plan answer changed while an add-on required the old plan | The add-on removed and the plan's lines moved, with no message | Not ordered |
| Part of a component moved to another plan (−n, new +n line) | Refused by a CML rule; with rules off, a component-group (max one) Warning log; either log blocked `createOrdersFromQuote` | Not ordered |
| Renewal with `renewalStartDate` and `renewalEndDate` | Term Defined lines per lot with the uplift agreed at the sale; evergreen component and one-time lines "No Change" at 0 | Same assets extended; `LifecycleEndDate` moved; "Change / Renewals" |
| Price amendment on an evergreen component line, dated on the renewal's start | Amend / FieldAmendment; delta 0; credit per lot at the old price, charge at the new | New state period MRR at the new price; "Change / Upsells" for the difference |

Amendments on a CML bundle depend on the configurator's node status: on one of these orgs
(the answer reset reproduced on the other) `AssetActionSource.RLM_ConstraintEngineNodeStatus__c`
was empty after every activation while `OrderItem.RLM_ConstraintEngineNodeStatus__c` was
filled. That conflicts with the platform reading in SKILL.md Quick Rule 2, where item-sourced
rows take a mapped line value; the cause is **Open** (live check: which rows were blank). Copying the order lines' value onto the asset action sources before amending stopped
the reset. SKILL.md Quick Rule 2 has the cause, measured on a third org.

## Open: measure before promising

- **Term Defined top-level cancellation** (`initiateCancellation`): a Term Defined
  component's reduction to 0 prorated by day (above); the cancellation of a Term Defined
  top-level asset wasn't measured.
- **Swap values with constraints in force.**
- **Invoice values** for every change: the quote and order values above aren't the
  invoice. Billing verification is in `rlm-business-apis` → `backdated-asset-lifecycle.md`.
- **Whether the configurator can restore the reset attributes** on an amendment line.
- **Changing a bundle component's plan:** a plan held as an attribute on the component's
  line, or a swap of the component asset. A price amendment on a component's line, a plan
  held as a root answer, and a partial move under a one-plan group are measured (above;
  [change-policy-mapping.md](change-policy-mapping.md)).
- **Evergreen reductions and swaps:** what an amendment with `quantityChange` < 0, or a
  swap's outgoing side, credits on an evergreen line. Reductions priced on quotes that weren't
  ordered; the only evergreen credit measured through activation is a cancellation's (above).
- **Renewing a standalone evergreen asset.** Help rules out uplift and end-date changes for
  evergreen assets but doesn't say what the renewal quote does to the line
  ([change-policy-mapping.md](change-policy-mapping.md)). In a bundle renewal the evergreen
  component was a "No Change" line at quantity 0 (above).
- **An earlier-dated change against a future-dated one:** the amend and cancel articles
  say it's refused, while *Future-Dated Changes* and its examples allow it
  ([change-policy-mapping.md](change-policy-mapping.md) → Replay the source's changes in
  date order). The repo's group-ramp runs changed assets before a ramp segment's future
  state period, which comes from the ramp schedule rather than a future-dated transaction,
  so they don't settle it [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`]. In the
  group-ramped bundle runs, a future ramped renewal, or an ordered plain renewal, refused an
  earlier amend [Repo: `ramped-quotes/bundle-children-lifecycle.md` → Amend date window],
  which matches the amend article for that case. That record doesn't cover a future-dated
  amendment or cancellation.
- **Amendment dates at a term end:** the recorded amend date window was measured on
  group-ramped bundles. Whether it holds for other assets, and its upper bound for assets
  with no end date, are open. An amendment dated exactly on a renewal's start date was
  accepted after the renewal was activated (above;
  [change-policy-mapping.md](change-policy-mapping.md) → Changes dated at or after the term
  end).
