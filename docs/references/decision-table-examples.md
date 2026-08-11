# Decision Table Management Task Examples

> **See also:** `docs/references/decision-table-api-reference.md` (the setup
> objects, Metadata deploy + Tooling authoring paths, enum catalog, and
> definition-vs-data model), the Decision Tables skill
> (`.cursor/skills/decision-tables/SKILL.md`), and the standalone read/mutate
> toolkit (`scripts/decision_tables/`). This file stays **ops/task-centric** —
> `manage_decision_tables` and refresh examples.

This document provides working examples for the `manage_decision_tables` CumulusCI task and related refresh tasks and flows.

## Decision Table Management (`manage_decision_tables`)

Decision Tables are Business Rules Engine (BRE) objects in Salesforce Revenue Cloud that store decision logic. This task provides comprehensive management capabilities: **list** (with UsageType), **query**, **refresh**, **activate**, **deactivate**, and **validate_lists** (compare org to project list anchors).

> ⚠ **Incremental-refresh caveat.** The CCI task implementations send
> `isIncremental`, which the Release 262 action silently ignores; their
> `--is_incremental true` option therefore still queues a **full** refresh. Use
> `scripts/decision_tables/refresh_decision_table.py --incremental --confirm`
> when an actual incremental refresh is required; it sends the platform's
> `isDecisionTableIncremental` input.

> **Org targeting.** `manage_decision_tables` and every `refresh_dt_*` task accept
> `--org "your-cci-alias"`. The examples below omit it and therefore run against the
> default CCI org; pass `--org` to target another.

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
cci task run manage_decision_tables --operation query --status ""
```
(The status filter defaults to `Active`. Pass an **empty string** to clear it and
include every status — a literal `--status null` would filter for a status named
`null` and match nothing.)

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

#### 11. Legacy Incremental Option (Currently Falls Back to Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --is_incremental true
```

#### 12. Refresh Specific Decision Tables (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification"
```

#### 13. Legacy Incremental Option for Specific Tables (Currently Full)
```bash
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification" --is_incremental true
```

#### 14. Refresh Single Decision Table (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names RLM_ProductQualification
```

#### 15. Legacy Incremental Option for One Table (Currently Full)
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
cci task run manage_decision_tables --operation validate_lists -o list_anchors "dt_rating_decision_tables,dt_commerce_decision_tables"
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

#### 25. Legacy Incremental Option with Limit (Currently Full)
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

**Note:** Full refreshes use separate org-wide hourly pools: 40 Standard and 60
Advanced; CSV tables use the Advanced pool. Batch initial setup accordingly.

### Regular Maintenance - Incremental Refresh

For a real incremental refresh, use the standalone toolkit:

```bash
python scripts/decision_tables/refresh_decision_table.py \
  --target-org "your-sf-alias" --developer-name RLM_CostBookEntries \
  --incremental --confirm
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

### Refreshing without the UI

Decision tables are refreshed interactively from the **Decision Table Manager** on the
Home page, which also shows a freshness verdict per table. (It replaced the
`RLM_Refresh_Decision_Tables` screen flow, which is gone.) The `manage_decision_tables`
task does the same job non-interactively:

```bash
# Instead of running the flow manually, use the task for a full refresh:
cci task run manage_decision_tables --operation refresh
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

