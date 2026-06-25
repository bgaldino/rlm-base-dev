# Invoice Ingestion — Contracts

> ✅ VERIFIED LIVE Draft and Posted (2026-06-25, `rlm-base__jun17_1`).
> Posted requires an active non-taxable `TaxTreatment` seeded in the org
> (see *Posted Path Prerequisites* below). Tax-on Posted ingestion
> (`taxable: true` lines) still requires `InvoiceLineTax` graph records
> and is rejected at parse time — see `followups.md`.

The ingestion path bypasses the PST spine entirely. One POST to
`/services/data/v67.0/commerce/invoicing/invoices/collection/actions/ingest` produces
an `Invoice` with `CreationMode = External` plus its `InvoiceLine` rows in a single
Composite Graph call — no `Opportunity`/`Quote`/`Order`/`Activate`/`BillingSchedule`.
The wire format is the **typed graph record shape** described in the dev guide at
`docs/salesforce/262/dev-guide/articles/connect_requests_graph_record_input.htm.md`,
NOT the generic Composite Graph subrequest shape (`{url, method, body}`).

## Verified payload shape (Draft, against `rlm-base__jun17_1`, 2026-06-25)

```jsonc
POST /services/data/v67.0/commerce/invoicing/invoices/collection/actions/ingest
{
  "invoices": [{
    "shouldCalculateTax": false,      // Current invariant: no InvoiceLineTax
    "taxCalculationStatus": "Pending", // Draft. Posted requires "Posted"; see below.
    "correlationId": "<run_id>",
    "graph": {
      "graphId": "invoiceGraph",
      "records": [
        { "referenceId": "refInvoice", "record": {
          "attributes": { "type": "Invoice", "method": "POST" },
          "uniqueIdentifier": "<run_id>",        // idempotency key
          "billingAccountId": "<Account.Id>",    // FK target is Account, NOT BillingAccount
          "billToContactId": "<Contact.Id>",     // Required
          "status": "Draft",
          "invoiceDate": "2026-06-25"
        }},
        { "referenceId": "refBillingAddress", "record": {
          "attributes": { "type": "InvoiceAddressGroup", "method": "POST" },
          "invoiceId": "@{refInvoice.id}",
          "street": "...", "city": "...", "state": "...",
          "postalCode": "...", "country": "..."   // all five Required
        }},
        { "referenceId": "refShippingAddress", "record": {
          "attributes": { "type": "InvoiceAddressGroup", "method": "POST" },
          "invoiceId": "@{refInvoice.id}",
          "street": "...", "city": "...", "state": "...",
          "postalCode": "...", "country": "..."
        }},
        { "referenceId": "refInvoiceLine1", "record": {
          "attributes": { "type": "InvoiceLine", "method": "POST" },
          "invoiceId": "@{refInvoice.id}",
          "billingAddressId": "@{refBillingAddress.id}",   // Required
          "shippingAddressId": "@{refShippingAddress.id}", // Required
          "taxTreatmentId": "1tt...",  // Required on Posted; stamped on Draft too -- see Posted Path Prerequisites
          "name": "API Flex",
          "quantity": 10, "unitPrice": 25.0, "chargeAmount": 250.0,
          "invoiceLineStartDate": "2026-06-25",  // Required
          "invoiceLineEndDate":   "2026-06-25",  // Required
          "product2Id": "01t..."                 // Optional
        }}
      ]
    }
  }]
}
```

## Response shape (verified)

```jsonc
{
  "invoices": [{
    "invoiceId": "3ttWI00000084EXYAY",
    "requestIdentifier": "...",
    "statusURL": "/services/data/v67.0/sobjects/AsyncOperationTracker/<id>",
    "success": true,
    "errors": []
  }]
}
```

`statusURL` points at the same `AsyncOperationTracker` shape used by `actions/post`;
we reuse `_await_async_tracker` to gate completion. On failure `success:false` with
errors in the same envelope (Composite Graph rolls back atomically — partial line
errors abort the whole request).

## Required fields surfaced by live verification

