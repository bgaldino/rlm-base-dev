# qb-dro Data Plan

SFDMU data plan for QuantumBit (QB) Dynamic Revenue Orchestrator (DRO) configuration. Creates fulfillment step definitions, groups, dependencies, decomposition rules, fulfillment scenarios, workspaces, fallout rules, jeopardy rules, and updates products with DRO-specific fields. Uses dynamic user resolution at runtime.

## CCI Integration

### Flow: `prepare_dro`

This plan is executed as **step 1** of the `prepare_dro` flow (when `dro=true`, `qb=true`).

| Step | Task                     | Description                                            |
|------|--------------------------|--------------------------------------------------------|
| 1    | `insert_qb_dro_data`    | Runs this SFDMU plan (single pass, dynamic user)       |

**Note:** Unlike billing and tax, `prepare_dro` has no Apex activation step. DRO records do not have a status lifecycle. A separate `create_dro_rule_library` task (in `prepare_core`) creates the DRO Rule Library record.

### Task Definition

```yaml
insert_qb_dro_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-dro"
    dynamic_assigned_to_user: true
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with 14 objects. No activation is required.

```
Single Pass (SFDMU)
────────────────────────────────────────────────────
Upsert all DRO objects in dependency order
(dynamic user resolution for AssignedTo fields)
```

### Objects

| #  | Object                          | Operation | External ID                                                        | Records |
|----|---------------------------------|-----------|--------------------------------------------------------------------|---------|
| 1  | Product2                        | Update    | `StockKeepingUnit`                                                 | 164     |
| 2  | ProductFulfillmentDecompRule    | Upsert    | `Name;SourceProduct.StockKeepingUnit;DestinationProduct.StockKeepingUnit` | 28 |
| 3  | ValTfrmGrp                      | Upsert    | `Name`                                                             | 0       |
| 4  | ValTfrm                         | Upsert    | `Name`                                                             | 0       |
| 5  | ProductDecompEnrichmentRule     | Upsert    | `Name`                                                             | 0       |
| 6  | FulfillmentStepDefinitionGroup  | Upsert    | `Name`                                                             | 10      |
| 7  | FulfillmentStepDefinition       | Upsert    | `Name;StepDefinitionGroup.Name`                                    | 17      |
| 8  | FulfillmentStepDependencyDef    | Upsert    | `Name;DependsOnStepDefinition.Name;FulfillmentStepDefinition.Name` | 13      |
| 9  | ProductFulfillmentScenario      | Upsert    | `Name;Product.StockKeepingUnit`                                    | 13      |
| 10 | FulfillmentWorkspace            | Upsert    | `Name`                                                             | 2       |
| 11 | FulfillmentWorkspaceItem        | Upsert    | `FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name`    | 7       |
| 12 | FulfillmentFalloutRule          | Upsert    | `Name`                                                             | 3       |
| 13 | FulfillmentStepJeopardyRule     | Upsert    | `Name`                                                             | 6       |
| 14 | FulfillmentTaskAssignmentRule   | Upsert    | `Name`                                                             | 0       |

**Note:** Objects 3-5 (ValTfrmGrp, ValTfrm, ProductDecompEnrichmentRule) and Object 14 (FulfillmentTaskAssignmentRule) have empty CSVs (0 data records) — placeholders for future data. Product2 is Update-only (sets `CustomDecompositionScope`, `DecompositionScope`, `FulfillmentQtyCalcMethod`).

## Dynamic User Resolution

The plan uses a **runtime placeholder** `__DRO_ASSIGNED_TO_USER__` for the `AssignedTo.Name` field on `FulfillmentStepDefinition` records. At load time, the CCI task (`dynamic_assigned_to_user: true`) resolves this placeholder to the target org's default user name.

Supporting files:
- `UserAndGroup.csv` contains the placeholder value `__DRO_ASSIGNED_TO_USER__` — SFDMU uses this to resolve the User record for the `AssignedToId` lookup
- `FulfillmentStepDefinition.csv` references `AssignedTo.Name` with the same placeholder

This ensures the plan works across any org without hardcoded user references.

## Key Object Groups

### Product DRO Configuration (Objects 1-2)

Product2 Update sets DRO-specific fields (`CustomDecompositionScope`, `DecompositionScope`, `FulfillmentQtyCalcMethod`). ProductFulfillmentDecompRule defines how products decompose from source to destination (28 rules mapping parent products to fulfillment sub-products).

### Value Transforms (Objects 3-4) — Placeholders

ValTfrmGrp and ValTfrm are empty placeholders for value transformation groups and mappings. These may be needed for attribute mapping during decomposition in future configurations.

### Enrichment Rules (Object 5) — Placeholder

ProductDecompEnrichmentRule is an empty placeholder for decomposition enrichment rules that map attributes between source and destination products.

### Fulfillment Steps (Objects 6-8)

Three-level hierarchy: FulfillmentStepDefinitionGroup (10 groups like "Order Processing", "Finance", "Billing and Invoicing") -> FulfillmentStepDefinition (17 steps like "Convert Order to Asset", "Provision Platform") -> FulfillmentStepDependencyDef (13 dependency links between steps).

### Fulfillment Scenarios (Object 9)

ProductFulfillmentScenario (13 records) maps products to their fulfillment step groups and actions (e.g., "QuantumBit Database (Token Based) - Billing", "Finance Service").

### Workspaces (Objects 10-11)

FulfillmentWorkspace (2 workspaces) with FulfillmentWorkspaceItem (7 items) defining the UI layout for fulfillment management.

### Rules (Objects 12-14)

FulfillmentFalloutRule (3 rules) for error handling, FulfillmentStepJeopardyRule (6 rules) for SLA monitoring, and FulfillmentTaskAssignmentRule (0 records — placeholder).

## Composite External IDs

| Object                        | Composite Key                                                     | CSV `$$` Column |
|-------------------------------|-------------------------------------------------------------------|-----------------|
| ProductFulfillmentDecompRule  | `Name;SourceProduct.StockKeepingUnit;DestinationProduct.StockKeepingUnit` | Yes      |
| FulfillmentStepDefinition     | `Name;StepDefinitionGroup.Name`                                   | Yes             |
| FulfillmentStepDependencyDef  | `Name;DependsOnStepDefinition.Name;FulfillmentStepDefinition.Name`| Yes             |
| ProductFulfillmentScenario    | `Name;Product.StockKeepingUnit`                                   | Yes             |
| FulfillmentWorkspaceItem      | `FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name`   | Yes             |

Nested `$$` columns are used for parent lookup resolution in FulfillmentStepDependencyDef (e.g., `DependsOnStepDefinition.$$Name$StepDefinitionGroup.Name`).

## Portability

All external IDs use portable, human-readable fields:

- **Name** fields: All human-readable (e.g., "Order Processing", "Convert Order to Asset", "QuantumBit Database (Token Based)- Billing")
- **StockKeepingUnit** for Product2 references
- **DeveloperName** for IntegrationDefinition references
- **Dynamic user resolution**: `__DRO_ASSIGNED_TO_USER__` placeholder ensures cross-org compatibility

No auto-numbered Name fields are used.

## Extra CSV Files Not in export.json

Several CSV files exist in the directory but are **not referenced** in `export.json`:

- `IntegrationProviderDef.csv` (1 record — `DeveloperName`)
- `UserAndGroup.csv` (1 record — placeholder for dynamic user resolution)
- `AttributeDefinition.csv` (empty)
- `AttributePicklistValue.csv` (empty)
- `ExpressionSet.csv` (empty)
- `FlowOrchestration.csv` (empty)
- `ProductClassification.csv` (empty)

These may be SFDMU artifacts from previous runs, supporting data for the dynamic user resolution, or placeholders for future schema expansion.

## Dependencies

**Upstream:**
- **qb-pcm** — Product2 records must exist (matched by `StockKeepingUnit`)
- **`create_dro_rule_library`** (in `prepare_core`) — Creates the DRO RuleLibrary record

**Downstream:**
- Runtime DRO engine consumes this configuration for order decomposition and fulfillment orchestration

## File Structure

```
qb-dro/
├── export.json                          # SFDMU data plan (single pass, 14 objects)
├── README.md                            # This file
│
│  Source CSVs — Products
├── Product2.csv                         # 164 records (Update only)
│
│  Source CSVs — Decomposition
├── ProductFulfillmentDecompRule.csv     # 28 records
├── ValTfrmGrp.csv                       # 0 records (placeholder)
├── ValTfrm.csv                          # 0 records (placeholder)
├── ProductDecompEnrichmentRule.csv      # 0 records (placeholder)
│
│  Source CSVs — Fulfillment Steps
├── FulfillmentStepDefinitionGroup.csv   # 10 records
├── FulfillmentStepDefinition.csv        # 17 records
├── FulfillmentStepDependencyDef.csv     # 13 records
│
│  Source CSVs — Scenarios and Workspaces
├── ProductFulfillmentScenario.csv       # 13 records
├── FulfillmentWorkspace.csv             # 2 records
├── FulfillmentWorkspaceItem.csv         # 7 records
│
│  Source CSVs — Rules
├── FulfillmentFalloutRule.csv           # 3 records
├── FulfillmentStepJeopardyRule.csv      # 6 records
├── FulfillmentTaskAssignmentRule.csv    # 0 records (placeholder)
│
│  Source CSVs — Supporting (not in export.json)
├── IntegrationProviderDef.csv           # 1 record (reference)
├── UserAndGroup.csv                     # 1 record (dynamic user placeholder)
├── AttributeDefinition.csv              # 0 records (placeholder)
├── AttributePicklistValue.csv           # 0 records (placeholder)
├── ExpressionSet.csv                    # 0 records (placeholder)
├── FlowOrchestration.csv               # 0 records (placeholder)
├── ProductClassification.csv            # 0 records (placeholder)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Idempotency

