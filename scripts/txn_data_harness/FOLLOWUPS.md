# Transaction Data Harness — Follow-ups & Open Questions

Companion to `CONTRACTS.md`. **CONTRACTS.md is the source of
live-verified truth** — only behaviors that have been probed against
a live org belong there. This file is the inverse: known gaps, things
that *look* like they work but haven't been live-verified, anomalies
spotted in passing, and probes that would generalize a finding.

This is an evidence notebook, not an operator guide. It may include observed org
aliases, run ids, dates, order numbers, and invoice numbers so a future probe can
be retraced. Treat those values as evidence only; user-facing docs should use
placeholders or explicitly labeled QB example data.

## How to use this file

- **Adding an item.** When you spot a gap or anomaly while working on
  the harness — anywhere — add an entry here rather than asserting
  the answer in CONTRACTS.md. Include: what's open, why it matters,
  what would prove it, and a back-link to whichever CONTRACTS.md /
  README / scenarios section the question relates to.
- **Resolving an item.** When a probe lands a definitive answer:
  1. Write the finding into `CONTRACTS.md` (with the live-verify
     date + org alias).
  2. Move this entry to the [Resolved](#resolved) section below
     with a one-line summary and the CONTRACTS.md anchor.
  3. Update any user-facing doc (`scenarios/README.md`,
     `AI_TOOLS.md`) that asserted "TBD" or "treat as a known gap".
- **Status legend.** Use these prefixes so the open list scans
  quickly:
  - `[gap]` — behavior is unspecified / untested; the harness
    currently sidesteps it.
  - `[anomaly]` — a readback surprised us; need to characterize
    before generalizing.
  - `[probe]` — a specific experiment that would resolve a gap
    or anomaly. Usually one PST call + one SOQL.
  - `[verify]` — something CONTRACTS.md *asserts* but that hasn't
    been re-verified after a relevant change (release upgrade,
    schema change, etc).

---

## Open

### Standalone-billing ingestion (Phase 2)

PR 6 landed the Phase 1 Draft path live-verified (see CONTRACTS.md §7). Phase 2
extends ingestion to the Posted path, taxed lines, and bulk-ingest concurrency.

- `[gap]` **Posted ingestion requires a non-taxable `TaxTreatment` OR an `InvoiceLineTax`
  graph record.** Live-verified blocker on `rlm-base__jun17_1` (2026-06-25): the
  default org seed has one Active `TaxTreatment` (`Default Tax Policy`,
  `IsTaxable=true`), and the ingest API rejects Posted lines without a related
  `InvoiceLineTax` record:
  > `INVALID_API_INPUT: You can't specify a tax treatment with the isTaxable value as
  > true when the invoice line doesn't have a related InvoiceLineTax record.`
  Same precondition gates `commerce/invoicing/.../actions/post`, so Draft→Posted
  resume hits the identical wall. The Phase 1 lifecycle already wires the Posted
  payload correctly (status, `taxCalculationStatus: Posted`, `invoiceNumber:
  <run_id>`, `postedDate: today`) — only the tax dependency is missing.
  - `[probe]` Discover an active `TaxTreatment WHERE IsTaxable = false`. If one
    exists, stamp `InvoiceLine.taxTreatmentId` on every Posted line and re-run
    `15-standalone-billing.yaml`. If none exists, decide whether the harness should
    create one on first run (single setup write, like the PRM Network placeholder)
    or surface a clear LifecycleError directing the user to seed one.
  - `[probe]` Once Posted ingestion lands, re-run the Draft→Posted resume flow
    (`cli step --to-stage post`) end-to-end on an existing Draft ingestion
    manifest; confirm the resume reuses the Draft invoice id rather than creating
    a second Invoice row.
  - Ref: `CONTRACTS.md` → §7, *Posted path — Phase 2 dependency*.

- `[probe]` **`InvoiceLineTax` graph record design.** The dev guide
  (`docs/salesforce/262/dev-guide/articles/connect_requests_graph_record_input.htm.md`,
  Table 3) defines a tax graph record with seven Required fields
  (`taxTransactionNumber`, `taxAmount`, `taxRate`, `taxName`, `taxCode`,
  `taxEffectiveDate`, `invoiceLine`, `taxDocumentNumber`). Open design questions:
  - Where do `taxAmount` / `taxRate` come from in a generated-data context? Pinned
    via a scenario override (`tax_rate: 0.08`) and the harness computes
    `taxAmount`, or fully scripted (line-level `tax: {amount, rate, name, code}`)?
  - Should the Phase 1 `taxable: true` parse-time rejection lift naturally once
    `InvoiceLineTax` exists, or remain explicit so tax-on scenarios must add the
    new tax block?
  - Per the dev guide, the `invoiceLineTax` graph record **must not** include
    `taxCalculationStatus = Pending` — confirm whether the harness needs to flip
    the invoice's `taxCalculationStatus` to `Posted` automatically when any line
    carries an InvoiceLineTax, or whether the scenario must do so.
  - Ref: dev guide Table 3, *Tax Record*.

- `[probe]` **Composite Batch / multi-invoice per request.** The ingest action
  accepts an `invoices[]` array (`"invoices": [...]`); today the harness ships
  one invoice per POST and parallelises scenarios in the thread pool. Open:
  - What's the per-request invoice cap (the dev guide notes a Graph record count
    of 500 across the whole `invoices[]` payload — so the cap is per-graph, not
    per-invoice)?
  - Are Composite Graph errors per-invoice (one bad payload doesn't abort the
    batch) or whole-batch (one bad payload rejects all)? Live verify with a 2-
    invoice payload where one references a bogus account.
  - If per-invoice rollback is real, batching N small invoices into one POST is
    the throughput win for high-volume demos (cuts N-1 round-trips and N-1
    AsyncOperationTracker polls).
  - Ref: dev guide → "Invoice ingestion supports a Graph record count of 500."

