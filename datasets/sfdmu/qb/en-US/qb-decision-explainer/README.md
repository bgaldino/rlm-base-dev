# qb-decision-explainer Data Plan

SFDMU data plan for QuantumBit (QB) Decision Explainer setup — configures the Explainability Action framework required for **Product Configuration Logs**. Creates the Application Subtype Definition, Business Process Type Definition, Explainability Action Definition, and Explainability Action Version records with the `SolverPath` configuration that enables the constraint solver to emit diagnostic logs viewable in the Revenue Cloud Operations Console.

## Data Plan Overview

The plan uses a **single SFDMU pass** with 5 objects (all Upsert). No activation step is required beyond record creation.

```
Single Pass (SFDMU)
────────────────────────────────────────────────────
Upsert all Decision Explainer objects in dependency order
```

### Objects

| # | Object | Operation | External ID | Records | Notes |
|---|--------|-----------|-------------|---------|-------|
| 1 | ApplicationSubtypeDefinition | Upsert | `DeveloperName` | 1 | `SolverPath`, ApplicationUsageType = `ExplainabilityService` |
| 2 | BusinessProcessTypeDef | Upsert | `DeveloperName` | 1 | `SolverPath`, ApplicationUsageType = `ExplainabilityService` |
| 3 | ExplainabilityActionDef | Upsert | `DeveloperName` | 1 | References both parents via relationship traversal |
| 4 | ExplainabilityActionVersion | Upsert | `DeveloperName` | 1 | Active version linked to ActionDef |
| 5 | ProductConfigurationFlow | Upsert | `FlowIdentifier` | 1 | Registers `RLM_Debug_Configurator` flow as a configurator flow |

## Dependency Chain

```
ApplicationSubtypeDefinition (SolverPath)
BusinessProcessTypeDef (SolverPath)
  └─ ExplainabilityActionDef (SolverPath)  ← references both parents
       └─ ExplainabilityActionVersion (SolverPath)  ← references ActionDef

ProductConfigurationFlow (RLM_Debug_Configurator)  ← standalone
```

## Prerequisites

- **Permission Set**: Users must have a permission set with the `Product Configuration User` license and the `Read and write configuration logs` user permission enabled before logs will be captured at runtime.

## Portability

Decision Explainer objects use `DeveloperName` — a platform-enforced unique field on setup definition objects. Parent lookups use relationship traversal (`ApplicationSubtype.DeveloperName`, `ProcessType.DeveloperName`, `ExplainabilityActionDef.DeveloperName`) for cross-org portability. ProductConfigurationFlow uses `FlowIdentifier` (the flow API name) as its external ID.

## Idempotency

This plan is idempotent — re-running on an org that already has the `SolverPath` records produces zero net changes (Upsert matches on `DeveloperName`).

## Dependencies

**Upstream:**
- **post_utils metadata** — the `RLM_Debug_Configurator` flow must be deployed before the ProductConfigurationFlow record can reference it.

**Downstream:**
- Product Configurator runtime uses the Explainability Action framework to emit configuration logs when `explainabilityEnabled = true` is passed in the configurator options.
- Logs are viewable in the **Revenue Cloud Operations Console** app.

## File Structure

```
qb-decision-explainer/
├── export.json                          # SFDMU data plan (single pass, 5 objects)
├── README.md                            # This file
├── ApplicationSubtypeDefinition.csv     # 1 record
├── BusinessProcessTypeDef.csv           # 1 record
├── ExplainabilityActionDef.csv          # 1 record
├── ExplainabilityActionVersion.csv      # 1 record
└── ProductConfigurationFlow.csv         # 1 record
```