This plan should be idempotent via SFDMU's Upsert operation with composite external IDs. Re-running on an org that already has the data should match all existing records and leave them untouched.

**Not yet validated** — idempotency testing against a 260 org is pending.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

5 polymorphic fields found across DRO objects (excluding standard OwnerId):

| Object                        | Field                   | Label                       | Polymorphic Targets                   | In Current SOQL? |
|-------------------------------|-------------------------|-----------------------------|---------------------------------------|-------------------|
| **FulfillmentStepDefinition** | `AssignedToId`          | Assigned To ID              | **Group, User**                       | Yes (dynamic user)|
| **FulfillmentStepDefinition** | `ExecuteOnRuleId`       | Execute On Rule ID          | **ExpressionSet, Ruleset**            | No (not in query) |
| **FulfillmentStepDefinition** | `ResumeOnRuleId`        | Resume On Rule ID           | **ExpressionSet, Ruleset**            | Yes (in query)    |
| **FulfillmentTaskAssignmentRule** | `DestinationId`     | Assignment Destination ID   | **Group, User**                       | Yes (in query)    |
| **FulfillmentTaskAssignmentRule** | `ConditionId`       | Assignment Condition ID     | **ExpressionSet, Ruleset**            | Yes (in query)    |
| **ProductDecompEnrichmentRule** | `CalculationDefinitionId` | Calculation Definition ID | **DecisionMatrixDefinition, ExpressionSet** | No (not in query) |

