// Delete customer-template catalog slice: PCM scaffolding, demo Product2 rows, Standard PricebookEntry,
// and Snowflake-named billing foundation loaded by customer-template-billing.
//
// Prerequisites (run in order via purge_customer_demo_catalog flow):
//   1) customer_demo_purge_records — QLIURP / QLIURG / order grants
//   2) delete_customer_demo_rates_data — CD-DEMO rate cards
//   3) delete_customer_demo_rating_data — PUR/PUG/PURP/SF-UR-* / OC-UR-*
//
// Scope: Product2 where StockKeepingUnit matches SF-SNOW-%, SF-USG-%, SF-BLNG-%, OC-%, or APT-%;
// ProductCatalog Code = SF-DEMO-CAT, OC-DEMO-CAT, or CAT-APT-DEMO; ProductClassification Code = SF-SW or OC-CLUB;
// demo UsageGrantRenewalPolicy / UsageGrantRolloverPolicy codes SF-DEMO-USG-*;
// billing records named in customer-template-billing CSVs.
//
// Does NOT delete: UnitOfMeasure / UnitOfMeasureClass (DATAVOL, SNFCRED), shared UsageResourceBillingPolicy
// (monthlypeak/monthlytotal), Default Usage Overage Policy, global RatingFrequencyPolicy, ProductSellingModel rows.
//
// Quote lines or order items referencing demo SKUs will block PricebookEntry/Product2 delete — remove those
// transaction rows first, then re-run this script.

final List<String> DEMO_CATALOG_CODES = new List<String>{ 'SF-DEMO-CAT', 'OC-DEMO-CAT', 'CAT-APT-DEMO' };
final List<String> DEMO_CLASSIFICATION_CODES = new List<String>{ 'SF-SW', 'OC-CLUB' };
final List<List<String>> DEMO_BILLING_STACKS = new List<List<String>>{
    new List<String>{
        'Snowflake Demo Billing Policy',
        'Snowflake Demo Billing Treatment - US',
        'Snowflake Demo Legal Entity - US'
    },
    new List<String>{
        'Olympic Demo Billing Policy',
        'Olympic Demo Billing Treatment - US',
        'Olympic Demo Legal Entity - US'
    },
    new List<String>{
        'APTIM Demo Billing Policy',
        'APTIM Demo Billing Treatment - US',
        'APTIM Demo Legal Entity - US'
    }
};

List<Product2> demoProducts = [
    SELECT Id, Type, StockKeepingUnit
    FROM
        Product2
    WHERE
        (StockKeepingUnit LIKE 'SF-SNOW-%')
        OR (StockKeepingUnit LIKE 'SF-USG-%')
        OR (StockKeepingUnit LIKE 'SF-BLNG-%')
        OR (StockKeepingUnit LIKE 'OC-%')
        OR (StockKeepingUnit LIKE 'APT-%')
];
Set<Id> demoProductIds = new Map<Id, Product2>(demoProducts).keySet();

