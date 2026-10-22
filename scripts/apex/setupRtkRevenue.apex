// Idempotent Rentokil revenue setup:
//  1. Service zones (ZIP / prefix → multiplier) for location pricing
//  2. Price book entries for RTK-* products
//  3. Required Initial Service ProductRelatedComponent on each plan
//  4. Initial Service milestone billing policy
//  5. Point BillRepair / re-service product billing policies from a QB template when present

final Map<String, Decimal> PRICES = new Map<String, Decimal>{
    'RTK-ESSENTIAL' => 45,
    'RTK-HOME-PROT' => 59,
    'RTK-HOME-PROT-PLUS' => 79,
    'RTK-TERMITE' => 39,
    'RTK-MOSQUITO' => 69,
    'RTK-INITIAL' => 199,
    'RTK-RESERVICE' => 149,
    'RTK-INSPECTION' => 0
};
final Set<String> EVERGREEN_SKUS = new Set<String>{
    'RTK-ESSENTIAL', 'RTK-HOME-PROT', 'RTK-HOME-PROT-PLUS', 'RTK-TERMITE', 'RTK-MOSQUITO'
};
final List<String> PLAN_SKUS = new List<String>{
    'RTK-ESSENTIAL', 'RTK-HOME-PROT', 'RTK-HOME-PROT-PLUS', 'RTK-TERMITE', 'RTK-MOSQUITO'
};

// --- Service zones ---
Map<String, RLM_RTK_Service_Zone__c> zoneByPrefix = new Map<String, RLM_RTK_Service_Zone__c>();
for (RLM_RTK_Service_Zone__c z : [
    SELECT Id, Postal_Code_Prefix__c FROM RLM_RTK_Service_Zone__c
    WHERE Postal_Code_Prefix__c IN ('606','60108','60140','605','600','604','601')
]) {
    zoneByPrefix.put(z.Postal_Code_Prefix__c, z);
}
List<RLM_RTK_Service_Zone__c> zoneUpserts = new List<RLM_RTK_Service_Zone__c>();
List<List<Object>> zoneSeed = new List<List<Object>>{
    new List<Object>{'Dense Chicago Metro', '606', 'DenseMetro', 0.95},
    new List<Object>{'Chicago Suburbs (Bloomingdale)', '60108', 'Suburb', 1.00},
    new List<Object>{'Chicago Suburbs prefix', '601', 'Suburb', 1.00},
    new List<Object>{'West Suburbs', '605', 'Suburb', 1.00},
    new List<Object>{'North Shore', '600', 'Suburb', 1.00},
    new List<Object>{'South Suburbs', '604', 'Exurban', 1.10},
    new List<Object>{'Rural Fox Valley', '60140', 'Rural', 1.20}
};
for (List<Object> row : zoneSeed) {
    String prefix = (String) row[1];
    RLM_RTK_Service_Zone__c zone = zoneByPrefix.containsKey(prefix)
        ? zoneByPrefix.get(prefix)
        : new RLM_RTK_Service_Zone__c(Postal_Code_Prefix__c = prefix);
    zone.Name = (String) row[0];
    zone.Zone_Code__c = (String) row[2];
    zone.Zone_Multiplier__c = (Decimal) row[3];
    zoneUpserts.add(zone);
}
upsert zoneUpserts Postal_Code_Prefix__c;

