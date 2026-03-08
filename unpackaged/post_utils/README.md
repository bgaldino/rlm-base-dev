# RC Utilities

Salesforce utility classes and flows for Revenue Lifecycle Management (RLM), deployed via the `unpackaged/post_utils` source directory.

## Contents

- [Account Reset Tool](#account-reset-tool)
- [Asset Action Validator](#asset-action-validator)
- [Permission Set](#permission-set)

---

## Account Reset Tool

Deletes all related objects for a Salesforce Account in the correct dependency order. Invoked via the **Account.RLM_ResetAccount** Quick Action on the Account page layout.

### Class Architecture

```
RLM_Utils_AccountReset          — Orchestrator (@InvocableMethod entry point)
├── RLM_Utils_AccountUsageDeleter   — UsageBillingPeriodItem, UsageRatableSummary, UsageSummary,
│                               UsageRatableSumCmtAssetRt, TransactionJournal,
│                               UsageEntitlementBucket (bottom-up), TUE, UEA
├── RLM_Utils_AccountBindingDeleter — BindingObjUsageRsrcPlcy, BindingObjectRateCardEntry,
│                               AssetRateCardEntry
├── RLM_Utils_AccountOrderDeleter   — Order (with self-ref handling), OrderSummaryRelationship,
│                               FulfillmentOrder/LineItem/Plan/Step/Asset/Decomp
├── RLM_Utils_AccountBillingDeleter — Invoice, BillingScheduleGroup, Contract,
│                               PriceAdjustmentSchedule, RecordAlert (contract)
├── RLM_Utils_AccountAssetDeleter   — Asset, AssetRelationship, UsageCmtAssetRelatedObj,
│                               RecordAlert (asset), Case, ServiceContract, WorkOrder
└── RLM_Utils_AccountCrmDeleter     — Quote, Opportunity
```

### InputVariables

| Variable | Type | Required | Default | Controls |
|----------|------|----------|---------|----------|
| `accountId` | String | Yes | — | Target account |
| `DeleteAssets` | Boolean | Yes | — | Assets and their restrict-delete children |
| `DeleteFulfillment` | Boolean | Yes | — | All Fulfillment* objects |
| `DeleteBilling` | Boolean | Yes | — | Draft Invoices |
| `DeleteOrders` | Boolean | No | `true` | Orders, OrderItems, OrderSummaryRelationship |
| `DeleteContracts` | Boolean | No | `true` | Contracts, PriceAdjustmentSchedule |
| `DeleteOpportunities` | Boolean | No | `true` | Opportunities |
| `DeleteQuotes` | Boolean | No | `true` | Quotes |

New flags (`DeleteOrders`, `DeleteContracts`, `DeleteOpportunities`, `DeleteQuotes`) default to `true` for backward compatibility with existing flows that don't pass them.

### Deletion Order

The orchestrator calls helper classes in this sequence:

| Step | Class | Method | Always? | Flag |
|------|-------|--------|---------|------|
| 1 | UsageDeleter | `deleteUsageSummaries` | Yes | — |
| 2 | UsageDeleter | `deleteUsageRatableSumCmtAssetRts` | Yes | — |
| 3 | UsageDeleter | `deleteUsageRatableSummaries` | Yes | — |
| 4 | UsageDeleter | `deleteUsageBillingPeriodItems` | Yes | — |
| 5 | UsageDeleter | `deleteEntitlements` | Yes | — |
| 6 | BindingDeleter | `deleteAll` | Yes | — |
| 7 | UsageDeleter | `deleteTransactionJournals` | Yes | — |
| 8 | BillingDeleter | `deleteBillingScheduleGroups` | Yes | — |
| 9 | BillingDeleter | `deleteInvoices` | Conditional | `DeleteBilling` |
| 10 | OrderDeleter | `deleteFulfillment` | Conditional | `DeleteFulfillment` |
| 11 | OrderDeleter | `deleteOrders` | Conditional | `DeleteOrders` |
| 12 | BillingDeleter | `deleteContracts` | Conditional | `DeleteContracts` |
| 13 | AssetDeleter | `deleteAll` | Conditional | `DeleteAssets` |
| 14 | CrmDeleter | `deleteQuotes` | Conditional | `DeleteQuotes` |
| 15 | CrmDeleter | `deleteOpportunities` | Conditional | `DeleteOpportunities` |

### Restrict-Delete Dependencies

These are **platform-enforced** constraints. The parent cannot be deleted while any child exists.

#### Asset children
| Child Object | Field | Handled by |
|-------------|-------|------------|
| TransactionUsageEntitlement | AssetId, GrantBindingTargetId | UsageDeleter |
| UsageEntitlementAccount | GrantBindingTargetId | UsageDeleter |
| UsageBillingPeriodItem | AssetId, GrantBindingTargetId, UsageEntitlementBucketId | UsageDeleter |
| UsageRatableSummary | AssetId, GrantBindingTargetId, UsageEntitlementBucketId | UsageDeleter |
| UsageSummary | AssetId, GrantBindingTargetId, UsageEntitlementBucketId | UsageDeleter |
| UsageRatableSumCmtAssetRt | CommitmentAssetId | UsageDeleter |
| BindingObjUsageRsrcPlcy | BindingObjectId | BindingDeleter |
| BindingObjectRateCardEntry | SourceAssetId | BindingDeleter |
| AssetRateCardEntry | BindingObjectId | BindingDeleter |
| AssetRelationship | AssetId, RelatedAssetId | AssetDeleter |
| TransactionJournal | ReferenceRecordId | UsageDeleter (via AccountId) |
| UsageCmtAssetRelatedObj | AssetId, RelatedObjectId | AssetDeleter |
| RecordAlert | ParentId, WhatId | AssetDeleter / BillingDeleter |
| Case | AssetId | AssetDeleter |

#### UEB children (must delete before UsageEntitlementBucket)
| Child Object | Field |
|-------------|-------|
| UsageEntitlementBucket | ParentId (self-referential) |
| UsageBillingPeriodItem | UsageEntitlementBucketId |
| UsageRatableSummary | UsageEntitlementBucketId |
| UsageSummary | UsageEntitlementBucketId |

#### UBPI children (must delete before UsageBillingPeriodItem)
| Child Object | Field |
|-------------|-------|
| UsageSummary | UsageBillingPeriodItemId |

#### TUE children (must delete before TransactionUsageEntitlement)
| Child Object | Field |
|-------------|-------|
| UsageEntitlementBucket | TransactionUsageEntitlementId |

#### UEA children (must delete before UsageEntitlementAccount)
| Child Object | Field |
|-------------|-------|
| UsageEntitlementBucket | ParentId |

#### Contract children
| Child Object | Field | Handled by |
|-------------|-------|------------|
| PriceAdjustmentSchedule | ContractId | BillingDeleter |
| RecordAlert | ParentId, WhatId | BillingDeleter |
| BindingObjUsageRsrcPlcy | BindingObjectId | BindingDeleter |
| BindingObjectRateCardEntry | BindingObjectId | BindingDeleter |

#### Order children
| Child Object | Field | Handled by |
|-------------|-------|------------|
| Order | OriginalOrderId (self-ref) | OrderDeleter (nullified before delete) |
| Order | RelatedOrderId (self-ref) | OrderDeleter (nullified before delete) |
| OrderSummaryRelationship | MainAttachedToId | OrderDeleter |

### Account Reset Flow Integration

The `RLM_Utils_AccountReset` flow invokes the Apex action. It presents a screen with boolean toggles for each flag, all defaulting to `true`, and passes them as `inputParameters` to the `RLM_Utils_AccountReset` Apex action. After the reset, it refreshes PricingDiscovery decision tables via a subflow.

### Known Limitations

1. **Savepoint rollback** — The orchestrator wraps all deletions in a savepoint. If any step throws an unhandled exception, ALL deletions roll back. Individual delete steps use `Database.delete(records, false)` (allOrNone=false), so partial failures within a step won't cause rollback — only uncaught exceptions will.

2. **Governor limits** — Large accounts with thousands of related records may approach SOQL query limits (100 queries) or DML row limits (10,000 rows). The usage summary deletions query by multiple fields (AccountId, AssetId, GrantBindingTargetId, UsageEntitlementBucketId) to be thorough, which uses more queries.

3. **UEB hierarchy depth** — The bottom-up bucket deletion loop is capped at 10 rounds. Hierarchies deeper than 10 levels will leave orphaned buckets.

4. **Invoice filter** — Only Draft invoices are deleted. Posted/finalized invoices are preserved.

### Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `DELETE_FAILED: entity is associated with TransactionUsageEntitlement` | TUE records still reference the Asset via AssetId or GrantBindingTargetId | Ensure usage summaries are deleted first (they block UEB deletion, which blocks TUE deletion) |
| `DELETE_FAILED: entity is associated with UsageEntitlementAccount` | UEA records reference the Asset via GrantBindingTargetId | The refactored code now queries by GrantBindingTargetId instead of the non-existent AssetId |
| `DELETE_FAILED: entity is associated with UsageBillingPeriodItem` | UBPI records reference UEB or Asset | Usage summaries must be deleted before UEBs and before Assets |
| `FIELD_INTEGRITY_EXCEPTION on Order` | Order self-references (OriginalOrderId/RelatedOrderId) | The refactored code nullifies these fields before deletion |
| `DELETE_FAILED: PriceAdjustmentSchedule` on Contract | PAS records restrict-delete on Contract | The refactored code deletes PAS before Contracts |

---

## Asset Action Validator

Validates whether assets are eligible for lifecycle actions (Swap, Upgrade, Downgrade, Transfer, Rollback) before the user proceeds. Implemented as an `@InvocableMethod` Apex class called by the `RLM_ARC_Assets` flow.

### Salesforce Documented Limitations

The following limitations are documented by Salesforce for Release 260 (Spring '26). These constraints may be relaxed in future releases.

#### Swap, Upgrade, and Downgrade

- You can't swap, upgrade, or downgrade **ramped** or group ramp assets.
- You can't swap, upgrade, or downgrade **usage-based** assets.
- You can't swap, upgrade, or downgrade **expired** assets.
- You can't swap, upgrade, or downgrade **derived-price** products.
- The swaps feature isn't compatible with Dynamic Revenue Orchestration (DRO).
- You can't roll back swap transactions.

#### Transfer

- You can't transfer **ramped** assets.
- You can't transfer **usage-based** products.
- You can't transfer an **expired** asset.
- Asset Transfer supports a maximum of 50 line items per transaction.
- You can't reconfigure bundles or change product attributes during a transfer.
- You can't use different price books for a transfer.
- The Transfer API is synchronous. Any issue during processing reverts the entire transaction.
- If you adjust the transfer quantity on one quote or order, you must manually update the corresponding quantity on the other destination quote or order.

#### Rollback

- Rollbacks for asset transactions involving **ramps** aren't supported.
- Rollbacks for asset transactions involving **usage-based** products aren't supported.
- Rollbacks for Salesforce Billing and DRO features aren't supported.
- You can only roll back future-dated transactions that haven't started. If the start date of the last transaction is in the past or today, it can't be rolled back.
- Partial rollback of a transaction isn't supported.
- Assets created before the 258 release can't be rolled back.
- You can't roll back a rollback transaction.
- The rollback action always applies to the most recent (last) transaction. Multiple rollbacks undo transactions sequentially.
- Rollback of an initial sale, cancellation, or transfer transaction isn't supported.

### Validation Matrix

The validator checks four conditions. Each blocks a different set of actions:

| Condition | Swap / Upgrade / Downgrade | Transfer | Rollback |
|-----------|:-:|:-:|:-:|
| Ramped assets | Blocked | Blocked | Blocked |
| Usage-based assets | Blocked | Blocked | Blocked |
| Expired assets | Blocked | Blocked | -- |
| Derived-price products | Blocked | -- | -- |

**Not yet automated** (enforced server-side by Salesforce, not in the validator):
- DRO incompatibility (Swap, Rollback)
- Transfer 50 line-item limit
- Rollback of non-future-dated, initial sale, cancellation, transfer, or rollback transactions
- Pre-258 asset rollback restriction

### RLM_ARC_AssetValidator (Apex)

**File:** `unpackaged/post_utils/classes/RLM_ARC_AssetValidator.cls`

#### How It Works

1. **Expand** — The input asset IDs are expanded to include related assets found via `AssetRelationship` (queried in both directions). This ensures bundle components and linked assets are also validated.

2. **Query** — Four validation checks run as bulk SOQL queries across all expanded assets:
   - Ramped assets
   - Expired assets
   - Usage-based assets
   - Derived-price products

3. **Map** — Results are intersected back to each request's asset set, producing boolean flags and ID lists per request.

#### Detection Methods

| Condition | Detection Query | Key Field |
|-----------|----------------|-----------|
| Ramped | `AssetStatePeriod WHERE AssetId IN :ids AND RampIdentifier != NULL` | `AssetStatePeriod.RampIdentifier` |
| Expired | `Asset WHERE Id IN :ids AND LifecycleEndDate < TODAY` | `Asset.LifecycleEndDate` |
| Usage-based | `Asset` -> `Product2Id` -> `ProductUsageResource WHERE Status = 'Active'` | `ProductUsageResource.Status` |
| Derived-price | `Asset` -> `Product2Id` -> `PricebookEntry WHERE IsDerived = true` | `PricebookEntry.IsDerived` |

The usage-based and derived-price checks share a single `Asset` query to build a `Product2Id -> Set<Asset Id>` map, avoiding a redundant SOQL call.

#### Inputs and Outputs

**Request (input):**

| Field | Type | Description |
|-------|------|-------------|
| `recordIds` | `List<Id>` | Asset record IDs to validate (required) |

**Result (output):**

| Field | Type | Description |
|-------|------|-------------|
| `hasRampedAssets` | `Boolean` | True if any asset (or related asset) has ramp pricing |
| `hasUsageBasedAssets` | `Boolean` | True if any asset's product has active usage resources |
| `hasExpiredAssets` | `Boolean` | True if any asset's `LifecycleEndDate` is in the past |
| `hasDerivedPriceAssets` | `Boolean` | True if any asset's product has a derived PricebookEntry |
| `rampedAssetIds` | `List<Id>` | IDs of ramped assets |
| `usageBasedAssetIds` | `List<Id>` | IDs of usage-based assets |
| `expiredAssetIds` | `List<Id>` | IDs of expired assets |
| `derivedPriceAssetIds` | `List<Id>` | IDs of derived-price assets |
| `swapBlockedMessage` | `String` | Dynamic error message for Swap/Upgrade/Downgrade (null if allowed) |
| `transferBlockedMessage` | `String` | Dynamic error message for Transfer (null if allowed) |
| `rollbackBlockedMessage` | `String` | Dynamic error message for Rollback (null if allowed) |

The message fields list the exact blocking conditions with counts, e.g.:
> "This action can't be completed. The selected assets include ramped (2), expired (1) assets that don't support swap, upgrade, or downgrade. Remove the affected assets and try again."

#### SOQL Budget

The validator uses a fixed number of SOQL queries regardless of input size:

| # | Query | Purpose |
|---|-------|---------|
| 1 | `AssetRelationship` | Expand input IDs with related assets |
| 2 | `AssetStatePeriod` | Detect ramped assets |
| 3 | `Asset` (by Id, for LifecycleEndDate) | Detect expired assets |
| 4 | `Asset` (by Id, for Product2Id) | Build product-to-asset map |
| 5 | `ProductUsageResource` | Detect usage-based assets |
| 6 | `PricebookEntry` | Detect derived-price assets |

**Total: 6 SOQL queries** (constant, not proportional to input size).

#### Security Model

The class uses `without sharing` intentionally. The validator must see all related assets regardless of the running user's record access to produce accurate results. No record data is returned to the caller — only boolean flags and ID lists.

### RLM_ARC_Assets Flow

**File:** `unpackaged/post_utils/flows/RLM_ARC_Assets.flow-meta.xml`
**Template:** `runtime_revenue_arcflows__arcFlow`

A screen flow that handles all Asset Relationship Center (ARC) lifecycle actions. It is invoked from Asset record pages and receives asset IDs, action type, and configuration parameters as input.

**Supported action types:** Amend, Renew, Cancel, Transfer, Rollback, Swap (with Upgrade and Downgrade subtypes).

#### Validation Gates

The flow calls `RLM_ARC_AssetValidator` (via the `Check_Assets_for_Usage_or_Ramps` action call) at the very start, before routing to any action. Three validation gates use the results:

**1. Swap / Upgrade / Downgrade Gate**

Location: `Resolve_Action_From_Flow_Entry` decision, `Swap_From_Flow_Entry` rule. Requires `hasRampedAssets`, `hasUsageBasedAssets`, `hasExpiredAssets`, and `hasDerivedPriceAssets` to all be `false`. If the action is `Swap` but any condition is `true`, routes to `Set_Swap_Blocked_Error` -> `error` screen.

**2. Transfer Gate**

Location: `Validate_Transfer_Assets` decision. Requires `hasRampedAssets`, `hasUsageBasedAssets`, and `hasExpiredAssets` to all be `false`. If any is `true`, routes to `Set_Transfer_Blocked_Error` -> `error` screen.

**3. Rollback Gate**

Location: `Validate_Rollback_Assets` decision. Requires `hasRampedAssets` and `hasUsageBasedAssets` to all be `false`. If any is `true`, routes to `Set_Rollback_Blocked_Error` -> `error` screen.

#### Flow Path Diagram

```
Start
  |
  v
Check_Assets_for_Usage_or_Ramps (Apex: RLM_ARC_AssetValidator)
  |
  v
Resolve_Action_From_Flow_Entry (Decision)
  |
  |-- Amend -----> Set_actionTypeNoun_to_Amendment -> Amend_or_Renew_From_Account_or_Contract -> ...
  |-- Renew -----> Set_actionTypeNoun_to_Renewal   -> Amend_or_Renew_From_Account_or_Contract -> ...
  |-- Cancel ----> Set_actionTypeNoun_to_Cancellation -> Cancel_From_Account_Or_Contract -> ...
  |-- Transfer --> Set_actionTypeNoun_to_Transfer  -> Validate_Transfer_Assets (Decision)
  |                                                     |-- Valid ----> Transfer_Selector_Screen -> ...
  |                                                     |-- Blocked -> Set_Transfer_Blocked_Error -> error
  |-- Rollback --> Set_actionTypeNoun_to_Rollback  -> Validate_Rollback_Assets (Decision)
  |                                                     |-- Valid ----> Rollback_Last_Action -> ...
  |                                                     |-- Blocked -> Set_Rollback_Blocked_Error -> error
  |-- Swap (all checks pass) -> Effective_Date_selector_screen -> Swap_from_Account_or_Contract -> ...
  |-- Swap (any check fails) -> Set_Swap_Blocked_Error -> error
  |-- Default (no action) ----> error
```

### Future Considerations

These items are enforced server-side by Salesforce but are **not** currently validated in the flow or Apex class. Revisit when upgrading beyond Release 260:

| Limitation | Action | Notes |
|-----------|--------|-------|
| DRO incompatibility | Swap, Rollback | No reliable client-side detection method identified yet |
| 50 line-item limit | Transfer | Could be added as a count check on `recordIds.size()` but related-asset expansion complicates the count |
| Future-dated transactions only | Rollback | Requires querying `AssetAction` for the last transaction's start date |
| Pre-258 asset restriction | Rollback | No standard field indicates the release under which an asset was created |
| Can't rollback initial sale, cancellation, transfer, or rollback | Rollback | Requires querying `AssetAction.Type` for the most recent transaction |
| Salesforce Billing incompatibility | Rollback | Requires checking if Billing is enabled and assets have billing records |

If Salesforce lifts any of the current restrictions (ramped, usage-based, expired, derived-price), update the validator and flow validation gates accordingly.

---

## Permission Set

**`RC_Utilities`** (`permissionsets/RC_Utilities.permissionset-meta.xml`) grants access to:
- Apex classes: `RLM_Utils_AccountReset`, `RLM_ARC_AssetValidator`
- Flows: `RLM_Utils_AccountReset`, `RLM_ARC_Assets`
- Custom fields on `TransactionJournal`, `UsageBillingPeriodItem`, `UsageSummary`
