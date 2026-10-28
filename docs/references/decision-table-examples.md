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

> ⚠ **Refresh-type caveat.** The CCI tasks' incremental option
> (`is_incremental` here, `isIncremental` on `refresh_dt_*`) sends the platform's
> `isDecisionTableIncremental` input. Before issue #351 they sent `isIncremental`,
> which the action silently ignores. In Release 264 `true` runs an incremental, but
> `false` lets the platform choose: a "full" request can run as incremental and stamp
> only `LastIncrementalSyncDate`. Judge a refresh by the later of the two stamps. See
> the decision-tables skill, `lifecycle-and-refresh.md` → *Release 264 chooses the
> refresh type*.

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

#### 11. Incremental Refresh
```bash
cci task run manage_decision_tables --operation refresh --is_incremental true
```

#### 12. Refresh Specific Decision Tables (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification"
```

#### 13. Incremental Refresh of Specific Tables
```bash
cci task run manage_decision_tables --operation refresh --developer_names "RLM_CostBookEntries,RLM_ProductCategoryQualification" --is_incremental true
```

#### 14. Refresh Single Decision Table (Full Refresh)
```bash
cci task run manage_decision_tables --operation refresh --developer_names RLM_ProductQualification
```

#### 15. Incremental Refresh of One Table
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
- Reports: **Decision tables in org by UsageType**; **In org but not in any list**; **In configured lists but not active in org**.
- Each list with missing names is attributed to the flow steps that use it, read from `cumulusci.yml`: a task whose `developerNames`/`developer_names` option holds the list, and the `when:` of every flow step that runs it, evaluated as the flow runner does. A missing name is **expected** when every such step is off for this project's flags (the `dt_commerce_decision_tables` names on a `commerce: false`, `tso: false` build), and **UNEXPECTED** when one runs, or when no flow uses the list. It is **UNKNOWN** when a condition can't be evaluated: CumulusCI isn't installed, or the expression errors (which would fail the flow too). Every flow counts, not only the build. A name in several lists is judged once per list. Each missing name also says whether it exists in the org in another status.
- Flags come from the project config, not from the org: a build run with a runtime `-o` override can differ.
- `-o strict true` fails the task on any name not explained by a flag (UNEXPECTED or UNKNOWN). With no active tables at all it still runs the comparison, so every list in use fails. Default: report only.

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

#### 25. Incremental Refresh with a Status Filter
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

⚠ **Release 264 does not consult `isIncrementalSyncEnabled`** (read from Core source
and confirmed live, 2026-10-27): an incremental request runs whatever the flag says,
and a full request can run as incremental too. See the decision-tables skill,
`lifecycle-and-refresh.md` → *Release 264 chooses the refresh type*. The flag is
`false` on every table this repo ships, and nothing here gates on it.

Request an incremental refresh with the standalone toolkit:

```bash
python scripts/decision_tables/refresh_decision_table.py \
  --target-org "your-sf-alias" --developer-name RLM_CostBookEntries \
  --incremental --confirm