// --- Price book entries ---
ProductSellingModel evergreen;
ProductSellingModel oneTime;
for (ProductSellingModel m : [
    SELECT Id, Name, SellingModelType, PricingTermUnit FROM ProductSellingModel
    WHERE Status = 'Active' AND (
        (SellingModelType = 'Evergreen' AND (PricingTermUnit = 'Months' OR PricingTermUnit = 'Monthly' OR Name = 'Evergreen Monthly'))
        OR SellingModelType = 'OneTime'
    )
    ORDER BY Name
]) {
    if (m.SellingModelType == 'Evergreen' && evergreen == null) {
        evergreen = m;
    }
    if (m.SellingModelType == 'OneTime' && oneTime == null) {
        oneTime = m;
    }
}
if (evergreen == null || oneTime == null) {
    System.debug(LoggingLevel.ERROR, 'Missing Evergreen Monthly or OneTime ProductSellingModel');
} else {
    Pricebook2 standardBook = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
    Map<String, Id> productIdBySku = new Map<String, Id>();
    for (Product2 p : [SELECT Id, StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN :PRICES.keySet()]) {
        productIdBySku.put(p.StockKeepingUnit, p.Id);
    }
    Set<String> existingOptions = new Set<String>();
    for (ProductSellingModelOption o : [
        SELECT Product2.StockKeepingUnit, ProductSellingModelId FROM ProductSellingModelOption
        WHERE Product2.StockKeepingUnit IN :PRICES.keySet()
    ]) {
        existingOptions.add(o.Product2.StockKeepingUnit + ':' + o.ProductSellingModelId);
    }
    List<ProductSellingModelOption> newOptions = new List<ProductSellingModelOption>();
    for (String sku : PRICES.keySet()) {
        Id productId = productIdBySku.get(sku);
        if (productId == null) {
            continue;
        }
        Id modelId = EVERGREEN_SKUS.contains(sku) ? evergreen.Id : oneTime.Id;
        if (!existingOptions.contains(sku + ':' + modelId)) {
            newOptions.add(new ProductSellingModelOption(
                Product2Id = productId,
                ProductSellingModelId = modelId,
                IsDefault = true
            ));
        }
    }
    insert newOptions;

    Set<String> existingKeys = new Set<String>();
    for (PricebookEntry e : [
        SELECT Product2.StockKeepingUnit, ProductSellingModelId FROM PricebookEntry
        WHERE Product2.StockKeepingUnit IN :PRICES.keySet()
            AND Pricebook2Id = :standardBook.Id AND CurrencyIsoCode = 'USD'
    ]) {
        existingKeys.add(e.Product2.StockKeepingUnit + ':' + e.ProductSellingModelId);
    }
    List<PricebookEntry> newPrices = new List<PricebookEntry>();
    for (String sku : PRICES.keySet()) {
        Id productId = productIdBySku.get(sku);
        if (productId == null) {
            continue;
        }
        Id modelId = EVERGREEN_SKUS.contains(sku) ? evergreen.Id : oneTime.Id;
        if (existingKeys.contains(sku + ':' + modelId)) {
            continue;
        }
        newPrices.add(new PricebookEntry(
            Product2Id = productId,
            Pricebook2Id = standardBook.Id,
            ProductSellingModelId = modelId,
            CurrencyIsoCode = 'USD',
            UnitPrice = PRICES.get(sku),
            IsActive = true
        ));
    }
    insert newPrices;
    System.debug('Inserted ' + newPrices.size() + ' PricebookEntry rows');

    // Mark plans as Sets and attach required Initial Service (standard UI constraint path).
    // FieldQuote Apex always adds RTK-INITIAL even if this relationship step is skipped.
    try {
        List<Product2> planProducts = [
            SELECT Id, Type FROM Product2 WHERE StockKeepingUnit IN :PLAN_SKUS AND Type != 'Set'
        ];
        for (Product2 p : planProducts) {
            p.Type = 'Set';
        }
        update planProducts;

        Id initialId = productIdBySku.get('RTK-INITIAL');
        ProductRelationshipType setType;
        List<ProductRelationshipType> types = [
            SELECT Id FROM ProductRelationshipType WHERE Name = 'Set to Set Component Relationship' LIMIT 1
        ];
        if (types.isEmpty()) {
            setType = new ProductRelationshipType(
                Name = 'Set to Set Component Relationship',
                MainProductRoleCat = 'Set',
                AssociatedProductRoleCat = 'SetComponent'
            );
            insert setType;
        } else {
            setType = types[0];
        }
        if (initialId != null) {
            Set<Id> parentsWithInitial = new Set<Id>();
            for (ProductRelatedComponent c : [
                SELECT ParentProductId FROM ProductRelatedComponent
                WHERE ChildProductId = :initialId AND ParentProduct.StockKeepingUnit IN :PLAN_SKUS
            ]) {
                parentsWithInitial.add(c.ParentProductId);
            }
            List<ProductRelatedComponent> newComponents = new List<ProductRelatedComponent>();
            for (String sku : PLAN_SKUS) {
                Id parentId = productIdBySku.get(sku);
                if (parentId == null || parentsWithInitial.contains(parentId)) {
                    continue;
                }
                newComponents.add(new ProductRelatedComponent(
                    ParentProductId = parentId,
                    ChildProductId = initialId,
                    ProductRelationshipTypeId = setType.Id,
                    ParentSellingModelId = evergreen.Id,
                    ChildSellingModelId = oneTime.Id,
                    Quantity = 1,
                    MinQuantity = 1,
                    MaxQuantity = 1,
                    IsComponentRequired = true,
                    IsDefaultComponent = true,
                    IsQuantityEditable = false,
                    DoesBundlePriceIncludeChild = false,
                    QuoteVisibility = 'Always',
                    Sequence = 1
                ));
            }
            insert newComponents;
        }
    } catch (Exception e) {
        System.debug(LoggingLevel.WARN, 'Initial Service product relationship skipped: ' + e.getMessage());
    }
}

