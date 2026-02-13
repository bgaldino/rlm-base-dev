# Decision Table Management Task Examples

This document provides working examples for the `manage_decision_tables` CumulusCI task and related refresh tasks and flows.

## Decision Table Management (`manage_decision_tables`)

Decision Tables are Business Rules Engine (BRE) objects in Salesforce Revenue Cloud that store decision logic. This task provides comprehensive management capabilities: **list** (with UsageType), **query**, **refresh** (full or incremental), **activate**, **deactivate**, and **validate_lists** (compare org to project list anchors).

### Basic Operations

#### 1. List All Active Decision Tables (with UsageType)
```bash
cci task run manage_decision_tables --operation list
```
The list output includes **UsageType** (e.g. DefaultPricing, DefaultRating, RatingDiscovery) to help organize and filter decision tables.

#### 2. List Decision Tables with Limit
```bash
cci task run manage_decision_tables --operation list --limit 10
```

#### 3. Query Decision Tables (Returns JSON Data)
```bash
cci task run manage_decision_tables --operation query --limit 5
```

### Filtering by Status

#### 4. List Active Decision Tables
```bash
cci task run manage_decision_tables --operation list --status Active
```

#### 5. List Inactive Decision Tables
```bash
cci task run manage_decision_tables --operation list --status Inactive
```

#### 6. Query All Decision Tables (No Status Filter)
```bash
cci task run manage_decision_tables --operation query --status null
```

### Filtering by Developer Names

#### 7. List Specific Decision Tables
```bash
cci task run manage_decision_tables --operation list --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification"
```

#### 8. Query Specific Decision Tables
```bash
cci task run manage_decision_tables --operation query --developer_names RLM_CostBookEntries
```

#### 9. List Single Decision Table
```bash
cci task run manage_decision_tables --operation list --developer_names RLM_ProductQualification
```

### Refreshing Decision Tables

#### 10. Refresh All Active Decision Tables (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh
```

#### 11. Refresh All Active Decision Tables (Incremental Refresh)
```bash
cci task run manage_decision_tables --operation refresh --is_incremental true
```

#### 12. Refresh Specific Decision Tables (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification"
```

#### 13. Refresh Specific Decision Tables (Incremental Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification" --is_incremental true
```

#### 14. Refresh Single Decision Table (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names RLM_ProductQualification
```

#### 15. Refresh Single Decision Table (Incremental Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names RLM_ProductQualification --is_incremental true
```

### Activate and Deactivate Operations

#### 16. Activate Decision Tables (e.g. for prepare_decision_tables)
```bash
cci task run manage_decision_tables --operation activate --developer_names "RLM_ProductCategoryQualification,RLM_ProductQualification,RLM_CostBookEntries"
```
Uses the list from `dt_activation_decision_tables` in project config. Required for scratch org setup so qualification and cost book decision tables are Active.

#### 17. Deactivate Decision Tables
```bash
cci task run manage_decision_tables --operation deactivate --developer_names "RLM_ProductQualification"
```
Sets the specified decision table(s) to Inactive via the API.

### Validate Lists Operation

Compare decision tables in the org to the project's configured list anchors (`dt_*_decision_tables` in `cumulusci.yml`). Use this to ensure no org table is missing from refresh lists and no list entry points to a non-existent table.

#### 18. Validate All Project Decision Table Lists
```bash
cci task run manage_decision_tables --operation validate_lists
```
- Queries all active decision tables from the org (with UsageType).
- Discovers all anchors matching `dt_*_decision_tables` from project custom config.
- Reports: **Decision tables in org by UsageType**; **In org but not in any list**; **In lists but not in org** (invalid entries).

#### 19. Validate Specific List Anchors
```bash
cci task run manage_decision_tables --operation validate_lists -o list_anchors:"['dt_rating_decision_tables','dt_commerce_decision_tables']"
```
Validates only the specified anchors. Useful when you add a new list and want to verify it without scanning all anchors.

### Sorting Options

#### 20. List Decision Tables Sorted by LastSyncDate (Ascending)
```bash
cci task run manage_decision_tables --operation list --sort_by LastSyncDate --sort_order Asc
```

#### 21. List Decision Tables Sorted by DeveloperName
```bash
cci task run manage_decision_tables --operation list --sort_by DeveloperName --sort_order Asc
```

#### 22. Query Decision Tables Sorted by SetupName
```bash
cci task run manage_decision_tables --operation query --sort_by SetupName --sort_order Asc
```

### Combined Operations

#### 23. List Active Decision Tables with Custom Sorting
```bash
cci task run manage_decision_tables --operation list --status Active --sort_by LastSyncDate --sort_order Desc --limit 10
```

#### 24. Query Inactive Decision Tables
```bash
cci task run manage_decision_tables --operation query --status Inactive
```

#### 25. Refresh Active Decision Tables (Incremental) with Limit
```bash
cci task run manage_decision_tables --operation refresh --status Active --is_incremental true
```

---

## Common Use Cases

### Initial Setup - Refresh All Decision Tables

When setting up a new org, you typically need to refresh all decision tables:

```bash
# Full refresh of all active decision tables (recommended for initial setup)
cci task run manage_decision_tables --operation refresh
```

**Note:** There is a limit of 100 refreshes per hour. For initial setup, refresh all tables. For subsequent updates, use incremental refresh or refresh specific tables.

### Regular Maintenance - Incremental Refresh

For regular maintenance, use incremental refresh:

```bash
# Incremental refresh of all active decision tables
cci task run manage_decision_tables --operation refresh --is_incremental true
```

### Refresh Specific Decision Tables

When you know which tables need updating:

```bash
# Refresh specific decision tables (full refresh)
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification,RLM_ProductQualification"
```

### Audit Decision Table Status

Check the status and last sync date of all decision tables:

```bash
# List all active decision tables with their sync dates
cci task run manage_decision_tables --operation list --status Active --sort_by LastSyncDate --sort_order Desc
```

### Find Stale Decision Tables

Find decision tables that haven't been synced recently:

```bash
# Query all decision tables sorted by LastSyncDate (oldest first)
cci task run manage_decision_tables --operation query --sort_by LastSyncDate --sort_order Asc
```

### Check Decision Table Status Before Deployment

Before deploying decision table metadata, check which tables are active:

```bash
# List active decision tables (these cannot be edited while active)
cci task run manage_decision_tables --operation list --status Active
```

**Note:** Active decision tables cannot be edited. You may need to deactivate them before deployment (see `rlm_exclude_active_decision_tables` task).

---

## Integration with Other Tasks

### Using with RC_UpdateDecisionTables Flow

The `manage_decision_tables` task provides similar functionality to the `RC_UpdateDecisionTables` Screen Flow, but can be automated:

```bash
# Instead of running the flow manually, use the task:
cci task run manage_decision_tables --operation refresh --is_incremental true
```

### Using with Deployment Flows

Before deploying decision table metadata, check active tables:

```bash
# Check which decision tables are active
cci task run manage_decision_tables --operation list --status Active

