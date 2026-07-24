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
 * Run AFTER assets are created (order activation). Idempotent and bulk-safe.
 * For an always-on fix, a record-triggered before-save flow on AssetRateCardEntry
 * that assigns {!$Record.Asset.CurrencyIsoCode} achieves the same automatically.
 */
List<AssetRateCardEntry> toFix = new List<AssetRateCardEntry>();
for (AssetRateCardEntry arce : [
        SELECT Id, CurrencyIsoCode, Asset.CurrencyIsoCode
        FROM AssetRateCardEntry
        WHERE AssetId != null]) {
    if (arce.Asset.CurrencyIsoCode != null
            && arce.CurrencyIsoCode != arce.Asset.CurrencyIsoCode) {
        toFix.add(new AssetRateCardEntry(
            Id = arce.Id,
            CurrencyIsoCode = arce.Asset.CurrencyIsoCode));
    }
}
if (!toFix.isEmpty()) {
    update toFix;
    System.debug('setAssetRateCardEntryCurrency: corrected ' + toFix.size()
        + ' AssetRateCardEntry record(s) to their parent Asset currency.');
} else {
    System.debug('setAssetRateCardEntryCurrency: no mismatched records — nothing to do.');
}
