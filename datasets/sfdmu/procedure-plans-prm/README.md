# procedure-plans-prm Data Plan

PRM-only overlay for `RLM_Quote_Pricing_Procedure_Plan`.

This dataset is intentionally scoped to run **only when PRM is enabled**. It
adds and configures the PRM conditional branch in the existing procedure plan:

- Section `IFPartnerDistributorOnQuote` (`RuleBased`, sequence 2)
- Option to run `RLM_PRM_DISTI_Pricing_Procedure` with `CriteriaLogic=1`
- Criterion: `PartnerAccount.BillingAddress IsNotNull`
- Reorders `HeaderDistribution` to sequence 3 for PRM parity with source org

The default shared dataset (`datasets/sfdmu/procedure-plans`) remains
unchanged and continues to run by default in `prepare_procedureplans`.

## Flow behavior and guardrails

The PRM overlay runs in `prepare_prm_pricing` when `prm=true`,
`prm_pricing=true`, and `procedureplans=true`.

To avoid silent partial overlays, the flow now:

1. deactivates the Procedure Plan version
2. waits until deactivation is confirmed (`IsActive=false`)
3. runs `insert_prm_procedure_plan_data`
   - pass 1 moves `HeaderDistribution` from sequence 2 to 3
   - pass 2 inserts `IFPartnerDistributorOnQuote` at sequence 2
   - pass 3 wires the PRM procedure option
   - pass 4 wires the PRM criterion
4. runs `verify_prm_procedure_plan_overlay` (fails loudly if records are missing)
5. reactivates the Procedure Plan version

The section move and insert are intentionally split into separate passes. On a
clean org, the shared procedure-plan dataset creates `HeaderDistribution` at
sequence 2. The PRM branch must move that existing section before inserting the
new PRM section at sequence 2, otherwise the first run can partially apply and
only succeed on a rerun.

If verification fails, rerun `insert_prm_procedure_plan_data` and inspect
SFDMU reports under this dataset directory to identify the missing record(s).

## Object Sets

| Pass | Object | Operation | External ID | Records |
| ---- | ------ | --------- | ----------- | ------- |
| 1 | `ProcedurePlanDefinitionVersion` | Readonly | `DeveloperName` | 1 |
| 1 | `ProcedurePlanSection` | Upsert | `SubSectionType` | 1 |
| 2 | `ProcedurePlanDefinitionVersion` | Readonly | `DeveloperName` | 1 |
| 2 | `ProcedurePlanSection` | Upsert | `SubSectionType` | 1 |
| 3 | `ProcedurePlanSection` | Readonly | `SubSectionType` | 1 |
| 3 | `ExpressionSetDefinition` | Readonly | `DeveloperName` | 1 |
| 3 | `ProcedurePlanOption` | Upsert | `ProcedurePlanSection.SubSectionType;Priority` | 1 |
| 4 | `ProcedurePlanOption` | Readonly | `ProcedurePlanSection.SubSectionType;Priority` | 1 |
| 4 | `ProcedurePlanCriterion` | Upsert | `ProcedurePlanOption.ProcedurePlanSection.SubSectionType;ProcedurePlanOption.Priority;Sequence` | 1 |

## Known SFDMU v5 Constraints

`python scripts/validate_sfdmu_v5_datasets.py` currently reports medium-risk
nested relationship warnings for the `ProcedurePlanCriterion` external ID
(`ProcedurePlanOption.ProcedurePlanSection.SubSectionType;ProcedurePlanOption.Priority;Sequence`).
The plan also uses traversal keys for `ProcedurePlanOption` because the stable
business key is the parent section plus priority, not an autonumbered direct
field.

These Upserts are accepted here because the overlay is tiny, feature-owned, and
guarded by the deactivate/load/verify/reactivate flow above. If SFDMU fails to
resolve one of the traversal keys, `verify_prm_procedure_plan_overlay` fails
loudly before the procedure plan is reactivated.
