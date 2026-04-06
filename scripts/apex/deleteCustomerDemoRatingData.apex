// Delete customer-demo usage rating slice (CD-* SKUs and CD-UR-DATAXFR only).
// Does not delete shared UnitOfMeasure / UnitOfMeasureClass rows.
// Run before insert_customer_demo_rating_data for idempotent reloads.

final Set<String> demoProductSkus = new Set<String>{
    'CD-USG-DATA',
    'CD-DATA-THPT-BLNG'
};
final String demoUsageResourceCode = 'CD-UR-DATAXFR';
final String demoBillingPolicyCode = 'CD-DEMO-URBILL';

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
    System.debug('No CD-* demo products — skipped PUR/PUG/PURP cleanup.');
}

List<UsageResource> demoUrs = [
    SELECT Id, Status FROM UsageResource WHERE Code = :demoUsageResourceCode
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

List<UsageResourceBillingPolicy> bp = [
    SELECT Id, Status
    FROM UsageResourceBillingPolicy
    WHERE Code = :demoBillingPolicyCode
];
if (!bp.isEmpty()) {
    for (UsageResourceBillingPolicy pol : bp) {
        if (pol.Status == 'Active') {
            pol.Status = 'Inactive';
        }
    }
    update bp;
    delete bp;
    System.debug('Deleted demo UsageResourceBillingPolicy CD-DEMO-URBILL.');
}

System.debug('Customer demo rating cleanup complete.');