- `[probe]` **Account.bill_to_contact_id pinning.** The current `_resolve_default_contact_id`
  picks the most-recently-created Contact per account. A scenario may want to
  pin a specific Contact (e.g. the "AP" contact for finance demos). Design knob
  on `InvoiceIngestionScenarioSpec.invoice.bill_to_contact_name` (resolved at
  the same discovery phase as the account).

- `[probe]` **InvoiceAddressGroup address overrides.** Both addresses derive from
  the Account's Billing/Shipping fields today. Open: should the scenario allow
  per-invoice address overrides (different ship-to per line for the same
  invoice)? The dev guide allows distinct `InvoiceAddressGroup` records per
  line, so the API supports it.

### Billing & invoicing

- `[anomaly]` **Monthly-Advance short-span proration denominator.**
  Two `BillingSchedule` rows from `scenarios/14-end-date-overrides.yaml`
  scenarios #3 (Aug 31 → Sep 30, 30 days) and #4 (Jan 31 → Feb 28,
  28 days) both produced `TotalAmount = 1548.39` against
  `BillingPeriodAmount = 1500` — the engine prorated **up** on both,
  using a fixed internal day denominator (~30.97) rather than
  calendar-month days. We do not yet know:
  - Whether the denominator is exactly 30.97 or some other
    constant (`365/12 = 30.4166…`; `1500 × 31/30 = 1550`; neither
    matches 1548.39 cleanly).
  - Whether the over-bill caps at one period or continues linearly
    past `BillingPeriodAmount` as the span grows.
  - Whether the same math applies to Quarterly / Semi-Annual SOMs
    with short spans.
  - `[probe]` Place three Monthly-SOM lines: one at exactly 31 days
    (e.g. 2026-07-01 → 2026-07-31), one at 60 days, one at 365
    days; read back `TotalAmount` and back-solve the denominator.
  - Ref: `CONTRACTS.md` → *BillingSchedule fan-out across `end_date`
    scenarios*, observation 4.

- `[gap]` **Per-period BillingSchedule fan-out timing.** At
  activation, every scenario emits exactly **one** `BillingSchedule`
  row spanning the full deal. We assume periodic rows are an
  invoicing-time artifact (driven by `NextBillingDate` advancing),
  but haven't observed the fan-out actually happening — every harness
  flow stops at `post`, which creates one Posted invoice per
  activation. Open:
  - Do periodic rows ever materialize as separate `BillingSchedule`
    records, or is the single activation-time row the only
    schedule object that ever exists for the deal?
  - If periodic rows do appear, when (next billing cycle?
    explicit re-billing?), and what triggers them?
  - `[probe]` Activate a 3-year Annual deal, post the first invoice,
    advance `NextBillingDate` (or wait/mock), and re-query
    `BillingSchedule` to see if a second row appeared.
  - Ref: `CONTRACTS.md` → *BillingSchedule fan-out*, observation 1.

- `[gap]` **Quarterly / Semi-Annual activation-time fan-out.** All 9
  scenarios we verified were Annual or Monthly SOMs. We assert in
  CONTRACTS.md that "one BillingSchedule per OrderItem at activation"
  generalizes, but Quarterly / Semi-Annual were not exercised.
  - `[probe]` Place a 4-Quarterly and a 2-Semi-Annual line, activate,
    confirm one schedule row each.

