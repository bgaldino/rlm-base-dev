# Usage Management Domain

The 23 objects of the Usage Management domain — entitlements, grants, metering,
rating policies, and consumption tracking — plus `RatingFrequencyPolicy`, which the
ERD files under Rate Management but which is configured alongside these.

Verify this list with `python scripts/ai/query_erd.py domain Usage`.

## Core Design-Time Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `UsageResource` | Defines a usage resource (API calls, storage, data, etc.) | Code (unique), UsageDefinitionProductId (→ Product2), TokenResourceId (self-ref), UnitOfMeasureClassId — `UsageResourceBillingPolicyId` was **removed in 264**; bind the accumulation policy via `ProductUsageResourcePolicy.UsageAggregationPolicyId` instead |
| `ProductUsageResource` (PUR) | Binds a Product to a UsageResource | ProductId, UsageResourceId, TokenResourceId |
| `ProductUsageResourcePolicy` (PURP) | Policy config for a PUR | ProductUsageResourceId, RatingFrequencyPolicyId, UsageAggregationPolicyId, UsageCommitmentPolicyId, UsageOveragePolicyId — but see the commitment restriction below |
| `ProductUsageGrant` (PUG) | Entitlement grant for a product/resource | ProductUsageResourceId, UsageResourceId, RenewalPolicyId, RolloverPolicyId, UnitOfMeasureClassId, UnitOfMeasureId |
| `UsageResourceBillingPolicy` | Billing policy for usage resources | Code |

> ⛔ **A commitment product's PURP may carry ONLY a `UsageCommitmentPolicy` — platform-enforced.**
> When the PURP's product has `UsageModelType` ∈ **Commit / CommitmentQuantity /
> CommitmentSpend**, setting *either* period field fails with
> `INVALID_INPUT: "This field must be empty when the product associated with the
> product usage resource is one of the commitment usage model types.:
> [RatingFrequencyPolicyId]"` — and the identical message for
> `[UsageAggregationPolicyId]`. Commit-only is the *only* legal shape; it is not a
> data-quality preference. Live-verified 2026-07-24. The offline invariant
> `check_commitment_purp_has_no_periods` in `tests/test_qb_multicurrency_data.py`
> guards this.

> ⚠ `UsageAggregationPolicy` is a **relationship name only** — there is no SObject by
> that name. The object behind `UsageAggregationPolicyId` is `UsageResourceBillingPolicy`.
> `Schema.UsageAggregationPolicy` does not compile.

## Policy Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `RatingFrequencyPolicy` | How often to rate usage | RatingPeriod, ProductId, UsageResourceId |
| `UsageCommitmentPolicy` | Commitment/minimum usage rules | Name |
| `UsageOveragePolicy` | Overage handling rules | Name |
| `UsageGrantRenewalPolicy` | Grant renewal rules | Code, UsageSummaryId |
| `UsageGrantRolloverPolicy` | Unused grant rollover rules | Code |
| `UsagePrdGrantBindingPolicy` | Binding policy for grants | Name, Product2Id |
| `UsageResourcePolicy` | Aggregate policy binding | UsageAggregationPolicyId, UsageCommitmentPolicyId, UsageOveragePolicyId |

