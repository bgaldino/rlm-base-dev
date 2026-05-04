// Delete customer-demo DRO records scoped to OAI-* prefix.
// Safe to run when QB DRO data coexists in the same org — WHERE clause is name-scoped.
//
// Both ProductFulfillmentDecompRule and ProductFulfillmentScenario are standalone records
// with no master-detail cascade relationships — both can be deleted via direct DML.
//
// Product2.DecompositionScope is intentionally NOT reset — the SFDMU Update operation in
// insert_customer_demo_dro_data will overwrite it on re-run. Resetting it here would cause
// a brief window where products have no decomposition scope if delete runs without a
// follow-up insert.
//
// Runs as step 11 of prepare_customer_demo_catalog (delete_customer_demo_dro_data)
// before the SFDMU Upsert in step 12.

List<ProductFulfillmentScenario> scenarios = [
    SELECT Id FROM ProductFulfillmentScenario WHERE Name LIKE 'OAI %'
];

if (!scenarios.isEmpty()) {
    delete scenarios;
    System.debug('deleteCustomerDemoDROData: deleted ' + scenarios.size() + ' ProductFulfillmentScenario row(s).');
} else {
    System.debug('deleteCustomerDemoDROData: no OAI ProductFulfillmentScenario rows — nothing to delete.');
}

List<ProductFulfillmentDecompRule> rules = [
    SELECT Id FROM ProductFulfillmentDecompRule WHERE Name LIKE 'OAI %'
];

if (!rules.isEmpty()) {
    delete rules;
    System.debug('deleteCustomerDemoDROData: deleted ' + rules.size() + ' ProductFulfillmentDecompRule row(s).');
} else {
    System.debug('deleteCustomerDemoDROData: no OAI ProductFulfillmentDecompRule rows — nothing to delete.');
}
