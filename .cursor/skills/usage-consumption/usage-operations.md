# Usage Consumption - Operating, Resetting and Reading Usage

Day-2 facts for people running a metered build: who may reset an account, what blocks a delete,
what the usage dashboard shows, and what is still unconfirmed. Build steps are in
[building-usage-assets.md](building-usage-assets.md); checks are in [verification.md](verification.md).
Tag meaning: Measured is a run on an org; Help is a captured article; Open is unconfirmed.

## Who may reset an account

The in-org reset (`RLM_AccountUtilities`, the Reset Account quick action) is for administrators
and demos, POCs and testing. A user without Modify All Data and View All Data is refused before
anything is read, with a message that nothing was changed [Repo: unpackaged/post_utils/classes/RLM_AccountUtilities.cls].
[Measured: 2026-11-26, 264, scratch, one org] An admin lacking Customize Application completes the
reset, but the decision-table refresh that follows a reset is not queued for that user.
The sales-rep persona does not carry `RLM_UtilitiesPermset` [Repo: cumulusci.yml]; the permission set is assigned to the running admin [Repo: unpackaged/post_utils/README.md].

## What blocks a delete

[Measured: 2026-11-26, 264, scratch, one org] Each of these refuses the delete until the blocker is
removed first:
- A `TransactionUsageEntitlement` whose order line is on another account's order blocks deleting
  that line and order.
- A `BindingObjectRateCardEntry` whose `SourceAssetId` is an asset blocks that asset's delete, even
  when the entry is bound to a contract that is kept.
- A `RecordAlert` on a `TransactionJournal` blocks the journal's delete; delete the alerts first.
- `UsageCmtAssetRelatedObj`, the commitment junction, blocks only the anchor asset's delete.
  Deleting the commitment asset succeeds and takes the junction with it.
[Measured: 2026-11-26, 264, scratch, one org] `UsageRatableSumCmtAssetRt` is deleted with its
`UsageRatableSummary`. `BillingPeriodItem.RelatedUsageBillPeriodItemId` was judged non-blocking from
the describe only [Open: not measured; no billing period item could be inserted].
`UsageEntitlementEntry` deletion was not measured, an insert raised an internal platform error
[Open: not measured].
A junction is accepted only on commitment products the org has already set up; a junction on assets
with no product raises an internal error [Measured: 2026-11-26, 264, scratch, one org]. A delete list
that holds the same Id twice fails both rows with "Duplicate id in list" [Measured: 2026-11-26, 264,
scratch, one org].

## Reading usage in the UI

The Unified Usage Dashboard has Usage Details, Grants, Policies, Rates, Wallet, Related and Wallet
Statement tabs, and it is where wallet balances, overages and the winning rate are checked after
assetization and entitlement [Help: ind.um_track_usage_with_unified_dashboard]. Where the
dashboard is placed on a record page, and the overage field behind its display (reported as
`UsageSummary.OverageUnits` per contract), are [Open: placement not measured; field name from a
customer report, not confirmed]. The Consumption Traceabilities and Get Usage Details APIs are
the read route for per-asset detail [Open: request and response shapes not verified here].

## Units and late usage

Whether summarization and rating convert units is [Open: reported as none; until measured, record
journals in the usage resource's default unit]. How late usage for a period that is already billed
is rated and billed is [Open: not measured; rate on a disposable account before promising a
credit or a rebill].

## Grants on amendment

Quantity change and early cancellation recalculate grants [Help: ind.qocal_amending_rates_and_grants_on_usage_based_products].
The bill-day gate on the 264 proration, the 266 admin policy for it, and whether pack grants are
prorated are [Open: the proration article is not in the 264 snapshot; measure on a build]. Per-line grant
overrides on a quote (the quote line usage resource grant path) are [Open: not measured; the
validity edit is reported off in the line editor panel].
