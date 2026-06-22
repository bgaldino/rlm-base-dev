# Demo Sales Data Generator — Locked Contracts (Phase 0)

> **Status:** in progress. Read-only describes are verified live against sf alias
> `rlm-base__jun17_1` (API v67.0 confirmed available). Live-POST bodies/response
> shapes for the action endpoints are still **TODO** (task #2) and marked below.
>
> No tool code (`lifecycle.py` etc.) is written until every `TODO (live)` here is
> filled in. `lifecycle.py` is then a direct transcription of this file.

## Environment verified

- **Org:** `rlm-base__jun17_1`
- **API version:** `67.0` is present (org max == `67.0`); the tool defaults to `67.0`.
- **Auth (verified):**
  - Token → `sf org auth show-access-token --target-org <alias> --json` returns
    **only** `{ result: { accessToken } }` (no instanceUrl).
  - Instance URL → `sf org display --target-org <alias> --json` returns
    `result.instanceUrl` (non-secret). Two calls; see plan Auth section.

## Object describes — polling FK fields (VERIFIED live)

| Object | `createable` | Polling FK | `referenceTo` | Notes |
|--------|--------------|------------|---------------|-------|
| **Invoice** | **false** (system-generated — confirms premise) | **`ReferenceEntityId`** | `CreditMemo, Opportunity, Order, OrderSummary, Quote` | Poll by `ReferenceEntityId = '<orderId>'`. ✓ |
| **BillingSchedule** | **false** | **`ReferenceEntityId`** | `Order, OrderSummary, Quote` | Also `ReferenceEntityItemId` → `OrderItem` for line-level. |
| **Asset** | true | **none** (no `ReferenceEntityId`) | — | Has `AccountId` + `Product2Id`. **Poll by account + product + created-date window** (finding confirmed). |
| **Order** | true | — | `QuoteId`, `AccountId`, `LegalEntityId`, `PaymentTermId` | Custom tag-field candidate present: **`RLM_Billing_Profile__c`** → `BillingAccount`. Standard `Description` field used for run_id tag. |

## Terminal-state detection (VERIFIED live — picklists + error log)

This resolves the plan's "async failure detection" open item.

- **Invoice.Status** values:
  `Draft`, `Draft In Progress`, `Pending`, `Posting In Progress`, `Posted`,
  `Canceled`, `Error`, `Void In Progress`, `Voided`, `Split In Progress`, `Split`,
  `Split Draft`, `Split Posting In Progress`, `Split Posted`, `Split Canceled`,
  `Split Error`, `Split Void In Progress`, `Split Voided`, `Processing`.
  - **Generate success:** terminal `Draft` (transient `Draft In Progress` / `Processing`).
  - **Post success:** terminal `Posted` (transient `Posting In Progress`).
  - **Failure:** **`Error`** (and `Split Error`).
- **BillingSchedule.Status** values:
  `ReadyForInvoicing`, `CompletelyBilled`, `Processing`, `Error`,
  `WaitingForMilestoneEventAccomplishment`.
  - **Success:** `ReadyForInvoicing` / `CompletelyBilled`. **Failure:** `Error`.
- **`RevenueTransactionErrorLog`** — exists, `queryable: true`. Relevant FKs:
  `PrimaryRecordId`, `RelatedRecordId`, **`AsyncOperationTrackerId`**,
  `BillingScheduleGroupId`. → `AsyncOperationTracker` is real on this org; failures
  correlate via `PrimaryRecordId` / `AsyncOperationTrackerId`.

**Polling rule (locked):** poll the target object's `Status` by validated FK until
it reaches a success state; treat `Error` (or timeout) as failure and query
`RevenueTransactionErrorLog` (by `PrimaryRecordId` / `AsyncOperationTrackerId`) for
the reason. Never treat a poll timeout as success.

---

## Lifecycle steps — endpoints, bodies, responses

Documented-first (DG = v262 dev-guide). `TODO (live)` = must be confirmed with a
real call in task #2 before transcription.

### 1. Opportunity (optional head)
- **Endpoint:** `POST /services/data/v67.0/sobjects/Opportunity`
- **Body:** `{ Name, AccountId, StageName, CloseDate }` (StageName from discovery).
- **Response:** `{ id, success, errors }` (standard sObject create). VERIFIED shape (standard REST).
- **Async:** none (synchronous).

### 2. Quote — Place Sales Transaction (PST) — ✅ VERIFIED LIVE
- **Endpoint (PRIMARY, works):** `POST /services/data/v67.0/connect/rev/sales-transaction/actions/place`
- **Body:** graph shape (the **documented** form, not the simplified Postman shape).
  Minimal working quote-create payload verified live:
  ```json
  {
    "pricingPref": "System",
    "taxPref": "Skip",
    "graph": {
      "graphId": "createQuote",
      "records": [
        { "referenceId": "refQuote",
          "record": { "attributes": {"method":"POST","type":"Quote"},
                      "Name": "<name>",
                      "QuoteAccountId": "<accountId>",
                      "Pricebook2Id": "<standardPbId>" } },
        { "referenceId": "refQuoteLine0",
          "record": { "attributes": {"type":"QuoteLineItem","method":"POST"},
                      "QuoteId": "@{refQuote.id}",
                      "Product2Id": "<prodId>",
                      "PricebookEntryId": "<pbeId>",
                      "Quantity": "1",
                      "StartDate": "<ISO>", "EndDate": "<ISO>" } }
      ]
    }
  }
  ```
- **Response:** `{ isSuccess, salesTransactionId, errorResponse:[ {errorCode,message,referenceId} ], contextDetails }`.
  On success `salesTransactionId` = the **Quote id** (`0Q0…`), `errorResponse:[]`.
- **Async:** synchronous (response carries the result directly; no polling needed for place).
- **GOTCHAS (verified live, all important):**
  1. **`AccountId` is NOT writable** on the Quote graph record (`createable:false`).
     Use **`QuoteAccountId`** (writable) instead — confirmed by describe. `AccountId`
     is derived (from linked Opportunity or QuoteAccountId). Without an account the
     quote places but downstream `createOrderFromQuote` fails "Select an account".
  2. **Do NOT send `ProductSellingModelId` on QuoteLineItem** — FLS error
     "You do not have the access on field QuoteLineItem : ProductSellingModelId."
     The selling model is carried by the PricebookEntry / dates, not this field.
  3. **Term/subscription products need `StartDate` + `EndDate`** (or Subscription
     Term + unit) on the line, else `END_DATE_MISSING`.
  4. **PST commits the Quote header even when `isSuccess:false`** — a failed place
     left a real orphan Quote with a populated `salesTransactionId`. Confirms the
     plan's "probes leave real artifacts" rule → probe quotes must be tagged and
     cleaned up.

### 3. Order — Create Order from Quote — ✅ VERIFIED LIVE
- **Endpoint (PRIMARY, works):** `POST /services/data/v67.0/actions/standard/createOrderFromQuote`
- **Body:** `{ "inputs": [ { "quoteRecordId": "<quoteId>" } ] }`
- **Response:** an **array**; `[0].isSuccess`, `[0].outputValues.orderId` (`801…`),
  `[0].outputValues.orderNumber`, `[0].errors`. Synchronous.
- **GOTCHA:** the source Quote **must have an account** (`QuoteAccountId`), else
  `[0].errors[0]` = `REQUIRED_FIELD_MISSING` "Select an account."

### 4. Activate Order — ✅ VERIFIED LIVE (mechanism corrected)
- **The documented/Postman `POST .../connect/revenue-management/orders/actions/activate`
  endpoint returns `NOT_FOUND` on this org** (v67.0) — it is NOT the activation route
  here. (Also confirmed `connect/revenue-management` namespace is not resolvable.)
- **Working mechanism:** plain sObject update —
  `PATCH /services/data/v67.0/sobjects/Order/<id>` body `{ "Status": "Activated" }`.
  `Order.Status` picklist is just `["Draft","Activated"]`. This matches how the
  robot E2E suite activates (UI click → poll `Status == Activated`).
- **PRECONDITION (verified + RESOLVED):** activation fails `FAILED_ACTIVATION`
  "Enter the shipping address associated with the account" if the **Order** has no
  shipping address. `createOrderFromQuote` does **not** copy the account's shipping
  address to the order (order ShippingStreet/City/... came back null even though
  Infinitech has a ShippingAddress). **Fix:** before activating, `PATCH` the order
  with `ShippingStreet/ShippingCity/ShippingState/ShippingPostalCode/ShippingCountry`
  (copied from the account). After that, activation succeeds.
- **`PATCH` returns 204 No Content (empty body) on success** — the client must treat
  an empty 2xx body as success, not try to JSON-parse it.
- **RESOLVED — activation auto-generates BillingSchedule AND Asset** (no explicit
  step 5 needed for QB products):
  - `BillingSchedule`: 1 row, `Status=ReadyForInvoicing`, `ReferenceEntityId=<orderId>`,
    `BillingAccountId=<acct>`, `TotalAmount=450`. Poll by `ReferenceEntityId`.
  - `Asset`: 1 row for the line's `Product2Id` under the account (no ReferenceEntityId
    field — poll by account+product as planned).