# The prepare_core flow includes exclude_active_decision_tables task
# which automatically excludes active tables from deployment
```

---

## Operation Details

### List Operation

The `list` operation displays decision tables in a formatted table with:
- DeveloperName
- Status
- **UsageType** (e.g. DefaultPricing, DefaultRating, RatingDiscovery, RevenueStandardTax)
- LastSyncDate
- SetupName

**Example Output:**
```
Found 3 decision table(s):

DeveloperName                                    Status     LastSyncDate            SetupName
-------------------------------------------------------------------------------------------------------------------
RLM_CostBookEntries                              Active     2026-01-17 10:30:00     Cost Book Entries
RLM_ProductCategoryQualification                 Active     2026-01-17 09:15:00     Product Category Qualification
RLM_ProductQualification                         Active     2026-01-16 14:20:00     Product Qualification
```

### Query Operation

The `query` operation returns decision table data as JSON, useful for scripting or further processing.

**Example Output:**
```json
[
  {
    "DeveloperName": "RLM_CostBookEntries",
    "Status": "Active",
    "LastSyncDate": "2026-01-17T10:30:00.000Z",
    "SetupName": "Cost Book Entries"
  }
]
```

### Refresh Operation

The `refresh` operation triggers Salesforce to refresh decision table data from external sources.

**Refresh Types:**
- **Full Refresh** (`is_incremental: false`): Complete refresh of all data
- **Incremental Refresh** (`is_incremental: true`): Only refresh changed data since last sync

**Refresh Process:**
1. The task calls the Salesforce `refreshDecisionTable` action via Connect API
2. Salesforce processes the refresh asynchronously
3. The task reports success/failure for each table
4. Status is updated to reflect the refresh operation

**Important Notes:**
- Refresh operations are asynchronous and may take several minutes
- There is a limit of 100 refreshes per hour per org
- Active decision tables cannot be edited until refreshed/deactivated
- Refresh status can be checked via the `Status` field after refresh

---

## Task Options Reference

### Operation
- **Required**: Yes
- **Options**: `list`, `query`, `refresh`, `activate`, `deactivate`, `validate_lists`
- **Description**: The operation to perform

### Developer Names
- **Required**: No
- **Type**: String or comma-separated list
- **Description**: Specific decision table DeveloperNames to operate on
- **Example**: `"RLM_CostBookEntries"` or `"RLM_CostBookEntries,RLM_ProductCategoryQualification"`

### Status
- **Required**: No
- **Options**: `Active`, `Inactive`, or `null` (for all)
- **Default**: `Active` (for `list` and `refresh` operations)
- **Description**: Filter decision tables by status

### Is Incremental
- **Required**: No (only for `refresh` operation)
- **Type**: Boolean
- **Default**: `false` (full refresh)
- **Description**: `true` for incremental refresh, `false` for full refresh

### Sort By
- **Required**: No
- **Options**: `LastSyncDate`, `DeveloperName`, `SetupName`, `Status`
- **Default**: `LastSyncDate`
- **Description**: Field to sort results by

### Sort Order
- **Required**: No
- **Options**: `Asc`, `Desc`
- **Default**: `Desc`
- **Description**: Sort order (ascending or descending)

### Limit
- **Required**: No
- **Type**: Integer
- **Default**: None (no limit)
- **Description**: Maximum number of decision tables to return

### List Anchors (validate_lists only)
- **Required**: No
- **Type**: List of strings (YAML list or comma-separated)
- **Default**: All anchors matching `dt_*_decision_tables` in project custom config
- **Description**: Restrict validation to specific list anchor names (e.g. `dt_rating_decision_tables`, `dt_commerce_decision_tables`)

---

## Project List Anchors and Refresh Flow

Decision table lists are defined in `cumulusci.yml` under `project.custom` as YAML anchors and used by both CCI tasks and the **refresh_all_decision_tables** flow:

| Anchor | Purpose |
|--------|---------|
| `dt_rating_decision_tables` | Rating and rate card decision tables |
| `dt_rating_discovery_decision_tables` | Rating discovery resolution tables |
| `dt_default_pricing_decision_tables` | Default pricing and contract pricing tables (includes StandardTax) |
| `dt_asset_decision_tables` | Asset-specific rate and adjustment tables |
| `dt_pricing_discovery_decision_tables` | Pricing discovery and derived pricing tables |
| `dt_activation_decision_tables` | Tables activated during org prepare (RLM_ProductCategoryQualification, RLM_ProductQualification, RLM_CostBookEntries) |
| `dt_commerce_decision_tables` | Commerce decision tables (refreshed when `commerce: true`) |

The **refresh_all_decision_tables** flow runs: sync_pricing_data → refresh_dt_pricing_discovery → (rating steps when `rating: true`) → refresh_dt_commerce (when `commerce: true`). Individual refresh tasks (`refresh_dt_rating`, `refresh_dt_default_pricing`, etc.) use these same anchors.

---

## Org Utility Flows (Screen Flows)

Screen flows in the org provide manual refresh by category. Deployed from **unpackaged/post_utils** and **unpackaged/post_commerce**:

| Flow | Location | Description |
|------|----------|-------------|
| RC Refresh Pricing Decision Tables | post_utils | Refresh default pricing tables; includes Incremental toggle |
| RC Refresh Asset Decision Tables | post_utils | Refresh asset decision tables; includes Incremental toggle |
| RC Refresh Rate Card Decision Tables | post_utils | Refresh usage & rating decision tables; includes Incremental toggle |
| RC Refresh Commerce Decision Tables | post_commerce | Refresh Commerce decision tables (when Commerce is enabled) |
| RC UpdateDecisionTables | post_utils | Generic: select which decision tables to refresh from a list |

The Incremental toggle on Pricing, Asset, and Rate Card flows is wired to the **refreshDecisionTable** action (`IsIncremental` input) so the run is incremental or full based on user choice. Deploy post_utils: `cci task run deploy_post_utils`. Deploy Commerce flows: `cci task run deploy_post_commerce` (or enable `deploy_post_commerce` in prepare when `commerce: true`).

---

## Notes

- **Developer Names**: Use the exact `DeveloperName` of the decision table (e.g., `RLM_CostBookEntries`)
- **Status Values**: `Active`, `Inactive`
- **Refresh Limits**: Maximum 100 refreshes per hour per org
- **Active Tables**: Active decision tables cannot be edited. Use `rlm_exclude_active_decision_tables` task to exclude them from deployment, or deactivate them first.
- **Refresh Timing**: Refresh operations are asynchronous. Check the `LastSyncDate` field to verify completion.
- **Incremental vs Full**: 
  - Use **full refresh** for initial setup or when you need complete data refresh
  - Use **incremental refresh** for regular maintenance to only update changed data
- **Field Names**: 
  - `DeveloperName`: The API name of the decision table
  - `SetupName`: The user-friendly name
  - `UsageType`: Category (DefaultPricing, DefaultRating, RatingDiscovery, PricingDiscovery, RevenueStandardTax, etc.)
  - `LastSyncDate`: When the table was last refreshed
  - `Status`: `Active` or `Inactive`
- **SFDMU**: Expression set and decision table activate/deactivate are handled by CCI tasks (`manage_expression_sets`, `manage_decision_tables` / `activate_decision_tables`). The former SFDMU data plans for these have been removed from the repo.

---

## Troubleshooting

### Error: "Can't edit an active Decision Table"
**Solution**: Active decision tables cannot be edited. Either:
1. Deactivate the table first (if supported)
2. Use `rlm_exclude_active_decision_tables` task to exclude from deployment
3. Wait for the table to be refreshed/deactivated

### Error: "Limit of 100 refreshes per hour exceeded"
**Solution**: 
- Wait before refreshing more tables
- Use incremental refresh when possible
- Refresh only specific tables that need updating

### Refresh Operation Shows Success But Status Not Updated
**Solution**: 
- Refresh operations are asynchronous
- Wait a few minutes and check `LastSyncDate` again
- Use `list` or `query` operation to verify status

### No Decision Tables Found
**Solution**:
- Check if decision tables exist in the org
- Try querying without status filter: `--status null`
- Verify you're connected to the correct org
