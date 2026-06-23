# Transaction Data Harness — Locked Contracts (Phase 0)

> **Status:** implemented and live-verified against a Revenue Cloud R262
> scratch org with the bundled QB demo dataset (API v67.0). `lifecycle.py` is a
> direct transcription of the endpoint bodies, response shapes, async barriers,
> and sequencing rules captured here. Re-verify against a live org and update
> this file before changing lifecycle behavior.

## Environment verified

- **Org:** Revenue Cloud R262 scratch org with the QB demo dataset loaded.
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

Documented-first (DG = v262 dev-guide), then transcribed into `lifecycle.py` after
live verification against the target org.

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

#### Line discounts — ✅ VERIFIED LIVE (survives PST → order → posted invoice)
Set `Discount` (a standard **percent** field on QuoteLineItem, `createable:true`)
on the line record in the place graph. With `pricingPref: "System"` the engine
applies it to the derived net prices, and those flow through to the posted invoice.

Live probe (one quote, example SKU `QB-API-FLEX` @ $450, qty 2, **25%**; substitute any term-defined SKU on your standard pricebook):

| Where | Field | Value | Note |
|-------|-------|-------|------|
| QuoteLineItem | `UnitPrice` / `ListPrice` | 450 | undiscounted |
| QuoteLineItem | `NetUnitPrice` | **337.50** | 450 × 0.75 → 25% applied |
| QuoteLineItem | `NetTotalPrice` | 667.60 | discounted line total (prorated term) |
| QuoteLineItem | `Discount` | **0** | ⚠ engine consumes the input; does **not** round-trip it onto this field |
| Invoice | `Status` / `TotalAmount` | Posted / **667.60** | discounted amount reached the posted invoice |
| InvoiceLine | `ChargeAmount` | 667.60 | matches |

**Key gotcha:** verify a discount by the **net prices**, not by reading back
`QuoteLineItem.Discount` (it reads `0` post-place even when applied). `InvoiceLine`
has **no** `NetUnitPrice`/`Amount` columns — use `ChargeAmount`; `Invoice` has no
`NetAmount` — use `TotalAmount`.

#### Bundles — PST auto-expands default-configured bundles (✅ VERIFIED LIVE R262)

Sending one flat input line whose `Product2Id` is a **`ProductClass = 'Bundle'`**
SKU does **not** fail. PST resolves the bundle's component graph server-side and
returns a fully configured set of child `QuoteLineItem`s wired to the parent via
`ParentQuoteLineItemId`, each with its own `ProductSellingModelId`, quantity, and
list/total price. The harness's single input line places the configured bundle
end-to-end — no client-side component graph is needed.

Live probe (R262 scratch org, billing-ready account from the QB demo dataset
— `Infinitech` in QB — example bundle SKU `QB-COMPLETE`, qty 1; substitute any
default-configured bundle on your pricebook):

| Where | Result |
|-------|--------|
| Input PST graph | **1** flat line: `Product2Id = <QB-COMPLETE>` |
| Resulting `QuoteLineItem` rows | **5** — 1 Bundle root (`ParentQuoteLineItemId = null`, `TotalPrice = 0`) + 4 Simple children (`QB-DB`, `QB-API-REQT`, `QB-SRV-OG-PSH`, `QB-API-MGMT`) all linked via `ParentQuoteLineItemId = <root>` |
| `Quote.GrandTotal` | **$91,000** — sum of priced child lines |
| Downstream | `createOrderFromQuote` → activation → 7 `BillingSchedule`s → 1 Asset → Draft invoice → Posted `INV-US-06-2026-000039` |

**Caveats:**

- Only **default-configured** bundles are exercised. Bundles with mandatory slots
  requiring user choice (no default, or required attributes with no default
  value) are expected to fail at PST place — the harness has no way to express
  those choices.
- The YAML's `quantity:` / `discount_percent:` apply to the **root** line only.
  Child quantities and prices come from the bundle definition.
- One BillingSchedule is created per child component slot at activation, **not**
  one per input line. `steps.py:run_activate` derives `expected_count` from
  `count_order_items(orderId)` (a `SELECT COUNT(Id) FROM OrderItem` against the
  freshly-created order) so the BillingSchedule and Asset polls wait for the
  full bundle-expanded fan-out, not just the input-line count.
