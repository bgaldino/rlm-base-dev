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
4. runs `verify_prm_procedure_plan_overlay` (fails loudly if records are missing
   or duplicated)
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
guarded by the deactivate/load/verify/reactivate flow above. The verifier checks
for exactly one section, option, and criterion, so missing records and duplicate
inserts fail before the procedure plan is reactivated.

### Idempotency Validation

Run the guarded overlay sequence twice against a prepared PRM org:

```bash
cci task run deactivate_procedure_plan_version --org <org>
cci task run insert_prm_procedure_plan_data --org <org>
cci task run verify_prm_procedure_plan_overlay --org <org>
cci task run activate_procedure_plan_version --org <org>
```

After the second run, SOQL spot checks should confirm the same expected rows
still exist exactly once.

| Record Type | Query Scope | Expected Result |
| ----------- | ----------- | --------------- |
| `ProcedurePlanSection` | `SubSectionType = 'IFPartnerDistributorOnQuote'` on `RLM_Quote_Pricing_Procedure_Plan` | Exactly 1 |
| `ProcedurePlanOption` | Priority 1 option for `RLM_PRM_DISTI_Pricing_Procedure` under the PRM section | Exactly 1 |
| `ProcedurePlanCriterion` | Sequence 1 `PartnerAccount.BillingAddress IsNotNull` criterion under the PRM option | Exactly 1 |

`verify_prm_procedure_plan_overlay` enforces those exact counts and logs
`section=1 option=1 criterion=1` on success. The static validator still reports
medium nested-relationship warnings for the criterion external ID, but the
org-backed validation confirms this controlled overlay is idempotent when those
exact counts hold after repeated guarded loads.