**Notes:**
- `AssignedToId` is already handled via `dynamic_assigned_to_user: true` (runtime placeholder substitution)
- `ExecuteOnRuleId` exists in the 260 schema but is **not in the current SOQL query** — if used, needs `$ExpressionSet` or `$Ruleset` suffix
- `ResumeOnRuleId` is in the current SOQL but the polymorphic targets are not handled — currently the field is always null in the data
- `DestinationId` and `ConditionId` on FulfillmentTaskAssignmentRule are polymorphic but the CSV is empty (0 records)
- `CalculationDefinitionId` on ProductDecompEnrichmentRule is polymorphic but the CSV is empty (0 records)

### New Fields Found in 260 (Not in Current SOQL)

| Object                        | Field                    | Type        | Notes                                           |
|-------------------------------|--------------------------|-------------|--------------------------------------------------|
| **FulfillmentStepDefinition** | `RunAsUserId`            | REFERENCE   | Lookup to User — run-as user for step execution  |
| **FulfillmentStepDefinition** | `ExecuteOnConditionData` | TEXTAREA    | JSON condition data for execution rules          |
| **FulfillmentStepDefinition** | `ResumeOnConditionData`  | TEXTAREA    | JSON condition data for resume rules             |
| **FulfillmentStepDefinition** | `ExecuteOnRuleId`        | POLY REF    | ExpressionSet or Ruleset (see above)             |
| **FulfillmentTaskAssignmentRule** | `ConditionData`     | TEXTAREA    | JSON condition data                              |
| **FulfillmentTaskAssignmentRule** | `UsageType`          | PICKLIST    | Usage type categorization                        |
| **ProductFulfillmentScenario** | `ScenarioRuleId`        | REFERENCE   | Lookup to Ruleset — scenario execution rules     |
| **ProductFulfillmentDecompRule** | `ExecuteOnRuleId`     | REFERENCE   | Lookup to Ruleset — conditional decomposition    |