- Some bundle slots produce a `BillingSchedule` with `TotalAmount = 0` (a $0
  root slot, e.g.). No `InvoiceLine` is created against a $0 schedule, so the
  invoice-correlation poll **must** scan across all schedules in the generate
  call — picking any single id (e.g. `[0]`) risks polling the one that never
  yields a row. See *Invoice correlation* below.

#### Selling models — line date rules (✅ VERIFIED LIVE)

The line's date fields are **selling-model-dependent**, and the model is resolved
from the **PricebookEntry**, not from anything writable on the line. This drove a
real multi-line failure (`INVALID_INPUT` "You can't specify EndDate for evergreen
order products" at `createOrderFromQuote`) before the rule was encoded.

- **`PricebookEntry` binds a single `ProductSellingModelId`.** The engine resolves
  the selling model from the PBE used on the line — **not** from
  `ProductSellingModelOption.IsDefault`. To sell a product under a different model,
  use the PBE bound to that model.
- **`ProductSellingModelId` is unwritable on `QuoteLineItem` even as admin** —
  `PATCH`/place both fail FLS `INVALID_API_INPUT` / "You do not have the access on
  field QuoteLineItem : ProductSellingModelId." You cannot pin the model from the
  line; it comes from the PBE.
- **`SellingModelType` picklist = `{OneTime, TermDefined, Evergreen}`.** EndDate
  rule, verified at `createOrderFromQuote` for all three:

  | `SellingModelType` | `StartDate` | `EndDate` | Behavior |
  |--------------------|-------------|-----------|----------|
  | **TermDefined**    | safe        | **required** | rejects `END_DATE_MISSING` without it |
  | **Evergreen**      | safe        | **rejected** | `INVALID_INPUT` "can't specify EndDate for evergreen order products" |
  | **OneTime**        | safe        | **rejected** | same — only term-defined takes an EndDate |

- **Implementation:** `discovery.py` captures `ProductSellingModel.SellingModelType`
  onto each `Product`; `Product.needs_end_date` is `True` only for `TermDefined`,
  and `place_sales_transaction` sets `EndDate` on the line **only** when
  `needs_end_date`. `StartDate` is always set (safe for all three). A multi-line
  quote mixing a TermDefined and an Evergreen product was live-verified through to a
  Posted invoice (`INV-US-06-2026-000006`, order `00000118`): per-line quantities and
  discounts (QB-API-FLEX x2 @20% → NetUnitPrice 360; QB-API x1 @10% → NetUnitPrice
  1800) both survived.

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
  the source account had a populated ShippingAddress). **Fix:** before activating, `PATCH` the order
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

### 4b. Usage consumption — TransactionJournal create (sObject Collections) — ⚠ DOCUMENTED, NEEDS LIVE VERIFICATION

Bound to `unpackaged/post_utils/classes/RLM_UsageUploaderController.cls` (the
canonical in-org TJ writer) and the v262 `TransactionJournal` /
`ProductUsageResource` field docs under `docs/salesforce/262/dev-guide/`.
**Live verification against a scratch org with the QB rating dataset loaded
(`insert_qb_rating_data`) is required before merging behavioral changes here.**

- **Endpoint:** `POST /services/data/v67.0/composite/sobjects`
- **Body (verified shape — chunked at 200 records per call):**
  ```json
  {
    "allOrNone": true,
    "records": [
      {
        "attributes": {"type": "TransactionJournal"},
        "ReferenceRecordId": "<assetId>",
        "AccountId": "<accountId>",
        "UsageResourceId": "<usageResourceId>",
        "QuantityUnitOfMeasureId": "<unitOfMeasureId>",
        "Quantity": 123.45,
        "ActivityDate": "2026-06-22",
        "StartDate": "2026-06-22",
        "EndDate":   "2026-06-22",
        "UsageType": "UsageManagement",
        "Status":    "Pending",
        "UniqueIdentifier": "txn-harness-<run_id>-<assetId>-<targetIdx>-<rowIdx>"
      }
    ]
  }
  ```
