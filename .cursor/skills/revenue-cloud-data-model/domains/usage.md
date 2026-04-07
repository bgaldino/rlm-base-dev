# Usage Management Domain

22 objects managing usage entitlements, grants, metering, rating policies, and consumption tracking.

## Core Design-Time Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `UsageResource` | Defines a usage resource (API calls, storage, data, etc.) | Code (unique), UsageDefinitionProductId (→ Product2), TokenResourceId (self-ref), UnitOfMeasureClassId, UsageResourceBillingPolicyId |
| `ProductUsageResource` (PUR) | Binds a Product to a UsageResource | ProductId, UsageResourceId, TokenResourceId |
| `ProductUsageResourcePolicy` (PURP) | Policy config for a PUR | ProductUsageResourceId, RatingFrequencyPolicyId, UsageAggregationPolicyId, UsageCommitmentPolicyId, UsageOveragePolicyId |
| `ProductUsageGrant` (PUG) | Entitlement grant for a product/resource | ProductUsageResourceId, UsageResourceId, RenewalPolicyId, RolloverPolicyId, UnitOfMeasureClassId, UnitOfMeasureId |
| `UsageResourceBillingPolicy` | Billing policy for usage resources | Code |

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
| `UsageSummary` | Aggregated usage per resource | UsageResourceId (self-ref for hierarchy) |
| `TransactionJournal` | Individual usage event/transaction | UsageResourceId |
| `UsageEntitlementBucket` | Entitlement balance tracking | BucketBalanceUomId |
| `UsageEntitlementEntry` | Individual entries against buckets | ParentEntitlementBucketId, TransactionUsageEntitlementId, TransactionalBucketId |
| `UsageEntitlementAccount` | Account-level entitlement tracking | — |
| `TransactionUsageEntitlement` | Entitlement context for transactions | UsageCommitmentPolicyId, UsageOveragePolicyId |
| `UsageBillingPeriodItem` | Usage billing period tracking | — |
| `UsageRatableSummary` | Ratable usage summary | — |
| `UsageCmtAssetRelatedObj` | Commitment asset linkage | UsageResourceId |
| `UsageRatableSumCmtAssetRt` | Ratable summary commitment | UsageResourceId |

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
UsageResourceBillingPolicy ← UsageResource (UsageResourceBillingPolicyId)
UnitOfMeasure ← UnitOfMeasureClass (BaseUnitOfMeasureId, DefaultUnitOfMeasureId)
```

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

PUR, PURP, and PUG use `Insert` + `deleteOldData: true` due to SFDMU v5 Bug 3 (relationship-traversal externalIds never match on Upsert).