### 5. Billing Schedule create — ✅ NOT NEEDED for QB (activation auto-generates)
- Verified: activating the order produced a `BillingSchedule` (Status
  `ReadyForInvoicing`) automatically. The explicit create endpoint is a fallback
  only for products/orgs that don't auto-generate; not exercised in the happy path.
- Fallback endpoint (unverified): `POST /services/data/v67.0/commerce/invoicing/billing-schedules/actions/create`
  body `{ billingTransactionIds: [ <orderId> ] }`.

### 6. Invoice generate → post — ✅ VERIFIED LIVE (full chain to Posted)
- **Generate (PRIMARY, works):** `POST /services/data/v67.0/commerce/invoicing/invoices/collection/actions/generate`
  - **Body (verified):** `{ "billingScheduleIds": ["<bsId>"], "action": "Draft", "invoiceDate": "<ISO>", "targetDate": "<ISO>", "correlationId": "<runId>" }`
  - **Response (verified):** `{ requestIdentifier, success, errors }` — **NO `statusURL`**
    (confirms the plan's "cannot assume a tracker URL" finding for *generate*).
- **Post (PRIMARY, works):** `POST /services/data/v67.0/commerce/invoicing/invoices/collection/actions/post`
  - **Body (verified):** `{ "invoiceIds": ["<invId>"], "correlationId": "<runId>" }`
  - **Response (verified):** `{ requestIdentifier, success, errors, statusURL }` —
    **post DOES return `statusURL`** → `/services/data/v67.0/sobjects/AsyncOperationTracker/<id>`.
    ⚠️ **Asymmetry:** generate has no statusURL, post does. Note the capitalization
    is **`statusURL`** (not `statusUrl`).
- **Result (verified):** invoice reached `Posted`, got `InvoiceNumber`
  (`INV-US-06-2026-000001`), `TotalAmount=450`.

#### Invoice correlation — RESOLVED (deterministic; no recency heuristic needed)

`Invoice.ReferenceEntityId` is **null on freshly generated** invoices (the billing
engine does not stamp it for billing-schedule-generated invoices), so the plan's
poll-by-orderId returns 0 rows *as generated*. Investigated three correlation paths
live — all verified on `rlm-base__jun17_1`:

1. **PRIMARY — `InvoiceLine.BillingScheduleId` back-link (deterministic, zero extra writes).**
   We already hold the `billingScheduleId` we passed to `generate`. `InvoiceLine`
   carries **`BillingScheduleId`** (→ BillingSchedule) and exposes the parent via
   `Invoice.*`. Verified query:
   ```sql
   SELECT InvoiceId, Invoice.Status, Invoice.InvoiceNumber
   FROM   InvoiceLine
   WHERE  BillingScheduleId = '<bsId we passed to generate>'
   ```
   → returns the exact invoice. **This is the locked correlation for generate.** No
   account+recency guessing; survives concurrent runs against the same account.
   (`InvoiceLine` also has `ReferenceEntityItemId` → OrderItem/QuoteLineItem and
   `BillingScheduleGroupId` as secondary keys.)

2. **`Invoice.ReferenceEntityId` is `updateable=true` → we can stamp it ourselves,
   but ONLY once Posted (Draft rejects it).**
   Verified: `PATCH /sobjects/Invoice/<id> {"ReferenceEntityId":"<orderId>"}` (Order
   is in its `referenceTo`) succeeds (204) on a **Posted** invoice, and **`Invoice
   WHERE ReferenceEntityId = '<orderId>'` then returns the row** — i.e. we can *make*
   the plan's original poll-by-orderId work by writing the FK.
   ⚠️ **CORRECTION (Phase 3, re-verified):** the same PATCH on a **Draft** invoice is
   **rejected** — HTTP 400 `INVALID_FIELD_FOR_INSERT_UPDATE` *"Can't change this
   field's value on Draft invoices."* Phase 0's success was on an already-Posted
   invoice. So this link must be written **after** `post`, not during draft tagging.
   The tool splits this out: `tag_invoice` (Description, at draft time) vs.
   `link_invoice_to_order` (ReferenceEntityId, after post). It is purely cosmetic —
   correlation already works via `InvoiceLine.BillingScheduleId` (path 1).

3. **`Invoice.Description` is `updateable=true` and writable even after Posted.**
   Verified: `PATCH {"Description":"DEMO-<run_id>"}` on a **Posted** invoice
   succeeded (`IsInvoiceLocked=false`). So the `run_id` pseudo-tag can be stamped at
   draft time and survives posting → bulk cleanup via
   `... WHERE Description LIKE 'DEMO-%'` works for invoices too.

Dead ends (do not rely on):
- **`Invoice.CorrelationIdentifier`** — the `correlationId` passed to generate/post
  is **NOT** persisted here (came back null), and the field is `create=F update=F`
  (read-only), so we can neither read our id from it nor write it. It is **not** a
  usable correlation carrier despite the promising name.
- **Post `statusURL` → AsyncOperationTracker** *(JobType `InvoiceDraftToPosted`)*
  exists and reaches `Status=Completed`, **but** its `CorrelationIdentifier`,
  `ReferenceEntityId`, `Request`, and `Response` all came back **null** — it is a
  completion *signal* only, carrying no invoice id or correlation. Use it to confirm
  post finished; do not expect to read the invoice id back from it.
- **Generate emits NO AsyncOperationTracker** at all (only post, context, and
  assetization jobs appeared) — so there is no generate tracker to query.

#### Locked correlation strategy
- **generate** → poll `InvoiceLine.BillingScheduleId = <bsId>` for the InvoiceId
  (deterministic). Then PATCH the invoice's `Description = DEMO-<run_id>` (writable on
  Draft; survives posting). Do **not** PATCH `ReferenceEntityId` here — Draft rejects it.
