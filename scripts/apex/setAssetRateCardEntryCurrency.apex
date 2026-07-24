/*
 * setAssetRateCardEntryCurrency.apex
 * ----------------------------------
 * Multicurrency fix for usage rating.
 *
 * AssetRateCardEntry.CurrencyIsoCode is a restricted picklist that DEFAULTS TO
 * "USD" and is NOT inherited from the parent Asset when the entitlement-creation
 * process generates the record at order activation. On a non-USD asset it is
 * therefore left stamped "USD" (Salesforce 262; no documented setup/config path
 * makes it inherit the asset currency — verified against the Usage/Rate corpus).
 *
 * This backfill sets AssetRateCardEntry.CurrencyIsoCode = parent Asset.CurrencyIsoCode
 * for every mismatched row. It is a DATA-INTEGRITY / dashboard fix (corrects the
 * read-only "Usage Rates" tab and protects any custom decision tables/reports that
 * key on the stamp); usage billing already denominates in the account's currency
 * (Invoice/InvoiceLine), and rating math is currency-blind, so this does NOT change
 * invoiced amounts.
 *
 * Run AFTER assets are created (order activation). Idempotent; corrects up to 10,000
 * rows per run (rerun until it reports 0 corrected for very large backfills).
 * For an always-on fix, a record-triggered before-save flow on AssetRateCardEntry
 * that assigns {!$Record.Asset.CurrencyIsoCode} achieves the same automatically.
 */
// Bulk-safety: SOQL cannot compare two fields in a WHERE, but the documented bug
// leaves CurrencyIsoCode at the default 'USD' on a non-USD asset, so the mismatched
// rows are exactly (CurrencyIsoCode = 'USD' AND Asset.CurrencyIsoCode != 'USD').
// Filtering in SOQL bounds the run to <= 10,000 DML rows (the per-transaction limit),
// and because corrected rows adopt the asset's non-USD currency they drop out of this
// filter — so if a very large backfill exceeds one batch, simply rerun until it
// reports 0 corrected. (`!= 'USD'` also excludes null-currency assets in SOQL.)
List<AssetRateCardEntry> toFix = new List<AssetRateCardEntry>();
for (AssetRateCardEntry arce : [
        SELECT Id, CurrencyIsoCode, Asset.CurrencyIsoCode
        FROM AssetRateCardEntry
        WHERE AssetId != null
          AND CurrencyIsoCode = 'USD'
          AND Asset.CurrencyIsoCode != 'USD'
        LIMIT 10000]) {
    toFix.add(new AssetRateCardEntry(
        Id = arce.Id,
        CurrencyIsoCode = arce.Asset.CurrencyIsoCode));
}
if (!toFix.isEmpty()) {
    update toFix;
    System.debug('setAssetRateCardEntryCurrency: corrected ' + toFix.size()
        + ' AssetRateCardEntry record(s) to their parent Asset currency'
        + (toFix.size() == 10000 ? ' (batch cap reached — rerun to correct any remaining).' : '.'));
} else {
    System.debug('setAssetRateCardEntryCurrency: no mismatched records — nothing to do.');
}