- `[gap]` **Per-line `end_date:` override coverage.** Scenario #9 in
  `14-end-date-overrides.yaml` puts two SKUs in a `products:` pool —
  one pins `end_date: "6mo"`, the other inherits the scenario
  default. The pool randomizes per transaction, so a `count: 1`
  scenario sometimes draws only one of the two. We have not yet
  observed both lines landing on the same quote with their
  divergent `EndDate`s.
  - `[probe]` Re-run scenario #9 with `count: 5` (or pin the pool
    to always emit both) and read back both `OrderItem.EndDate`
    rows on a single order.
  - Ref: `CONTRACTS.md` → *BillingSchedule fan-out*, scenario #9
    note.

### Subscription terms

- `[gap]` **"EndDate wins" generalization beyond Annual.** Both
  `EndDate`-disagreement probes (`CONTRACTS.md` → *Probed edge cases*,
  table 2) used `QB-API-FLEX` (Term Annual SOM). We haven't
  confirmed the same `(EndDate − StartDate) / 365` rule on Monthly,
  Quarterly, or Semi-Annual SOMs — the denominator could shift on
  non-Annual cadences.
  - `[probe]` Repeat the disagreement matrix on a Monthly SOM
    (e.g. `QB-API` with `selling_model: "Term Monthly"`) and a
    Quarterly SOM; check whether `PricingTermCount` is still
    days/365 or switches to days/30 (Months) / days/91.25
    (Quarterly).

- `[gap]` **`SubscriptionTermUnit` silent coercion.** Probe row 3 of
  the disagreement matrix sent `Term=6 Months` with an
  `EndDate` 3 months out against an Annual PSM — the platform
  stored `SubscriptionTermUnit = Annual` (coerced from `Months`).
  The harness's `runner._resolve_term` consistency guard prevents
  this through the normal config path, but we don't know:
  - Is coercion always to the PBE's PSM unit, or could it pick
    something else?
  - Does coercion happen if `SubscriptionTermUnit` matches the
    PSM and `SubscriptionTerm` disagrees with `EndDate`? (Probe
    row 3 conflated both.)
  - `[probe]` Send `Term=6 Annual` with a 3-month `EndDate`
    against an Annual PSM (matching unit, mismatched count) and
    see whether `SubscriptionTerm` reads back as `6` or gets
    coerced.

### Order activation prerequisites

- `[verify]` **Bill to Contact + Billing Address requirement.** A
  Salesforce billing doc states: *"After turning on Billing, order
  activation succeeds only if the Order records have values for the
  Bill to Contact, Billing Address, and Shipping Address fields.
  Order activation fails if any of these values are missing."*
  The harness only sets shipping (`lifecycle.set_shipping_address`,
  `_SHIPPING_FIELDS` at `lifecycle.py:36-39`); it does **not** set
  `BillToContactId` or `BillingStreet/City/State/PostalCode/Country`.
  Live readback on `rlm-base__jun17_1` (2026-06-23) shows our
  activated orders (`00000156`, `00000164`, and the full 9-scenario
  set) have empty `BillToContactId` and empty billing address yet
  activated cleanly **and** generated `BillingSchedule`s — and prior
  smoke runs have reached `post`. So one of these is true:
  1. The doc requirement is gated on a Billing setup toggle this
     org doesn't have on.
  2. The requirement applies at a later step (invoice generate /
     post) and our prior `post` runs got lucky on data (e.g. the
     account's primary contact resolved implicitly, or this version
     of R262 dropped the requirement).
  3. The doc is stale / pre-R262 wording.
  - `[probe]` On a clean order, attempt activation deliberately
    without setting `BillToContactId` / `BillingStreet…` and observe
    whether it fails on a setup toggle this org doesn't have set
    (look in **Setup → Billing** / Revenue Cloud Billing config),
    OR succeeds.
  - `[probe]` If the requirement is real but lazy, probe what
    breaks downstream: drive a `post` against an order with no
    `BillingAddress` and see whether `Invoice.generate` /
    `Invoice.post` fail (`MISSING_BILLING_ADDRESS` or similar).
  - **Action if confirmed:** mirror the existing
    `set_shipping_address` helper as `set_billing_address` (copy
    `Account.Billing{Street,City,State,PostalCode,Country}` →
    `Order.Billing*`), add a `set_bill_to_contact` (resolve
    `Account.PersonContactId` or the primary contact from
    `AccountContactRelation` and write `Order.BillToContactId`),
    and wire both into `steps.py` between `create_order` and
    `activate_order`. Capture in CONTRACTS.md → *Mandatory
    pre-activation ordering* alongside the existing shipping
    rule.
  - Ref: Salesforce billing docs (cite user-provided wording);
    `lifecycle.py:256-277` (existing shipping helper);
    `CONTRACTS.md:730-733` (current pre-activation ordering note).