if (demoProductIds.isEmpty()) {
    System.debug('deleteCustomerDemoCatalogData: no demo Product2 rows — skip product cleanup.');
} else {
    List<ProductRelatedComponent> prcs = [
        SELECT Id
        FROM ProductRelatedComponent
        WHERE ParentProductId IN :demoProductIds OR ChildProductId IN :demoProductIds
    ];
    if (!prcs.isEmpty()) {
        Database.delete(prcs, false);
        System.debug('Deleted ' + prcs.size() + ' ProductRelatedComponent row(s).');
    }

    List<ProductComponentGroup> pcgs = [SELECT Id FROM ProductComponentGroup WHERE ParentProductId IN :demoProductIds];
    if (!pcgs.isEmpty()) {
        Database.delete(pcgs, false);
        System.debug('Deleted ' + pcgs.size() + ' ProductComponentGroup row(s).');
    }

    List<ProductCategoryProduct> pcps = [SELECT Id FROM ProductCategoryProduct WHERE ProductId IN :demoProductIds];
    if (!pcps.isEmpty()) {
        Database.delete(pcps, false);
        System.debug('Deleted ' + pcps.size() + ' ProductCategoryProduct row(s).');
    }

    List<ProductSellingModelOption> psmos = [
        SELECT Id FROM ProductSellingModelOption WHERE Product2Id IN :demoProductIds
    ];
    if (!psmos.isEmpty()) {
        Database.delete(psmos, false);
        System.debug('Deleted ' + psmos.size() + ' ProductSellingModelOption row(s).');
    }

    List<UsagePrdGrantBindingPolicy> ugbs = [
        SELECT Id FROM UsagePrdGrantBindingPolicy WHERE Product2Id IN :demoProductIds
    ];
    if (!ugbs.isEmpty()) {
        Database.delete(ugbs, false);
        System.debug('Deleted ' + ugbs.size() + ' UsagePrdGrantBindingPolicy row(s).');
    }

    List<Product2> toClearBilling = [SELECT Id FROM Product2 WHERE Id IN :demoProductIds AND BillingPolicyId != NULL];
    if (!toClearBilling.isEmpty()) {
        for (Product2 p : toClearBilling) {
            p.BillingPolicyId = null;
        }
        Database.update(toClearBilling, false);
        System.debug('Cleared BillingPolicyId on ' + toClearBilling.size() + ' Product2 row(s).');
    }

    List<Pricebook2> stdPb = [SELECT Id FROM Pricebook2 WHERE IsStandard = TRUE LIMIT 1];
    if (!stdPb.isEmpty()) {
        List<PricebookEntry> pbes = [
            SELECT Id FROM PricebookEntry WHERE Pricebook2Id = :stdPb[0].Id AND Product2Id IN :demoProductIds
        ];
        if (!pbes.isEmpty()) {
            Database.DeleteResult[] pbeDr = Database.delete(pbes, false);
            Integer pbeOk = 0;
            for (Database.DeleteResult dr : pbeDr) {
                if (dr.isSuccess()) {
                    pbeOk++;
                }
            }
            System.debug(
                'PricebookEntry delete: ' + pbeOk + ' succeeded, ' + (pbes.size() - pbeOk) + ' failed (see quotes).'
            );
        }
    }

    List<Product2> nonBundles = [
        SELECT Id
        FROM Product2
        WHERE Id IN :demoProductIds AND (Type != 'Bundle' OR Type = NULL)
    ];
    if (!nonBundles.isEmpty()) {
        Database.DeleteResult[] dr1 = Database.delete(nonBundles, false);
        Integer nbOk = 0;
        for (Database.DeleteResult dr : dr1) {
            if (dr.isSuccess()) {
                nbOk++;
            } else {
                for (Database.Error err : dr.getErrors()) {
                    System.debug(LoggingLevel.WARN, 'Product2 non-bundle: ' + err.getMessage());
                }
            }
        }
        System.debug('Product2 (non-bundle) delete: ' + nbOk + '/' + nonBundles.size() + ' ok.');
    }

    List<Product2> bundles = [SELECT Id FROM Product2 WHERE Id IN :demoProductIds AND Type = 'Bundle'];
    if (!bundles.isEmpty()) {
        Database.DeleteResult[] dr2 = Database.delete(bundles, false);
        Integer bOk = 0;
        for (Database.DeleteResult dr : dr2) {
            if (dr.isSuccess()) {
                bOk++;
            } else {
                for (Database.Error err : dr.getErrors()) {
                    System.debug(LoggingLevel.WARN, 'Product2 bundle: ' + err.getMessage());
                }
            }
        }
        System.debug('Product2 (bundle) delete: ' + bOk + '/' + bundles.size() + ' ok.');
    }
}

