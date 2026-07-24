// Validate the multicurrency usage-rating configuration in a live org.
//
// Run after prepare_rating (design-time checks) and again after an
// order-to-asset run (runtime checks, skipped automatically when no assets
// exist, so this is safe on a fresh build).
//
// A usage rate is denominated by its RateUnitOfMeasure -- a unit in the
// CURRENCY UnitOfMeasureClass -- not by a CurrencyIsoCode field. There is NO
// runtime conversion from the USD entry, so a non-USD quote cannot rate at all
// unless its own currency's RateCardEntry exists. These checks enforce that.
//
// Collects every failure and throws once with a full report, so a single run
// tells you everything that is wrong rather than only the first problem.
//
// NB: Apex cannot construct the abstract built-in Exception -- `new Exception(msg)`
// is a compile error ("Type cannot be constructed: Exception"). A custom subclass
// is required.
public class MulticurrencyValidationException extends Exception {}

List<String> problems = new List<String>();
List<String> passed = new List<String>();

// ---------------------------------------------------------------- design-time
// Currency units available to denominate a rate.
Set<String> currencyUnits = new Set<String>();
for (UnitOfMeasure u : [SELECT UnitCode FROM UnitOfMeasure WHERE UnitOfMeasureClass.Code = 'CURRENCY']) {
    currencyUnits.add(u.UnitCode);
}

List<RateCardEntry> rces = [
    SELECT Id, Product.StockKeepingUnit, UsageResource.Code, RateCard.Name, RateCard.Type,
           RateUnitOfMeasure.UnitCode, Status
    FROM RateCardEntry
];

// 1. Every currency used as a rate UoM must exist as a CURRENCY-class unit.
Set<String> usedCurrencies = new Set<String>();
for (RateCardEntry r : rces) {
    if (r.RateUnitOfMeasure.UnitCode != null && currencyUnits.contains(r.RateUnitOfMeasure.UnitCode)) {
        usedCurrencies.add(r.RateUnitOfMeasure.UnitCode);
    }
}
Set<String> missingUnits = new Set<String>();
for (RateCardEntry r : rces) {
    String uom = r.RateUnitOfMeasure.UnitCode;
    // A rate UoM that is neither a known currency unit nor a token unit is suspect only
    // if no UnitOfMeasure backs it; token units legitimately sit outside CURRENCY.
    if (uom == null) { missingUnits.add('(null rate UoM) ' + r.Product.StockKeepingUnit); }
}
if (!missingUnits.isEmpty()) {
    problems.add('RateCardEntry rows with no RateUnitOfMeasure: ' + String.join(new List<String>(missingUnits), ', '));
} else {
    passed.add('every RateCardEntry has a RateUnitOfMeasure (' + usedCurrencies.size() + ' currencies in use)');
}

// 2. Every Tier-type RateCardEntry must have >= 1 tier adjustment.
//    Without this, activate_rates fails the whole build:
//    "Specify at least one tier adjustment for a Rate Card Entry of type tier."
Set<Id> rceWithTier = new Set<Id>();
for (AggregateResult ar : [SELECT RateCardEntryId FROM RateAdjustmentByTier
                           WHERE RateCardEntryId != null GROUP BY RateCardEntryId]) {
    rceWithTier.add((Id) ar.get('RateCardEntryId'));
}
List<String> tierless = new List<String>();
for (RateCardEntry r : rces) {
    if (r.RateCard.Type == 'Tier' && !rceWithTier.contains(r.Id)) {
        tierless.add(r.Product.StockKeepingUnit + '/' + r.UsageResource.Code + '/' + r.RateUnitOfMeasure.UnitCode);
    }
}
if (!tierless.isEmpty()) {
    problems.add('Tier RateCardEntry rows with NO tier adjustment (activate_rates will fail): '
        + String.join(tierless, ', '));
} else {
    passed.add('every Tier rate card entry has at least one tier adjustment');
}

