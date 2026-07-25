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

// The QuantumBit products this validator owns. Declared up front because the
// design-time queries below MUST be scoped to them: an unscoped RateCardEntry
// query pulls in unrelated datasets (q3, mfg, ...) and then applies the
// seven-currency coverage rule to data that was never meant to satisfy it.
Set<String> QB_USAGE_SKUS = new Set<String>{
    'QB-DB', 'QB-DB-TOKEN', 'QB-CMT-TKN-FLAT', 'QB-CMT-TKN-BND',
    'QB-CMT-TKN-EACH', 'QB-CMT-TKN-TIER', 'QB-QTY-CMT', 'QB-MTY-CMT',
    'QB-TOKENS-PACK', 'QB-DAT-THPT'
};

// The currencies this configuration is REQUIRED to cover. Declared explicitly,
// not derived from whichever CURRENCY units happen to exist in the org: deriving
// it makes a coordinated omission invisible -- a partial load that leaves only
// USD would satisfy "every entry covers all currencies" vacuously.
Set<String> EXPECTED_CURRENCIES = new Set<String>{
    'USD', 'GBP', 'EUR', 'AUD', 'CAD', 'CHF', 'JPY'
};

// ---------------------------------------------------------------- design-time
// 0. COMPLETENESS FIRST. Every other check scopes its queries to QB_USAGE_SKUS,
//    so a product that never loaded is absent from every result set and produces
//    no rows to complain about -- the validator would pass over a build missing
//    QB-CMT-TKN-BND entirely. Assert the catalog is whole before validating it.
Set<String> loadedSkus = new Set<String>();
for (Product2 p : [SELECT StockKeepingUnit FROM Product2
                   WHERE StockKeepingUnit IN :QB_USAGE_SKUS]) {
    loadedSkus.add(p.StockKeepingUnit);
}
Set<String> missingProducts = new Set<String>(QB_USAGE_SKUS);
missingProducts.removeAll(loadedSkus);
if (!missingProducts.isEmpty()) {
    problems.add('Expected QuantumBit usage product(s) missing from the org: '
        + missingProducts + ' -- every check below scopes to these SKUs, so their '
        + 'absence would otherwise produce no findings at all. Load the catalog '
        + '(qb-pcm / qb-pricing / qb-rating) before validating.');
} else {
    passed.add('all ' + QB_USAGE_SKUS.size() + ' expected usage products exist');
}

// Same trap one level down: a product can exist with no ProductUsageResource, in
// which case it contributes no PUR/rate rows and every later check is silent.
Set<String> skusWithPur = new Set<String>();
for (ProductUsageResource pur : [SELECT Product.StockKeepingUnit
                                 FROM ProductUsageResource
                                 WHERE Product.StockKeepingUnit IN :QB_USAGE_SKUS
                                   AND Status = 'Active']) {
    skusWithPur.add(pur.Product.StockKeepingUnit);
}
Set<String> withoutPur = new Set<String>(loadedSkus);
withoutPur.removeAll(skusWithPur);
if (!withoutPur.isEmpty()) {
    problems.add('QuantumBit usage product(s) with NO Active ProductUsageResource: '
        + withoutPur + ' -- they contribute no rows, so the rate and coverage checks '
        + 'below say nothing about them.');
} else if (missingProducts.isEmpty()) {
    passed.add('every expected usage product has at least one Active ProductUsageResource');
}

// Currency units available to denominate a rate. Used to CLASSIFY an entry as
// currency- vs token-denominated; coverage is asserted against EXPECTED_CURRENCIES.
// ACTIVE only. UnitOfMeasure.Status is Active/Draft/Inactive, and this one set
// does double duty -- it satisfies the completeness check AND classifies a rate
// as currency- vs token-denominated. Unfiltered, a Draft or Inactive currency
// unit makes an unusable setup look complete and gets its rates treated as
// currency-denominated, so the validator passes on a configuration that cannot
// rate at runtime.
Set<String> currencyUnits = new Set<String>();
for (UnitOfMeasure u : [SELECT UnitCode FROM UnitOfMeasure
                        WHERE UnitOfMeasureClass.Code = 'CURRENCY'
                          AND Status = 'Active']) {
    currencyUnits.add(u.UnitCode);
}
Set<String> absentCurrencyUnits = new Set<String>(EXPECTED_CURRENCIES);
absentCurrencyUnits.removeAll(currencyUnits);
if (!absentCurrencyUnits.isEmpty()) {
    problems.add('Active CURRENCY unit(s) missing from the org: ' + absentCurrencyUnits
        + ' -- the unit is absent, Draft or Inactive, so it cannot denominate a rate at '
        + 'runtime and every coverage check below would otherwise pass vacuously.');
} else {
    passed.add('all ' + EXPECTED_CURRENCIES.size() + ' expected CURRENCY units exist and are Active');
}