## Runtime Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `UsageSummary` | Aggregated usage per resource | UsageResourceId (self-ref for hierarchy), `Status` |
| `TransactionJournal` | Individual usage event/transaction | UsageResourceId, `Status` (`Pending` until a summary absorbs it) |
| `UsageEntitlementBucket` | Entitlement balance tracking | BucketBalanceUomId, ParentId |
| `UsageEntitlementEntry` | Individual entries against buckets | ParentEntitlementBucketId, TransactionUsageEntitlementId, TransactionalBucketId |
| `UsageEntitlementAccount` | Account-level entitlement tracking | — |
| `TransactionUsageEntitlement` (TUE) | Entitlement context for transactions. **Transactional** — the platform writes it during order activation / assetization, and `ProductId` is `createable: false` | ProductId, UsageResourceId, UsageGrantRefreshPolicyId, UsageGrantRolloverPolicyId, `EntitlementProcessingStatus` (**no `Status` field** — values `PENDING` / `PROCESSED`). **TUE carries no commitment or overage policy lookup** — see the note below |
| `UsageBillingPeriodItem` | Usage billing period tracking | — |
| `UsageRatableSummary` | Ratable usage summary | `TierQuantity`, `OverageQuantity` — see caveat below |
| `UsageCmtAssetRelatedObj` | **Commitment → anchor junction.** `AssetId` = the *commitment* asset, `RelatedObjectId` = the *anchor* asset. Without this row the commitment is inert. | AssetId, RelatedObjectId, UsageResourceId |
| `UsageRatableSumCmtAssetRt` | Ratable summary commitment | UsageResourceId |

> ⚠ **`TransactionUsageEntitlement` has never carried `UsageCommitmentPolicyId` or
> `UsageOveragePolicyId` — on 262 *or* 264.** This table listed both until 2026-08-14; that was
> an authoring error, **not** a 264 removal, so do not "restore" them and do not describe them
> as removed in 264. Verified by describing TUE on a true 262 org and a fresh 264 org: **40
> fields → 36, exactly four removed** (`ChargeForOverage`, `DrawdownOrder`,
> `RatingFrequencyPolicyId`, `UsageAggregationPolicyId`), none added, and both policy lookups
> absent on **both** releases. The only policy lookups TUE has ever had are
> `UsageGrantRefreshPolicyId` and `UsageGrantRolloverPolicyId`.
>
> Commitment and overage bind at the **policy** objects instead —
> `ProductUsageResourcePolicy` and `UsageResourcePolicy` each carry all four
> (`RatingFrequencyPolicyId`, `UsageAggregationPolicyId`, `UsageCommitmentPolicyId`,
> `UsageOveragePolicyId`), which is why 264 re-sources overage chargeability from
> `UsageOveragePolicy.OverageChargeable` **via `ProductUsageResourcePolicy`**. Because that
> join is scoped to a *product-and-resource* pair, a lookup keyed on resource alone can return
> another product's policy — see the Anchor-only overage rule below.

> ⚠ **`UsageRatableSummary.OverageQuantity` mirrors `TierQuantity` on ordinary rows.**
> It means "charged beyond the *included allowance*", **not** "beyond the
> commitment". Do not read a non-zero `OverageQuantity` as commitment exhaustion.

## Unit of Measure Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `UnitOfMeasure` | Individual unit (Each, GB, Hour, etc.) | UnitCode (unique) |
| `UnitOfMeasureClass` | Groups related units (Data, Time, etc.) | Code (unique), BaseUnitOfMeasureId, DefaultUnitOfMeasureId |

## Key Relationships

```
UsageResource ← ProductUsageResource (UsageResourceId)
Product2 ← ProductUsageResource (ProductId)
ProductUsageResource ← ProductUsageResourcePolicy (ProductUsageResourceId)
ProductUsageResource ← ProductUsageGrant (ProductUsageResourceId)
UsageResource ← ProductUsageGrant (UsageResourceId)
UsageGrantRenewalPolicy ← ProductUsageGrant (RenewalPolicyId)
UsageGrantRolloverPolicy ← ProductUsageGrant (RolloverPolicyId)
UnitOfMeasureClass ← ProductUsageGrant (UnitOfMeasureClassId)
UnitOfMeasureClass ← UsageResource (UnitOfMeasureClassId)
UsageResource ← UsageResource (TokenResourceId, self-ref)
UsageResource ← TransactionJournal (UsageResourceId)
UsageResource ← UsageSummary (UsageResourceId)
UsageResourceBillingPolicy ← ProductUsageResourcePolicy (UsageAggregationPolicyId)
    (through 262 also: UsageResourceBillingPolicy ← UsageResource
     (UsageResourceBillingPolicyId) — that field was removed in 264)
UnitOfMeasure ← UnitOfMeasureClass (BaseUnitOfMeasureId, DefaultUnitOfMeasureId)
```