- **Response:** standard sObject Collections `[{success, id, errors}, …]` per
  input record.
- **Tag column is `UniqueIdentifier`, NOT `Description`.** `TransactionJournal`
  has no `Description` field per the v262 dev guide. `UniqueIdentifier` is
  `Create+Filter+idLookup`, which is exactly what the harness needs for
  idempotent retry and bulk cleanup (`WHERE UniqueIdentifier LIKE
  'txn-harness-%'`).
- **`UsageType` picklist value used: `UsageManagement`.** Matches
  `RLM_UsageUploaderController.cls` (`buildTransactionJournal`).
- **`Status = Pending` on create.** Becomes `Processed` after the rating job
  completes; that is the verification signal that rating ran end-to-end.
- **`ActivityDate`, `StartDate`, `EndDate` are all set to the same day** for
  single-day usage rows (the QB demo shape). `days_back` spreads
  `ActivityDate` across the last N days but each row still uses one calendar
  day for all three.
- **Idempotent retry contract (lifecycle-side):** before posting, the harness
  pre-queries `SELECT Id, UniqueIdentifier FROM TransactionJournal WHERE
  UniqueIdentifier IN (…)` for the expected ids, excludes already-present
  rows from the POST, and returns `existing_ids ∪ new_ids`. A retry under
  the same `run_id` converges on the complete TJ id set whether the prior
  attempt wrote zero, some, or all rows.
- **Partial-failure isolation:** `allOrNone: true` per chunk. A bad row
  aborts the chunk; the harness raises `LifecycleError("usage", …)` and the
  manifest records zero new ids for that chunk so the retry can reuse the
  same `UniqueIdentifier`s.
- **TODO live-verify on a scratch org:** end-to-end run of
  `scenarios/12-usage-consumption.yaml`, then `SELECT COUNT(Id), Status FROM
  TransactionJournal WHERE UniqueIdentifier LIKE 'txn-harness-%' GROUP BY
  Status` showing the expected `Pending` count before rating and `Processed`
  count after `cli rate`.

### 4c. ProductUsageResource discovery SOQL — ⚠ DOCUMENTED, NEEDS LIVE VERIFICATION

Bound to the v262 `ProductUsageResource` field doc and the seed CSV at
`datasets/sfdmu/qb/en-US/qb-rating/ProductUsageResource.csv`. Live-verify
the binding count against the QB seed once `insert_qb_rating_data` runs.

```sql
SELECT ProductId,
       UsageResourceId,
       UsageResource.Code,
       UsageResource.Name,
       UsageResource.UnitOfMeasureClassId,
       UsageResource.DefaultUnitOfMeasureId,
       UsageResource.DefaultUnitOfMeasure.UnitCode,
       UsageResource.DefaultUnitOfMeasure.Name,
       Status
FROM ProductUsageResource
WHERE ProductId IN (…)
```

- **FK is `ProductId`** (relationship to `Product2`), NOT `Product2Id` — the
  field doc and the seed CSV's `Product.StockKeepingUnit` matcher both
  confirm.
- **User-facing identifier is `UsageResource.Code`** (e.g. `UR-CPUTIME`,
  `UR-DATASTORAGE`, `QB-TOKEN`), not `Name`. The QB seed CSV keys on Code.
- **Do NOT filter by `Status`.** The QB seed loads bindings as `Draft` (per
  `ProductUsageResource.csv`); filtering on `Active` would surface zero
  bindings against the seeded org. If a future pass adds a status filter,
  make it `IN ('Draft','Active')`.
- **Override path (`usage.unit_of_measure` in the YAML):** when a scenario
  pins a UoM code, resolve it via `SELECT Id FROM UnitOfMeasure WHERE
  UnitCode = :code AND UnitOfMeasureClassId = :binding.uom_class_id AND
  Status = 'Active'`. The class-id constraint mirrors
  `RLM_UsageUploaderController.cls:240` — a UoM is only valid against the
  resource if it shares the resource's class.

### 4d. Asset → Product2 map — ⚠ DOCUMENTED, NEEDS LIVE VERIFICATION

```sql
SELECT Id, Product2Id FROM Asset WHERE Id IN (…)
```