DeveloperName                                      Status     UsageType                    LastSyncDate              SetupName
-------------------------------------------------------------------------------------------------------------------
RLM_CostBookEntries                                Active     DefaultPricing               <timestamp>               Cost Book Entries
RLM_ProductCategoryQualification                   Active     DefaultPricing               <timestamp>               Product Category Qualification
RLM_ProductQualification                           Active     DefaultPricing               <timestamp>               Product Qualification
```

### Query Operation

The `query` operation returns decision table data as JSON, useful for scripting or further processing.

**Example Output:**
```json
[
  {
    "Id": "0lD...",
    "DeveloperName": "RLM_CostBookEntries",
    "Status": "Active",
    "LastSyncDate": "<timestamp>",
    "SetupName": "Cost Book Entries",
    "UsageType": "DefaultPricing"
  }
]
```

### Refresh Operation

The `refresh` operation triggers Salesforce to refresh decision table data from external sources.

**Refresh Types:**
- **Full Refresh** (`is_incremental: false`): Complete refresh of all data
- **Incremental Refresh**: Use the standalone toolkit command above; the CCI
  tasks perform full refreshes.

**Refresh Process:**
1. The task calls the Salesforce `refreshDecisionTable` standard action
2. Salesforce processes the refresh asynchronously
3. The task reports success/failure for each table
4. The relevant sync timestamp advances when the asynchronous refresh completes

**Important Notes:**
- Refresh operations are asynchronous and may take several minutes
- Full refreshes use separate hourly pools: 40 Standard and 60 Advanced per org
- Active decision tables must be deactivated before their definitions can be edited
- Refresh completion can be checked via `LastSyncDate` (full) or
  `LastIncrementalSyncDate` (incremental), not the table lifecycle `Status`

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
- **Options**: `Active`, `Inactive`, or `""` (empty string, for all)
- **Default**: `Active` (applied by `_build_soql_query`, so it backs `list`, `query`, `refresh`, and `validate_lists`; pass an empty `--status ""` to include all statuses — a non-empty value including the literal `null` is used as-is in the `Status =` filter and matches only a status of that name)
- **Description**: Filter decision tables by status

### Is Incremental
- **Required**: No (only for `refresh` operation)
- **Type**: Boolean
- **Default**: `false` (full refresh)
- **Description**: These CCI tasks perform a full refresh. Use the standalone
  toolkit when an incremental refresh is required.

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
| `dt_commerce_decision_tables` | Commerce decision tables (refreshed when `commerce: true` **or** `tso: true`) |
| `dt_prm_pricing_decision_tables` | PRM partner-pricing decision tables (refreshed when `prm` **and** `prm_pricing`) |

The **refresh_all_decision_tables** flow runs: sync_pricing_data → refresh_dt_pricing_discovery → (rating steps when `rating: true`) → refresh_dt_default_pricing (always) → refresh_dt_commerce (when `commerce: true` **or** `tso: true`) → refresh_dt_prm_pricing (when `prm` and `prm_pricing`). Individual refresh tasks (`refresh_dt_rating`, `refresh_dt_default_pricing`, etc.) use these same anchors.

The Commerce step is also gated on `tso` because that template includes Commerce
tables even when the Commerce feature is not configured.

---

## In-Org Refresh Entry Points

Interactive refresh uses the **Decision Table Manager** component on the Revenue
Cloud Home page. The remaining `post_utils` refresh flows are autolaunched.

| Entry point | Location | Type | Use |
|---|---|---|---|
| **Decision Table Manager** | `post_utils` LWC, Home page | Component | Interactive: per-table verdict, selective refresh, status polling |
| `RLM_Refresh_Decision_Tables_Bulk` | `post_utils` | **Autolaunched** | The only way Apex can reach the refresh action — `Flow.Interview.createInterview(...).start()`. Carries the incremental input |
| `RLM_Refresh_Decision_Tables_By_Usage_Type` | `post_utils` | **Autolaunched** | Refreshes every table sharing a usage type; called by `RLM_Account_Utilities` |
| `RLM_Refresh_Commerce_Decision_Tables` | `post_commerce` | **Screen flow** | The one surviving screen flow — Commerce tables, when Commerce is enabled |
| `check_decision_table_freshness` | CCI task | Headless | Verdicts without a browser; `-o param1 strict` fails a build on any stale table |

The action input is `isDecisionTableIncremental`, not `isIncremental`. The
`RLM_Refresh_Decision_Tables_Bulk` flow maps its flow variable to the correct
action input.

⚠ Incremental sync is **disabled on every decision table this repo ships**, so an
incremental request is accepted and then changes nothing. The Manager refuses one on such
a table rather than queueing a no-op.

Deploy: `cci task run deploy_post_utils`. Commerce flow: `cci task run deploy_post_commerce`
(or enable `deploy_post_commerce` in prepare when `commerce: true`).

---

## Notes

- **Developer Names**: Use the exact `DeveloperName` of the decision table (e.g., `RLM_CostBookEntries`)
- **Status Values**: `Active`, `Inactive`
- **Refresh Limits**: Separate 40 Standard / 60 Advanced full-refresh pools per org/hour
- **Active Tables**: Active decision tables cannot be edited. Use `rlm_exclude_active_decision_tables` task to exclude them from deployment, or deactivate them first.
- **Refresh Timing**: Refresh operations are asynchronous. Check the `LastSyncDate` field to verify completion.
- **Incremental vs Full**:
  - Use **full refresh** for initial setup or when you need complete data refresh
  - Use the standalone toolkit for a true **incremental refresh**
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

### Error: Full-refresh hourly limit exceeded
**Solution**: 
- Wait before refreshing more tables
- Use the standalone toolkit's incremental refresh when the table supports it
- Refresh only specific tables that need updating

### Refresh Operation Shows Success But Status Not Updated
**Solution**: 
- Refresh operations are asynchronous
- Wait a few minutes and check `LastSyncDate` again
- Use `list` or `query` operation to verify status

### No Decision Tables Found
**Solution**:
- Check if decision tables exist in the org
- Try querying without status filter: `--status ""` (empty string; the default is `Active`)
- Verify you're connected to the correct org