// --- Milestone billing for Initial Service ---
final String POLICY_NAME = 'Initial Treatment Milestone Billing Policy';
final String TREATMENT_NAME = 'Initial Treatment Milestone Billing Treatment';
final String ITEM_NAME = 'Initial Treatment Complete';

List<BillingPolicy> policies = [SELECT Id, Status, DefaultBillingTreatmentId FROM BillingPolicy WHERE Name = :POLICY_NAME LIMIT 1];
BillingPolicy policy;
if (policies.isEmpty()) {
    policy = new BillingPolicy(
        Name = POLICY_NAME,
        Status = 'Draft',
        BillingTreatmentSelection = 'Default',
        Description = 'Bill Initial Service and start subscription when the first treatment Work Order completes'
    );
    insert policy;
} else {
    policy = policies[0];
}

List<BillingTreatment> treatments = [SELECT Id, Status FROM BillingTreatment WHERE Name = :TREATMENT_NAME LIMIT 1];
BillingTreatment treatment;
if (treatments.isEmpty()) {
    treatment = new BillingTreatment(
        Name = TREATMENT_NAME,
        BillingPolicyId = policy.Id,
        IsMilestoneBilling = true,
        ExcludeFromBilling = 'No',
        CanChangeBillingFrequency = false,
        Status = 'Draft'
    );
    insert treatment;
} else {
    treatment = treatments[0];
}

List<BillingTreatmentItem> items = [
    SELECT Id, Status FROM BillingTreatmentItem
    WHERE BillingTreatmentId = :treatment.Id AND Name = :ITEM_NAME LIMIT 1
];
BillingTreatmentItem item;
if (items.isEmpty()) {
    item = new BillingTreatmentItem(
        Name = ITEM_NAME,
        BillingTreatmentId = treatment.Id,
        Type = 'Percentage',
        Percentage = 100,
        MilestoneType = 'Event',
        BillingType = 'None',
        Controller = 'None',
        Handling0Amount = 'None',
        Sequencing = 'None',
        ProcessingOrder = 1,
        Status = 'Draft',
        Description = 'Bill 100% when the initial treatment Work Order is completed'
    );
    insert item;
} else {
    item = items[0];
}

if (item.Status != 'Active') {
    item.Status = 'Active';
    update item;
}
if (treatment.Status != 'Active') {
    treatment.Status = 'Active';
    update treatment;
}
if (policy.DefaultBillingTreatmentId != treatment.Id || policy.Status != 'Active') {
    policy.DefaultBillingTreatmentId = treatment.Id;
    policy.Status = 'Active';
    update policy;
}

List<Product2> initialProducts = [
    SELECT Id, BillingPolicyId FROM Product2
    WHERE StockKeepingUnit = 'RTK-INITIAL' AND BillingPolicyId != :policy.Id
];
for (Product2 p : initialProducts) {
    p.BillingPolicyId = policy.Id;
}
update initialProducts;

// Copy tax / billing policy from a known-good product onto all RTK catalog products
List<Product2> template = [
    SELECT BillingPolicyId, TaxPolicyId FROM Product2
    WHERE StockKeepingUnit IN ('QB-SVC-REPAIR', 'QB-SRV-OG-PSH') AND BillingPolicyId != null
    ORDER BY CreatedDate DESC LIMIT 1
];
if (!template.isEmpty()) {
    List<Product2> toUpdate = [
        SELECT Id, BillingPolicyId, TaxPolicyId FROM Product2
        WHERE StockKeepingUnit LIKE 'RTK-%'
    ];
    for (Product2 p : toUpdate) {
        if (p.BillingPolicyId == null) {
            p.BillingPolicyId = template[0].BillingPolicyId;
        }
        if (p.TaxPolicyId == null) {
            p.TaxPolicyId = template[0].TaxPolicyId;
        }
    }
    update toUpdate;
}

System.debug('setupRtkRevenue complete: zones=' + zoneUpserts.size());