### Quote / order placement

- `[verify]` **`QuoteLineItem.Discount` reads as `0` post-place.**
  `CONTRACTS.md:112-131` records this on the original probe;
  Workstream 2 of the polished-babbage plan flagged that the UI
  may persist the discount % via a different call. The harness
  exposes `discount:` and we've live-verified it flows through to
  net price + posted invoice — but the `Discount` field readback
  has **not** been re-probed since the original entry. Worth
  re-confirming on R262 / `rlm-base__jun17_1`.
  - `[probe]` Place a single-line QB-API-FLEX with 25% discount
    via the harness, then via the UI on the same org, and diff
    the `QuoteLineItem` rows + captured UI network call. (This is
    the W2 probe from the polished-babbage plan, which was not
    executed in the end-date workstream.)

- `[gap]` **Bundles with mandatory user-input slots.** CONTRACTS.md
  confirms `QB-COMPLETE` (default-configured bundle) places end to
  end. We assume bundles with mandatory attributes or required
  slots without defaults fail to place but haven't enumerated the
  failure mode — error code, error message, partial state — so
  consumers can't catch and explain it.
  - `[probe]` Identify a bundle in the QB catalog with at least
    one mandatory-no-default slot, attempt to place via PST, and
    record the exact error response shape.

### Lifecycle async behavior

- `[gap]` **`AsyncOperationTracker` failure-path coverage.**
  CONTRACTS.md notes the tracker is real and surfaces failures;
  the harness retries on transient classifications. We have not
  systematically exercised:
  - Terminal `BillingSchedule.Status = Failed` and what
    `AsyncOperationTracker` carries in that case.
  - Whether `Status = Canceled` ever appears for a schedule we
    created (vs. only the row-locking transient path).

### Deferred from /code-review (2026-06-23)

A high-effort review surfaced these on the `feat/txn-data-harness`
branch. Three findings (silent `Months` fallback in
`runner._resolve_term`, `parse_retention` duplication, and the
`_coerce_*` range duplication) were fixed in the same pass; the rest
land here because each needs either live verification or a wider
design decision.

