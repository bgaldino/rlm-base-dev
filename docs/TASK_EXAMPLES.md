# Flow and Expression Set Management Task Examples

This document provides working examples for the `manage_flows` and `manage_expression_sets` CumulusCI tasks.

## Flow Management (`manage_flows`)

### Basic Operations

#### 1. List All Flows
```bash
cci task run manage_flows --operation list
```

#### 2. List Flows with Limit
```bash
cci task run manage_flows --operation list --limit 10
```

#### 3. Query Flows (Returns JSON Data)
```bash
cci task run manage_flows --operation query --limit 5
```

### Filtering by Process Type

#### 4. List Screen Flows
```bash
cci task run manage_flows --operation list --process_type ScreenFlow
```

#### 5. List AutoLaunched Flows
```bash
cci task run manage_flows --operation list --process_type AutoLaunchedFlow
```

#### 6. List Approval Workflows
```bash
cci task run manage_flows --operation list --process_type ApprovalWorkflow
```

### Filtering by Status

#### 7. List Active Flows
```bash
cci task run manage_flows --operation list --status Active
```

#### 8. List Inactive Flows
```bash
cci task run manage_flows --operation list --status Inactive
```

#### 9. List Draft Flows
```bash
cci task run manage_flows --operation list --status Draft
```

### Combined Filters

#### 10. List Active AutoLaunched Flows
```bash
cci task run manage_flows --operation list --status Active --process_type AutoLaunchedFlow
```

#### 11. Query Active Screen Flows (Limit 5)
```bash
cci task run manage_flows --operation query --status Active --process_type ScreenFlow --limit 5
```

### Activate/Deactivate Operations

#### 12. Activate a Specific Flow
```bash
cci task run manage_flows --operation activate --developer_names RC_UpdateDecisionTables
```

#### 13. Activate Multiple Flows
```bash
cci task run manage_flows --operation activate --developer_names "RC_UpdateDecisionTables,RC_Account_Utilities"
```

#### 14. Deactivate All Draft Flows
```bash
cci task run manage_flows --operation deactivate --status Draft
```

#### 15. Deactivate Specific Flows
```bash
cci task run manage_flows --operation deactivate --developer_names "Flow1,Flow2"
```

### Sorting Options

#### 16. List Flows Sorted by Created Date (Ascending)
```bash
cci task run manage_flows --operation list --sort_by CreatedDate --sort_order Asc
```

#### 17. List Flows Sorted by Process Type
```bash
cci task run manage_flows --operation list --sort_by ProcessType --sort_order Asc
```

---

## Expression Set Management (`manage_expression_sets`)

Expression set **version** activation and deactivation are performed by this task (operations `activate_versions` / `deactivate_versions` or single-version `activate_version` / `deactivate_version`). SFDMU data plans for expression sets are no longer used; use these CCI operations instead.

### Basic Operations

#### 1. List All Expression Sets
```bash
cci task run manage_expression_sets --operation list
```

#### 2. List Expression Sets with Limit
```bash
cci task run manage_expression_sets --operation list --limit 10
```

#### 3. Query Expression Sets (Returns JSON Data)
```bash
cci task run manage_expression_sets --operation query --limit 5
```

### Filtering by Interface Source Type

#### 4. List Pricing Procedures
```bash
cci task run manage_expression_sets --operation list --interface_source_type PricingProcedure
```

#### 5. List Rating Procedures
```bash
cci task run manage_expression_sets --operation list --interface_source_type RatingProcedure
```

#### 6. List Discovery Procedures
```bash
cci task run manage_expression_sets --operation list --interface_source_type DiscoveryProcedure
```

### Filtering by Process Type

#### 7. List Default Pricing Procedures
```bash
cci task run manage_expression_sets --operation list --process_type DefaultPricing
```

#### 8. List Default Rating Procedures
```bash
cci task run manage_expression_sets --operation list --process_type DefaultRating
```

#### 9. List Pricing Discovery Procedures
```bash
cci task run manage_expression_sets --operation list --process_type PricingDiscovery
```

### Combined Filters

#### 10. List Active Pricing Procedures
```bash
cci task run manage_expression_sets --operation list --status Active --interface_source_type PricingProcedure
```

#### 11. Query Active Rating Procedures (Limit 5)
```bash
cci task run manage_expression_sets --operation query --status Active --interface_source_type RatingProcedure --limit 5
```