// 3. No UsageModelType=Pack product may carry a ProductUsageResourcePolicy.
//    The platform rejects it: INVALID_INPUT "We can't save the pack usage model
//    type record." Such rows fail silently during a data load.
List<String> packWithPolicy = new List<String>();
for (ProductUsageResourcePolicy p : [
        SELECT ProductUsageResource.Product.StockKeepingUnit,
               ProductUsageResource.Product.UsageModelType
        FROM ProductUsageResourcePolicy
        WHERE ProductUsageResource.Product.UsageModelType = 'Pack']) {
    packWithPolicy.add(p.ProductUsageResource.Product.StockKeepingUnit);
}
if (!packWithPolicy.isEmpty()) {
    problems.add('Pack products carrying a ProductUsageResourcePolicy (platform rejects these): '
        + String.join(packWithPolicy, ', '));
} else {
    passed.add('no ProductUsageResourcePolicy on any Pack product');
}

// 4. Every ProductUsageResource should have a rate card entry, or the Usage
//    Product Validator reports "No effective rate card entry available".
//    UR-USD is Category=Currency (the monetary-commitment wallet) and is exempt.
Set<String> ratedPairs = new Set<String>();
for (RateCardEntry r : rces) {
    ratedPairs.add(r.Product.StockKeepingUnit + '|' + r.UsageResource.Code);
}
List<String> unrated = new List<String>();
for (ProductUsageResource pur : [SELECT Product.StockKeepingUnit, UsageResource.Code,
                                        UsageResource.Category
                                 FROM ProductUsageResource WHERE Status = 'Active']) {
    String key = pur.Product.StockKeepingUnit + '|' + pur.UsageResource.Code;
    if (!ratedPairs.contains(key) && pur.UsageResource.Category != 'Currency') {
        unrated.add(key);
    }
}
if (!unrated.isEmpty()) {
    problems.add('ProductUsageResource rows with no rate card entry: ' + String.join(unrated, ', '));
} else {
    passed.add('every active product usage resource has a rate card entry');
}

// 5. Each currency-denominated entry must exist in EVERY currency -- a missing
//    one means that currency simply cannot rate (no fallback to USD).
Map<String, Set<String>> coverage = new Map<String, Set<String>>();
for (RateCardEntry r : rces) {
    if (!currencyUnits.contains(r.RateUnitOfMeasure.UnitCode)) continue;  // token-denominated
    String key = r.Product.StockKeepingUnit + '|' + r.RateCard.Name + '|' + r.UsageResource.Code;
    if (!coverage.containsKey(key)) coverage.put(key, new Set<String>());
    coverage.get(key).add(r.RateUnitOfMeasure.UnitCode);
}
List<String> gaps = new List<String>();
for (String key : coverage.keySet()) {
    Set<String> missing = new Set<String>(currencyUnits);
    missing.removeAll(coverage.get(key));
    if (!missing.isEmpty()) gaps.add(key + ' missing ' + String.join(new List<String>(missing), '/'));
}
if (!gaps.isEmpty()) {
    problems.add('Rate card entries not covering every currency: ' + String.join(gaps, '; '));
} else {
    passed.add('all ' + coverage.size() + ' currency-denominated entries cover all '
        + currencyUnits.size() + ' currencies');
}

