// Delete customer-demo attribute-based pricing records scoped to OAI-* rules.
// Safe to run even when QB pricing data coexists in the same org — WHERE clause is name-scoped.
//
// AttributeAdjustmentCondition is a master-detail child of AttributeBasedAdjRule with
// cascade delete — direct DML Delete on AAC is not permitted. Deletion order:
//   1. AttributeBasedAdjustment (no cascade from ABR; must be deleted explicitly first)
//   2. AttributeBasedAdjRule (cascades AttributeAdjustmentCondition automatically)
//
// Runs as step 8 of prepare_customer_demo_catalog (delete_customer_demo_pricing_data)
// before the SFDMU Insert of the same objects in step 9.

List<AttributeBasedAdjRule> rules = [
    SELECT Id FROM AttributeBasedAdjRule WHERE Name LIKE 'OAI-%'
];

if (rules.isEmpty()) {
    System.debug('deleteCustomerDemoPricingData: no OAI-* AttributeBasedAdjRule rows — nothing to delete.');
    return;
}

Set<Id> ruleIds = new Map<Id, AttributeBasedAdjRule>(rules).keySet();

// AttributeBasedAdjustment does NOT cascade from ABR — delete explicitly first.
List<AttributeBasedAdjustment> abas = [
    SELECT Id FROM AttributeBasedAdjustment WHERE AttributeBasedAdjRuleId IN :ruleIds
];
if (!abas.isEmpty()) {
    delete abas;
    System.debug('deleteCustomerDemoPricingData: deleted ' + abas.size() + ' AttributeBasedAdjustment row(s).');
}

// Deleting AttributeBasedAdjRule cascades AttributeAdjustmentCondition (master-detail).
delete rules;
System.debug('deleteCustomerDemoPricingData: deleted ' + rules.size() + ' AttributeBasedAdjRule row(s) (AAC cascade).');