List<RateCardEntry> rces = [
    SELECT Id, Product.StockKeepingUnit, UsageResource.Code, RateCard.Name, RateCard.Type,
           RateUnitOfMeasure.UnitCode, Status
    FROM RateCardEntry
    WHERE Product.StockKeepingUnit IN :QB_USAGE_SKUS
      // ACTIVE only, for the same reason as the CURRENCY units above: a Draft or
      // Inactive entry cannot rate at runtime, so letting one satisfy the coverage,
      // UoM and tier checks means a FAILED activate_rates still passes this
      // validator. Restricting the set makes the existing coverage checks report
      // the missing *active* combinations instead.
      AND Status = 'Active'
];

// 1. Every currency used as a rate UoM must exist as a CURRENCY-class unit.
Set<String> usedCurrencies = new Set<String>();
// NB: test the RELATIONSHIP for null before dereferencing UnitCode. An entry with
// no RateUnitOfMeasure -- the exact defect this validator reports -- has a null
// relationship, so r.RateUnitOfMeasure.UnitCode would throw and abort the run
// instead of recording the problem.
for (RateCardEntry r : rces) {
    if (r.RateUnitOfMeasure != null && r.RateUnitOfMeasure.UnitCode != null
            && currencyUnits.contains(r.RateUnitOfMeasure.UnitCode)) {
        usedCurrencies.add(r.RateUnitOfMeasure.UnitCode);
    }
}
Set<String> missingUnits = new Set<String>();
for (RateCardEntry r : rces) {
    String uom = (r.RateUnitOfMeasure == null) ? null : r.RateUnitOfMeasure.UnitCode;
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
        tierless.add(r.Product.StockKeepingUnit + '/' + r.UsageResource.Code + '/'
            + (r.RateUnitOfMeasure == null ? '(no UoM)' : r.RateUnitOfMeasure.UnitCode));
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
        WHERE ProductUsageResource.Product.UsageModelType = 'Pack'
          AND ProductUsageResource.Product.StockKeepingUnit IN :QB_USAGE_SKUS]) {
    packWithPolicy.add(p.ProductUsageResource.Product.StockKeepingUnit);
}
// 3b. A COMMITMENT product's PURP may carry ONLY a UsageCommitmentPolicy. Setting
//     either period field fails with INVALID_INPUT ("This field must be empty when
//     the product associated with the product usage resource is one of the
//     commitment usage model types"), and SFDMU drops the row silently -- this is
//     the exact defect this PR was opened to fix, where 10 PURP rows failed to load
//     on every build and nothing reported it.
//
//     The offline CSV invariant proves the SHIPPED DATA is shaped correctly; it
//     cannot prove the rows actually landed. Only a live query can, which is why
//     this check has to exist here as well.
Set<String> COMMITMENT_MODELS = new Set<String>{
    'Commit', 'CommitmentQuantity', 'CommitmentSpend'
};
List<String> commitWithPeriods = new List<String>();
Set<String> commitSkusWithPurp = new Set<String>();
for (ProductUsageResourcePolicy p : [
        SELECT ProductUsageResource.Product.StockKeepingUnit,
               ProductUsageResource.UsageResource.Code,
               RatingFrequencyPolicyId, UsageAggregationPolicyId, UsageCommitmentPolicyId
        FROM ProductUsageResourcePolicy
        WHERE ProductUsageResource.Product.UsageModelType IN :COMMITMENT_MODELS
          AND ProductUsageResource.Product.StockKeepingUnit IN :QB_USAGE_SKUS]) {
    String sku = p.ProductUsageResource.Product.StockKeepingUnit;
    String res = p.ProductUsageResource.UsageResource.Code;
    commitSkusWithPurp.add(sku);
    List<String> carried = new List<String>();
    if (p.RatingFrequencyPolicyId != null) { carried.add('rating'); }
    if (p.UsageAggregationPolicyId != null) { carried.add('accumulation'); }
    if (p.UsageCommitmentPolicyId == null) { carried.add('NO commitment policy'); }
    if (!carried.isEmpty()) {
        commitWithPeriods.add(sku + '/' + res + ' carries ' + String.join(carried, '+'));
    }
}
if (!commitWithPeriods.isEmpty()) {
    problems.add('Commitment PURP rows with an illegal shape (' + commitWithPeriods.size()
        + '): ' + String.join(commitWithPeriods, '; ')
        + ' -- a commitment PURP may carry ONLY a UsageCommitmentPolicy.');
} else if (!commitSkusWithPurp.isEmpty()) {
    passed.add('every commitment PURP across ' + commitSkusWithPurp.size()
        + ' product(s) carries a commitment policy and no period fields');
}
// Presence, not just shape: a silently-dropped row leaves the product with NO PURP
// at all, which the shape check above cannot see.
Set<String> commitSkus = new Set<String>();
for (Product2 p : [SELECT StockKeepingUnit FROM Product2
                   WHERE StockKeepingUnit IN :QB_USAGE_SKUS
                     AND UsageModelType IN :COMMITMENT_MODELS]) {
    commitSkus.add(p.StockKeepingUnit);
}
Set<String> commitSkusMissingPurp = new Set<String>(commitSkus);
commitSkusMissingPurp.removeAll(commitSkusWithPurp);
if (!commitSkusMissingPurp.isEmpty()) {
    problems.add('Commitment product(s) with NO ProductUsageResourcePolicy at all: '
        + commitSkusMissingPurp + ' -- the rows were almost certainly dropped during '
        + 'the data load (the classic silent failure); the commitment cannot discount '
        + 'anything without them.');
} else if (!commitSkus.isEmpty()) {
    passed.add('all ' + commitSkus.size() + ' commitment product(s) have PURP rows loaded');
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
// Scoped to QB_USAGE_SKUS to match `rces` above. Unscoped, every non-QuantumBit
// PUR would be reported unrated purely because ratedPairs only holds QB entries.
for (ProductUsageResource pur : [SELECT Product.StockKeepingUnit, UsageResource.Code,
                                        UsageResource.Category
                                 FROM ProductUsageResource
                                 WHERE Status = 'Active'
                                   AND Product.StockKeepingUnit IN :QB_USAGE_SKUS]) {
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
    // A null relationship is already reported by check 1; skip rather than NPE here.
    if (r.RateUnitOfMeasure == null) continue;
    if (!currencyUnits.contains(r.RateUnitOfMeasure.UnitCode)) continue;  // token-denominated
    String key = r.Product.StockKeepingUnit + '|' + r.RateCard.Name + '|' + r.UsageResource.Code;
    if (!coverage.containsKey(key)) coverage.put(key, new Set<String>());
    coverage.get(key).add(r.RateUnitOfMeasure.UnitCode);
}
List<String> gaps = new List<String>();
for (String key : coverage.keySet()) {
    // Compare against the EXPECTED set, not the org's own units: if one currency's
    // UoM and all of its rate rows are absent together, deriving the expectation
    // from the org would make that coordinated omission invisible.
    Set<String> missing = new Set<String>(EXPECTED_CURRENCIES);
    missing.removeAll(coverage.get(key));
    if (!missing.isEmpty()) gaps.add(key + ' missing ' + String.join(new List<String>(missing), '/'));
}
if (!gaps.isEmpty()) {
    problems.add('Rate card entries not covering every currency: ' + String.join(gaps, '; '));
} else {
    passed.add('all ' + coverage.size() + ' currency-denominated entries cover all '
        + EXPECTED_CURRENCIES.size() + ' expected currencies');
}

// ------------------------------------------------------------------- runtime
// Only meaningful once an order-to-asset run has produced entitlements.
// Scoped to QB_USAGE_SKUS (declared at the top): an unrelated product's entries
// would otherwise be pulled into the per-asset shape comparison below.
List<AssetRateCardEntry> arces = [
    SELECT AssetId, Asset.CurrencyIsoCode, Asset.Account.Name,
           Asset.Product2.StockKeepingUnit, CurrencyIsoCode,
           UsageResource.Code, RateUnitOfMeasure.UnitCode,
           RateCardEntry.RateUnitOfMeasure.UnitCode
    FROM AssetRateCardEntry
    WHERE Asset.Product2.StockKeepingUnit IN :QB_USAGE_SKUS
];
// Skip only when there are genuinely no QuantumBit assets. Zero AssetRateCardEntry
// rows while assets DO exist is itself the failure -- the order-to-asset run
// produced an asset that resolved no rates at all -- so treating "no ARCEs" as
// "nothing to check" would report a pass over exactly that broken state.
Map<Id, Asset> qbAssets = new Map<Id, Asset>([
    SELECT Id, Account.Name, CurrencyIsoCode, Product2.StockKeepingUnit
    FROM Asset WHERE Product2.StockKeepingUnit IN :QB_USAGE_SKUS
]);
if (qbAssets.isEmpty()) {
    passed.add('runtime checks skipped -- no QuantumBit usage assets exist yet');
} else {
    // Compare PER ASSET, not in aggregate. Checking only `arces.isEmpty()` catches
    // just the all-assets-broken case: one regional asset with zero ARCE rows is
    // simply absent from the per-asset maps below, so every subsequent runtime
    // check passes over it silently -- which is exactly the defect this validator
    // exists to find (a per-currency entry missing for one region).
    Set<Id> assetsWithRates = new Set<Id>();
    for (AssetRateCardEntry a : arces) { assetsWithRates.add(a.AssetId); }
    List<String> rateless = new List<String>();
    for (Id assetId : qbAssets.keySet()) {
        if (!assetsWithRates.contains(assetId)) {
            Asset a = qbAssets.get(assetId);
            rateless.add(a.Account.Name + '/' + a.Product2.StockKeepingUnit
                + ' (' + a.CurrencyIsoCode + ')');
        }
    }
    if (!rateless.isEmpty()) {
        problems.add(rateless.size() + ' of ' + qbAssets.size() + ' QuantumBit usage '
            + 'asset(s) have NO AssetRateCardEntry rows -- they resolved no rates at '
            + 'all: ' + String.join(rateless, ', ')
            + '. Check the order-to-asset run and that a rate card entry exists and is '
            + 'Active for that product in that currency.');
    } else {
        passed.add('all ' + qbAssets.size() + ' QuantumBit usage asset(s) resolved rates');
    }
}
if (!arces.isEmpty()) {
    // 6. asset currency == ARCE currency == ARCE rate UoM == resolved entry's UoM.
    //    A divergence means the asset resolved a rate denominated in another
    //    currency (usually a missing per-currency entry falling back to USD).
    List<String> misaligned = new List<String>();
    Map<String, Integer> arceByCurrency = new Map<String, Integer>();
    for (AssetRateCardEntry a : arces) {
        String ac = a.Asset.CurrencyIsoCode;
        String rc = (a.RateUnitOfMeasure == null) ? null : a.RateUnitOfMeasure.UnitCode;
        String pc = (a.RateCardEntry == null || a.RateCardEntry.RateUnitOfMeasure == null)
                    ? null : a.RateCardEntry.RateUnitOfMeasure.UnitCode;
        // Token-denominated rates are currency-NEUTRAL by design: the rate is
        // expressed in TOKEN-UOM and the token->currency conversion happens at the
        // second rating step. Requiring rateUoM == asset currency would flag every
        // token product on every account. Only the ARCE's own CurrencyIsoCode has
        // to track the asset.
        Boolean tokenDenominated = (rc == 'TOKEN-UOM' || pc == 'TOKEN-UOM');
        Boolean bad = tokenDenominated
            ? (ac != a.CurrencyIsoCode || rc != pc)
            : (ac != a.CurrencyIsoCode || ac != rc || ac != pc);
        if (bad) {
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

    // 7. Compare rate-entry shape PER ASSET, grouped by product -- not per currency.
    //    A per-currency total is meaningless once accounts hold different products:
    //    two USD assets vs one GBP asset fails even when each asset is correct, and
    //    one 6-entry USD asset vs two 3-entry GBP assets wrongly passes. The real
    //    invariant is that the same product yields the same entries in any currency.
    Map<Id, Integer> arceCountByAsset = new Map<Id, Integer>();
    Map<Id, String> skuByAsset = new Map<Id, String>();
    Map<Id, String> ccyByAsset = new Map<Id, String>();
    for (AssetRateCardEntry a : arces) {
        Integer n = arceCountByAsset.get(a.AssetId);
        arceCountByAsset.put(a.AssetId, n == null ? 1 : n + 1);
        skuByAsset.put(a.AssetId, a.Asset.Product2.StockKeepingUnit);
        ccyByAsset.put(a.AssetId, a.Asset.CurrencyIsoCode);
    }
    Map<String, Map<Integer, List<String>>> countsBySku =
        new Map<String, Map<Integer, List<String>>>();
    for (Id assetId : arceCountByAsset.keySet()) {
        String sku = skuByAsset.get(assetId);
        if (!countsBySku.containsKey(sku)) countsBySku.put(sku, new Map<Integer, List<String>>());
        Integer n = arceCountByAsset.get(assetId);
        if (!countsBySku.get(sku).containsKey(n)) countsBySku.get(sku).put(n, new List<String>());
        countsBySku.get(sku).get(n).add(ccyByAsset.get(assetId));
    }
    List<String> shapeGaps = new List<String>();
    for (String sku : countsBySku.keySet()) {
        if (countsBySku.get(sku).size() > 1) {
            List<String> detail = new List<String>();
            for (Integer n : countsBySku.get(sku).keySet()) {
                detail.add(n + ' entries in ' + countsBySku.get(sku).get(n));
            }
            shapeGaps.add(sku + ': ' + String.join(detail, ' vs '));
        }
    }
    if (!shapeGaps.isEmpty()) {
        problems.add('Same product yields a different number of AssetRateCardEntry rows '
            + 'depending on currency: ' + String.join(shapeGaps, '; '));
    } else {
        passed.add('every product yields a consistent AssetRateCardEntry shape across the '
            + arceCountByAsset.size() + ' asset(s) built, in '
            + (new Set<String>(ccyByAsset.values())).size() + ' currencies');
    }

    // 8. The SAME product must yield the same entitlement shape in any currency.
    //    Grouped per asset and keyed by product, not lumped per currency: accounts
    //    deliberately hold different consumption products now, so a per-currency
    //    union compares a token commitment against a quantity commitment and always
    //    differs. Entitlement quantities are currency-neutral (grants are counts of
    //    tokens/minutes/TB), so the shape genuinely must match across currencies.
    Map<Id, String> tueSkuByAsset = new Map<Id, String>();
    Map<Id, String> tueCcyByAsset = new Map<Id, String>();
    Map<Id, Set<String>> tueByAsset = new Map<Id, Set<String>>();
    for (TransactionUsageEntitlement t : [
            SELECT AssetId, Asset.CurrencyIsoCode, Asset.Product2.StockKeepingUnit,
                   UsageResource.Code, EntitlementQuantity
            FROM TransactionUsageEntitlement
            WHERE AssetId != null
              AND Asset.Product2.StockKeepingUnit IN :QB_USAGE_SKUS]) {
        if (!tueByAsset.containsKey(t.AssetId)) tueByAsset.put(t.AssetId, new Set<String>());
        tueByAsset.get(t.AssetId).add(t.UsageResource.Code + '=' + t.EntitlementQuantity);
        tueSkuByAsset.put(t.AssetId, t.Asset.Product2.StockKeepingUnit);
        tueCcyByAsset.put(t.AssetId, t.Asset.CurrencyIsoCode);
    }
    // An asset with ZERO entitlements never enters tueByAsset, so the shape
    // comparison below would silently run on the healthy assets only and report
    // success -- the same partial-failure blind spot as the ARCE check above.
    List<String> noEntitlements = new List<String>();
    for (Id assetId : qbAssets.keySet()) {
        if (!tueByAsset.containsKey(assetId)) {
            Asset a = qbAssets.get(assetId);
            noEntitlements.add(a.Account.Name + '/' + a.Product2.StockKeepingUnit
                + ' (' + a.CurrencyIsoCode + ')');
        }
    }
    if (!noEntitlements.isEmpty()) {
        problems.add(noEntitlements.size() + ' of ' + qbAssets.size() + ' asset(s) have NO '
            + 'TransactionUsageEntitlement rows: ' + String.join(noEntitlements, ', ')
            + ' -- entitlement creation did not run or failed for them.');
    }
    Map<String, Map<String, List<String>>> tueShapeBySku =
        new Map<String, Map<String, List<String>>>();
    for (Id assetId : tueByAsset.keySet()) {
        List<String> shapeList = new List<String>(tueByAsset.get(assetId));
        shapeList.sort();
        String shape = String.join(shapeList, ', ');
        String sku = tueSkuByAsset.get(assetId);
        if (!tueShapeBySku.containsKey(sku)) tueShapeBySku.put(sku, new Map<String, List<String>>());
        if (!tueShapeBySku.get(sku).containsKey(shape)) {
            tueShapeBySku.get(sku).put(shape, new List<String>());
        }
        tueShapeBySku.get(sku).get(shape).add(tueCcyByAsset.get(assetId));
    }
    List<String> tueGaps = new List<String>();
    for (String sku : tueShapeBySku.keySet()) {
        if (tueShapeBySku.get(sku).size() > 1) {
            List<String> detail = new List<String>();
            for (String shape : tueShapeBySku.get(sku).keySet()) {
                detail.add(tueShapeBySku.get(sku).get(shape) + ': [' + shape + ']');
            }
            tueGaps.add(sku + ' -- ' + String.join(detail, ' | '));
        }
    }
    if (!tueGaps.isEmpty()) {
        problems.add('Same product yields a different TransactionUsageEntitlement shape '
            + 'depending on currency: ' + String.join(tueGaps, '; '));
    } else if (!tueByAsset.isEmpty()) {
        passed.add('every product yields a consistent TransactionUsageEntitlement shape across '
            + tueByAsset.size() + ' asset(s)');
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
