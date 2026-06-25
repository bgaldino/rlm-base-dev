# Shared Contracts

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
| **Asset** | true | **none** (no `ReferenceEntityId`) | — | Has `AccountId` + `Product2Id`, but those are not unique enough for harness attribution. **Poll via `AssetActionSource → AssetAction.AssetId` by OrderItem**, filtered to `AssetAction.CategoryEnum = 'Initial Sale'`. |
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
   Reversing the last two fails. Live re-probe on 2026-06-25 (`rlm-base__jun17_1`,
   order `00000246`) confirmed the current R262 org does **not** require
   `Order.BillToContactId` or `Order.Billing*` address fields for activation,
   BillingSchedule generation, invoice generation, or posting: those fields remained
   null while the invoice reached `Posted`.

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

## Composite Batching Decision

Composite is intentionally skipped because CRUD round-trips are not the
meaningful wall-clock cost:

- The lifecycle spine is **async-poll-bound**, not request-bound. Wall-clock is
  dominated by the generate (~10–15s) and post (~12s) polling barriers, plus
  BillingSchedule/Asset waits — not by HTTP round-trip count. Batching the handful
  of non-Connect CRUD calls (Opportunity create, tag/link PATCHes) into one
  Composite request saves a few hundred ms against ~30s of unavoidable polling.
- The Connect **action** endpoints (PST place, createOrderFromQuote, activate,
  invoice generate/post) **cannot** be Composite-merged anyway — Composite is for
  the sObject/connect-record REST API, and each action has a polling barrier before
  the next. The spine stays sequential regardless.
- The real throughput win — **scenario-level concurrency** with a
  session-per-worker thread pool — overlaps those poll waits across independent
  scenarios. That is where the parallelism budget belongs.

Revisit only if a future profiling run shows CRUD round-trips are a measurable
fraction of wall-clock (they are not today). `SfRestClient` is the single place a
`composite()` verb would land if that ever changes.