- Used by the `usage` step to pair each `LineItem` to the correct activated
  Asset by `Product2Id`. `poll_assets` returns ids ordered by `Id`, not by
  the order of input lines (`CONTRACTS.md` already notes this for the
  Asset-poll path), so a mixed-SKU scenario must NOT pair by list index.
- Duplicate-SKU lines (the same Product2 used on two lines) consume the
  asset pool **1:1 in order** (`steps.run_usage` pops the candidate list)
  so each TJ batch lands on a distinct asset.

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
live — all verified on a Revenue Cloud R262 scratch org:

1. **PRIMARY — `InvoiceLine.BillingScheduleId` back-link (deterministic, zero extra writes).**
   We already hold the `billingScheduleId`(s) we passed to `generate`. `InvoiceLine`
   carries **`BillingScheduleId`** (→ BillingSchedule) and exposes the parent via
   `Invoice.*`. Verified query — use `IN (…)` across **every** schedule submitted
   to that generate call, not just one:
   ```sql
   SELECT InvoiceId, Invoice.Status, Invoice.InvoiceNumber
   FROM   InvoiceLine
   WHERE  BillingScheduleId IN ('<bs1>', '<bs2>', ...)
   ```
   → returns the exact invoice. All submitted schedules land on a **single
   Invoice** (single-invoice per generate, verified), so the first row with a
   non-null `InvoiceId` wins. **This is the locked correlation for generate.** No
   account+recency guessing; survives concurrent runs against the same account.
   (`InvoiceLine` also has `ReferenceEntityItemId` → OrderItem/QuoteLineItem and
   `BillingScheduleGroupId` as secondary keys.)

   ⚠ **Do not poll a single `BillingScheduleId =`.** Bundles activate into one
   schedule per child slot; zero-amount slots (e.g. a $0 bundle root) produce
   **no** `InvoiceLine`, so the invoice is real but the single-id query hangs
   until timeout. Live-verified: a default-configured bundle (example:
   `QB-COMPLETE`) activated into 7 schedules; the first was `TotalAmount = 0`
   and yielded no InvoiceLine, but the $91,000 invoice was visible
   immediately via the other six.

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
- **generate** → poll `InvoiceLine.BillingScheduleId IN (<all submitted bsIds>)`
  for the InvoiceId (deterministic; works for both single-line and bundle cases —
  see the warning above about single-id polls hanging on $0 bundle slots). Then
  PATCH the invoice's `Description = DEMO-<run_id>` (writable on Draft; survives
  posting). Do **not** PATCH `ReferenceEntityId` here — Draft rejects it.
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
of these is a real ordering hazard observed on a live R262 scratch org:

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
Probes ran as an org admin and all calls succeeded. The harness is designed to
run as an admin; the minimal PSL/PS for a non-admin integration user is out of
scope for this contract (likely the RLM/Billing permission sets the build
assigns).

## Phase 5 (Composite) — DECIDED: skipped

The plan gated Composite on *"only if Phase 0 proved CRUD round-trips matter."*
They do **not**, so Composite is **not implemented** and is intentionally dropped:

- The lifecycle spine is **async-poll-bound**, not request-bound. Wall-clock is
  dominated by the generate (~10–15s) and post (~12s) polling barriers, plus
  BillingSchedule/Asset waits — not by HTTP round-trip count. Batching the handful
  of non-Connect CRUD calls (Opportunity create, tag/link PATCHes) into one
  Composite request saves a few hundred ms against ~30s of unavoidable polling.
- The Connect **action** endpoints (PST place, createOrderFromQuote, activate,
  invoice generate/post) **cannot** be Composite-merged anyway — Composite is for
  the sObject/connect-record REST API, and each action has a polling barrier before
  the next. The spine stays sequential regardless.
- The real throughput win — **scenario-level concurrency** (Phase 4, thread pool,
  session-per-worker) — overlaps those poll waits across independent scenarios and
  is already shipped. That is where the parallelism budget belongs.

Revisit only if a future profiling run shows CRUD round-trips are a measurable
fraction of wall-clock (they are not today). `SfRestClient` is the single place a
`composite()` verb would land if that ever changes.
