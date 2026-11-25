# Flow and Expression Set Management Task Examples

This document provides working examples for the `manage_flows` and `manage_expression_sets` CumulusCI tasks. Pass options with `-o <name> <value>`.

## Flow Management (`manage_flows`)

`list` and `query` read the Tooling API `Flow` object, which has one row per flow **version**. `activate` and `deactivate` change the flow's `FlowDefinition` (one row per flow) by setting the active version number; a version's Status cannot be changed directly.

### Options

| Option | Used by | Meaning |
|--------|---------|---------|
| `operation` | all | `list`, `query`, `activate`, `deactivate` |
| `developer_names` | all | Comma-separated flow DeveloperNames (a FlowDefinition Id also works). **Required** for `activate` and `deactivate`. For `list` and `query`, omitted means all flows. A name that matches no flow is an error and nothing is changed. |
| `status` | list, query | `Active`, `Draft`, `Obsolete` or `InvalidDraft`. Rejected by `activate` and `deactivate`. |
| `process_type` | list, query | For example `AutoLaunchedFlow`, `Flow` (screen flow), `Workflow`. |
| `sort_by` | list, query | `DeveloperName`, `Label`, `Status`, `ProcessType`, `VersionNumber`, `CreatedDate` (default). `LastModifiedDate` is accepted as `CreatedDate`. |
| `sort_order` | list, query | `Asc` or `Desc` (default). |
| `limit` | list, query | Positive integer. Rejected by `activate` and `deactivate`. |

### Listing and querying

```bash
# All flow versions (newest first)
cci task run manage_flows --org <org> -o operation list

# First 10
cci task run manage_flows --org <org> -o operation list -o limit 10

# Same rows, returned to the caller
cci task run manage_flows --org <org> -o operation query -o limit 5
```

### Filtering

```bash
# Screen flows (ProcessType is `Flow`)
cci task run manage_flows --org <org> -o operation list -o process_type Flow

# Auto-launched flows
cci task run manage_flows --org <org> -o operation list -o process_type AutoLaunchedFlow

# Active versions, or Draft versions
cci task run manage_flows --org <org> -o operation list -o status Active
cci task run manage_flows --org <org> -o operation list -o status Draft

# Active auto-launched flows
cci task run manage_flows --org <org> -o operation list -o status Active -o process_type AutoLaunchedFlow

# Specific flows, every version
cci task run manage_flows --org <org> -o operation list -o developer_names "MyFlow_One,MyFlow_Two"
```

### Sorting

```bash
cci task run manage_flows --org <org> -o operation list -o sort_by CreatedDate -o sort_order Asc
cci task run manage_flows --org <org> -o operation list -o sort_by ProcessType -o sort_order Asc
```

### Activating and deactivating

`activate` activates the newest `Draft` or `Active` version, so a newly saved draft goes live and a flow whose newest live version is already active is skipped. An `Obsolete` version is chosen only when no `Draft` or `Active` version exists (re-activating a deactivated flow), so a rollback to an older active version is never undone. `InvalidDraft` versions are never chosen. `deactivate` leaves no version active; a flow with no active version is skipped. The task checks every name before changing anything, continues past a per-flow failure, and fails at the end if any flow failed.

```bash
# One flow
cci task run manage_flows --org <org> -o operation activate -o developer_names MyFlow_One

# Several flows
cci task run manage_flows --org <org> -o operation activate -o developer_names "MyFlow_One,MyFlow_Two"

# Deactivate
cci task run manage_flows --org <org> -o operation deactivate -o developer_names MyFlow_One
```

To act on "all draft flows" or similar, list them with `status`/`process_type` first and pass the names you want.

## Expression Set Management (`manage_expression_sets`)

Expression set **version** activation and deactivation are performed by this task (operations `activate_versions` / `deactivate_versions` or single-version `activate_version` / `deactivate_version`). SFDMU data plans for expression sets are no longer used; use these CCI operations instead.

### Options

| Option | Used by | Meaning |
|--------|---------|---------|
| `operation` | all | `list`, `query`, `list_versions`, `activate_version`, `deactivate_version`, `activate_versions`, `deactivate_versions` |
| `developer_names` | list, query, list_versions | Comma-separated expression set DeveloperNames. Omitted means all. |
| `status` | list, query, list_versions | `Active`, `Draft` or `Inactive`. Status lives on the **version**, so this keeps sets that have at least one version with that Status. |
| `interface_source_type` | list, query, list_versions | For example `PricingProcedure`, `RatingProcedure`, `DiscoveryProcedure`. InterfaceSourceType exists only in the set's metadata, so the task reads each candidate set (one request per set). |
| `process_type` | list, query, list_versions | For example `DefaultPricing`, `DefaultRating`, `PricingDiscovery`. Same cost note as above. |
| `version_full_name` | activate_version, deactivate_version | Version FullName, for example `RLM_DefaultPricingProcedure_V1`. |
| `version_full_names` | activate_versions, deactivate_versions | Comma-separated FullNames; otherwise every version under `metadata_path`. |
| `sort_by` | list, query, list_versions | `DeveloperName`, `Label`, `LastModifiedDate` (default), `CreatedDate`. |
| `sort_order` | list, query, list_versions | `Asc` or `Desc` (default). |
| `limit` | list, query, list_versions | Positive integer, applied after every filter. |

When `interface_source_type` or `process_type` is used, the list adds InterfaceSourceType and ProcessType columns.

### Listing and querying

