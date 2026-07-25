// Clear the high-volume usage records for an org (or one account).
//
// WHEN TO USE THIS vs RLM_AccountUtilities:
//   * This script  -- ORG-WIDE, usage-only. Drains the whole usage graph across
//     every account in a fixed, small number of queries. The right tool for
//     resetting a scratch org between demo runs, and for clearing usage without
//     touching orders, quotes, assets or opportunities.
//   * RLM_AccountUtilities.delAccountRelatedObjects -- PER-ACCOUNT, full reset.
//     Removes the account's usage graph *and* its transactional records. That is
//     the in-org utility demo users run.
//
// The two now share the same teardown design: a convergent loop with a DML-row
// budget clamp. RLM_AccountUtilities also deletes UsageEntitlementEntry and
// AssetRateCardEntry, so this script is no longer required as a prerequisite for
// a per-account reset -- prefer it when the job is org-wide or usage-only.
//
// Two objects worth knowing about, because leaving them behind has non-obvious
// consequences:
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

// The 10,000-row DML limit is per TRANSACTION, not per statement. This script
// issues up to 26 deletes (4 per round x 6 rounds, plus 2 tail deletes), so a
// fixed per-statement cap of 10,000 would blow the limit in the first round.
// Each delete is therefore capped by the REMAINING budget, and the script stops
// cleanly and asks to be re-run when the budget is spent -- a partial drain that
// reports itself beats a LimitException that rolls the whole thing back.
final String ACCOUNT_NAME = '';        // '' = every account
final Integer MAX_ROUNDS = 6;
final Integer BATCH = 2000;            // per-statement ceiling, further clamped below
Boolean budgetSpent = false;

// ⚠ OFF BY DEFAULT. AssetRateCardEntry rows are created when the asset is created,
// and the entitlement process does NOT recreate them for an asset that already
// exists. Deleting them therefore leaves a rate-less asset that can never be rated
// again -- which breaks the documented "clear usage, keep the assets" path and is
// reported as a failure by validateMulticurrencyRates (an asset with no ARCE rows
// resolved no rates at all).
//
// Turn this ON only for a rate reload or a full reset where the assets are going
// away too: ARCEs reference the design-time RateCardEntry rows, so leaving them
// behind is why reloading qb-rates against an org with live assets inserts a
// second Draft copy of every entry instead of replacing the Active ones.
final Boolean DELETE_ASSET_RATE_CARD_ENTRIES = false;

// Deletes and REPORTS. A discarded DeleteResult is the reason a stalled round is
// undiagnosable: the row that refused is exactly the relationship still holding
// the graph, and it later resurfaces as an unexplained failure on the asset.
// Logged at the default level on purpose -- LoggingLevel.FINE is hidden by the
// default log level, which is how these stayed invisible before.
// Mirrors RLM_AccountUtilities.deleteQuietly(); see .cursor/rules/apex-scripts.mdc.
// NB: instance method, not static -- anonymous Apex treats a declared class as an
// inner type and rejects "static can only be used on methods of a top level type".
public class Drain {
    public Integer run(List<SObject> records, String label) {
        if (records == null || records.isEmpty()) { return 0; }
        Integer removed = 0;
        for (Database.DeleteResult r : Database.delete(records, false)) {
            if (r.isSuccess()) {
                removed++;
            } else {
                for (Database.Error e : r.getErrors()) {
                    System.debug('CLEAR blocked (' + label + '): ' + e.getMessage());
                }
            }
        }
        return removed;
    }
}

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
Drain drain = new Drain();

Integer q0 = Limits.getQueries();
Integer uee = 0, ubpi = 0, us = 0, urs = 0;

Integer take = 0;

for (Integer round = 1; round <= MAX_ROUNDS && !budgetSpent; round++) {
    Integer progress = 0;

    take = Math.min(BATCH, Limits.getLimitDmlRows() - Limits.getDmlRows());
    if (take <= 0) { budgetSpent = true; break; }
    List<UsageEntitlementEntry> entries = scoped
        ? [SELECT Id FROM UsageEntitlementEntry
           WHERE TransactionUsageEntitlement.Account.Id = :accountId LIMIT :take]
        : [SELECT Id FROM UsageEntitlementEntry LIMIT :take];
    Integer nEntries = drain.run(entries, 'UsageEntitlementEntry');
    uee += nEntries; progress += nEntries;

    // Inside the loop on purpose: UBPI is blocked by its summaries too, so
    // deleting it once up front strands rows behind summaries that only become
    // deletable on a later round.
    take = Math.min(BATCH, Limits.getLimitDmlRows() - Limits.getDmlRows());
    if (take <= 0) { budgetSpent = true; break; }
    List<UsageBillingPeriodItem> items = scoped
        ? [SELECT Id FROM UsageBillingPeriodItem
           WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :take]
        : [SELECT Id FROM UsageBillingPeriodItem LIMIT :take];
    Integer nItems = drain.run(items, 'UsageBillingPeriodItem');
    ubpi += nItems; progress += nItems;

    take = Math.min(BATCH, Limits.getLimitDmlRows() - Limits.getDmlRows());
    if (take <= 0) { budgetSpent = true; break; }
    List<UsageSummary> summaries = scoped
        ? [SELECT Id FROM UsageSummary
           WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :take]
        : [SELECT Id FROM UsageSummary LIMIT :take];
    Integer nSum = drain.run(summaries, 'UsageSummary');
    us += nSum; progress += nSum;

    take = Math.min(BATCH, Limits.getLimitDmlRows() - Limits.getDmlRows());
    if (take <= 0) { budgetSpent = true; break; }
    List<UsageRatableSummary> ratable = scoped
        ? [SELECT Id FROM UsageRatableSummary
           WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :take]
        : [SELECT Id FROM UsageRatableSummary LIMIT :take];
    Integer nRat = drain.run(ratable, 'UsageRatableSummary');
    urs += nRat; progress += nRat;

    System.debug('CLEAR: round ' + round + ' removed ' + progress + ' record(s)');
    if (progress == 0) { break; }
}

