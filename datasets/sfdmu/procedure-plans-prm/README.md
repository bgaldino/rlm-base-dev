# procedure-plans-prm Data Plan

PRM-only overlay for `RLM_Quote_Pricing_Procedure_Plan`.

This dataset is intentionally scoped to run **only when PRM is enabled**. It
adds and configures the PRM conditional branch in the existing procedure plan:

- Section `IFPartnerDistributorOnQuote` (`RuleBased`, sequence 2)
- Option to run `PRM_DISTI_Pricing_Procedure` with `CriteriaLogic=1`
- Criterion: `PartnerAccount.BillingAddress IsNotNull`
- Reorders `HeaderDistribution` to sequence 3 for PRM parity with source org

The default shared dataset (`datasets/sfdmu/procedure-plans`) remains
unchanged and continues to run by default in `prepare_procedureplans`.