```bash
cci task run manage_expression_sets --org <org> -o operation list
cci task run manage_expression_sets --org <org> -o operation list -o limit 10
cci task run manage_expression_sets --org <org> -o operation query -o limit 5
```

### Filtering

```bash
# By interface source type
cci task run manage_expression_sets --org <org> -o operation list -o interface_source_type PricingProcedure
cci task run manage_expression_sets --org <org> -o operation list -o interface_source_type RatingProcedure
cci task run manage_expression_sets --org <org> -o operation list -o interface_source_type DiscoveryProcedure

# By process type
cci task run manage_expression_sets --org <org> -o operation list -o process_type DefaultPricing
cci task run manage_expression_sets --org <org> -o operation list -o process_type DefaultRating
cci task run manage_expression_sets --org <org> -o operation list -o process_type PricingDiscovery

# Combined: sets with an Active version that are pricing procedures
cci task run manage_expression_sets --org <org> -o operation list -o status Active -o interface_source_type PricingProcedure

# Specific sets
cci task run manage_expression_sets --org <org> -o operation list -o developer_names "RLM_DefaultPricingProcedure,RLM_DefaultRatingProcedure"
```

### Version management

`list_versions` shows each version's FullName, Status and version number, oldest first.

```bash
cci task run manage_expression_sets --org <org> -o operation list_versions -o developer_names RLM_DefaultPricingProcedure
cci task run manage_expression_sets --org <org> -o operation list_versions -o developer_names "RLM_DefaultPricingProcedure,RLM_DefaultRatingProcedure"
cci task run manage_expression_sets --org <org> -o operation activate_version -o version_full_name RLM_DefaultPricingProcedure_V1
cci task run manage_expression_sets --org <org> -o operation deactivate_version -o version_full_name RLM_DefaultPricingProcedure_V1
```

### Sorting

```bash
cci task run manage_expression_sets --org <org> -o operation list -o sort_by LastModifiedDate -o sort_order Asc
cci task run manage_expression_sets --org <org> -o operation list -o sort_by DeveloperName -o sort_order Asc
```

---

## Transaction Processing Type Management (`manage_transaction_processing_types`)

### Basic Operations

#### 1. List Transaction Processing Types
```bash
cci task run manage_transaction_processing_types --org <org> -o operation list
```

#### 2. Upsert Transaction Processing Types from File
```bash
cci task run manage_transaction_processing_types --org <org> -o operation upsert -o input_file <path/to/transaction_processing_types.json>
```

### Example Input File

```json
[
  {
    "DeveloperName": "RLM_Example",
    "MasterLabel": "RLM Example",
    "Description": "Example TransactionProcessingType",
    "Language": "en_US",
    "RuleEngine": "StandardConfigurator",
    "SaveType": "Standard"
  }
]
```

Notes:
- `DeveloperName` is the default key field.
- Use `-o dry_run true` to validate without changes.
- Also accepts `-o key_field` (default `DeveloperName`).
- For the SFDMU-based load order used in deployments, see `docs/guides/constraints-setup.md`.

---

## Common Use Cases

### Activate the Decision Table Refresh Flow
```bash
# Activating the flow does not itself refresh any table. To refresh tables see the
# decision-tables skill.
cci task run manage_flows --org <org> -o operation activate -o developer_names RLM_Refresh_Decision_Tables_Bulk
```

### Activate a Pricing Procedure Version
```bash
# List the versions and their status first
cci task run manage_expression_sets --org <org> -o operation list_versions -o developer_names RLM_DefaultPricingProcedure

# Then activate a specific version
cci task run manage_expression_sets --org <org> -o operation activate_version -o version_full_name RLM_DefaultPricingProcedure_V1
```

### Audit Flow Status
```bash
# Get all flow versions with their status
cci task run manage_flows --org <org> -o operation query -o sort_by Status -o sort_order Asc
```

### Find Inactive Expression Set Versions
```bash
# List versions for a specific expression set
cci task run manage_expression_sets --org <org> -o operation list_versions -o developer_names RLM_DefaultPricingProcedure
```

---

## Notes

- **Developer Names**: flows and expression sets both take DeveloperNames (comma-separated). For flows a FlowDefinition Id also works, and `activate` and `deactivate` require the option.
- **Version Full Names**: Expression set versions use the format `{DeveloperName}_V{VersionNumber}` (e.g., `RLM_DefaultPricingProcedure_V1`).
- **Process Types**: Common flow process types include `Flow` (screen flow), `AutoLaunchedFlow`, `Workflow`.
- **Interface Source Types & Process Types**: these exist only in an expression set definition's metadata, not as queryable fields. `list`, `query` and `list_versions` read each candidate set to filter on them, so they cost one request per set.
- **Status Values**: flow versions are `Active`, `Draft`, `Obsolete` or `InvalidDraft`. Expression set versions are `Active`, `Draft` or `Inactive`; `--status` keeps the sets that have at least one version with that Status.
- **Field Names**:
  - Flows (one row per version) use: `Definition.DeveloperName`, `MasterLabel`, `VersionNumber`, `CreatedDate`
  - Expression Sets use: `DeveloperName`, `MasterLabel`, `LastModifiedDate`

> **PRM Network Email and App Launcher** — See [PRM Network email](../guides/org-operations.md#prm-network-email) for deploy-time sender substitution and cleanup, and [App Launcher order](../guides/org-operations.md#app-launcher-order) for capture and ordering tasks.