Integer arce = 0;
if (DELETE_ASSET_RATE_CARD_ENTRIES) {
    take = Math.min(BATCH, Limits.getLimitDmlRows() - Limits.getDmlRows());
    if (take > 0) {
        List<AssetRateCardEntry> arces = scoped
            ? [SELECT Id FROM AssetRateCardEntry WHERE Asset.AccountId = :accountId LIMIT :take]
            : [SELECT Id FROM AssetRateCardEntry LIMIT :take];
        arce = drain.run(arces, 'AssetRateCardEntry');
    } else { budgetSpent = true; }
} else {
    System.debug('CLEAR: AssetRateCardEntry PRESERVED (DELETE_ASSET_RATE_CARD_ENTRIES=false) '
        + '-- the assets keep their rates. Set it true only for a rate reload or a '
        + 'full reset where the assets are being removed too.');
}

Integer tj = 0;
take = Math.min(BATCH, Limits.getLimitDmlRows() - Limits.getDmlRows());
if (take > 0) {
    List<TransactionJournal> journals = scoped
        ? [SELECT Id FROM TransactionJournal WHERE AccountId = :accountId LIMIT :take]
        : [SELECT Id FROM TransactionJournal LIMIT :take];
    tj = drain.run(journals, 'TransactionJournal');
} else { budgetSpent = true; }

System.debug('CLEAR: entitlementEntries=' + uee + ' billingPeriodItems=' + ubpi
    + ' summaries=' + us + ' ratable=' + urs + ' assetRateCardEntries=' + arce
    + ' journals=' + tj);
// The remaining counts MUST use the same scope as the deletes. Reported org-wide
// after a per-account run, other accounts' rows make a complete cleanup look
// unfinished -- and the rerun-until-zero guidance below would then never be
// satisfiable.
// EVERY object this script deletes must appear here. An omitted one can survive
// blocked while all printed counts read zero, so the rerun-until-zero check below
// would report a false clean state -- UsageBillingPeriodItem was exactly that.
Integer remEntries, remUbpi, remSummaries, remRatable, remArce, remJournals;
if (scoped) {
    remEntries   = [SELECT COUNT() FROM UsageEntitlementEntry
                    WHERE TransactionUsageEntitlement.Account.Id = :accountId];
    remUbpi      = [SELECT COUNT() FROM UsageBillingPeriodItem
                    WHERE AccountId = :accountId OR AssetId IN :assetIds];
    remSummaries = [SELECT COUNT() FROM UsageSummary
                    WHERE AccountId = :accountId OR AssetId IN :assetIds];
    remRatable   = [SELECT COUNT() FROM UsageRatableSummary
                    WHERE AccountId = :accountId OR AssetId IN :assetIds];
    remArce      = [SELECT COUNT() FROM AssetRateCardEntry WHERE Asset.AccountId = :accountId];
    remJournals  = [SELECT COUNT() FROM TransactionJournal WHERE AccountId = :accountId];
} else {
    remEntries   = [SELECT COUNT() FROM UsageEntitlementEntry];
    remUbpi      = [SELECT COUNT() FROM UsageBillingPeriodItem];
    remSummaries = [SELECT COUNT() FROM UsageSummary];
    remRatable   = [SELECT COUNT() FROM UsageRatableSummary];
    remArce      = [SELECT COUNT() FROM AssetRateCardEntry];
    remJournals  = [SELECT COUNT() FROM TransactionJournal];
}
// arce is labelled "preserved" when the flag is off, so it is not read as an
// outstanding row the rerun-until-zero check below must drive to zero.
System.debug('CLEAR: remaining (' + (scoped ? 'account ' + ACCOUNT_NAME : 'org-wide')
    + ') -- entries=' + remEntries + ' billingPeriodItems=' + remUbpi
    + ' summaries=' + remSummaries + ' ratable=' + remRatable
    + ' journals=' + remJournals
    + ' | arce=' + remArce
    + (DELETE_ASSET_RATE_CARD_ENTRIES ? '' : ' (preserved by design, not counted)'));
System.debug('CLEAR: SOQL used = ' + (Limits.getQueries() - q0) + ' of 100'
    + ', DML rows used = ' + Limits.getDmlRows() + ' of ' + Limits.getLimitDmlRows());
if (budgetSpent) {
    System.debug('CLEAR: ⚠ STOPPED EARLY -- the transaction\'s DML row budget was spent. '
        + 'Records remain (see the counts above). RE-RUN this script until every remaining '
        + 'count reads 0'
        + (DELETE_ASSET_RATE_CARD_ENTRIES ? '.' : ' (arce excluded -- preserved by design).'));
}