## Runtime: Recording and Rating Usage

This section is the **object-level** reference. For the procedure — building assets,
recording, orchestrating, verifying, resetting — use
`.cursor/skills/usage-consumption/SKILL.md`. Worked arithmetic:
`docs/guides/qb-consumption-demo-scenarios.md`. End-user runbook:
`docs/guides/usage-consumption-runbook.md`.

These rules came from **live verification**, not the doc snapshots: the dev guide
gives object/field shape and Help gives one-line value definitions, but neither
documents drawdown ordering or interaction.

### Usage is always recorded against the ANCHOR

A commitment is a **rate modifier**, not a consumption target. Journals uploaded
against a commitment asset stay `Pending` forever and are never rated. Record usage
on the anchor asset; the commitment applies itself through the junction.

### Selling a commitment takes three steps

1. Sell the **anchor** asset.
2. Sell the **commitment** asset (a separate sale — it is its own product).
3. Link them with a `UsageCmtAssetRelatedObj` row
   (`AssetId` = commitment, `RelatedObjectId` = anchor).

Skipping step 3 leaves a commitment that exists, activates, and does nothing.

### Drawdown order and bases

Consumption settles **commitment first, then grant, then overage**:

| Consumer | Decrements by | Note |
|----------|---------------|------|
| commitment bucket | the **discounted** quantity | e.g. 27,777.78 raw × 0.90 = exactly 25,000 |
| anchor grant | the **raw** quantity | a grant is an included *allowance*, not a discount — what it absorbs is never discounted |
| overage | rated per `UsageCommitmentPolicy.CommitmentRate` | see below |

### `UsageCommitmentPolicy.CommitmentRate` decides overage pricing

| Value | Behaviour past the commitment boundary |
|-------|----------------------------------------|
| `Lowest Commitment Rate` | the commitment discount **survives** into overage |
| `Bounded Object Rate` | reverts to the **standard anchor rate** |

Both behave identically up to the boundary. This is a **design-time global switch —
no runtime object snapshots it**, so you cannot tell from runtime data which
behaviour applied; you must read the policy.

### ⛔ Three ways to silently get zeros

Each item below is a **mistake**, not an instruction. All three fail with **no
error** — the rated summary simply reads zero:

1. **Recording usage AFTER that period was orchestrated.** A `UsageSummary` that
   has reached `RatableSummaryComplete` / `LiableSummaryComplete` **never reopens**,
   so journals arriving afterwards stay `Pending` forever.
   → *Record usage BEFORE orchestrating the period.*
2. **Orchestrating an account for the first time before consuming.** The first pass
   closes every past period EMPTY, and you get one attempt per account.
   → *Consume first, then orchestrate.*
3. **Booking into the CURRENT period.** It stays open indefinitely, so the usage
   sits at `InProgress` with buckets untouched — which reads as "full discount, no
   drawdown" and is not a real result.
   → *Book into a PAST, completed period.*

A fourth, less severe: orchestration needs **several passes** to settle; one run is
not enough, and stopping early looks like zero.

The corresponding *rules* (stated positively, with worked arithmetic) are in
`docs/guides/qb-consumption-demo-scenarios.md`.

### ⛔ Two more silent-zero traps (established live 2026-07-26)

4. **A usage clear does NOT reopen a closed period.** `clearUsageData.apex` drains
   the summaries, but the period state on `UsageEntitlementAccount` / the buckets
   survives, and a closed period never reopens. Re-recording into the **same**
   period after a clear therefore reproduces trap 1 exactly: the journals strand
   (`"stranded behind a period that already closed"`), `UsageSummary` /
   `UsageRatableSummary` / `UsageBillingPeriodItem` all read 0, and
   `TransactionJournal` holds what you recorded.
   → *Re-testing one period needs a full account reset and an asset rebuild, not a
   usage clear. A clear only frees you to use a DIFFERENT period.*
