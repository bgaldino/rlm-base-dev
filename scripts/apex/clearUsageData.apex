// Clear the high-volume usage records for an org (or one account).
//
// WHY THIS EXISTS: RLM_AccountUtilities.delAccountRelatedObjects is structurally
// over the 100-SOQL governor limit -- it fails with "Too many SOQL queries: 101"
// on ANY account that has assets, not merely on ones with a long history. Until
// that is refactored, run this first; it drains the usage graph in a fixed, small
// number of queries so the reset utility has far less to walk.
//
// It is also the only way to remove two objects the reset utility does not touch
// at all:
//   * UsageEntitlementEntry -- holds a rated UsageSummary ("associated with the
//     following usage entitlement entries"), so any account whose usage reached
//     LiableSummaryComplete cannot be reset without deleting these first.
//   * AssetRateCardEntry    -- references the design-time RateCardEntry rows, so
//     leaving them behind is why reloading qb-rates against an org with live
//     assets inserts a second Draft copy of every entry instead of replacing the
//     Active ones.
//
// DELETION ORDER IS NOT THE OBVIOUS CHILD-FIRST GUESS. A UsageRatableSummary
// cannot be deleted while an associated UsageSummary exists, and some
// UsageSummary rows are in turn held by ratable rows. Rather than hard-code an
// order a future release can invert, this alternates the objects and stops when
// a full round makes no progress.
//
// Scope: set ACCOUNT_NAME to limit to one account, or leave blank for the whole
// org (the usual case on a scratch org being reset between demo runs).

final String ACCOUNT_NAME = '';        // '' = every account
final Integer MAX_ROUNDS = 6;
final Integer BATCH = 10000;

Set<Id> assetIds = new Set<Id>();
Id accountId = null;
if (String.isNotBlank(ACCOUNT_NAME)) {
    List<Account> accts = [SELECT Id FROM Account WHERE Name = :ACCOUNT_NAME LIMIT 1];
    if (accts.isEmpty()) {
        throw new IllegalArgumentException('No account named ' + ACCOUNT_NAME);
    }
    accountId = accts[0].Id;
    for (Asset a : [SELECT Id FROM Asset WHERE AccountId = :accountId]) { assetIds.add(a.Id); }
}
Boolean scoped = (accountId != null);

Integer q0 = Limits.getQueries();
Integer uee = 0, ubpi = 0, us = 0, urs = 0;

for (Integer round = 1; round <= MAX_ROUNDS; round++) {
    Integer progress = 0;

    List<UsageEntitlementEntry> entries = scoped
        ? [SELECT Id FROM UsageEntitlementEntry
           WHERE TransactionUsageEntitlement.Account.Id = :accountId LIMIT :BATCH]
        : [SELECT Id FROM UsageEntitlementEntry LIMIT :BATCH];
    for (Database.DeleteResult r : Database.delete(entries, false)) {
        if (r.isSuccess()) { uee++; progress++; }
    }

    // Inside the loop on purpose: UBPI is blocked by its summaries too, so
    // deleting it once up front strands rows behind summaries that only become
    // deletable on a later round.
    List<UsageBillingPeriodItem> items = scoped
        ? [SELECT Id FROM UsageBillingPeriodItem
           WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :BATCH]
        : [SELECT Id FROM UsageBillingPeriodItem LIMIT :BATCH];
    for (Database.DeleteResult r : Database.delete(items, false)) {
        if (r.isSuccess()) { ubpi++; progress++; }
    }

    List<UsageSummary> summaries = scoped
        ? [SELECT Id FROM UsageSummary
           WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :BATCH]
        : [SELECT Id FROM UsageSummary LIMIT :BATCH];
    for (Database.DeleteResult r : Database.delete(summaries, false)) {
        if (r.isSuccess()) { us++; progress++; }
    }

    List<UsageRatableSummary> ratable = scoped
        ? [SELECT Id FROM UsageRatableSummary
           WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :BATCH]
        : [SELECT Id FROM UsageRatableSummary LIMIT :BATCH];
    for (Database.DeleteResult r : Database.delete(ratable, false)) {
        if (r.isSuccess()) { urs++; progress++; }
    }

    System.debug('CLEAR: round ' + round + ' removed ' + progress + ' record(s)');
    if (progress == 0) { break; }
}

Integer arce = 0;
List<AssetRateCardEntry> arces = scoped
    ? [SELECT Id FROM AssetRateCardEntry WHERE Asset.AccountId = :accountId LIMIT :BATCH]
    : [SELECT Id FROM AssetRateCardEntry LIMIT :BATCH];
for (Database.DeleteResult r : Database.delete(arces, false)) { if (r.isSuccess()) arce++; }

Integer tj = 0;
List<TransactionJournal> journals = scoped
    ? [SELECT Id FROM TransactionJournal WHERE AccountId = :accountId LIMIT :BATCH]
    : [SELECT Id FROM TransactionJournal LIMIT :BATCH];
for (Database.DeleteResult r : Database.delete(journals, false)) { if (r.isSuccess()) tj++; }

System.debug('CLEAR: entitlementEntries=' + uee + ' billingPeriodItems=' + ubpi
    + ' summaries=' + us + ' ratable=' + urs + ' assetRateCardEntries=' + arce
    + ' journals=' + tj);
System.debug('CLEAR: remaining -- entries=' + [SELECT COUNT() FROM UsageEntitlementEntry]
    + ' summaries=' + [SELECT COUNT() FROM UsageSummary]
    + ' ratable=' + [SELECT COUNT() FROM UsageRatableSummary]
    + ' arce=' + [SELECT COUNT() FROM AssetRateCardEntry]
    + ' journals=' + [SELECT COUNT() FROM TransactionJournal]);
System.debug('CLEAR: SOQL used = ' + (Limits.getQueries() - q0) + ' of 100');