These were each rejected with `INVALID_API_INPUT` on 2026-06-25 against
`rlm-base__jun17_1` until added. The dev guide tags them Required (or Optional in
one case), but the live ingest endpoint enforces the full set:

| Field | Marker source | Notes |
|---|---|---|
| `Invoice.billToContactId` | Dev guide Required | Resolved via `_resolve_default_contact_id` (most-recent `Contact` per `Account`). |
| `Invoice.currencyIsoCode` | Multi-currency only | Org probed via `Account.CurrencyIsoCode`; absent on single-currency orgs (SOQL returns `INVALID_FIELD`, cached by stable org identity, not raw alias). |
| `InvoiceLine.billingAddressId` | Dev guide Required | One `InvoiceAddressGroup` graph record per invoice; line references via `@{refBillingAddress.id}`. |
| `InvoiceLine.shippingAddressId` | Dev guide Required | Separate `InvoiceAddressGroup` record even when the addresses are identical. |
| `InvoiceLine.invoiceLineStartDate` / `invoiceLineEndDate` | Dev guide Required | Defaulted to the invoice's `invoiceDate` when the scenario omits per-line dates. |
| `InvoiceAddressGroup.{street,city,state,postalCode,country}` | Dev guide Required | All five must be non-null; the harness raises `LifecycleError` on an Account with a partial address rather than letting the API reject. |
| `Invoice.invoiceNumber` (Posted only) | **Dev guide says Optional, live API rejects without it** | Defaulted to `run_id` for Posted; surfaced as an under-documented contract violation in the dev guide. |

## Posted Path Prerequisites

Posted ingestion is live-verified against `rlm-base__jun17_1` (2026-06-25)
**when the org has an active non-taxable `TaxTreatment`**. The
default-seeded `Default Tax Policy` is `IsTaxable=true`; ingesting a
Posted invoice with no `taxTreatmentId` (or a taxable one) is rejected:

> `INVALID_API_INPUT: You can't specify a tax treatment with the isTaxable value as true
> when the invoice line doesn't have a related InvoiceLineTax record.`

The harness handles this in three places:

1. **Discovery** — `discovery.resolve_non_taxable_tax_treatment` runs at
   the same bootstrap as `discover_accounts` / `discover_products` and
   caches the result on `OrgContext.non_taxable_tax_treatment_id` (org-
   scoped module cache mirroring `_MULTI_CURRENCY_BY_ORG`).
   SOQL: `SELECT Id FROM TaxTreatment WHERE IsTaxable = false AND
   Status = 'Active' ORDER BY CreatedDate ASC LIMIT 1`. `TaxTreatment`
   has no `IsActive` field; the active set is `Status = 'Active'`
   (verified via describe).
2. **Stamping** — `lifecycle.ingest_invoice` stamps `taxTreatmentId` on
   every InvoiceLine graph record (Draft and Posted alike). Stamping
   on Draft matters for the resume path: live-verified that posting
   an unstamped Draft via `actions/post` silently resolves the
   default taxable policy and produces a taxable invoice (`$100`
   line → `TaxAmount=10`). Stamping at Draft ingest blocks that
   regression.
3. **Loud rejection** — Posted ingest without a discovered treatment
   raises `LifecycleError` with seed instructions
   (`Setup → Tax Treatments`, `IsTaxable=false`, `Status=Active`).
   `run_promote_to_posted` re-reads `InvoiceLine.TaxTreatmentId` and
   raises the same `LifecycleError` if any line is untagged --
   `InvoiceLine.TaxTreatmentId` is not updateable per describe, so a
   PATCH fixup is not available; the operator must delete the Draft
   manifest and re-ingest after seeding.

Tax-on Posted ingestion (lines with `taxable: true`) still requires
`InvoiceLineTax` graph records and is rejected at parse time -- see
`followups.md`.

## Verified Posted shapes (non-taxable)

