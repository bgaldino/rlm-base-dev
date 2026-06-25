# Sales Transaction (Order) — Contracts

> **Status:** stub. This document will be populated after Phase 0 live probes
> characterize the direct-order path — placing an Order via PST without a
> preceding Quote.
>
> The `sales_txn_order` kind is intentionally **not registered** until Phase 3.
> Its stage sequence (`STAGES_ORDER`) omits `quote_placed` and runs
> `opportunity_created` → `order_draft` → `order_activated` → `usage_upload` →
> `invoice_draft` → `invoice_posted`.

## Phase 0 probe checklist (against R262)

Before implementing `place_order_transaction()`, live-verify each item below
and record the findings here:

1. Exact Order + OrderItem fields required by PST `actions/place` for the
   Order-graph variant.
2. Response shape — key names, graph wrapping (parity with quote path?).
3. ShippingAddress — auto-set by PST or does the manual
   `set_shipping_address()` still gate activation?
4. Term derivation — is `EndDate` auto-derived from `SubscriptionTerm` on the
   Order line, or must it be sent explicitly?
5. Bundle expansion — does PST expand default-configured bundles into child
   `OrderItem`s the same way it does for `QuoteLineItem`s?
6. Discounts — is the `Discount` percent field present on `OrderItem`, or does
   the discount enter through a different mechanism?
7. Partial-commit / orphan behavior on failure (PST commits the Quote header
   even on `isSuccess:false`; does the same happen for an Order?).
8. Post-activation — are `BillingSchedule` and `Asset` generation identical to
   the quote-sourced path?
9. Invoice generation from a directly-placed Order — same `generate` endpoint
   and correlation strategy?
10. Cleanup — is a directly-placed Order deletable while in `Draft`?

See [`../FOLLOWUPS.md`](../FOLLOWUPS.md) for tracking and any partial findings
that surface before the full probe lands.
