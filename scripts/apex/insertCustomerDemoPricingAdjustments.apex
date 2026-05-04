/**
 * insertCustomerDemoPricingAdjustments.apex
 *
 * Inserts AttributeAdjustmentCondition (AAC) and AttributeBasedAdjustment (ABA)
 * records for all customer-demo AttributeBasedAdjRules (Name LIKE 'OAI-%').
 *
 * Why Apex instead of SFDMU?
 * SFDMU parallelizes all objectSet data fetching before any inserts are committed.
 * Even with a separate two-phase SFDMU run, the Readonly FK resolution for
 * relationship-traversal columns (ABR.Name → Id, AttrDef.Code → Id, etc.) does
 * not correctly map to real Salesforce IDs in the INSERT payload — SFDMU reports
 * SOURCE:0 for AAC/ABA despite populated CSVs. Apex resolves IDs explicitly and
 * is fully idempotent (skips if records already exist).
 *
 * Run AFTER insert_customer_demo_pricing_data (ABRs must already exist).
 * Wired as CCI task insert_customer_demo_pricing_adjustments.
 */

// ─── Parent record lookup ──────────────────────────────────────────────────

Map<String, Id> abrMap = new Map<String, Id>();
for (AttributeBasedAdjRule r : [
    SELECT Id, Name FROM AttributeBasedAdjRule WHERE Name LIKE 'OAI-%'
]) {
    abrMap.put(r.Name, r.Id);
}

if (abrMap.isEmpty()) {
    System.debug('insertCustomerDemoPricingAdjustments: no OAI-* ABRs found — skipping.');
    return;
}

Id attrDefId = [
    SELECT Id FROM AttributeDefinition WHERE Code = 'OAI-MODEL-TIER' LIMIT 1
].Id;

Map<String, Id> productMap = new Map<String, Id>();
for (Product2 p : [
    SELECT Id, StockKeepingUnit FROM Product2
    WHERE StockKeepingUnit IN ('OAI-API-DEV', 'OAI-API-ENT')
]) {
    productMap.put(p.StockKeepingUnit, p.Id);
}

Id pasId = [
    SELECT Id FROM PriceAdjustmentSchedule
    WHERE Name = 'Standard Attribute Based Adjustment' AND CurrencyIsoCode = 'USD'
    LIMIT 1
].Id;

Map<String, Id> psmMap = new Map<String, Id>();
for (ProductSellingModel m : [
    SELECT Id, Name FROM ProductSellingModel
    WHERE Name IN ('Term Monthly', 'Term Annual')
]) {
    psmMap.put(m.Name, m.Id);
}

// ─── Idempotency check ─────────────────────────────────────────────────────

Integer existingAac = [
    SELECT COUNT() FROM AttributeAdjustmentCondition
    WHERE AttributeBasedAdjRule.Name LIKE 'OAI-%'
];
Integer existingAba = [
    SELECT COUNT() FROM AttributeBasedAdjustment
    WHERE AttributeBasedAdjRule.Name LIKE 'OAI-%'
];

if (existingAac > 0 || existingAba > 0) {
    System.debug(
        'insertCustomerDemoPricingAdjustments: found ' + existingAac +
        ' AAC and ' + existingAba + ' ABA records — already loaded, skipping.'
    );
    return;
}

// ─── AttributeAdjustmentCondition ─────────────────────────────────────────
// One condition per rule: attribute equals the tier value that triggers the rule.

List<AttributeAdjustmentCondition> aacs = new List<AttributeAdjustmentCondition>{
    new AttributeAdjustmentCondition(
        AttributeBasedAdjRuleId = abrMap.get('OAI-API-DEV-FRONTIER'),
        AttributeDefinitionId   = attrDefId,
        ProductId               = productMap.get('OAI-API-DEV'),
        Operator                = 'equals',
        StringValue             = 'Frontier'
    ),
    new AttributeAdjustmentCondition(
        AttributeBasedAdjRuleId = abrMap.get('OAI-API-ENT-EFFICIENT'),
        AttributeDefinitionId   = attrDefId,
        ProductId               = productMap.get('OAI-API-ENT'),
        Operator                = 'equals',
        StringValue             = 'Efficient'
    ),
    new AttributeAdjustmentCondition(
        AttributeBasedAdjRuleId = abrMap.get('OAI-API-ENT-FRONTIER'),
        AttributeDefinitionId   = attrDefId,
        ProductId               = productMap.get('OAI-API-ENT'),
        Operator                = 'equals',
        StringValue             = 'Frontier'
    )
};
insert aacs;
System.debug('insertCustomerDemoPricingAdjustments: inserted ' + aacs.size() + ' AAC records.');

// ─── AttributeBasedAdjustment ──────────────────────────────────────────────
// Percentage adjustments on list price per rule:
//   DEV Frontier  → +25% (Percentage, monthly)
//   ENT Efficient → -15% (Percentage, annual)
//   ENT Frontier  → +30% (Percentage, annual)

List<AttributeBasedAdjustment> abas = new List<AttributeBasedAdjustment>{
    new AttributeBasedAdjustment(
        AttributeBasedAdjRuleId  = abrMap.get('OAI-API-DEV-FRONTIER'),
        ProductId                = productMap.get('OAI-API-DEV'),
        ProductSellingModelId    = psmMap.get('Term Monthly'),
        PriceAdjustmentScheduleId= pasId,
        AdjustmentType           = 'Percentage',
        AdjustmentValue          = 25,
        CurrencyIsoCode          = 'USD',
        EffectiveFrom            = Date.valueOf('2024-01-01')
    ),
    new AttributeBasedAdjustment(
        AttributeBasedAdjRuleId  = abrMap.get('OAI-API-ENT-EFFICIENT'),
        ProductId                = productMap.get('OAI-API-ENT'),
        ProductSellingModelId    = psmMap.get('Term Annual'),
        PriceAdjustmentScheduleId= pasId,
        AdjustmentType           = 'Percentage',
        AdjustmentValue          = -15,
        CurrencyIsoCode          = 'USD',
        EffectiveFrom            = Date.valueOf('2024-01-01')
    ),
    new AttributeBasedAdjustment(
        AttributeBasedAdjRuleId  = abrMap.get('OAI-API-ENT-FRONTIER'),
        ProductId                = productMap.get('OAI-API-ENT'),
        ProductSellingModelId    = psmMap.get('Term Annual'),
        PriceAdjustmentScheduleId= pasId,
        AdjustmentType           = 'Percentage',
        AdjustmentValue          = 30,
        CurrencyIsoCode          = 'USD',
        EffectiveFrom            = Date.valueOf('2024-01-01')
    )
};
insert abas;
System.debug('insertCustomerDemoPricingAdjustments: inserted ' + abas.size() + ' ABA records.');
