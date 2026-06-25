# Sales Transaction (Order) — Contracts

> ✅ VERIFIED LIVE end-to-end against `rlm-base__jun17_1` (R262, API v67.0)
> on `2026-06-25`. The direct-Order kind (`sales_txn_order`) reaches a
> **Posted invoice** (`INV-US-06-2026-000090`, $450) via PST place → activate
> → BillingSchedule + Asset → generate → post, **provided** the harness
> creates the `AppUsageAssignment` "RevenueLifecycleManagement" row before
> activating. Without that row, activation no-ops silently and produces no
> downstream artifacts. With it, the activation path is identical to the
> quote kind.
>
> The order-path lifecycle drives `opportunity_created → order_draft →
> order_activated → usage_upload → invoice_draft → invoice_posted`. Shared
> foundations (environment, object describes, terminal-state detection,
> timing / sequencing rules, permissions) live in
> [`contracts-shared.md`](contracts-shared.md); the activation, BillingSchedule
> polling, generate, post, and AssetActionSource queries are unchanged from
> the quote path documented in [`contracts-sales-txn-quote.md`](contracts-sales-txn-quote.md).
> This file captures what's **different** about the place step and the
> activation-gating record.

## Lifecycle steps — endpoints, bodies, responses

### 1. Opportunity (NOT SUPPORTED on this kind)

The direct-Order PST chain has no Opportunity step. **The R262 `Order` sobject
has no `OpportunityId` field** — verified via describe on `2026-06-25` against
`rlm-base__jun17_1`:

```
$ sf sobject describe --sobject Order --target-org rlm-base__jun17_1 \
    | jq '[.fields[] | select(.name | test("[Oo]pportunity"))]'
[]
```

Sending `OpportunityId` on the PST Order graph returns
`INVALID_FIELD` ("No such column 'OpportunityId' on sobject of type Order")
and rejects the entire place call. The harness pins this at the config layer:
`with_opportunity: true`, `opportunity_stage: <…>`, and
`target_stage: opportunity_created` are all rejected at parse time when
`kind: sales_txn_order`. To link a transaction to an Opportunity, use
`kind: sales_txn_quote` instead — `Quote.OpportunityId` IS writable on R262.

### 2. Order — Place Sales Transaction (PST) — ✅ VERIFIED LIVE

- **Endpoint:** `POST /services/data/v67.0/connect/rev/sales-transaction/actions/place`
  (same endpoint as the quote graph; the discriminator is the graph shape).
- **Body:** Order header + `OrderAction(Type=Add)` + N OrderItem children,
  with each child's `OrderActionId` pointing at the action.
  Minimum working payload, live-verified:
  ```json
  {
    "pricingPref": "System",
    "taxPref": "Skip",
    "graph": {
      "graphId": "createOrderDirect",
      "records": [
        { "referenceId": "refOrder",
          "record": { "attributes": {"method":"POST","type":"Order"},
                      "Name": "<name>",
                      "AccountId": "<accountId>",
                      "Pricebook2Id": "<standardPbId>",
                      "EffectiveDate": "<ISO>",
                      "Status": "Draft",
                      "Description": "<runTag>" } },
        { "referenceId": "refOrderAction",
          "record": { "attributes": {"method":"POST","type":"OrderAction"},
                      "OrderId": "@{refOrder.id}",
                      "Type": "Add" } },
        { "referenceId": "refOrderLine0",
          "record": { "attributes": {"method":"POST","type":"OrderItem"},
                      "OrderId": "@{refOrder.id}",
                      "OrderActionId": "@{refOrderAction.id}",
                      "Product2Id": "<prodId>",
                      "PricebookEntryId": "<pbeId>",
                      "Quantity": "1",
                      "ServiceDate": "<ISO>",
                      "SubscriptionTerm": 1 } }
      ]
    }
  }
  ```
- **Response:** `{ isSuccess, salesTransactionId, errorResponse:[ {errorCode,message,referenceId} ], contextDetails }`.
  On success `salesTransactionId` = the **Order id** (`801…`), parallel to
  how the quote graph returns a Quote id (`0Q0…`).