### Version Management

#### 12. List Versions for a Specific Expression Set
```bash
cci task run manage_expression_sets --operation list_versions --developer_names RLM_DefaultPricingProcedure
```

#### 13. List Versions for Multiple Expression Sets
```bash
cci task run manage_expression_sets --operation list_versions --developer_names "RLM_DefaultPricingProcedure,RLM_DefaultRatingProcedure"
```

#### 14. Activate a Specific Version
```bash
cci task run manage_expression_sets --operation activate_version --version_full_name RLM_DefaultPricingProcedure_V1
```

#### 15. Deactivate a Specific Version
```bash
cci task run manage_expression_sets --operation deactivate_version --version_full_name RLM_DefaultPricingProcedure_V1
```

### Filtering by Developer Names

#### 16. List Specific Expression Sets
```bash
cci task run manage_expression_sets --operation list --developer_names "RLM_DefaultPricingProcedure,RLM_DefaultRatingProcedure"
```

#### 17. Query Specific Expression Sets
```bash
cci task run manage_expression_sets --operation query --developer_names RLM_DefaultPricingProcedure
```

### Sorting Options

#### 18. List Expression Sets Sorted by Last Modified (Ascending)
```bash
cci task run manage_expression_sets --operation list --sort_by LastModifiedDate --sort_order Asc
```

#### 19. List Expression Sets Sorted by Process Type
```bash
cci task run manage_expression_sets --operation list --sort_by ProcessType --sort_order Asc
```

---

## Transaction Processing Type Management (`manage_transaction_processing_types`)

### Basic Operations

#### 1. List Transaction Processing Types
```bash
cci task run manage_transaction_processing_types --operation list
```

#### 2. Upsert Transaction Processing Types from File
```bash
cci task run manage_transaction_processing_types --operation upsert --input_file datasets/transaction_processing_types.json
```

### Example Input File

```json
[
  {
    "DeveloperName": "RLM_Example",
    "MasterLabel": "RLM Example",
    "Description": "Example TransactionProcessingType",
    "Language": "en_US",
    "RuleEngine": "Pricing",
    "SaveType": "Draft"
  }
]
```

Notes:
- `DeveloperName` is the default key field.
- Use `--dry_run true` to validate without changes.
- For the SFDMU-based load order used in deployments, see `docs/constraints_setup.md`.

---

## Common Use Cases

### Refresh Decision Tables (Using Flow)
```bash
# First, activate the decision table refresh flow
cci task run manage_flows --operation activate --developer_names RC_UpdateDecisionTables
```

### Activate All Active Pricing Procedures
```bash
# List active pricing procedures first
cci task run manage_expression_sets --operation list --status Active --interface_source_type PricingProcedure

# Then activate specific versions
cci task run manage_expression_sets --operation activate_version --version_full_name RLM_DefaultPricingProcedure_V1
```

### Audit Flow Status
```bash
# Get all flows with their status
cci task run manage_flows --operation query --sort_by Status --sort_order Asc
```

### Find Inactive Expression Set Versions
```bash
# List versions for a specific expression set
cci task run manage_expression_sets --operation list_versions --developer_names RLM_DefaultPricingProcedure
```

---

## Notes

- **Developer Names**: 
  - For flows, use `DefinitionId` (not DeveloperName) when filtering by developer_names
  - For expression sets, use `DeveloperName`
- **Version Full Names**: Expression set versions use the format `{DeveloperName}_V{VersionNumber}` (e.g., `RLM_DefaultPricingProcedure_V1`).
- **Process Types**: Common flow process types include `ScreenFlow`, `AutoLaunchedFlow`, `Workflow`, `ApprovalWorkflow`.
- **Interface Source Types & Process Types**: 
  - These fields exist on `ExpressionSetDefinitionVersion`, not `ExpressionSetDefinition`
  - Use `list_versions` operation to see these fields for expression sets
  - Filtering by these fields at the definition level is not supported (they're on versions)
- **Status Values**: `Active`, `Inactive`, `Draft` (for flows), `Active`, `Inactive`, `Draft` (for expression sets).
- **Field Names**:
  - Flows use: `DefinitionId`, `MasterLabel`, `VersionNumber`, `CreatedDate`
  - Expression Sets use: `DeveloperName`, `MasterLabel`, `LastModifiedDate`
