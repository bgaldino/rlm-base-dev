# Large-Deal Preprocess / Reprice / Activation — Behavior Reference

> Sub-file of `troubleshooting/SKILL.md`. Reference for diagnosing the large-deal
> (`IsLargeDeal=true`) "Prepare for Activation" flow: reprice → preprocess →
> activate. Facts below were validated against Salesforce core (Release 262) and
> empirically on a live org. Use it to interpret the signals you capture (see the
> live-org evidence-capture section of the parent skill).

## The pipeline and where it breaks

On a large-deal order created from a quote (`createOrdersFromQuote`), the order's
line items were written by direct DML, so the order is flagged "modified since
pricing" and **preprocess validation rejects it** until an explicit reprice clears
that flag. The feature therefore does: **reprice → wait for pricing to commit →
preprocess → activate.** The classic first-attempt failure is enqueueing preprocess
before the (async) reprice has actually committed.

## Signal 1 — `Order.ValidationResult` (the authoritative "prices current" gate)

- The preprocess "We couldn't activate the order because the prices aren't updated.
  Click Reprice All and try again." error fires while `Order.ValidationResult` is
  **non-null** (`TransactionIncomplete`, set when items are changed via direct DML;
  also `MissingContributor`).
- A **successful** pricing run **clears `ValidationResult` back to null**.
- ⇒ **Gate enqueue-preprocess on `Order.ValidationResult == null`** — this is the field
  the platform actually checks. `CalculationStatus` is a *secondary* confirmation that
  pricing finished, not the gate. **Do NOT** use `Order.LastPricedDate` — it can stay
  null even after a successful large-deal reprice.

## Signal 2 — `Order.CalculationStatus` (pricing lifecycle)

Reprice for `IsLargeDeal=true` prices **asynchronously** (the executor returns
`isSuccess=true` on *accept*, HTTP 202, with a tracker id — not on completion).
Async dispatch is keyed **solely on `IsLargeDeal`** (no line-count/amount threshold);
there is **no synchronous mode** for large deals. Poll `CalculationStatus` (updated
transactionally at each step):

- **Terminal success (large deal):** `CompletedWithPricing` (tax is architecturally
  skipped for large deals — there is no `CompletedWithPricingAndTax`; the tax-complete
  value, for non-large deals, is `CompletedWithTax`). Also terminal: `CompletedWithoutPricing`.
- **In-progress (wait):** `NotStarted`, `ContextHydrationInProgress`, `QueuedForConfiguration`,
  `ConfigurationInProgress`, `QueuedForPricing`, `QueuedForPricingAndSaving`,
  `PriceCalculationInProgress`, `TaxCalculationWaiting`, `QueuedForSaving`, `Saving`,
  `ReconciliationInProgress`.
- **Failure (retry the reprice — bounded):** `PstBaseStepFailed` (transient infra:
  context-TTL/async-timing/hydration race), `ConfigurationFailed`,
  `GroupRampConfigurationFailed`, `PriceCalculationFailed`, `TaxCalculationFailed`,
  `SaveFailedOrIncomplete`, `ReconciliationFailed`, `OrderRequestFailed`.
- **Investigate (do NOT auto-retry):** `OrderRequestPartiallySaved`, `PartialSaveSuccess`.

`PstBaseStepFailed` is a sanctioned-retry transient (no prescribed count; bounded
2–3 attempts with short backoff is reasonable). Empirically the first reprice on a
fresh large order can fail and a retry succeeds.

## Signal 3 — `AsyncOperationTracker` (the async jobs)

A reprice emits **order-keyed** trackers (`ReferenceEntityId = Order.Id`) with JobTypes
**`PSTBaseJob`, `PSTPrice`, `PSTPersist`** (and `PSTConfig` when config runs); preprocess
emits **`PreprocessOrder`**; order creation emits `QuoteToOrderJob`. (Note: `ReferenceEntityId`
has been observed null on some runs — treat the order-keyed count as best-effort, with
`ValidationResult`/`CalculationStatus` as the primary gate.) Reprice failure surfaces as
`PSTBaseJob`/`PSTPrice` `Status=Failure`; success as those + `PSTPersist` `Completed`.

## `Order.PreprocessingStatus` decode

4-char string, one char per step: position 0 = **Validation**, 1 = BillingTreatment,
2 = TaxTreatment, 3 = UsageRate. Char values: `N` not-started, `Q` queued, `C` completed,
`F` failed. So `FCCC` = validation failed, others complete; `CCCC` (or `CNNN` with
invoicing off) = ready. A **null/blank** value (the API/SOQL result; the `sf` CLI and
Python render it as `None`) means the field was never stamped on that path — the standard
Activate button is a legacy action that does **not** gate on `PreprocessingStatus`; the
activation guard is enforced at DML time.

## Tax skip

Tax is architecturally skipped for large deals — `CompletedWithPricing` (no tax) is the
expected terminal state, confirmed by core automation tests.

## Diagnosing a failure (queries)

```bash
sf data query --target-org $ORG -q "SELECT Status, CalculationStatus, ValidationResult, PreprocessingStatus, RLM_Preprocessing_Complete__c FROM Order WHERE Id='<id>'"
sf data query --target-org $ORG -q "SELECT Category, ErrorCode, ErrorMessage, ConfiguratorErrorMessage FROM RevenueTransactionErrorLog WHERE PrimaryRecordId='<id>' ORDER BY CreatedDate"
sf data query --target-org $ORG -q "SELECT JobType, Status, CreatedDate FROM AsyncOperationTracker WHERE ReferenceEntityId='<id>' ORDER BY CreatedDate"
```

Capture these **before** any account/data reset (see the parent skill) — the evidence
is gone after a reset.

## Implementation in this repo

`unpackaged/post_large_stx/classes/RLM_PreProcessOrderController.cls` —
`startPreprocess` (reprice + stamp, returns phase), `getPricingStatus`
(`classifyPricingPhase` gates on `ValidationResult == null` + terminal status + no
pending async), `enqueuePreprocess` (re-verify + server idempotency). The LWC
`rlmPreProcessOrderAction` drives the reprice-wait poll + bounded re-reprice.