for (String catalogCode : DEMO_CATALOG_CODES) {
    List<ProductCatalog> demoCatalog = [
        SELECT Id, Code
        FROM ProductCatalog
        WHERE Code = :catalogCode
        LIMIT 1
    ];
    if (demoCatalog.isEmpty()) {
        continue;
    }
    Id catalogId = demoCatalog[0].Id;
    Integer guard = 0;
    while (guard++ < 25) {
        List<ProductCategory> allCats = [
            SELECT Id, ParentCategoryId FROM ProductCategory WHERE CatalogId = :catalogId
        ];
        if (allCats.isEmpty()) {
            break;
        }
        Set<Id> idsThatAreParents = new Set<Id>();
        for (ProductCategory pc : allCats) {
            if (pc.ParentCategoryId != null) {
                idsThatAreParents.add(pc.ParentCategoryId);
            }
        }
        List<ProductCategory> leaves = new List<ProductCategory>();
        for (ProductCategory pc : allCats) {
            if (!idsThatAreParents.contains(pc.Id)) {
                leaves.add(pc);
            }
        }
        if (leaves.isEmpty()) {
            Database.delete(allCats, false);
            break;
        }
        Database.delete(leaves, false);
        System.debug('Deleted ' + leaves.size() + ' ProductCategory leaf row(s) under demo catalog ' + catalogCode + '.');
    }
    delete demoCatalog;
    System.debug('Deleted ProductCatalog ' + catalogCode + '.');
}

for (String classificationCode : DEMO_CLASSIFICATION_CODES) {
    List<ProductClassification> demoClass = [
        SELECT Id
        FROM ProductClassification
        WHERE Code = :classificationCode
        LIMIT 1
    ];
    if (!demoClass.isEmpty()) {
        Database.delete(demoClass, false);
        System.debug('Deleted ProductClassification ' + classificationCode + ' (if no FK block).');
    }
}

List<UsageGrantRenewalPolicy> renewDemo = [
    SELECT Id FROM UsageGrantRenewalPolicy WHERE Code = 'SF-DEMO-USG-RENEW' LIMIT 1
];
if (!renewDemo.isEmpty()) {
    Database.delete(renewDemo, false);
}
List<UsageGrantRolloverPolicy> rollDemo = [
    SELECT Id FROM UsageGrantRolloverPolicy WHERE Code = 'SF-DEMO-USG-ROLL' LIMIT 1
];
if (!rollDemo.isEmpty()) {
    Database.delete(rollDemo, false);
}

for (List<String> stack : DEMO_BILLING_STACKS) {
    String demoBillingPolicy = stack[0];
    String demoBillingTreatment = stack[1];
    String demoLegalEntity = stack[2];
    List<BillingTreatmentItem> btis = [
        SELECT Id FROM BillingTreatmentItem WHERE BillingTreatment.Name = :demoBillingTreatment
    ];
    if (!btis.isEmpty()) {
        Database.delete(btis, false);
    }
    List<BillingTreatment> bts = [
        SELECT Id
        FROM BillingTreatment
        WHERE Name = :demoBillingTreatment AND BillingPolicy.Name = :demoBillingPolicy
    ];
    if (!bts.isEmpty()) {
        Database.delete(bts, false);
    }
    List<BillingPolicy> bps = [SELECT Id FROM BillingPolicy WHERE Name = :demoBillingPolicy LIMIT 1];
    if (!bps.isEmpty()) {
        Database.delete(bps, false);
    }
    List<LegalEntity> les = [SELECT Id FROM LegalEntity WHERE Name = :demoLegalEntity LIMIT 1];
    if (!les.isEmpty()) {
        Database.delete(les, false);
    }
}

// customer-template-billing demo payment terms (e.g. APTIM Demo Net 30) — not tied to BillingPolicy
List<PaymentTerm> demoTerms = [SELECT Id FROM PaymentTerm WHERE Name = 'APTIM Demo Net 30' LIMIT 1];
if (!demoTerms.isEmpty()) {
    List<PaymentTermItem> ptiApt = [
        SELECT Id FROM PaymentTermItem WHERE PaymentTermId = :demoTerms[0].Id
    ];
    if (!ptiApt.isEmpty()) {
        Database.delete(ptiApt, false);
    }
    Database.delete(demoTerms, false);
    System.debug('Deleted PaymentTerm APTIM Demo Net 30 (if no FK block).');
}

System.debug('deleteCustomerDemoCatalogData: finished.');
