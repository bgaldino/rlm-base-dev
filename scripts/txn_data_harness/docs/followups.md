# Transaction Data Harness — Follow-ups & Open Questions

Companion to `../CONTRACTS.md`. **The contract docs are the source of
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
  the answer in the contract docs. Include: what's open, why it matters,
  what would prove it, and a back-link to whichever contract / README /
  scenarios section the question relates to.
- **Resolving an item.** When a probe lands a definitive answer:
  1. Write the finding into the relevant contract doc (with the live-verify
     date + org alias).
  2. Move this entry to the [Resolved](#resolved) section below
     with a one-line summary and the contract anchor.
  3. Update any user-facing doc (`../scenarios/README.md`,
     `../AI_TOOLS.md`) that pointed at the now-resolved gap.
- **Status legend.** Use these prefixes so the open list scans
  quickly:
  - `[gap]` — behavior is unspecified / untested; the harness
    currently sidesteps it.
  - `[anomaly]` — a readback surprised us; need to characterize
    before generalizing.
  - `[probe]` — a specific experiment that would resolve a gap
    or anomaly. Usually one PST call + one SOQL.
  - `[verify]` — something the contract docs *assert* but that hasn't
    been re-verified after a relevant change (release upgrade,
    schema change, etc).

---

## Open

### Standalone-billing Posted ingestion

Posted ingestion is live-verified end-to-end against a non-taxable
`TaxTreatment` (2026-06-25, `rlm-base__jun17_1`). Tax-on Posted
ingestion -- lines that should carry their own `InvoiceLineTax` --
still needs the tax graph record implemented. Remaining gaps below.

- `[probe]` **Tax-on Posted ingestion via `InvoiceLineTax` graph records.**
  The dev guide
  (`../../../docs/salesforce/262/dev-guide/articles/connect_requests_graph_record_input.htm.md`,
  Table 3) defines a tax graph record with seven Required fields
  (`taxTransactionNumber`, `taxAmount`, `taxRate`, `taxName`, `taxCode`,
  `taxEffectiveDate`, `invoiceLine`, `taxDocumentNumber`). The current
  harness rejects `taxable: true` lines at parse time on Posted target;
  lifting that gate is the canonical follow-on. Open design questions:
  - Where do `taxAmount` / `taxRate` come from in a generated-data context? Pinned
    via a scenario override (`tax_rate: 0.08`) and the harness computes
    `taxAmount`, or fully scripted (line-level `tax: {amount, rate, name, code}`)?
  - Should the scenario stamp `InvoiceLine.taxTreatmentId` with a taxable
    treatment (e.g. the default `Default Tax Policy`) instead of the
    non-taxable one the standard path uses?
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
  Two `BillingSchedule` rows from `scenarios/sales_txn_quote/14-end-date-overrides.yaml`
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
  - Ref: `contracts-sales-txn-quote.md` → *BillingSchedule fan-out across
    `end_date` scenarios*, observation 4.

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
  - Ref: `contracts-sales-txn-quote.md` → *BillingSchedule fan-out*,
    observation 1.

- `[gap]` **Quarterly / Semi-Annual activation-time fan-out.** All 9
  scenarios we verified were Annual or Monthly SOMs. We assert in
  the contract docs that "one BillingSchedule per OrderItem at activation"
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
  - Ref: `contracts-sales-txn-quote.md` → *BillingSchedule fan-out*,
    scenario #9 note.

### Subscription terms

- `[gap]` **"EndDate wins" generalization beyond Annual.** Both
  `EndDate`-disagreement probes (`contracts-sales-txn-quote.md` →
  *Probed edge cases*, table 2) used `QB-API-FLEX` (Term Annual SOM).
  We haven't confirmed the same `(EndDate − StartDate) / 365` rule on
  Monthly, Quarterly, or Semi-Annual SOMs — the denominator could shift
  on non-Annual cadences.
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

### Quote / order placement

- `[verify]` **`QuoteLineItem.Discount` reads as `0` post-place.**
  `contracts-sales-txn-quote.md` records this on the original probe;
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

- `[gap]` **Bundles with mandatory user-input slots.** The contracts
  confirm `QB-COMPLETE` (default-configured bundle) places end to
  end. We assume bundles with mandatory attributes or required
  slots without defaults fail to place but haven't enumerated the
  failure mode — error code, error message, partial state — so
  consumers can't catch and explain it.
  - `[probe]` Identify a bundle in the QB catalog with at least
    one mandatory-no-default slot, attempt to place via PST, and
    record the exact error response shape.

### Lifecycle async behavior

- `[gap]` **`AsyncOperationTracker` failure-path coverage.**
  The contracts note the tracker is real and surfaces failures;
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

- `[verify]` **`EndDate` override anchors on `date.today()` when
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
  - **Implemented guard:** `LineItem.resolved_end_date` is now stamped
    during place and persisted on the manifest, so retries/resumes reuse
    the resolved ISO date instead of re-resolving the offset.
  - Remaining live check: run the cross-midnight resume probe once a
    convenient long-running test window exists, then move this to Resolved.
  - Ref: `lifecycle.py:154,192-194`; `models.py:115-205`
    (`LineItem` serialization).

- `[gap]` **Shipping-address copy is still the five standard address
  fields.** `discovery.PostalAddress` carries
  `Street/City/State/PostalCode/Country` and `set_shipping_address`
  copies those values to the Order. Non-US address layouts or custom
  address fields are not modeled by the harness; if a future org makes
  activation depend on additional fields, the current diagnostic will
  still point at a missing standard shipping address.
  - **Possible fix:** make `PostalAddress` / `discovery.OrgContext`
    configurable (e.g. include any custom shipping field discovered on
    Account's schema), or derive the copied field set from describe.

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

> Move entries here when the contract docs get the live-verified answer.
> Keep the one-line summary + contract anchor so future readers
> can trace the lineage.

- **Order activation does not require `BillToContactId` / `Billing*`
  address fields on the current R262 org.** Live re-probe on
  `rlm-base__jun17_1` (2026-06-25, run `DEMO-20260625T205734Z`,
  order `00000246`, invoice `INV-US-06-2026-000096`) reached Posted
  with `Order.BillToContactId` and every `Order.Billing*` address field
  still null. Contract anchor:
  `contracts-sales-txn-quote.md` → *Activate Order* and
  `contracts-shared.md` → *Mandatory pre-activation ordering*.

- **`poll_assets` stable-count convergence was hardened and bundle
  re-probed.** The default now requires two stable comparisons (three
  identical observations total). Live bundle re-probe on `rlm-base__jun17_1`
  (2026-06-25, run `DEMO-20260625T205948Z`, order `00000247`) returned all
  five `QB-COMPLETE` component assets; all five `AssetActionSource` rows had
  the same `CreatedDate` second. Contract anchor:
  `contracts-sales-txn-quote.md` → *Asset attribution*.

- **Asset-poll timeout visibility is implemented.** `manifest.asset_poll_status`
  records `converged`, `timeout_empty`, or `timeout_partial`, and batch reports
  surface non-converged statuses under poll warnings. Contract anchor:
  `contracts-sales-txn-quote.md` → *Harness checkpoint rule*.

- **`set_shipping_address` no longer re-queries Account shipping fields per
  order.** Discovery populates `Account.shipping_address`, and activation copies
  that cached value. Contract anchor:
  `contracts-shared.md` → *Mandatory pre-activation ordering*.

- **`poll_assets` is parameterized by asset action category.** The activation
  path still defaults to `AssetAction.CategoryEnum = 'Initial Sale'`, but the
  helper accepts a `category_enum` argument for future amendment / renewal
  callers. Contract anchor:
  `contracts-sales-txn-quote.md` → *Asset attribution*.

---

## See also

- `../CONTRACTS.md` — contract index.
- `contracts-sales-txn-quote.md`, `contracts-sales-txn-order.md`, and
  `contracts-invoice-ingestion.md` — live-verified lifecycle contracts.
- `../README.md` → *Known limitations* — productized gaps that are
  scoped out rather than open questions (concurrency, JWT,
  composite batching, etc).
- `../scenarios/README.md` — user-facing rules; any open anomaly mentioned there
  should point back to this file.