The shapes below are live-verified against `rlm-base__jun17_1`
(2026-06-25). They confirm that the non-taxable Posted path is not just
the canonical 5×1 smoke -- the same composite-graph payload handles
multi-line invoices, line-level discounts, multi-currency overrides,
and explicit date pinning. Reference scenario:
`scenarios/invoice_ingestion/15-standalone-billing-expanded.yaml`.

| Shape | Invoice | Round-trip evidence |
| ----- | ------- | ------------------- |
| **Multi-line + per-line dates + per-line `description`** | `3ttWI00000085TxYAI` | 3 `InvoiceLine` rows with `Quantity=10/10/1`, `ChargeAmount=250/250/1200`, `InvoiceLineStartDate`/`InvoiceLineEndDate` matching Q1/Q2/annual ranges; `Invoice.TotalAmount=1700`. Every line stamped with the discovered `TaxTreatmentId`. |
| **`charge_amount` override** | `3ttWI00000085VZYAY` | Line 1: `Quantity=4 UnitPrice=25` (implies 100) → `ChargeAmount=75` (override held verbatim). Line 2: `Quantity=2 UnitPrice=25` → `ChargeAmount=50` (default `qty × unit_price`). `Invoice.TotalAmount=125`. |
| **Invoice-level `currency` override on a multi-currency org** | `3ttWI00000085XBYAY` | USD-base account (`Global Media`) issued an `Invoice.CurrencyIsoCode=EUR`, `TotalAmount=500`. Confirms the harness's `Invoice.currencyIsoCode` plumbing (`lifecycle.py:1154`) accepts an explicit override regardless of the account's base currency. |
| **Explicit `invoice_date` / `due_date` / `posted_date`** | `3ttWI00000085YnYAI` | Run executed 2026-06-25; `Invoice.InvoiceDate=2026-06-01`, `DueDate=2026-07-01`, `PostedDate=2026-06-01` (the YAML-pinned values, not the default-`today` payment-terms derivation). Confirms `InvoiceOverrides` date fields render into the payload and the server respects them on Posted ingestion. |

All four shapes settled `Invoice.Status='Posted'`, `CreationMode='External'`,
`TotalTaxAmount=0`. Every `InvoiceLine.TaxTreatmentId` resolved to the
oldest active non-taxable `TaxTreatment` (deterministic via
`ORDER BY CreatedDate ASC LIMIT 1`), even on the org that had two
qualifying rows -- confirms the discovery tiebreaker is stable across
seeding operations.

## Side-effects (verified absent)

A successful ingest creates only `Invoice` + `InvoiceLine` + `InvoiceAddressGroup` rows.
Verified via SOQL on `rlm-base__jun17_1` after 5 Draft invoices (Infinitech +
Global Media):
- `BillingSchedule` count for the account window: unchanged.
- `Order` / `Quote` / `Opportunity` count: unchanged.
- `Invoice.ReferenceEntityId`: `null` (the ingestion path does not point at an Order).
- `Invoice.CreationMode`: `External` (PST-emitted invoices are `Salesforce`).

## Pipeline accounts (signature win)

`Account.Id` is the FK target for `Invoice.billingAccountId`, not `BillingAccount.Id`.
The Global Media account has no `BillingAccount` row and the ingestion path succeeds
natively against it — verified live: 2 invoices on `001WI00001GPloTYAT` with
`BillingAccountId = 001WI00001GPloTYAT`.

## Harness retry rule (Draft only)

Draft ingestion uses `Invoice.uniqueIdentifier = <run_id>` as the replay key, but
the harness retries narrowly: only transient failures before any `invoiceId` is
observed are retried. If the action or tracker failure includes an `invoiceId`,
the manifest records it and stops for operator inspection rather than replaying
a partially materialized graph. Posted ingestion uses the same single-attempt
policy (no retry once an `invoiceId` is observed), since duplicate Posted
inserts cannot be reconciled.

## Idempotency

`Invoice.uniqueIdentifier = run_id` is enforced server-side (verified: a repeat call
with the same identifier returns a Composite Graph rollback error rather than
duplicating). The harness sets it on every call so retries from the runner's
backoff path are safe.
