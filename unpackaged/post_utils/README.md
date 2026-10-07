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
| Flow `RLM_CreateContractFromQuote` | Quick-action: creates a contract from a quote (rolling back the transaction if creating or updating it faults); sets the contract term from the contract start date to the end of the quote's last-ending term-defined line, and the renewal term to that length divided by the pricing term of the first such line by line number (a deterministic tie-break when several lines end on the same date) (`PricingTerm` × `PricingTermUnit`; Weekly uses the day span), rounded to the nearest whole term (renewal reads `RenewalTerm2` as a count of the selling model's pricing term) |
| Flow `RLM_QuickQuote` + QuickAction `Account.RLM_QuickQuote` | Quick-action: creates a quote directly from an account |
| Flow `RLM_CreateQuoteFromRenewalOpp` + QuickAction `Opportunity.RLM_CreateQuoteFromRenewalOpp` | Quick-action ("Generate Renewal Quote"): renews the root assets of a renewal opportunity's lines (`OpportunityLineItem.AssetId` → `Asset.RootAssetId`, deduped) via the standard Initiate Renewal action and links the quote to the opportunity and, when set, its contract. Placed on `RLM_Opportunity_Record_Page` by the `utils` flexipage patch, visible only on open opportunities with Type Existing Business; the flow checks the same rule, so a won renewal can't be renewed twice. If the user can't read every line asset, it stops with a count of the missing ones instead of quoting a partial renewal; reading `OpportunityLineItem.AssetId` needs the `RLM_QuantumBit` read grant |
| Flow `RLM_ConsolidateRenewalOpportunities` + subflow `RLM_RenewalCoveredAssets` + QuickAction `Opportunity.RLM_ConsolidateRenewalOpportunities` | Quick-action ("Consolidate Renewals"): merges other open renewal opportunities on the same account (same price book and currency, picked from a list) into this one. When the account has renewable root assets (lifecycle-managed, active, not yet ended, same currency) that no open renewal opportunity covers, either on its lines or on its quotes' Renew quote actions, a checkbox adds them too. Coverage is read by the autolaunched subflow `RLM_RenewalCoveredAssets`, which runs in system context without sharing, is given the root assets the user already read, and returns only those that are covered (a covered bundle component marks its root covered), never an Id found in system context, so a renewal the user can't see still counts (passing no contract, since they may not belong to it). Renews the root assets of all their lines, and of the assets their quotes' Renew quote actions name (a consolidated quote isn't synced, so the assets it absorbed are on no line), onto one quote linked to this opportunity, cotermed to the last second (GMT) of an end date the user picks, which must fall after the latest asset ends (default one year after the latest asset ends), then closes the others as Closed Lost with a note in Description, re-read after the confirmation screen so their current Description is kept. Initiate Renewal takes one start date per call, so it is called once per asset end date and time, each starting the second after those assets end (computed from the end datetime, so it doesn't depend on the user's time zone), the first call creating the quote and later ones adding to it through `renewRecordId`; the contract is passed only when every opportunity shares it and it links every root asset (`AssetContractRelationship`; a relationship that has ended or not yet started still counts, as Initiate Renewal accepts it: the renewal reads the term from the asset, so it never needs a current relationship to copy the contract's term). Stops before quoting if the user can't read every line asset or every root asset, if a selected opportunity has a line linked to no asset (closing it would drop that product), if a selected opportunity or this one was closed or no longer matches (account, price book, currency) by the time the user confirms (after confirmation the coverage, opportunities, lines, quote actions, root assets, end dates and contract are all read again, and nothing is renewed unless the root assets, latest end date and contract still match what was confirmed), or if a root asset has no end date, ends too early for its renewal, which starts the second after it ends, to start today or later in GMT (a renewal can't start in the past), or has no Renewal Term and Renewal Term Unit (explicit dates read the term from the asset even when a contract is passed). Placed next to Generate Renewal Quote by the same `utils` flexipage patch and visibility rule. Ramped assets can't be cotermed |
| Flow `RLM_SyncRenewalQuoteOnOrderActivation` | Order after-save (async): when an order created from a quote activates, calls the standard `syncQuoteOpportunity` action for the quote's open opportunity, whatever its type. An opportunity with no synced quote is first set to sync with this quote; one that syncs with a different quote is left unchanged. The adopt step writes only while the opportunity still has no synced quote, and the flow rechecks the synced quote just before it syncs. Needs **Asynchronous Opportunity Sync** on in Revenue Settings, which this bundle turns on (`settings/RevenueManagement.settings-meta.xml`, `enableAsynchronousQuoteOpportunitySync`). If setting the synced quote faults, or the action faults or returns `isSuccess` false, it creates a high-priority task on the opportunity for its owner with the error, and the opportunity stays open |
| Flow `RLM_CloseRenewalOpportunityOnQuoteSync` | `QuoteToOpportunitySyncEvent` subscriber: when a sync succeeds, the quote has an activated order and none of its orders is still a draft, sets its open opportunity to Closed Won, whatever its type, if the opportunity still syncs with that quote, so a renewal just won doesn't stay open beside the next-term renewal opportunity; a quote split into several orders closes the opportunity only when the last one activates. When the background sync fails for a quote with an activated order, it leaves the opportunity open and creates a high-priority task for its owner with the event's error code and message |
| Flow `RLM_Event_Trigger` | Generic event trigger utility |
| Flow `RLM_Refresh_Decision_Tables_Bulk` | Bulk decision table refresh |
| Flow `RLM_Refresh_Decision_Tables_By_Usage_Type` | Decision table refresh filtered by usage type (called by account reset) |
| `RLM_Build_Info__mdt` | Custom metadata recording build provenance (branch, commit, timestamp, flags) |
| Settings `RevenueManagement` | Turns on Asynchronous Opportunity Sync (`enableAsynchronousQuoteOpportunitySync`), which the standard `syncQuoteOpportunity` action requires |
| `RLM_SessionId` (VF page) | Exposes session ID for tooling integrations |
