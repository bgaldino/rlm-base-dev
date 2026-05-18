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

## Flow behavior and guardrails

The PRM overlay runs in `prepare_prm_pricing` when both `prm=true` and
`procedureplans=true`.

To avoid silent partial overlays, the flow now:

1. deactivates the Procedure Plan version
2. waits until deactivation is confirmed (`IsActive=false`)
3. runs `insert_prm_procedure_plan_data`
4. runs `verify_prm_procedure_plan_overlay` (fails loudly if records are missing)
5. reactivates the Procedure Plan version

If verification fails, rerun `insert_prm_procedure_plan_data` and inspect
SFDMU reports under this dataset directory to identify the missing record(s).
