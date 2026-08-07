# Account & Demo Utilities

This bundle ships demo-support utilities deployed via `deploy_post_utils` in both the `quantumbit` and `tso` flows. It provides account reset, decision table management, expression set management, search index rebuild, usage data tools, and quick-action shortcuts.

## Account Reset

The primary utility: a screen flow + Apex invocable that deletes transactional data from an account so it can be reused for demos without re-creating it.

**Entry point:** QuickAction `Account.RLM_Reset_Account` → Flow `RLM_Account_Utilities` → Apex `RLM_AccountUtilities.delAccountRelatedObjects`

### Flow screen options

| Option | Default | Behavior |
|--------|---------|----------|
| Delete Assets | true | Removes assets, asset relationships, and asset rate card entries. The broader usage teardown runs regardless of this option. |
| Delete Fulfillment | true | Removes fulfillment orders, line items, plans, and decomposition records |
| Delete Billing | true | Removes invoices |
| Preserve Contracts with Contracted Prices | false | When checked, contracts that have at least one `ContractItemPrice` child are kept; contracts without contracted prices are still deleted |

All resets delete usage policies, binding object rate card entries, usage summaries, entitlements, buckets, transaction journals, orders, quotes, opportunities, and billing schedule groups regardless of the flags above.

### Deletion order

The reset runs in two phases:

1. **Pre-savepoint (convergent):** Usage resource policies, binding object rate card entries, and the usage summary graph are always processed; asset rate card entries are processed only when **Delete Assets** is enabled. These operations are idempotent, so partial progress survives a later failure.
2. **Transactional (savepoint-wrapped):** Entitlements, journals, billing, fulfillment, contracts, orders, assets, quotes, and opportunities. A thrown exception rolls back this phase. Some existing helpers use partial-success DML, so an individual row failure can leave records for a subsequent reset without triggering rollback.

The reset is designed for convergence: if it hits the DML row budget during the usage teardown, it stops and the next run resumes from the smaller graph.

### Permission set

`RLM_UtilitiesPermset` grants access to the `RLM_AccountUtilities` Apex class. Assigned in both `quantumbit` and `tso` flows, and to the salesrep persona in `prepare_personas`.

## Other components

| Component | Purpose |
|-----------|---------|
| `RLM_DecisionTableManagerController` + LWC `rlmDecisionTableManager` | UI for bulk decision table refresh |
| `RLM_ExpressionSetManagerController` + LWC `rlmExpressionSetManager` | UI for expression set activation/management |
| `RLM_RebuildSearchIndex` + LWC `rlmRebuildSearchIndex` | Triggers search index rebuild |
| `RLM_UsageDataController` + LWC `rlmUsageDataTable` | Displays usage data (summaries, journals, billing period items) |
| `RLM_UsageOrchestrationController` + LWC `rlmUsageOrchestration` | Usage event orchestration UI |
| `RLM_UsageUploaderController` + LWC `rlmUsageUploader` | Bulk usage event upload |
| `RLM_ARC_AssetValidator` + Flow `RLM_ARC_Assets` | Asset lifecycle validation for ARC (Amend/Renew/Cancel) |
| Flow `RLM_CreateContractFromQuote` | Quick-action: creates a contract from a quote |
| Flow `RLM_QuickQuote` + QuickAction `Account.RLM_QuickQuote` | Quick-action: creates a quote directly from an account |
| Flow `RLM_Event_Trigger` | Generic event trigger utility |
| Flow `RLM_Refresh_Decision_Tables_Bulk` | Bulk decision table refresh |
| Flow `RLM_Refresh_Decision_Tables_By_Usage_Type` | Decision table refresh filtered by usage type (called by account reset) |
| `RLM_Build_Info__mdt` | Custom metadata recording build provenance (branch, commit, timestamp, flags) |
| `RLM_SessionId` (VF page) | Exposes session ID for tooling integrations |
