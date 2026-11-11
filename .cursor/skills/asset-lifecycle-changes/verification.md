# Verifying a Change End to End

Read this when testing an amendment, swap, cancellation or renewal. Parent:
[asset-lifecycle-changes](SKILL.md).

## The test

For each change, record the state after every step:

1. **Initiate** with the change's invocable action:
   `POST /services/data/v68.0/actions/standard/<action>` with `{"inputs":[{...}]}`, where
   the action is `initiateAmendment`, `initiateCancellation` or `initiateRenewal`. Use
   output type `Quote` to inspect before committing. The inputs are in
   `rlm-business-apis` → `backdated-asset-lifecycle.md` → API path.
2. **Read the quote:**
    - each line's `Quantity`, `UnitPrice` and `TotalPrice`;
    - its `QuoteLineDetail` rows;
    - `QuoteLineItemAttribute` for configured products;
    - the header `Subtotal`, `Discount` and `TotalPrice`.
3. **Reprice** (Place Sales Transaction with a Quote PATCH) and read again: nothing
   should move.
4. **Create the order** (`createOrdersFromQuote`), reprice it, and read `OrderItem`,
   `OrderItemDetail` and `OrderItemAttribute`.
5. **Activate the order.** Fill its bill-to contact and addresses first: backdated-change
   orders were refused without them [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`
   → Activating the order].
6. **Read the asset:**
    - `AssetStatePeriod` (`StartDate`, `EndDate`, `Quantity`, `Amount`, `Mrr`);
    - `AssetStatePeriodAttribute`;
    - `AssetAction` (`Type`, `CategoryEnum`, `QuantityChange`, `Amount`), which links to
      the order lines through `AssetActionSource.ReferenceEntityItemId`.

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

## Open: measure before promising

- **Term Defined cancellation credit:** prorated by months remaining, or not?
- **Re-banding on amendment:** do new units price at the band for the new total, and do
  existing units keep their price?
- **Swap values with constraints in force.**
- **Invoice values** for every change: the quote and order values above aren't the
  invoice. Billing verification is in `rlm-business-apis` → `backdated-asset-lifecycle.md`.
- **Whether the configurator can restore the reset attributes** on an amendment line.
- **Removing a bundle component through an amendment** of the top-level asset.
- **Renewing a standalone evergreen asset.** Help rules out uplift and end-date changes for
  evergreen assets but doesn't say what the renewal quote does to the line
  ([change-policy-mapping.md](change-policy-mapping.md)).
- **Changing a bundle root's sizing attribute on an amendment:** do the children's
  quantities re-derive through CML, and at what price?
- **An earlier-dated change against a future-dated one:** the amend and cancel articles
  say it's refused, while *Future-Dated Changes* and its examples allow it
  ([change-policy-mapping.md](change-policy-mapping.md) → Replay the source's changes in
  date order). The repo's group-ramp runs changed assets before a ramp segment's future
  state period, which comes from the ramp schedule rather than a future-dated transaction,
  so they don't settle it [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`].