- **Async:** synchronous; the response carries the Order id directly.
- **GOTCHAS (verified live, all important):**
  1. **`OrderItem.StartDate` does NOT exist** on R262 — use **`ServiceDate`** for
     the line start date. (`OrderItem` has `ServiceDate`, `EndDate`, and a
     few other date columns; not `StartDate`.)
  2. **`OrderItem.SubscriptionTermUnit` does NOT exist** — only
     `SubscriptionTerm` (int). The unit is inherited from the PBE-bound
     `ProductSellingModel` (same rule as the quote path's "selling model
     comes from the PBE"). EndDate is auto-derived as
     `ServiceDate + SubscriptionTerm − 1 day` (inclusive convention,
     parallel to the quote path).
  3. **`OrderItem.Discount` (percent input) round-trips on readback.**
     This DIVERGES from `QuoteLineItem.Discount`, which reads back `0` even
     when applied. Verified live: `Discount = 25` on qty 2 produced
     `NetUnitPrice = 337.50`, `NetTotalPrice = 675`, and `Discount = 25`
     persisted on the OrderItem row.
  4. **`OrderAction(Type=Add)` and `OrderItem.OrderActionId` are REQUIRED.**
     Placing OrderItems without an OrderAction wire leaves the order in a
     state that the assetization pipeline cannot consume. The graph must
     include the OrderAction record and reference its id from each OrderItem.
  5. **PST commits the Order header even when `isSuccess:false`** for
     pricing-engine failures (e.g. `END_DATE_MISSING`) — same orphan rule as
     the quote path. Parse-time failures (e.g. `INVALID_FIELD` for unknown
     columns) return `salesTransactionId=""` and commit nothing.
  6. **`Order.ShippingCity/Street/State/PostalCode/Country` are null** after
     PST place. The engine does NOT auto-copy from `Account.ShippingAddress`.
     Activation requires shipping address to be set first (see step 3 below),
     identical to the quote-path requirement.
  7. **Bundle expansion** works identically to the quote path. Sending one
     flat OrderItem whose `Product2Id` is a `ProductClass='Bundle'` SKU
     resolves the bundle server-side and returns N OrderItems (1 root +
     children) linked via `ParentOrderItemId`. Verified live:
     `QB-COMPLETE` → 5 OrderItems, `Order.TotalAmount = $91,000`.

### 2a. AppUsageAssignment — the activation gate — ✅ VERIFIED LIVE (REQUIRED)

**Without this row, the Order activates as a no-op:** `Status` flips to
`Activated`, `ActivatedDate` is stamped, but **no `BillingSchedule`, no
`Asset`, no `AssetActionSource`, no `AsyncOperationTracker`** is produced.
The activation pipeline doesn't error — it doesn't fire at all. There is
no `RevenueTransactionErrorLog` entry, no failed `FlowInterview`, no
trace. From the platform's perspective, the Order is not a Revenue
Lifecycle Management order until this row is written.

`createOrderFromQuote` creates this row implicitly as part of its
invocable-action commit; PST place against the Order graph does not.

- **Endpoint:** `POST /services/data/v67.0/sobjects/AppUsageAssignment`
- **Body (verified):**
  ```json
  {
    "AppUsageType": "RevenueLifecycleManagement",
    "RecordId": "<orderId>"
  }
  ```
- **Response:** standard sObject create `{ id, success, errors:[] }`.
- **When to call:** after PST place succeeds, **before** PATCHing
  `Order.Status = 'Activated'`. Once the row exists, activation engages the
  Revenue Cloud pipeline and produces BillingSchedule + Asset + the
  matching `AsyncOperationTracker` JobTypes (`AssetizationAsyncJob`,
  `ContextPersistence`) on the same schedule as the quote path.
- **Createable fields:** `AppUsageType` (writable, picklist) and `RecordId`
  (writable, polymorphic id). `Name` is system-managed (reads back as
  "Revenue Lifecycle Management"). The row is **not updateable** — every
  field except those two has `IsCreatable=false`, `IsUpdatable=false`.
- **Already present on quote-path artifacts:** Quote, Order, and Asset
  records all receive `AppUsageAssignment` rows with
  `AppUsageType=RevenueLifecycleManagement` and `RecordId` pointing at
  them, all written automatically by `createOrderFromQuote`'s
  invocable-action plumbing.
- **Why we believe this is the gate:** the assetization async hook
  appears to fan out off the OrderAction commit event but **filter on
  `AppUsageAssignment` membership for the Order id**. Direct PST place
  never wrote that row, so the filter excluded every direct-place order
  and the activation flip was a no-op. Inserting the row before
  activation closes the gap end-to-end.

### 2b. Set shipping address — ✅ VERIFIED LIVE (REQUIRED post-AppUsageAssignment)

Once `AppUsageAssignment` exists, the platform applies the same activation
gate as the quote path: `FAILED_ACTIVATION "Enter the shipping address
associated with the account, and try again."` PST place does not copy the
address from the Account; the harness must PATCH the Order with the
account's shipping fields before flipping `Status`.

This is the same step as
[`contracts-sales-txn-quote.md` § 3b — Set shipping address](contracts-sales-txn-quote.md#3b-set-shipping-address-mandatory-before-activate-patch--204).
The PATCH body, response (204 No Content), and fields are identical.

> **Design rule (per direction, 2026-06-25):** keep the
> `set_shipping_address()` call in the order-kind flow even on releases
> where the platform may relax the requirement. Consistency with the
> quote path keeps demo data uniform and protects against future
> tightening of the gate.

### 3. Activate Order — ✅ VERIFIED LIVE (mechanism identical to quote path)

- **Endpoint:** `PATCH /services/data/v67.0/sobjects/Order/<id>` body
  `{ "Status": "Activated" }`. Returns 204 No Content on success.
- **PRECONDITIONS** (both REQUIRED, both verified live):
  1. `AppUsageAssignment` row exists for the Order id (see § 2a).
  2. Order shipping fields populated (see § 2b).
  Shared quote-path re-probe on 2026-06-25 confirmed `Order.BillToContactId`
  and `Order.Billing*` address fields are not activation / invoice-post
  preconditions on this R262 org; the direct-order path therefore mirrors the
  same shipping-only address write unless a future org/release proves otherwise.
- **Effect:** identical to the quote-path activation — fires
  `AssetizationAsyncJob` (`AsyncOperationTracker.ReferenceEntityId =
  <orderId>` reaches `Status=Completed`), creates one `BillingSchedule`
  per OrderItem in `Status=ReadyForInvoicing`, and creates the
  `AssetActionSource → AssetAction → Asset` chain with
  `AssetAction.CategoryEnum = 'Initial Sale'`.
- **Harness checkpoint rule:** `reached_stage = "order_activated"` means
  the activation PATCH succeeded and the derived BillingSchedule + Asset
  barriers have completed. Polling logic from
  [`contracts-sales-txn-quote.md` § 4](contracts-sales-txn-quote.md#4-activate-order--verified-live-mechanism-corrected)
  is reused as-is.

### 4. Usage consumption, BillingSchedule polling, Asset attribution

Identical to the quote-path contracts. See
[`contracts-sales-txn-quote.md` § 4b / 4c / 4d](contracts-sales-txn-quote.md#4b-usage-consumption--transactionjournal-create-sobject-collections--documented-needs-live-verification).
The `AssetActionSource` query (`ReferenceEntityItemId IN (SELECT Id FROM
OrderItem WHERE OrderId = '<orderId>')`) returned the expected single
Asset row on the direct-Order probe.

### 5. Invoice generate → post — ✅ VERIFIED LIVE

Identical to
[`contracts-sales-txn-quote.md` § 6](contracts-sales-txn-quote.md#6-invoice-generate--post--verified-live-full-chain-to-posted).
The probe ran:

- `POST .../invoicing/invoices/collection/actions/generate` with the
  activation-produced `BillingSchedule.Id` → `success=true`,
  `requestIdentifier`. Draft invoice (`3ttWI00000084jBYAQ`) appeared
  within ~15 seconds with `TotalAmount = 450`.
- `POST .../invoicing/invoices/collection/actions/post` →
  `statusURL → AsyncOperationTracker(JobType='InvoiceDraftToPosted')`
  reached `Completed`. Invoice landed `Status=Posted`,
  `InvoiceNumber = INV-US-06-2026-000090`, `TotalAmount = 450`.

Correlation strategy (`InvoiceLine.BillingScheduleId IN (<all submitted
bsIds>)`) returned the InvoiceId on the first try — same path as the
quote kind.

## Cleanup — ✅ VERIFIED LIVE

- **Draft Order:** `DELETE /services/data/v67.0/sobjects/Order/<id>` →
  HTTP 204. Cascades to child OrderItems.
- **Activated Order:** must be reset to Draft first. Activated direct
  attempt returns
  `[{ "errorCode": "DELETE_FAILED", "message": "unable to modify
  activated or superseded order: cannot delete order, or add or remove
  order products" }]` (HTTP 400). PATCH `Status: "Draft"` (204) then
  DELETE (204).
- **AppUsageAssignment rows:** not user-deletable on a live audit org;
  on a scratch they tag-along with the parent Order record's deletion
  via cascade in most cases (verified for Draft-deleted orders).
- **Activated + Posted invoice probe artifact:**
  `Order 801WI00001INR3pYAH` (`PHASE0-PROBE-AUA`) was left intact at the
  end of the probe — Posted invoices on Activated Orders are
  non-deletable through the standard sObject DELETE. The harness's
  normal cleanup task will pick it up via its `DEMO-<run_id>` tag
  convention; the probe artifact is left as evidence that the chain
  works.

## Final implementation contract for `place_order_transaction()`

`lifecycle.place_order_transaction()` MUST do the following in order:

1. Build the PST graph with `Order` root + `OrderAction(Type=Add)` + N
   `OrderItem` children, each child's `OrderActionId` pointing at the
   action's referenceId.
2. POST to `connect/rev/sales-transaction/actions/place`. On
   `isSuccess:false`, raise `LifecycleError("order", …)` with the returned
   `salesTransactionId` (which may be populated on pricing-engine failures
   for cleanup tracking).
3. Extract the Order id from `salesTransactionId`.
4. Immediately POST `AppUsageAssignment {AppUsageType:
   "RevenueLifecycleManagement", RecordId: <orderId>}`. Raise
   `LifecycleError("order", "AppUsageAssignment create failed: …", record_id=orderId)`
   on failure. **This is the critical step that no documentation surfaces.**
5. Return `(order_id, order_number)` — `order_number` is read from the
   readback (`SELECT OrderNumber FROM Order WHERE Id = <id>`), since the
   PST response doesn't include it.

`steps.run_order_direct()` then proceeds: `set_shipping_address(order, account)`
→ `activate_order(order)` → `poll_billing_schedules` + `poll_assets` — all
reused as-is from the quote-path implementation.

## Probe inventory (`rlm-base__jun17_1`, 2026-06-25)

| Tag | Order | Outcome |
| --- | ----- | ------- |
| `PHASE0-PROBE-3` | 00000228 (`801…IMBpKYAX`) | Direct-place succeeded; activation no-op (deleted) |
| `PHASE0-PROBE-BUNDLE` | 00000229 (`801…IM4dTYAT`) | Bundle expansion verified (5 lines, $91k); deleted |
| `PHASE0-PROBE-DISC` | 00000230 (`801…ILy5zYAD`) | Discount round-trip verified; deleted |
| `PHASE0-PROBE-ORPHAN` | 00000231 (`801…IN23CYAT`) | Pricing-engine failure orphan verified; deleted |
| `PHASE0-PROBE-ACT` | 00000232 (`801…IMuldYAD`) | OrderAction-in-graph alone insufficient; deleted |
| `PHASE0-PROBE-TYPE` | 00000233 (`801…IN1OxYAL`) | `Order.Type=New` no effect; deleted |
| `PHASE0-PROBE-DIAG` | 00000234 (`801…INRg9YAH`) | Diagnostic — null `BillToContactId` confirmed not the gate; deleted |
| `PHASE0-PROBE-AUA` | 00000235 (`801…INR3pYAH`) | **Full success: BillingSchedule, Asset, Posted invoice `INV-US-06-2026-000090` $450.** Retained as evidence. |
