// Delete customer-template catalog slice: PCM scaffolding, demo Product2 rows, Standard PricebookEntry,
// and Snowflake-named billing foundation loaded by customer-template-billing.
//
// Prerequisites (run in order via purge_customer_demo_catalog flow):
//   1) customer_demo_purge_records — QLIURP / QLIURG / order grants
//   2) delete_customer_demo_rates_data — CD-DEMO rate cards
//   3) delete_customer_demo_rating_data — PUR/PUG/PURP/SF-UR-*
//
// Scope: Product2 where StockKeepingUnit matches SF-SNOW-%, SF-USG-%, or SF-BLNG-%;
// ProductCatalog Code = SF-DEMO-CAT; ProductClassification Code = SF-SW;
// demo UsageGrantRenewalPolicy / UsageGrantRolloverPolicy codes SF-DEMO-USG-*;
// billing records named in customer-template-billing CSVs.
//
// Does NOT delete: UnitOfMeasure / UnitOfMeasureClass (DATAVOL, SNFCRED), shared UsageResourceBillingPolicy
// (monthlypeak/monthlytotal), Default Usage Overage Policy, global RatingFrequencyPolicy, ProductSellingModel rows.
//
// Quote lines or order items referencing demo SKUs will block PricebookEntry/Product2 delete — remove those
// transaction rows first, then re-run this script.

final String DEMO_CATALOG_CODE = 'SF-DEMO-CAT';
final String DEMO_CLASSIFICATION_CODE = 'SF-SW';
final String DEMO_BILLING_POLICY = 'Snowflake Demo Billing Policy';
final String DEMO_LEGAL_ENTITY = 'Snowflake Demo Legal Entity - US';
final String DEMO_BILLING_TREATMENT = 'Snowflake Demo Billing Treatment - US';

List<Product2> demoProducts = [
    SELECT Id, Type, StockKeepingUnit
    FROM
        Product2
    WHERE
        (StockKeepingUnit LIKE 'SF-SNOW-%')
        OR (StockKeepingUnit LIKE 'SF-USG-%')
        OR (StockKeepingUnit LIKE 'SF-BLNG-%')
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

List<ProductCatalog> demoCatalog = [
    SELECT Id
    FROM ProductCatalog
    WHERE Code = :DEMO_CATALOG_CODE
    LIMIT 1
];
if (!demoCatalog.isEmpty()) {
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
        System.debug('Deleted ' + leaves.size() + ' ProductCategory leaf row(s) under demo catalog.');
    }
    delete demoCatalog;
    System.debug('Deleted ProductCatalog ' + DEMO_CATALOG_CODE + '.');
}

List<ProductClassification> demoClass = [
    SELECT Id
    FROM ProductClassification
    WHERE Code = :DEMO_CLASSIFICATION_CODE
    LIMIT 1
];
if (!demoClass.isEmpty()) {
    Database.delete(demoClass, false);
    System.debug('Deleted ProductClassification ' + DEMO_CLASSIFICATION_CODE + ' (if no FK block).');
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

List<BillingTreatmentItem> btis = [
    SELECT Id FROM BillingTreatmentItem WHERE BillingTreatment.Name = :DEMO_BILLING_TREATMENT
];
if (!btis.isEmpty()) {
    Database.delete(btis, false);
}
List<BillingTreatment> bts = [
    SELECT Id FROM BillingTreatment WHERE Name = :DEMO_BILLING_TREATMENT AND BillingPolicy.Name = :DEMO_BILLING_POLICY
];
if (!bts.isEmpty()) {
    Database.delete(bts, false);
}
List<BillingPolicy> bps = [SELECT Id FROM BillingPolicy WHERE Name = :DEMO_BILLING_POLICY LIMIT 1];
if (!bps.isEmpty()) {
    Database.delete(bps, false);
}
List<LegalEntity> les = [SELECT Id FROM LegalEntity WHERE Name = :DEMO_LEGAL_ENTITY LIMIT 1];
if (!les.isEmpty()) {
    Database.delete(les, false);
}

System.debug('deleteCustomerDemoCatalogData: finished.');