### Self-Referencing Fields

| Object          | Field             | Notes                                         |
|-----------------|-------------------|-----------------------------------------------|
| UsageResource   | `TokenResourceId` | Self-ref to UsageResource (in qb-rating plan) |

No self-references in DRO-specific objects.

### Cross-Object References to Non-Plan Objects

Several DRO objects reference objects that are **not in the current export.json**:

| Referenced Object           | Referenced By                                              | Notes                            |
|-----------------------------|------------------------------------------------------------|----------------------------------|
| `IntegrationProviderDef`    | FulfillmentStepDefinition, FulfillmentFalloutRule, FulfillmentStepJeopardyRule | CSV exists but not in export.json |
| `ExpressionSet`             | FulfillmentStepDefinition (ExecuteOnRuleId, ResumeOnRuleId), FulfillmentTaskAssignmentRule (ConditionId), ProductDecompEnrichmentRule (CalculationDefinitionId) | Empty CSV exists as placeholder   |
| `Ruleset`                   | FulfillmentStepDefinition (ExecuteOnRuleId, ResumeOnRuleId), FulfillmentTaskAssignmentRule (ConditionId), ProductFulfillmentScenario (ScenarioRuleId), ProductFulfillmentDecompRule (ExecuteOnRuleId) | Not referenced anywhere in plan  |
| `DecisionMatrixDefinition`  | ProductDecompEnrichmentRule (CalculationDefinitionId)      | Not referenced anywhere in plan  |
| `AttributePicklistValue`    | ValTfrm (InputPicklistValueId, OutputPicklistValueId)      | Empty CSV exists as placeholder  |
| `Group`                     | FulfillmentFalloutRule (FalloutQueueId), FulfillmentTaskAssignmentRule (SourceId, DestinationId) | Queue references                |

### Plan for Polymorphic Field Support

When DRO features are enhanced for 260, the following polymorphic handling will be needed:

**FulfillmentStepDefinition:**
- `AssignedToId` — already handled via `__DRO_ASSIGNED_TO_USER__` dynamic resolution. For Group assignment, would need `AssignedToId$Group` with Group.Name lookup.
- `ExecuteOnRuleId` — if used, needs separate handling: `ExecuteOnRuleId$ExpressionSet` (by DeveloperName) or `ExecuteOnRuleId$Ruleset` (by Name/DeveloperName). May need polymorphic `$` suffix in SOQL.
- `ResumeOnRuleId` — same pattern as ExecuteOnRuleId.

**FulfillmentTaskAssignmentRule:**
- `DestinationId` — `DestinationId$User` (by Name) or `DestinationId$Group` (by Name). Similar to AssignedTo handling.
- `ConditionId` — `ConditionId$ExpressionSet` or `ConditionId$Ruleset`.

**ProductDecompEnrichmentRule:**
- `CalculationDefinitionId` — `CalculationDefinitionId$DecisionMatrixDefinition` or `CalculationDefinitionId$ExpressionSet`.

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

**None found.** No DRO objects have schema-enforced unique fields. All externalIds rely on convention-unique Names.

### Auto-Numbered Name Fields (Portability Assessment)

| Object                       | Name Auto-Num | Current ExternalId                                  | Assessment |
|------------------------------|---------------|-----------------------------------------------------|------------|
| FulfillmentWorkspaceItem     | **Yes**       | `FW.Name;FSDG.Name`                                | ✅ Good — composite from parents |
| FulfillmentFalloutRule       | **Yes**       | `Name`                                              | **PROBLEM** — auto-num Name |
| FulfillmentStepJeopardyRule  | **Yes**       | `Name`                                              | **PROBLEM** — auto-num Name |
| ValTfrm                      | **Yes**       | `Name`                                              | **PROBLEM** — auto-num Name |
| ProductDecompEnrichmentRule  | **Yes**       | `Name`                                              | **PROBLEM** — auto-num Name |

### Portability Fixes Needed

**FulfillmentFalloutRule** (`Name` auto-num): No lookup fields to parent. Available fields: `ErrorCode`, `FlowDefinitionName`, `StepType`, `FalloutQueueId`, `IntegrationDefinitionId`, `RetriesAllowed`, `RetryIntervals`, `RetryPolicy`. Consider a composite of `StepType;ErrorCode` or assign human-readable Names if possible.

