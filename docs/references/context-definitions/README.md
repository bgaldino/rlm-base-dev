# Reference Context Definitions (not deployed)

**Reference only.** These 10 MDAPI `.contextDefinition` files are snapshots of the repo's RLM context
definitions from before the Context Service tooling existed. Nothing deploys them, and they **should not**
deploy to Release 264: a ContextDefinition deploys as one atomic unit, so these older snapshots would
delete attributes 264 added (for example `ContractRampUpliftType__std` on Contract).

They moved here from `force-app/main/default/contextDefinitions/` on 2026-10-28 (todo 223). Under
`force-app/` they looked like live source, which misled sweeps. The `deploy_context_definitions` task
that pointed at them, and was in no flow, was retired in the same change.

| File | Last refreshed |
|---|---|
| `RLM_AssetContext`, `RLM_BillingContext`, `RLM_ProductDiscoveryContext`, `RLM_RatingDiscoveryContext`, `RLM_SalesTransactionContext` | `4364c6cf` (2026-01-20) |
| `RLM_CollectionPlanSegmentCtx`, `RLM_ContractsContextDefinition`, `RLM_FulfillmentAssetContext`, `RLM_ProductDeepCloneContext`, `RLM_RateManagementContext` | `333d2b11` (2025-09-29) |

**How context definitions are built today:** the build extends the platform's standard definitions
at runtime with the `extend_context_*`, `apply_context_*` and `manage_context_definition` tasks, driven by the JSON plans
in `datasets/context_plans/`. See `.cursor/skills/context-service/SKILL.md`. Use these files to read
the older MDAPI shape, not as a source to deploy.