- **post** → we already hold the invoice id; confirm completion via the returned
  `statusURL` AsyncOperationTracker reaching `Completed` (fallback: poll
  `Invoice.Status = Posted`). **`InvoiceNumber` is assigned at post time — it is
  `null` while Draft**, so read it back after post completes (the manifest's
  human-readable invoice number comes from here, not from generate). Then PATCH
  `ReferenceEntityId = <orderId>` for natural org linkage (Posted-only; cosmetic).
- **assets** (bonus find) → `AsyncOperationTracker` rows with
  `JobType='AssetizationAsyncJob'` carry **`ReferenceEntityId = <orderId>`**, giving
  a deterministic activation→asset correlation alongside the account+product+date poll.

#### Timing observed (single record, indicative only)
- PST place, createOrderFromQuote, Order Status PATCH: effectively synchronous.
- Invoice **generate** is async: invoice row was **not** present at +5s, **was**
  present (Draft) by ~+15s. Post→Posted within ~+12s.
- Both invoice steps need **poll-with-backoff**; do not assume the row exists
  immediately after a `success:true` generate response.

## Timing & Sequencing (live-verified — read before writing `lifecycle.py`)

The chain is **sequential with hard barriers**, not a fire-and-forget batch. Each
of these is a real ordering hazard observed on `rlm-base__jun17_1`:

