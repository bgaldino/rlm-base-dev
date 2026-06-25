# Invoice Ingestion — Contracts

> ✅ VERIFIED LIVE Draft; ⚠ Posted ingestion is not operator-supported today

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

## Posted Path Dependency

Posted ingestion is wired in the code (`status: "Posted"`, `taxCalculationStatus: "Posted"`,
`invoiceNumber: <run_id>`, `postedDate: today`) but **not live-verified** because it
requires either an `InvoiceLineTax` graph record or a non-taxable `TaxTreatment` in the
org. The default-seeded `Default Tax Policy` is `IsTaxable=true`, so the ingest API rejects:

> `INVALID_API_INPUT: You can't specify a tax treatment with the isTaxable value as true
> when the invoice line doesn't have a related InvoiceLineTax record.`

The same precondition gates the `actions/post` endpoint, so Draft→Posted resume hits the
identical wall. See `followups.md` for the tax graph design.

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
    a partially materialized graph. Posted ingestion remains unsupported until
the `InvoiceLineTax` prerequisite is implemented and live-verified.

## Idempotency

`Invoice.uniqueIdentifier = run_id` is enforced server-side (verified: a repeat call
with the same identifier returns a Composite Graph rollback error rather than
duplicating). The harness sets it on every call so retries from the runner's
backoff path are safe.