**FulfillmentStepJeopardyRule** (`Name` auto-num): Available fields: `EstimatedDuration`, `EstimatedDurationUnit`, `FlowDefinition`, `StepType`, `JeopardyThreshold`, `JeopardyThresholdUnit`, `IntegrationDefinition.DeveloperName`. Consider `StepType;IntegrationDefinition.DeveloperName` or assign human-readable Names.

**ValTfrm** (`Name` auto-num): Has parent `ValueTransformGroupId`. Consider `ValTfrmGrp.Name;InputString` or another composite from the transformation's input/output values.

**ProductDecompEnrichmentRule** (`Name` auto-num): Has parent `DecompositionRuleId`. Schema provides `SourceAttributeIdentifier` and `DestinationAttributeIdentifier` as `idLookup` fields. Consider `DecompositionRule.Name;SourceAttributeIdentifier;DestinationAttributeIdentifier` as a portable composite.

### ExternalId Assessment (Non-Auto-Num Objects)

| Object                        | Current ExternalId                               | Assessment |
|-------------------------------|--------------------------------------------------|------------|
| Product2                      | `StockKeepingUnit`                               | ✅ OK — platform-enforced unique when RLM enabled |
| ProductFulfillmentDecompRule  | `Name;SourceProduct.SKU;DestinationProduct.SKU`  | ✅ Good — also has `SourceIdentifier`/`SourceClassIdentifier` as idLookup |
| ValTfrmGrp                    | `Name`                                           | ✅ OK — human-readable |
| FulfillmentStepDefinitionGroup| `Name`                                           | ✅ OK — human-readable |
| FulfillmentStepDefinition     | `Name;StepDefinitionGroup.Name`                  | ✅ OK — 2-field composite |
| FulfillmentStepDependencyDef  | `Name;DependsOn.Name;FSD.Name`                   | ✅ OK — 3-field composite |
| ProductFulfillmentScenario    | `Name;Product.SKU`                               | ✅ OK — also has `SourceIdentifier`/`SourceClassIdentifier` as idLookup |
| FulfillmentWorkspace          | `Name`                                           | ✅ OK — human-readable |
| FulfillmentTaskAssignmentRule | `Name`                                           | ✅ OK — not auto-num, human-readable |

### Note: ProductFulfillmentDecompRule idLookup Fields

The schema shows `SourceIdentifier`, `DestinationIdentifier`, and `SourceClassIdentifier` as `isIdLookup=true` on ProductFulfillmentDecompRule. These could provide alternative portable matching, but the current composite key (`Name;SourceProduct.SKU;DestinationProduct.SKU`) is already good.

Similarly, `ProductFulfillmentScenario` has `SourceIdentifier` and `SourceClassIdentifier` as `isIdLookup=true`.

## Optimization Opportunities

1. **Fix auto-num Name externalIds**: Replace `Name` on FulfillmentFalloutRule, FulfillmentStepJeopardyRule, ValTfrm, and ProductDecompEnrichmentRule with portable composite keys or human-readable Names
2. **Add missing 260 fields to SOQL**: Add `RunAsUserId`, `ExecuteOnConditionData`, `ResumeOnConditionData`, `ExecuteOnRuleId` to FulfillmentStepDefinition; `ConditionData`, `UsageType` to FulfillmentTaskAssignmentRule; `ScenarioRuleId` to ProductFulfillmentScenario; `ExecuteOnRuleId` to ProductFulfillmentDecompRule
3. **Handle polymorphic fields**: Implement `$ObjectType` suffix handling for ExpressionSet/Ruleset/DecisionMatrixDefinition polymorphic targets when these features are used
4. **Add IntegrationProviderDef to export.json**: The CSV exists and is referenced by 3 objects — add as Readonly or Upsert
5. **Add extraction support**: Create `extract_qb_dro_data` CCI task for bidirectional operation
6. **Clean up extra CSVs**: Remove or document the CSV files that are not referenced in `export.json` (AttributeDefinition, AttributePicklistValue, ExpressionSet, FlowOrchestration, ProductClassification)
7. **Populate placeholder objects**: Investigate whether ValTfrmGrp, ValTfrm, ProductDecompEnrichmentRule, and FulfillmentTaskAssignmentRule should have data for 260 DRO features
8. **Review dynamic user resolution**: Ensure the `__DRO_ASSIGNED_TO_USER__` replacement mechanism works correctly in all target org types (scratch, sandbox, production)
9. **Consistency**: Uses `objectSets` wrapper — consider switching to flat `objects` array if appropriate