```

It is rejected on a LowVolume table, and runs full after a failed incremental or on a
source that hard-deletes records. `--allow-disabled-incremental` is accepted for
compatibility and has no effect.

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

**Note:** An Active table accepts an unchanged or non-structural redeploy (e.g. a description change) but rejects a structural one ("Can't edit an active Decision Table"). The build handles this with `deactivate_changed_decision_tables` (see below).

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

# prepare_core runs deactivate_changed_decision_tables before deploy_pre: it
# check-only deploys the repo's tables that are Active in the org and deactivates
# only those the platform refuses to edit in place, then deploys those tables
# itself: because the XML says <status>Active</status>, that deploy reactivates and
# syncs them (on failure it tries to reactivate them and
# fails, naming any it could not reactivate).
# deploy_post_prm_pricing does the same for the PRM table.
cci task run deactivate_changed_decision_tables --org <org>   # standalone, before a manual deploy
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
- **Full Refresh** (`is_incremental: false`): in Release 264 this lets the platform
  choose, and it can run as incremental
- **Incremental Refresh** (`is_incremental: true`): runs incremental unless the last
  incremental failed or the source hard-deletes. It usually advances `LastIncrementalSyncDate`
  only; a first incremental on a table with no incremental history was measured
  stamping both.

**Refresh Process:**
1. The task calls the Salesforce `refreshDecisionTable` standard action
2. Salesforce processes the refresh asynchronously
3. The task reports, per table, whether the refresh queued. `manage_decision_tables`
   fails if any table does not queue. The `refresh_dt_*` build tasks first skip, with a
   warning, any listed table that is missing or inactive in the org (the lists are not
   org-scoped), then fail if an active table does not queue
4. The relevant sync timestamp advances when the asynchronous refresh completes

**Important Notes:**
- Refresh operations are asynchronous and may take several minutes
- Full refreshes use separate hourly pools: 40 Standard and 60 Advanced per org
- Active decision tables must be deactivated before their definitions can be edited
- Refresh completion is the later of `LastSyncDate` (a full refresh ran) and
  `LastIncrementalSyncDate` (an incremental ran), not the table lifecycle `Status`.
  In Release 264 the type requested does not decide which one moves

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
- **Default**: `false` (in Release 264, the platform chooses full or incremental)
- **Description**: Sends `isDecisionTableIncremental`. In Release 264 `false` lets the
  platform choose full or incremental itself; `true` runs incremental.

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

### Strict (validate_lists only)
- **Required**: No
- **Type**: Boolean
- **Default**: False
- **Description**: Fail when a listed table is missing or inactive and its flags don't explain it (a step that uses its list runs, no flow uses the list, or a condition can't be evaluated)

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
| `RLM_Refresh_Decision_Tables_By_Usage_Type` | `post_utils` | **Autolaunched** | Selects every **active** table with a usage type and hands them to `RLM_Refresh_Decision_Tables_Bulk`; returns `queuedCount`, `failedCount`, `failedApiNames`. Called by `RLM_Account_Utilities`, which shows the counts on its result screen |
| `RLM_Refresh_Commerce_Decision_Tables` | `post_commerce` | **Screen flow** | The one surviving screen flow — Commerce tables, when Commerce is enabled. Refreshes through `RLM_Refresh_Decision_Tables_Bulk` and ends on a result screen, so deploy `post_utils` first |
| `check_decision_table_freshness` | CCI task | Headless | Verdicts without a browser; `-o param1 strict` fails a build on any stale table |

The action input is `isDecisionTableIncremental`, not `isIncremental`. The
`RLM_Refresh_Decision_Tables_Bulk` flow maps its flow variable to the correct
action input.

The Manager judges freshness by the later of `LastSyncDate` and
`LastIncrementalSyncDate`, the rule the Decision Table app page uses, because Release
264 can run a full request as incremental (issue #587). It no longer refuses an
incremental request on a table with `IsIncrementalSyncEnabled` false: 264 does not
consult that flag.

Deploy: `cci task run deploy_post_utils`. Commerce flow: `cci task run deploy_post_commerce`,
which no build flow runs. Deploy `post_utils`
first: the Commerce flow calls `RLM_Refresh_Decision_Tables_Bulk`, and `post_utils` only
deploys on its own when `quantumbit` or `tso` is on.

---

## Notes

- **Developer Names**: Use the exact `DeveloperName` of the decision table (e.g., `RLM_CostBookEntries`)
- **Status Values**: `Active`, `Inactive`
- **Refresh Limits**: Separate 40 Standard / 60 Advanced full-refresh pools per org/hour
- **Active Tables**: An Active table rejects a structural change. `deactivate_changed_decision_tables` (in `prepare_core`) deactivates exactly the tables that need it and deploys them at once, which reactivates them.
- **Refresh Timing**: Refresh operations are asynchronous. Check the later of `LastSyncDate` and `LastIncrementalSyncDate` to verify completion.
- **Incremental vs Full**:
  - Use **full refresh** for initial setup or when you need complete data refresh
  - In Release 264 a full request can run as incremental (see the caveat at the top), so
    check the later of `LastSyncDate` and `LastIncrementalSyncDate`
- **Field Names**: 
  - `DeveloperName`: The API name of the decision table
  - `SetupName`: The user-friendly name
  - `UsageType`: Category (DefaultPricing, DefaultRating, RatingDiscovery, PricingDiscovery, RevenueStandardTax, etc.)
  - `LastSyncDate`: When the table last had a full refresh (`LastIncrementalSyncDate`: an incremental one)
  - `Status`: `Active` or `Inactive`
- **SFDMU**: Expression set and decision table activate/deactivate are handled by CCI tasks (`manage_expression_sets`, `manage_decision_tables` / `activate_decision_tables`). The former SFDMU data plans for these have been removed from the repo.

---

## Troubleshooting

### Error: "Can't edit an active Decision Table"
**Solution**: Active decision tables cannot be edited. Either:
1. Run `cci task run deactivate_changed_decision_tables --org <org>`, which deploys the
   change itself, or deactivate with
   `manage_decision_tables -o operation deactivate -o developer_names <name>` and rerun the deploy.
   Either deploy reactivates the table because its XML carries `<status>Active</status>`.
2. If the error came from `prepare_core`, the pre-deploy check did not attribute it to a
   table — read that task's log for the check-only failure it reported.

### Error: Full-refresh hourly limit exceeded
**Solution**: 
- Wait before refreshing more tables
- Request an incremental refresh (`is_incremental: true`). It is not a full refresh, so it should not draw on the full-refresh pool (not verified). A forced full (after a failed incremental, or on a source that hard-deletes records) does. LowVolume tables reject it
- Refresh only specific tables that need updating

### Refresh Operation Shows Success But Status Not Updated
**Solution**: 
- Refresh operations are asynchronous
- Wait a few minutes and check the later of `LastSyncDate` and `LastIncrementalSyncDate` again
- Use `list` or `query` operation to verify status

### No Decision Tables Found
**Solution**:
- Check if decision tables exist in the org
- Try querying without status filter: `--status ""` (empty string; the default is `Active`)
- Verify you're connected to the correct org
