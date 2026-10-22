// Revenue setup for the FSL demo (idempotent):
//  1. One-time catalog products: Installation and Assembly (QB-INST-1000, quoted with the hardware) and
//     Break/Fix Repair Service (QB-SVC-REPAIR, billed by RLM_FSL_BillRepair when a repair isn't covered).
//  2. Installation milestone billing: hardware and install lines billed under this policy wait in
//     WaitingForMilestoneEventAccomplishment until RLM_FSL_Complete_Fulfillment_Step accomplishes
//     the "Installation Complete" milestone.
// Active billing treatments cannot be deleted, so records are looked up by name and reused.
// New prices are visible to pricing only after the pricing decision tables are refreshed.

final String INSTALL_SKU = 'QB-INST-1000';
final String REPAIR_SKU = 'QB-SVC-REPAIR';
final String POLICY_TEMPLATE_SKU = 'QB-SRV-OG-PSH';
final Map<String, Decimal> PRICES = new Map<String, Decimal>{ INSTALL_SKU => 2500, REPAIR_SKU => 1200 };
final String POLICY_NAME = 'Installation Milestone Billing Policy';
final String TREATMENT_NAME = 'Installation Milestone Billing Treatment';
final String ITEM_NAME = 'Installation Complete';
final Set<String> MILESTONE_SKUS = new Set<String>{ 'QB-BDL-R750', 'QB-BDL-RAXS', INSTALL_SKU };

if ([SELECT COUNT() FROM Product2 WHERE StockKeepingUnit = :REPAIR_SKU] == 0) {
    Product2 template = [SELECT BillingPolicyId, TaxPolicyId FROM Product2 WHERE StockKeepingUnit = :POLICY_TEMPLATE_SKU LIMIT 1];
    insert new Product2(Name = 'Break/Fix Repair Service', StockKeepingUnit = REPAIR_SKU, ProductCode = REPAIR_SKU,
        Family = 'Services', IsActive = true, BillingPolicyId = template.BillingPolicyId, TaxPolicyId = template.TaxPolicyId,
        Description = 'On-site diagnosis and repair of QuantumBit hardware not covered by a maintenance entitlement.');
}

ProductSellingModel oneTime = [SELECT Id FROM ProductSellingModel WHERE SellingModelType = 'OneTime' AND Status = 'Active' LIMIT 1];
ProductCategory services = [SELECT Id FROM ProductCategory WHERE Name = 'Services' AND Catalog.Name = 'QuantumBit Services' LIMIT 1];
Pricebook2 standardBook = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
Map<Id, String> skuById = new Map<Id, String>();
for (Product2 p : [SELECT Id, StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN :PRICES.keySet()]) {
    skuById.put(p.Id, p.StockKeepingUnit);
}
Set<Id> hasOption = new Set<Id>();
for (ProductSellingModelOption o : [SELECT Product2Id FROM ProductSellingModelOption
        WHERE Product2Id IN :skuById.keySet() AND ProductSellingModelId = :oneTime.Id]) {
    hasOption.add(o.Product2Id);
}
Set<Id> inCategory = new Set<Id>();
for (ProductCategoryProduct c : [SELECT ProductId FROM ProductCategoryProduct
        WHERE ProductId IN :skuById.keySet() AND ProductCategoryId = :services.Id]) {
    inCategory.add(c.ProductId);
}
Set<Id> hasPrice = new Set<Id>();
for (PricebookEntry e : [SELECT Product2Id FROM PricebookEntry WHERE Product2Id IN :skuById.keySet()
        AND Pricebook2Id = :standardBook.Id AND CurrencyIsoCode = 'USD' AND ProductSellingModelId = :oneTime.Id]) {
    hasPrice.add(e.Product2Id);
}
List<ProductSellingModelOption> newOptions = new List<ProductSellingModelOption>();
List<ProductCategoryProduct> newCategories = new List<ProductCategoryProduct>();
List<PricebookEntry> newPrices = new List<PricebookEntry>();
for (Id productId : skuById.keySet()) {
    if (!hasOption.contains(productId)) {
        newOptions.add(new ProductSellingModelOption(Product2Id = productId, ProductSellingModelId = oneTime.Id, IsDefault = true));
    }
    if (!inCategory.contains(productId)) {
        newCategories.add(new ProductCategoryProduct(ProductId = productId, ProductCategoryId = services.Id));
    }
    if (!hasPrice.contains(productId)) {
        newPrices.add(new PricebookEntry(Product2Id = productId, Pricebook2Id = standardBook.Id, CurrencyIsoCode = 'USD',
            ProductSellingModelId = oneTime.Id, UnitPrice = PRICES.get(skuById.get(productId)), IsActive = true));
    }
}
insert newOptions;
insert newCategories;
insert newPrices;

List<BillingPolicy> policies = [SELECT Id, Status, DefaultBillingTreatmentId FROM BillingPolicy WHERE Name = :POLICY_NAME LIMIT 1];
BillingPolicy policy;
if (policies.isEmpty()) {
    policy = new BillingPolicy(Name = POLICY_NAME, Status = 'Draft', BillingTreatmentSelection = 'Default',
        Description = 'Bill hardware when Field Service completes the installation');
    insert policy;
} else {
    policy = policies[0];
}

List<BillingTreatment> treatments = [SELECT Id, Status FROM BillingTreatment WHERE Name = :TREATMENT_NAME LIMIT 1];
BillingTreatment treatment;
if (treatments.isEmpty()) {
    treatment = new BillingTreatment(Name = TREATMENT_NAME, BillingPolicyId = policy.Id, IsMilestoneBilling = true,
        ExcludeFromBilling = 'No', CanChangeBillingFrequency = false, Status = 'Draft');
    insert treatment;
} else {
    treatment = treatments[0];
}

List<BillingTreatmentItem> items = [SELECT Id, Status FROM BillingTreatmentItem
    WHERE BillingTreatmentId = :treatment.Id AND Name = :ITEM_NAME LIMIT 1];
BillingTreatmentItem item;
if (items.isEmpty()) {
    item = new BillingTreatmentItem(Name = ITEM_NAME, BillingTreatmentId = treatment.Id, Type = 'Percentage',
        Percentage = 100, MilestoneType = 'Event', BillingType = 'None', Controller = 'None',
        Handling0Amount = 'None', Sequencing = 'None', ProcessingOrder = 1, Status = 'Draft',
        Description = 'Bill 100% when the installation Work Order is completed');
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

List<Product2> hardware = [SELECT Id, BillingPolicyId FROM Product2
    WHERE StockKeepingUnit IN :MILESTONE_SKUS AND BillingPolicyId != :policy.Id];
for (Product2 p : hardware) {
    p.BillingPolicyId = policy.Id;
}
update hardware;

System.debug('FSL revenue: policy ' + policy.Id + ', treatment ' + treatment.Id + ', item ' + item.Id
    + ', products moved to milestone billing ' + hardware.size() + ', new prices ' + newPrices.size());
