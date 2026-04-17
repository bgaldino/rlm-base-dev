// Delete customer-demo usage rating slice (Snowflake SF-* / OC-* usage SKUs, SF-UR-* / OC-UR-*),
// including ProductUsageGrant, ProductUsageResourcePolicy, PUR, then UsageResource.
// Does not delete shared UnitOfMeasure / UnitOfMeasureClass rows or UsageResourceBillingPolicy (monthlypeak / monthlytotal).
//
// Run before insert_customer_demo_rating_data for idempotent reloads.
// Prerequisite: remove CD-DEMO rate card entries first (delete_customer_demo_rates_data) — otherwise
// RateCardEntry rows block UsageResource delete.
// If delete fails on UsageResource with quote line item usage resource grants (QLIURG), remove or adjust
// those quote lines in the org, then retry.

final Set<String> demoProductSkus = new Set<String>{
    'SF-USG-STORAGE',
    'SF-USG-EGRESS',
    'SF-USG-COMPUTE',
    'SF-BLNG-STORAGE',
    'SF-BLNG-EGRESS',
    'SF-BLNG-COMPUTE',
    'OC-USG-GREEN-ROUNDS',
    'OC-BLNG-GREEN'
};
final Set<String> demoUsageResourceCodes = new Set<String>{
    'SF-UR-STORAGE',
    'SF-UR-EGRESS',
    'SF-UR-COMPUTE',
    'OC-UR-GREEN'
};
List<Product2> demoProducts = [
    SELECT Id FROM Product2 WHERE StockKeepingUnit IN :demoProductSkus
];
Set<Id> demoProductIds = new Map<Id, Product2>(demoProducts).keySet();

if (!demoProductIds.isEmpty()) {
    Set<Id> demoPurIds = new Set<Id>();
    for (ProductUsageResource pur : [
        SELECT Id FROM ProductUsageResource WHERE ProductId IN :demoProductIds
    ]) {
        demoPurIds.add(pur.Id);
    }

    List<ProductUsageGrant> pugs;
    if (demoPurIds.isEmpty()) {
        pugs = [
            SELECT Id, Status
            FROM ProductUsageGrant
            WHERE UsageDefinitionProductId IN :demoProductIds
        ];
    } else {
        pugs = [
            SELECT Id, Status
            FROM ProductUsageGrant
            WHERE UsageDefinitionProductId IN :demoProductIds
               OR ProductUsageResourceId IN :demoPurIds
        ];
    }
    if (!pugs.isEmpty()) {
        List<ProductUsageGrant> toDeactivate = new List<ProductUsageGrant>();
        for (ProductUsageGrant p : pugs) {
            if (p.Status == 'Active') {
                toDeactivate.add(p);
            }
        }
        for (ProductUsageGrant p : toDeactivate) {
            p.Status = 'Inactive';
        }
        if (!toDeactivate.isEmpty()) {
            Database.update(toDeactivate, false);
        }
        delete pugs;
        System.debug('Deleted ' + pugs.size() + ' demo ProductUsageGrant record(s).');
    }

    if (!demoPurIds.isEmpty()) {
        List<ProductUsageResourcePolicy> purps = [
            SELECT Id
            FROM ProductUsageResourcePolicy
            WHERE ProductUsageResourceId IN :demoPurIds
        ];
        if (!purps.isEmpty()) {
            delete purps;
            System.debug('Deleted ' + purps.size() + ' demo ProductUsageResourcePolicy record(s).');
        }
    }

    for (Integer pass = 1; pass <= 5; pass++) {
        List<ProductUsageResource> activePurs = [
            SELECT Id, Status
            FROM ProductUsageResource
            WHERE ProductId IN :demoProductIds AND Status = 'Active'
        ];
        if (activePurs.isEmpty()) {
            break;
        }
        for (ProductUsageResource p : activePurs) {
            p.Status = 'Inactive';
        }
        Database.update(activePurs, false);
    }

    List<ProductUsageResource> purs = [
        SELECT Id FROM ProductUsageResource WHERE ProductId IN :demoProductIds
    ];
    if (!purs.isEmpty()) {
        delete purs;
        System.debug('Deleted ' + purs.size() + ' demo ProductUsageResource record(s).');
    }
} else {
    System.debug('No SF-* demo usage products — skipped PUR/PUG/PURP cleanup.');
}

List<UsageResource> demoUrs = [
    SELECT Id, Status FROM UsageResource WHERE Code IN :demoUsageResourceCodes
];
if (!demoUrs.isEmpty()) {
    List<UsageResource> activeUr = new List<UsageResource>();
    for (UsageResource ur : demoUrs) {
        if (ur.Status == 'Active') {
            activeUr.add(ur);
        }
    }
    for (UsageResource ur : activeUr) {
        ur.Status = 'Inactive';
    }
    if (!activeUr.isEmpty()) {
        update activeUr;
    }
    delete demoUrs;
    System.debug('Deleted ' + demoUrs.size() + ' demo UsageResource record(s).');
}

System.debug('Customer demo rating cleanup complete.');
