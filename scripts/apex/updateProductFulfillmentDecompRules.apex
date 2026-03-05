// TEMPORARY FIX (260 bug): ExecuteOnRuleId is not created on INSERT, only on UPDATE.
// Affects ProductFulfillmentDecompRule, ProductFulfillmentScenario, FulfillmentStepDefinition,
// FulfillmentTaskAssignmentRule. Re-saving triggers ruleset generation. (#rlm-office-hours)
List<ProductFulfillmentDecompRule> rules = [SELECT Id FROM ProductFulfillmentDecompRule];
update rules;