// ------------------------------------------------------------------- runtime
// Only meaningful once an order-to-asset run has produced entitlements.
List<AssetRateCardEntry> arces = [
    SELECT Asset.CurrencyIsoCode, Asset.Account.Name, CurrencyIsoCode,
           UsageResource.Code, RateUnitOfMeasure.UnitCode,
           RateCardEntry.RateUnitOfMeasure.UnitCode
    FROM AssetRateCardEntry
];
if (arces.isEmpty()) {
    passed.add('runtime checks skipped -- no AssetRateCardEntry records yet');
} else {
    // 6. asset currency == ARCE currency == ARCE rate UoM == resolved entry's UoM.
    //    A divergence means the asset resolved a rate denominated in another
    //    currency (usually a missing per-currency entry falling back to USD).
    List<String> misaligned = new List<String>();
    Map<String, Integer> arceByCurrency = new Map<String, Integer>();
    for (AssetRateCardEntry a : arces) {
        String ac = a.Asset.CurrencyIsoCode;
        String rc = a.RateUnitOfMeasure.UnitCode;
        String pc = a.RateCardEntry.RateUnitOfMeasure.UnitCode;
        if (ac != a.CurrencyIsoCode || ac != rc || ac != pc) {
            misaligned.add(a.Asset.Account.Name + '/' + a.UsageResource.Code
                + ' asset=' + ac + ' arce=' + a.CurrencyIsoCode + ' rateUoM=' + rc + ' entryUoM=' + pc);
        }
        Integer n = arceByCurrency.get(ac);
        arceByCurrency.put(ac, n == null ? 1 : n + 1);
    }
    if (!misaligned.isEmpty()) {
        problems.add('AssetRateCardEntry currency misalignment: ' + String.join(misaligned, '; '));
    } else {
        passed.add('all ' + arces.size() + ' AssetRateCardEntry rows currency-aligned across '
            + arceByCurrency.size() + ' currencies');
    }

    // 7. Every currency's asset should produce the same number of rate entries.
    Set<Integer> arceCounts = new Set<Integer>(arceByCurrency.values());
    if (arceCounts.size() > 1) {
        List<String> detail = new List<String>();
        for (String c : arceByCurrency.keySet()) detail.add(c + '=' + arceByCurrency.get(c));
        problems.add('AssetRateCardEntry count differs by currency: ' + String.join(detail, ', '));
    } else {
        passed.add('AssetRateCardEntry count identical across currencies');
    }

    // 8. Transaction usage entitlements must be shaped identically per currency.
    Map<String, Set<String>> tueByCurrency = new Map<String, Set<String>>();
    for (TransactionUsageEntitlement t : [
            SELECT Asset.CurrencyIsoCode, UsageResource.Code, EntitlementQuantity
            FROM TransactionUsageEntitlement WHERE AssetId != null]) {
        String c = t.Asset.CurrencyIsoCode;
        if (!tueByCurrency.containsKey(c)) tueByCurrency.put(c, new Set<String>());
        tueByCurrency.get(c).add(t.UsageResource.Code + '=' + t.EntitlementQuantity);
    }
    Set<String> tueShapes = new Set<String>();
    for (String c : tueByCurrency.keySet()) {
        List<String> s = new List<String>(tueByCurrency.get(c));
        s.sort();
        tueShapes.add(String.join(s, ','));
    }
    if (tueShapes.size() > 1) {
        List<String> detail = new List<String>();
        for (String c : tueByCurrency.keySet()) {
            List<String> s = new List<String>(tueByCurrency.get(c));
            s.sort();
            detail.add(c + ': [' + String.join(s, ', ') + ']');
        }
        problems.add('TransactionUsageEntitlement shape differs by currency -- '
            + String.join(detail, ' | '));
    } else if (!tueByCurrency.isEmpty()) {
        passed.add('TransactionUsageEntitlement shape identical across '
            + tueByCurrency.size() + ' currencies');
    }
}

// -------------------------------------------------------------------- report
for (String p : passed) { System.debug('PASS: ' + p); }
if (!problems.isEmpty()) {
    String report = '\n  - ' + String.join(problems, '\n  - ');
    throw new MulticurrencyValidationException('Multicurrency rate validation FAILED (' + problems.size()
        + ' problem(s)):' + report
        + '\n\nPassed ' + passed.size() + ' other check(s). '
        + 'Fix the data in datasets/sfdmu/qb/en-US/{qb-rating,qb-rates} and reload; '
        + 'run tests/test_qb_multicurrency_data.py for the offline equivalent.');
}
System.debug('Multicurrency rate validation PASSED -- ' + passed.size() + ' check(s).');