1. **Synchronous spine, async tail.** PST place → createOrderFromQuote → Order
   `Status` PATCH all return their result inline (no polling). The billing tail
   (BillingSchedule generation, invoice generate, invoice post) is **asynchronous** —
   a `success:true` response means *accepted*, **not** *done*. The tool must poll
   after every billing step.

2. **Mandatory pre-activation ordering — set shipping address BEFORE activate.**
   `createOrderFromQuote` does **not** copy the account's shipping address onto the
   Order, and activation hard-fails `FAILED_ACTIVATION` without it. Sequence is
   strictly: create order → **PATCH order shipping address** → PATCH `Status=Activated`.
   Reversing the last two fails.

3. **Activation is the billing trigger — don't poll for BillingSchedule before it.**
   BillingSchedule (and Asset) are generated *as a consequence of* activation. They
   do not exist between create-order and activate; only start polling for them after
   the activate PATCH returns 2xx.

4. **Invoice generate lag: ~10–15s, and NO `statusURL`.** The generated invoice row
   was absent at +5s and present (Draft) by ~+15s. Generate returns only
   `{requestIdentifier, success, errors}` — there is **no tracker URL to GET** (and
   generate emits no AsyncOperationTracker at all). Must poll by query — deterministically
   via `InvoiceLine.BillingScheduleId = <bsId>` (see correlation note) — with backoff;
   do not read-after-write immediately.

5. **Generate vs. post async asymmetry.** Post **does** return a `statusURL` →
   AsyncOperationTracker (deterministic completion signal); generate does not. The
   poller therefore needs two modes: query-poll after generate, tracker-GET after
   post. (Field is spelled `statusURL`.)

6. **Don't post until the draft is queryable.** Because generate is laggy, posting
   immediately after a `success:true` generate can race the draft's existence. Gate
   post on having actually found the Draft invoice id via poll — not on the generate
   response alone.

7. **PST commits the Quote header even on failure (`isSuccess:false`).** A failed
   place still leaves a real orphan Quote. Sequencing implication: a mid-chain
   failure does not roll back upstream artifacts — the manifest must record each id
   at the stage it's created so cleanup can find partials.

8. **PATCH returns 204 (empty body).** Activation/tagging PATCHes succeed with an
   empty 2xx — the client must treat empty-body 2xx as success and not JSON-parse it.

9. **Concurrency model.** The per-record spine is serialized by these barriers, so
   the throughput win is running **independent scenarios in parallel** (overlapping
   each other's poll waits), not parallelizing within one record's chain.

## Required permission sets
Probes ran as the org admin (`rlm-base__jun17_1`) and all calls succeeded. `TODO`:
determine the minimal PSL/PS for a non-admin running user (likely the RLM/Billing
permission sets the build assigns). Not blocking the happy path on an admin-auth org.
