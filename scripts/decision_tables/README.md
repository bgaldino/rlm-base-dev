# Decision Table helper scripts

A self-contained toolkit for Salesforce Revenue Cloud **BRE Decision Tables** —
the lookup tables a pricing recipe (or any Business Rules Engine expression set)
consults to resolve a value from a set of input conditions. It has **two layers**:

- **Read-only inspectors:** **list / describe / diff / trace / dump-data**. Safe
  anytime, on any org.
- **Guarded lifecycle mutators:** create / update / activate / deactivate /
  refresh / delete (definition) + **upload** (a `CsvUpload` table's data layer),
  **preview-by-default** (`--confirm` to write), designed after live CRUD probing
  on scratch orgs. Destructive testing runs on **disposable scratch orgs only**,
  never the shared `beta`.

Auth is delegated to the **`sf` CLI** (`sf api request rest --target-org …`), so
**no access token is ever handled or passed**. `--target-org` is always the
**SF CLI alias** (e.g. `rlm-base__beta`), **never** the CCI alias (`beta`).
Pinned to Release 262 / API v67.0.

Full guidance lives in the **decision-tables skill**:
`.cursor/skills/decision-tables/SKILL.md` (+ `authoring-and-data-model.md`,
`lifecycle-and-refresh.md`), with the object/ID/enum/error reference in
`docs/references/decision-table-api-reference.md` and the ops/task-centric
cookbook in `docs/references/decision-table-examples.md`.

## Independent of the CCI tasks

This package imports **nothing** from `tasks/`, and nothing under `tasks/`
imports from it. The CCI tasks (`tasks/rlm_manage_decision_tables.py`,
`tasks/rlm_refresh_decision_table.py`,
`tasks/rlm_configure_pricing_recipe_table_mappings.py`, …) remain the
**org-build path**: they own list/refresh/activate/deactivate/validate_lists
inside `prepare_rlm_org` and the recipe-mapping wiring. This toolkit is the
**ad-hoc inspection** path — reach for it to understand, diff, and trace a table
outside the build, without editing the build flow. The two encode the same
platform truths independently; the toolkit does not duplicate the tasks' logic.

**How these fit the lifecycle** (what to reach for, and when):

| Lifecycle stage | Production path | These helpers |
|-----------------|-----------------|---------------|
| **Author / deploy / refresh** a table in the build | CCI tasks + `.decisionTable-meta.xml` under `unpackaged/pre/5_decisiontables/` | the mutators below — one-off exploration & updates **outside** the build, on a disposable org |
| **Inspect / describe / diff / trace / dump** a definition | — | the read-only CLIs below (safe anytime) |
| **Validate the project's recipe→table mappings** | `manage_decision_tables --operation validate_lists` (authoritative) | `trace_decision_table.py` (read-only introspection — *what uses this table?*) |

## The two-layer model (why there are 5 setup objects + a data dump)

A Decision Table is **two layers**:

1. **Definition** — the columns (INPUT / OUTPUT / ROWCRITERIA), the source
   object / dataset links, the hit policy, and the row-filter criteria. This
   lives in metadata and across **5 Tooling API setup objects** (`DecisionTable`
   `0lD`, `DecisionTableParameter` `0lP`, `DecisionTableDatasetLink` `0lX`,
   `DecisionTblDatasetParameter` `0lZ`, `DecisionTableSourceCriteria` `0VT`).
   `describe`/`diff`/`trace` operate on this layer.
2. **Data** — the actual rows the engine evaluates. For an SObject-backed table
   these are records in the `sourceObject`; for a `CsvUpload` table they are an
   uploaded CSV (loaded by `upload_decision_table_data.py`); for a
   `ContextDefinition` table they are hydrated at runtime. Rows are synced into
   the BRE engine cache by the async `refreshDecisionTable` action (~100
   refreshes/hr). `dump_decision_table_data.py` samples this layer, branching on
   `dataSourceType`.

## Scripts

**Read-only inspectors (safe anytime):**

| Script | Org? | Purpose |
|--------|------|---------|
| `list_decision_tables.py` | Read-only | Rows grouped by `usageType`; filter `--status` / `--usage-type` / `--developer-name` (comma-separated IN). Tooling query over `DecisionTable`. |
| `describe_decision_table.py` | Read-only | Full definition: the `Metadata` complexvalue (dataSource / execution / hit policy / type) + columns grouped INPUT / OUTPUT / ROWCRITERIA + dataset links & their join params + source criteria. `--connect` also reads the table through the **Connect Definitions** GET and prints its **divergent field vocabulary** (`sourceType` / `decisionResultPolicy` / title-case `usage`) side by side. |
| `diff_decision_tables.py` | Read-only | Structural diff of two tables — in one org, or the **same table across two orgs** (`--other-org`, e.g. a scratch clone vs beta). Compares table + metadata attributes, columns (added / removed / changed, keyed `usage:fieldName`), dataset links, and source criteria. The comparison core (`diff_definitions`) is a **pure function**, unit-tested with no org. |
| `trace_decision_table.py` | Read-only | *What pricing recipes use this table?* Resolves the `DecisionTable` via **Tooling**, then queries `PricingRecipeTableMapping` via **normal REST** and matches on **`LookupTableId` == DecisionTable.Id** (SObject-backed) **OR `FileBasedDecisionTableName` == DeveloperName** (file/CSV-backed) — there is **no** `DecisionTableId` field on the mapping. Correlated in Python (no single cross-surface SOQL join). |
| `dump_decision_table_data.py` | Read-only | Samples the **data layer** (`--limit`), branching on `dataSourceType`: **SingleSobject** → SOQL the `sourceObject` (projecting the definition's fields, Id-only fallback); **MultipleSobjects** → one sample per dataset-link `SourceObject`; **CsvUpload** → the Connect **CSV Based** data GET (`.../{id}/data`, `rowData` per row; an empty or gated table degrades to a note — no offset pager, `totalRows` counts *returned* rows), with **CsvUpload-only** `--filter FIELD:VALUE` (server-side **exact, case-sensitive** equality on one column — a non-existent field returns 0 rows silently; drops `--limit` when combined, since `filter`+`limit` throws `UNKNOWN_EXCEPTION`) and `--version-number N` (read a specific import version); **ContextDefinition** → runtime-hydrated, no static table, reported & skipped. `--filter`/`--version-number` against a non-CsvUpload table degrade to a note. |

**Mutators (preview-by-default; `--confirm` to write):**

| Script | Writes (path) |
|--------|---------------|
| `create_decision_table.py` | Create from a canonical spec: Metadata deploy (`--path metadata`, default → temp SFDX package outside the repo) · Tooling POST · Connect POST. `--generate-only <path>` (metadata only) writes the `.decisionTable-meta.xml` to a chosen path without deploying. `status` in the spec sets the table's initial state. |
| `update_decision_table.py` | Tooling PATCH / Connect PATCH of an existing table. **Active-edit guard:** an Active table is refused unless `--deactivate-first`, which runs the guarded deactivate → edit → reactivate (`--leave-deactivated` keeps it off). The spec's `status` **never drives an update** — the lifecycle engine owns activate/deactivate, so the spec's `status` can't re-activate the table mid-edit (a Tooling PATCH *requires* `status`, so `update` stamps the current **live** status; the Connect PATCH drops it). `decisionTableParameters` is a **full replace**. |
| `activate_decision_table.py` | `Status` → Active (Tooling `Metadata.status` PATCH). **Async** — polls past `ActivationInProgress` (raise `--max-wait` for slow orgs). Skips a no-op if already Active. |
| `deactivate_decision_table.py` | `Status` → Inactive (**synchronous**). Blocked while the table is still referenced by an active Expression Set / Context Rule / recipe. |
| `refresh_decision_table.py` | `refreshDecisionTable` action (full / `--incremental`). Sends the **live-verified `isDecisionTableIncremental`** flag (the CCI tasks send `isIncremental`, which the action ignores). Async + ~100/hr — watch `LastSyncDate`, not the returned `Queued`. |
| `upload_decision_table_data.py` | Loads the **data layer** of a `CsvUpload` table (two-phase: insert a `ContentVersion` with the base64 CSV → POST its `068…` id to the Connect `/file` sub-resource). **Append (default) is the only reliable write** — `--overwrite` (`deleteAllRows:true`) **FAILS on 262/v67.0** (`uploadStatus=Failed`, 0 rows, existing rows kept; replace = a fresh version/table + append). `--activate-version N` activates version *N* after the upload. Async — poll `dump_decision_table_data.py` for the rows, or opt into `--wait-for-status` (`--max-wait N`, default 120s) to poll `Metadata.uploadStatus` to a terminal state and surface `CompletedWithErrors` (bad rows drop silently) / `Failed` (non-zero exit). |
| `delete_decision_table.py` | Tooling / Connect DELETE. Same active-edit guard as update (`--deactivate-first` to deactivate an Active table before deleting). `--confirm` required. |

They mirror the `scripts/expression_sets/` mutator convention (preview-by-default,
`--confirm`, sf-CLI transport, no token). The six definition-CRUD per-path shapes,
required fields, the active-edit error, the refresh flag, and the `CsvUpload`
two-phase data load (ContentVersion → Connect `/file`) were all confirmed by live
destructive probing on scratch orgs.

**Shared modules (imported by the CLIs, not run directly):**

| Module | Purpose |
|--------|---------|
| `_client.py` | The `sf api request rest` wrapper, `DEFAULT_API_VERSION="67.0"`. Exposes **explicit Tooling helpers** (`tooling_query` → `/tooling/query`, `tooling_sobject_request` → `/tooling/sobjects/<Obj>[/<id>][/describe]`) distinct from **normal REST** (`sobjects_request`, `soql_query`) and the **Connect** base (`connect/business-rules/decision-table`, `connect_request`/`connect_get`), plus the **CSV data-layer** helpers (`content_version_insert` → base64 CSV `ContentVersion`, `upload_decision_table_csv` → the `/file` POST, `get_decision_table_data` → the `/data` GET). SOQL follows `nextRecordsUrl`. The injectable `Transport` seam binds `target_org`/`api_version`/`dry_run`/`logger` and exposes `connect` / `connect_get` / `tooling_query` / `tooling_sobject` / `sobject` / `soql` / `content_version_insert` / `upload_decision_table_csv` / `get_decision_table_data`. `DecisionTableClientError` carries `error_codes`/`body`/`returncode`. |
| `_resolve.py` | DeveloperName → `DecisionTable` (`0lD`) summary + child resolution across the 5 Tooling objects. `load_definition()` assembles the whole definition dict (`table` / `metadata` / `parameters` / `datasetLinks` / `datasetParameters` / `sourceCriteria`); `get_connect_definition()` reads + unwraps the Connect `decisionTable` envelope. `ResolveError` on a missing table. |
| `_schema.py` | Enum + key-prefix catalogs (`DATA_SOURCE_TYPES`, `EXECUTION_TYPES` incl. `DLO`, `FILTER_RESULT_BY`, `PARAM_USAGE`, `SETUP_OBJECT_PREFIXES`, …), the **field-name divergence map** (`FIELD_NAME_MAP`: concept → Metadata/Tooling name vs Connect name), and `validate_spec()` — a **pure** validator over a canonical (Metadata-vocabulary) DT spec. Stdlib-only; reused by the offline tests. |
| `_payload.py` | **Pure** canonical-spec → per-path translators: `to_metadata` (the shared `Metadata` body), `to_metadata_xml` (byte-identical to the shipped source XML — elements emitted alphabetically), `to_tooling` (`{FullName, Metadata}` for create), `tooling_metadata_only` (`{Metadata}` for a PATCH — drops the spec's `status`, stamping the caller-supplied **live** `status` the required-field PATCH demands, so the lifecycle engine owns transitions), and `to_connect` (flat Connect body: renames `dataSourceType`→`sourceType`, `filterResultBy`→`decisionResultPolicy`, `decisionTableParameters`→`parameters`, title-cases `usage`, adds `columnMapping`, requires `status`). Dependency-free — no `requests`, no CCI, no `sf`. |
| `_lifecycle.py` | `LifecycleEngine` over a `Transport`: `activate` (async — polls past `ActivationInProgress`) / `deactivate` (sync), the **active-edit guard** (`assert_editable` + `run_guarded_update`: deactivate → mutate → reactivate; leaves the table DEACTIVATED on a failed Connect PATCH, reactivates on a failed atomic Tooling PATCH), `refresh` (`isDecisionTableIncremental`), the temp-SFDX `deploy_metadata_xml`, and Tooling/Connect `delete`. `LifecycleError` on failure. |

**Tests:** `tests/test_decision_tables_toolkit.py` — offline unit tests (no org,
no `sf`, no pytest) for `_schema` (enums / prefixes / divergence map / validator,
incl. the `CsvUpload` `sourceObject="CSV"` convention), `_resolve` query builders
+ definition assembly, `diff_definitions`, `dump_data` branch selection (incl. the
`CsvUpload` `/data` rows / empty / gated cases), `trace_recipe_mappings`
correlation, the `_payload` translators + the XML round-trip (incl. a `CsvUpload`
spec preserving all 7 `dataType`s through `to_metadata`/`to_tooling`/`to_connect`),
the `_lifecycle` active-edit guard and guarded-update transitions
(deactivate/reactivate, connect-failure-left-off vs tooling-failure-reactivates,
the refresh flag) plus the `wait_for_upload_status` poll (terminates on a terminal
status, surfaces `CompletedWithErrors`/`Failed`, no-ops in dry-run), and every
CLI's argparse + preview-vs-`--confirm` gating via a stubbed transport (no real
writes) — including `dump_decision_table_data.py`'s `--filter`
(drops `--limit`) / `--version-number` threading and its degrade-to-note on a
non-CsvUpload table, and `upload_decision_table_data.py`'s two-phase upload,
`--overwrite`, `--activate-version`, and `--wait-for-status` (non-zero exit on a
terminal `Failed`). Run: `python tests/test_decision_tables_toolkit.py`.

## Quick start — list → describe → trace → dump

```bash
ORG=rlm-base__beta

# 1. See what's in the org, grouped by usageType.
python scripts/decision_tables/list_decision_tables.py --target-org $ORG

# 1a. Filter to active pricing tables.
python scripts/decision_tables/list_decision_tables.py --target-org $ORG \
    --status Active --usage-type DefaultPricing

# 2. Pretty-print one table's full definition (columns / dataset links / criteria).
python scripts/decision_tables/describe_decision_table.py --target-org $ORG \
    --developer-name RLM_CostBookEntries

# 2a. Compare the Tooling + Connect Definitions vocabularies side by side.
python scripts/decision_tables/describe_decision_table.py --target-org $ORG \
    --developer-name RLM_CostBookEntries --connect

# 3. Which pricing recipes reference this table?
python scripts/decision_tables/trace_decision_table.py --target-org $ORG \
    --developer-name RLM_CostBookEntries

# 4. Structurally diff the same table across two orgs (e.g. a clone vs beta).
python scripts/decision_tables/diff_decision_tables.py \
    --target-org rlm-base__scratch --developer-name RLM_CostBookEntries \
    --other RLM_CostBookEntries --other-org $ORG

# 5. Sample the data layer (branches on dataSourceType).
python scripts/decision_tables/dump_decision_table_data.py --target-org $ORG \
    --developer-name RLM_CostBookEntries --limit 5
```

## Quick start — mutate (SCRATCH ORGS ONLY)

Every mutator **previews** without `--confirm` (reads run; mutating verbs are
logged and skipped). Run destructive round-trips on a **disposable scratch org**,
never `beta`.

```bash
ORG=rlm-base__scratch      # a scratch org, NOT beta

# Create from a canonical spec (Tooling path). Preview, then confirm.
python scripts/decision_tables/create_decision_table.py --target-org $ORG \
    --spec my_table.json --path tooling
python scripts/decision_tables/create_decision_table.py --target-org $ORG \
    --spec my_table.json --path tooling --confirm

# Generate the .decisionTable-meta.xml only (no deploy), to a path you choose.
python scripts/decision_tables/create_decision_table.py --target-org $ORG \
    --spec my_table.json --path metadata --generate-only ./MyTable.decisionTable-meta.xml

# Edit an ACTIVE table: deactivate → patch → reactivate (guarded).
python scripts/decision_tables/update_decision_table.py --target-org $ORG \
    --spec my_table.json --deactivate-first --confirm

# Activate (async — polls past ActivationInProgress) / deactivate (sync).
python scripts/decision_tables/activate_decision_table.py   --target-org $ORG \
    --developer-name RLM_MyTable --confirm
python scripts/decision_tables/deactivate_decision_table.py --target-org $ORG \
    --developer-name RLM_MyTable --confirm

# Load a CsvUpload table's rows (two-phase, append), then activate its version. Preview, then confirm.
# --wait-for-status polls uploadStatus to terminal (surfaces silent per-row drops → CompletedWithErrors).
python scripts/decision_tables/upload_decision_table_data.py --target-org $ORG \
    --developer-name RLM_MyCsvTable --csv rows.csv
python scripts/decision_tables/upload_decision_table_data.py --target-org $ORG \
    --developer-name RLM_MyCsvTable --csv rows.csv --activate-version 1 --wait-for-status --confirm

# Read the data layer back; --filter is exact/case-sensitive on one column (CsvUpload only).
python scripts/decision_tables/dump_decision_table_data.py --target-org $ORG \
    --developer-name RLM_MyCsvTable --filter Region:North
python scripts/decision_tables/dump_decision_table_data.py --target-org $ORG \
    --developer-name RLM_MyCsvTable --version-number 1

# Refresh the data layer (async, ~100/hr). Watch LastSyncDate, not the return.
python scripts/decision_tables/refresh_decision_table.py --target-org $ORG \
    --developer-name RLM_MyTable --incremental --confirm

# Delete a throwaway table (deactivate first if Active).
python scripts/decision_tables/delete_decision_table.py --target-org $ORG \
    --developer-name RLM_MyTable --deactivate-first --confirm
```

## Safety model

- **The inspectors are read-only.** `list` / `describe` / `diff` / `trace` /
  `dump` only ever issue GETs and SOQL — they never mutate. Safe on any org,
  including the shared `beta`.
- **The mutators are preview-by-default.** Every mutator runs its transport in
  dry-run unless `--confirm` is passed: reads execute, mutating verbs are logged
  and skipped. Destructive lifecycle testing runs on **disposable scratch orgs
  only**, never the shared `beta`.
- **Active tables can't be edited in place.** Modifying or deleting an existing
  artifact on an **Active** table is platform-blocked (`FIELD_NOT_UPDATABLE` /
  "Can't edit an active Decision Table") — deactivate first. `update` / `delete`
  refuse an Active table up front unless `--deactivate-first` runs the guarded
  deactivate → mutate → reactivate. The spec's `status` never drives an update, so
  it can't re-activate the table mid-edit — the lifecycle engine alone drives
  activate/deactivate. (A Tooling `Metadata` PATCH *requires* `status`, so `update`
  stamps the table's current live status; the Connect PATCH drops it.)
- **Refresh is async + rate-limited.** The data layer syncs into the engine
  cache via the async `refreshDecisionTable` action, capped ~100 refreshes/hr.
  Definition changes are **not** live until a refresh completes.
- **`--target-org` is the SF CLI alias**, never the CCI alias. CCI alias `beta`
  → SF CLI alias `rlm-base__beta`.