5. **A commitment sold after the org was built can rate at the undiscounted anchor
   rate.** Selling a commitment creates its `AssetRateAdjustment` rows, and the
   commitment rate is looked up through the `Commitment_based_Rate_Adjustment`
   decision table. That table was missing from the `CreateAssetOrderEvent` refresh
   chain (`RLM_Platform_Event_CreateAssetOrderEvent_Stamp_Asset_Renewal_Info`) —
   every sibling rate table on the same source objects was in it, so only the
   commitment lookup went stale. Fixed by adding it to the chain; it now refreshes
   on order activation, measured at ~6s after the rows are created.
   → *On an org built BEFORE that fix, refresh by hand before recording usage, and
   confirm `DecisionTable.LastSyncDate` is later than the newest
   `AssetRateAdjustment.CreatedDate`.*

### Entitlement bucket tree

The bucket tree is **3 levels deep and NO bucket has a null `ParentId`** — the
wallet's parent is a grant-binding target (`1Gve…` prefix), not a bucket. Identify
children by **set membership**, never by `ParentId == null`.

### ⛔ The usage graph has CIRCULAR delete constraints

There is no valid fixed teardown order — `UsageSummary` ↔ `UsageRatableSummary` can
each hold the other, entries and journals hold summaries, and buckets self-nest. The
only correct algorithm is a **convergent loop**: attempt every object each round and
stop when a full round makes no progress. See `scripts/apex/clearUsageData.apex`
(org-wide) and `RLM_AccountUtilities.delAccountRelatedObjects` (per account).

## Activation Order

Rating objects require careful activation ordering:

1. Load UnitOfMeasure and UnitOfMeasureClass
2. Load UsageResource and policies
3. Load ProductUsageResource (PUR) — Insert + deleteOldData
4. Load ProductUsageResourcePolicy (PURP) — Insert + deleteOldData
5. Load ProductUsageGrant (PUG) — Insert + deleteOldData
6. Activate UnitOfMeasureClass and UsageResource (Pass 2)
7. Run `activateRatingRecords.apex` for PUR/PUG activation

## SFDMU Data Plan: `qb-rating`

16 objects across 2 passes. Upstream: `qb-pcm` (Product2, UoM, UoMClass), `qb-billing` (UsageResourceBillingPolicy).

PUR, PURP, and PUG in the **shipped** plans use `Insert` + `deleteOldData: true` — a **pre-5.6.4 workaround** for Bug 3, which is **fixed on the 5.6.4+ floor** (Upsert matches on traversal externalIds; new plans use `Upsert`, shipped-plan migration is the gated `sfdmu-v5-optimization` initiative). **PUG is not an operation-only migration**: its 3-field externalId is intentionally non-unique across parent PURs, so moving it to `Upsert` requires first adding a PUR component (e.g. `ProductUsageResourceId`) to the key.

⚠ **Reloading `qb-rating`/`qb-rates` against an org that already has live usage
assets does not work** — `Insert` + `deleteOldData` cannot clear design-time records
that live entitlements reference. Load a new product **surgically** instead. See
`.cursor/skills/sfdmu-data-plans/SKILL.md` → *Reloading a plan into a live org*.

## Tooling

| Tool | Purpose |
|------|---------|
| `python scripts/qb_usage.py audit \| report \| orchestrate` | Inspect usage config, report rated results, drive orchestration passes |
| `scripts/apex/consumeUsageProfile.apex` | Record the declared QB monthly profile against every anchor (`MULTIPLIER`, `USAGE_DATE`, `ONLY_ACCOUNTS`) |
| `scripts/apex/validateRatedUsage.apex` | Assert `amount = qty × rate` and commitment-drains-before-grant |
| `scripts/apex/clearUsageData.apex` | Convergent org-wide usage teardown |
| `cci task run validate_multicurrency_rates` | Design-time + runtime multicurrency rating checks (offline equivalent: `python tests/test_qb_multicurrency_data.py`) |