- `[gap]` **`poll_assets` stable-count convergence is too aggressive
  under staggered AAS writes.** `lifecycle.py:404-418` exits as soon
  as the AAS-derived asset id count is non-empty AND stable across
  two consecutive `_POLL_INTERVAL` (5s) ticks. If `OrderItem`
  expansion finishes asynchronously and AAS rows land in waves
  (e.g. 3 of 5 on tick 2, the other 2 on tick 4), the predicate
  fires on the partial set and the poll returns an incomplete list.
  `run_usage` (`steps.py:147`) hard-fails with `"no asset found"`
  on the orphan SKUs; same-SKU bundles could pair the wrong asset
  positionally. The CONTRACTS.md timing note ("Asset created
  01:28:44, AAS created 01:28:45") covers the well-behaved case
  only.
  - `[probe]` Activate a bundle that expands to >5 OrderItems and
    record AAS write timestamps for each row. If max spread > 5s,
    the current 2-tick window is unsafe.
  - **Possible fixes:** require N≥3 stable ticks, OR derive an
    expected lower bound from `count_order_items` and require the
    last poll to match it, OR add a minimum-stability-duration tied
    to OrderItem count.
  - Ref: `lifecycle.py:340-431` (`poll_assets`); `steps.py:113-117`
    (call site); CONTRACTS.md → *Asset attribution*.

- `[gap]` **`EndDate` override anchors on `date.today()` when
  `start_date` is None.** `lifecycle.py:192-194` resolves
  `line.end_date` against `start_date or date.today()`. The
  `StartDate` written to the QuoteLineItem (`line 154`) defaults the
  same way, so a single call lands consistently — but on a resumed
  scenario where `start_date` was None at original-place time and
  the resume happens across a date boundary (or the manifest
  carries a serialized override with no anchor recorded), the
  override and StartDate could disagree by a day. The class of bug
  is subtle and easy to miss in CI.
  - `[probe]` Resume an `end_date=mo:12` scenario across midnight
    UTC and confirm the EndDate readback matches StartDate + 12mo
    from the original-place day, not the resume day.
  - **Possible fix:** persist the resolved EndDate (not the
    unresolved override) on the manifest once the line places, so
    resume never re-resolves.
  - Ref: `lifecycle.py:154,192-194`; `models.py:115-205`
    (`LineItem` serialization).

- `[gap]` **`poll_assets` soft-fails empty on timeout, making
  zero-asset activations invisible.** `lifecycle.py:419-431` logs a
  warning and returns `[]` when the poll never converges. A
  scenario with no usage lines never trips `run_usage`'s
  empty-pool check, so the manifest records
  `reached_stage="activate"` and the batch report shows SUCCESS
  even though the activation produced no attributable assets. This
  is intentional per the docstring (assets are best-effort relative
  to the billing gate), but the silence makes it impossible to
  detect activation-asset gaps after the run.
  - **Possible fixes:** record `manifest.asset_poll_status`
    (`"converged"` / `"timeout_empty"` / `"timeout_partial"`) so
    the batch report can surface it, OR add a CLI flag that
    promotes `timeout_empty` to a failure when `usage_lines` is
    empty.
  - Ref: `lifecycle.py:340-431`; `report.py:build_batch_report`.

- `[gap]` **`_SHIPPING_FIELDS` hardcoded to 5 US-style fields.**
  `lifecycle.py:36-39` queries
  `Shipping{Street,City,State,PostalCode,Country}` and copies them
  to the order. Non-US address layouts (`ShippingAddress__c`
  compounds, JP-style Prefecture/Postal) won't surface and
  activation hard-fails `FAILED_ACTIVATION` with no harness-side
  diagnostic. Adjacent to the open `[verify] Bill to Contact +
  Billing Address requirement` item above.
  - **Possible fix:** make `_SHIPPING_FIELDS` configurable via
    `discovery.OrgContext` (e.g. include any custom shipping field
    discovered on Account's schema), or derive from describe.

- `[anomaly]` **`set_shipping_address` re-queries Account.Shipping
  fields once per order.** `lifecycle.py:258-277` issues a SOQL for
  the 5 shipping fields on every activation, even when many orders
  share the same account. A 50-scenario batch against one account
  spends 50 round-trips on identical reads. The discovery `Account`
  dataclass already exists; carrying the shipping payload at
  discovery time eliminates the per-order query. Pure efficiency;
  no correctness impact.
  - Ref: `lifecycle.py:258-277`; `discovery.py:179` (`resolve_account`).

- `[gap]` **`poll_assets` hardcodes `CategoryEnum='Initial Sale'`.**
  Correct for the activation path under test; not parameterized.
  An amendment/renewal scenario reusing `poll_assets` would
  silently return `[]` or just the initial-sale rows. Pre-emptive
  altitude fix: thread a `category_enum` kwarg through now to
  avoid the inevitable `poll_assets_for_amendment` copy.
  - Ref: `lifecycle.py:399`; CONTRACTS.md → *Asset attribution*.

- `[gap]` **`_BILLING_SCHEDULE_SUCCESS` enum set hardcoded.**
  `lifecycle.py:44` pins
  `{"ReadyForInvoicing", "CompletelyBilled"}`. A schema rename or
  new picklist value (e.g. `"PartiallyBilled"` becoming terminal)
  would make every activation poll time out after 180s with a
  generic `"fewer than N ready BillingSchedule(s)"` error pointing
  at activation rather than at the harness's stale enum list.
  - **Possible fix:** derive from `BillingSchedule.Status` picklist
    describe (cache per-run), or expose as config.
  - Ref: `lifecycle.py:44,323`.

### Cleanup

- `[gap]` **Activated → Draft revert side effects on
  BillingSchedule.** Reverting an activated Order to `Status=Draft`
  is documented as the precondition for deletion, but we haven't
  characterized what happens to the auto-generated
  `BillingSchedule` rows. Do they stay (orphaned)? Get marked
  Canceled? Become deletable?
  - `[probe]` Activate one scenario, revert to Draft, query
    `BillingSchedule WHERE ReferenceEntityId = <orderId>`, observe
    `Status` and whether a delete succeeds.

---

## Resolved

> Move entries here when CONTRACTS.md gets the live-verified answer.
> Keep the one-line summary + CONTRACTS.md anchor so future readers
> can trace the lineage.

*(none yet — this file is new as of 2026-06-23.)*

---

## See also

- `CONTRACTS.md` — the live-verified contract this file shadows.
- `README.md` → *Known limitations* — productized gaps that are
  scoped out rather than open questions (concurrency, JWT,
  composite batching, etc).
- `scenarios/README.md` — user-facing rules; treat any anomaly
  noted there with a "TBD" or "treat as a known gap" wording as a
  pointer back to this file.
