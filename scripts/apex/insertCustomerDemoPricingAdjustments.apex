/**
 * insertCustomerDemoPricingAdjustments.apex
 *
 * Inserts AttributeAdjustmentCondition (AAC) and AttributeBasedAdjustment (ABA)
 * records for the customer-demo AttributeBasedAdjRules (Name LIKE 'SFDC-%').
 *
 * Salesforce demo pricing — Success Plan attribute on Sales Cloud Core:
 *   SFDC-CORE-PREMIER    Success Plan equals Premier   → Percentage +30 (Term Annual)
 *   SFDC-CORE-SIGNATURE  Success Plan equals Signature → Percentage +60 (Term Annual)
 * The third picklist value, Standard, has no rule and sells at the list price.
 *
 * Why Apex instead of SFDMU?
 * For Insert operations SFDMU resolves FK columns (ABR.Name → Id, AttrDef.Code → Id, etc.)
 * from the parent's SOURCE collection. Readonly parents are fetched into the TARGET
 * collection, so SOURCE is empty and every child row is silently filtered (SOURCE: 0) even
 * when the ABRs exist in the org. Apex resolves the FKs explicitly via SOQL.
 *
 * Run AFTER insert_customer_demo_pricing_data (ABRs must already exist).
 * Wired as CCI task insert_customer_demo_pricing_adjustments.
 */

// ─── Parent record lookup ──────────────────────────────────────────────────

Map<String, Id> abrMap = new Map<String, Id>();
for (AttributeBasedAdjRule r : [
    SELECT Id, Name FROM AttributeBasedAdjRule WHERE Name LIKE 'SFDC-%'
]) {
    abrMap.put(r.Name, r.Id);
}

Set<String> requiredRules = new Set<String>{'SFDC-CORE-PREMIER', 'SFDC-CORE-SIGNATURE'};
if (!abrMap.keySet().containsAll(requiredRules)) {
    System.debug(
        'insertCustomerDemoPricingAdjustments: expected ' + requiredRules +
        ' but found ' + abrMap.keySet() +
        ' — run insert_customer_demo_pricing_data first. Skipping.'
    );
    return;
}

List<AttributeDefinition> attrDefs = [
    SELECT Id FROM AttributeDefinition WHERE Code = 'SFDC-SVC-PLAN' LIMIT 1
];
if (attrDefs.isEmpty()) {
    System.debug('insertCustomerDemoPricingAdjustments: AttributeDefinition SFDC-SVC-PLAN not found — run PCM first. Skipping.');
    return;
}
Id attrDefId = attrDefs[0].Id;

List<Product2> products = [
    SELECT Id FROM Product2 WHERE StockKeepingUnit = 'SFDC-SALES-CORE' LIMIT 1
];
if (products.isEmpty()) {
    System.debug('insertCustomerDemoPricingAdjustments: Product2 SFDC-SALES-CORE not found — run PCM first. Skipping.');
    return;
}
Id productId = products[0].Id;

Id pasId = [
    SELECT Id FROM PriceAdjustmentSchedule
    WHERE Name = 'Standard Attribute Based Adjustment' AND CurrencyIsoCode = 'USD'
    LIMIT 1
].Id;

Id psmId = [
    SELECT Id FROM ProductSellingModel
    WHERE Name = 'Term Annual' AND SellingModelType = 'TermDefined'
    LIMIT 1
].Id;

// ─── Idempotency check ─────────────────────────────────────────────────────

Integer existingAac = [
    SELECT COUNT() FROM AttributeAdjustmentCondition
    WHERE AttributeBasedAdjRule.Name LIKE 'SFDC-%'
];
Integer existingAba = [
    SELECT COUNT() FROM AttributeBasedAdjustment
    WHERE AttributeBasedAdjRule.Name LIKE 'SFDC-%'
];

if (existingAac > 0 || existingAba > 0) {
    System.debug(
        'insertCustomerDemoPricingAdjustments: found ' + existingAac +
        ' AAC and ' + existingAba + ' ABA records — already loaded, skipping.'
    );
    return;
}

// ─── AttributeAdjustmentCondition ─────────────────────────────────────────
// One condition per rule: Success Plan equals the value that triggers the rule.
// Operator must be the word 'equals' — '=' throws INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST.

List<AttributeAdjustmentCondition> aacs = new List<AttributeAdjustmentCondition>{
    new AttributeAdjustmentCondition(
        AttributeBasedAdjRuleId = abrMap.get('SFDC-CORE-PREMIER'),
        AttributeDefinitionId   = attrDefId,
        ProductId               = productId,
        Operator                = 'equals',
        StringValue             = 'Premier'
    ),
    new AttributeAdjustmentCondition(
        AttributeBasedAdjRuleId = abrMap.get('SFDC-CORE-SIGNATURE'),
        AttributeDefinitionId   = attrDefId,
        ProductId               = productId,
        Operator                = 'equals',
        StringValue             = 'Signature'
    )
};
insert aacs;
System.debug('insertCustomerDemoPricingAdjustments: inserted ' + aacs.size() + ' AAC records.');

// ─── AttributeBasedAdjustment ──────────────────────────────────────────────
// Percentage uplift on the 2340 USD Term Annual list price:
//   Premier   → +30% (mirrors Premier Success at 30% of net license fees)
//   Signature → +60% (quote-only in reality; demo estimate)
// Platform-computed fields (AttributeAdjConditionsHash, AttributeCount, PricingTerm,
// PricingTermUnit, ScheduleType, SellingModelType) are not writeable — omit them.

List<AttributeBasedAdjustment> abas = new List<AttributeBasedAdjustment>{
    new AttributeBasedAdjustment(
        AttributeBasedAdjRuleId  = abrMap.get('SFDC-CORE-PREMIER'),
        ProductId                = productId,
        ProductSellingModelId    = psmId,
        PriceAdjustmentScheduleId= pasId,
        AdjustmentType           = 'Percentage',
        AdjustmentValue          = 30,
        CurrencyIsoCode          = 'USD',
        EffectiveFrom            = Datetime.newInstanceGmt(2024, 1, 1, 0, 0, 0)
    ),
    new AttributeBasedAdjustment(
        AttributeBasedAdjRuleId  = abrMap.get('SFDC-CORE-SIGNATURE'),
        ProductId                = productId,
        ProductSellingModelId    = psmId,
        PriceAdjustmentScheduleId= pasId,
        AdjustmentType           = 'Percentage',
        AdjustmentValue          = 60,
        CurrencyIsoCode          = 'USD',
        EffectiveFrom            = Datetime.newInstanceGmt(2024, 1, 1, 0, 0, 0)
    )
};
insert abas;
System.debug('insertCustomerDemoPricingAdjustments: inserted ' + abas.size() + ' ABA records.');
