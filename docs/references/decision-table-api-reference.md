# Decision Table Programmatic Management — Reference

> **Release 262 / API v67.0.** Setup/admin reference for programmatically
> reading, authoring, and managing Business Rules Engine (BRE) **Decision
> Tables** — the definition (columns + source binding) and its data/refresh
> lifecycle. This is **not** a runtime business API (for runtime lookup/execute,
> see the *Runtime resources* section, secondary).
>
> Companion to the Decision Tables skill
> (`.cursor/skills/decision-tables/SKILL.md`, the task-level entry point), the
> read/mutate toolkit (`scripts/decision_tables/`), the CCI management tasks
> (`tasks/rlm_manage_decision_tables.py`, `tasks/rlm_refresh_decision_table.py`),
> and the ops examples (`docs/references/decision-table-examples.md`). For where
> Decision Tables fit the **pricing** layering model (recipes → table mappings),
> see `.cursor/skills/pricing-wiring/SKILL.md`.
>
> **Verification legend.** Sections marked **✅ live-verified** were confirmed
> against a live Release 262 / v67.0 org — reads on a shared org, and the
> destructive create/update/activate/deactivate/refresh/delete lifecycle on a
> disposable scratch org (never a shared one). A few sections remain
> **📄 doc-grounded** (from `meta_decisiontable.htm`, `dt_setup_objects.htm`,
> `lookup_table_resources.htm`) where no org exercised the path — each is called
> out inline (the other Connect runtime resources and the ~100/hr refresh-limit
> rejection text). The `CsvUpload` data layer — the two-phase `/file` upload and
> the `/data` GET — is now **✅ live-verified** (see *CSV Based tables*).
> Re-verify on the target release at merge time.

## The two-layer model

A Decision Table is **two layers**:

1. **Definition** — the columns (inputs / outputs / row-criteria), the hit
   policy, and the binding to a data source. Lives in **Metadata API**
   (`.decisionTable-meta.xml`) and, equivalently, in the **Tooling** setup
   objects (the `DecisionTable.Metadata` complexvalue inlines the children).
2. **Data** — the rows the engine evaluates. Rows live in the **source SObject**
   (`SingleSobject` / `MultipleSobjects` / `ContextDefinition`) or a **CSV
   upload** (`CsvUpload`). Rows are synced into the BRE engine cache by the
   **async `refreshDecisionTable` action** (rate-limited, see *Refresh*).

Editing the definition ≠ refreshing the data. A definition change is deployed;
a data change is picked up by a refresh. An **Active** table's definition cannot
be modified in place — deactivate first (see *Lifecycle*).

## Supported management paths

Decision Table authoring spans **three APIs with divergent field vocabularies**.
Pick by use case; the toolkit's canonical spec + per-path translators
(`scripts/decision_tables/_payload.py`) hide the divergence.

- **Metadata API — source-controlled authoring (primary).** ✅ The shipped
  path: `.decisionTable-meta.xml` under `unpackaged/pre/5_decisiontables/` (and
  `unpackaged/post_prm_pricing/decisionTables/`), deployed via
  `sf project deploy start` / CCI `Deploy`. Uses `dataSourceType`,
  `filterResultBy`, `decisionTableParameters`, `usage` = `INPUT`/`OUTPUT`.
- **Tooling API — the 5 setup objects.** ✅ Read/inspect via
  `/services/data/v67.0/tooling/query` and
  `/services/data/v67.0/tooling/sobjects/<Object>`; each `DecisionTable` carries
  a **`Metadata` complexvalue** that inlines the parameters/criteria/import
  versions and matches the Metadata-API vocabulary exactly.
- **Connect API — Decision Table Definitions CRUD.** ✅ (GET/POST verified read
  side) `connect/business-rules/decision-table/definitions[/{id}]`. Uses a
  **different vocabulary** (`sourceType`, `decisionResultPolicy`, `parameters`,
  `usage` = `Input`/`Output`, 15-char `id`). The **collection endpoint is
  POST-only** (create) — there is no list-GET; GET is by-id.

---

## Object / ID model (Tooling) — ✅ live-verified

| Object | Key prefix | Role |
|---|---|---|
| `DecisionTable` | `0lD` | The definition. `DeveloperName` = api name; `Status`, `UsageType`, `SourceObject`, `LastSyncDate`, and the **`Metadata`** complexvalue. |
| `DecisionTableParameter` | `0lP` | A column. `DecisionTableId`, `FieldName`, `Usage` (INPUT/OUTPUT/ROWCRITERIA), `Operator`, `Sequence`, `DataType`, `FieldPath`, `IsRequired`, `IsGroupByField`, `SortType`, `DomainObject`. |
| `DecisionTableDatasetLink` | `0lX` | Binds a source SObject for `MultipleSobjects`. `DecisionTableId`, `SourceObject`, `SetupName`, `IsDefault`, `Metadata`. |
| `DecisionTblDatasetParameter` | `0lZ` | Join layer: maps a dataset link's field to a parameter. `DecisionTableDatasetLinkId`, `DecisionTableParameterId`, `DatasetFieldName`, `DatasetSourceObject`. |
| `DecisionTableSourceCriteria` | `0VT` | Row-filter on the source (v59.0+). `DecisionTableId`, `SourceFieldName`, `Operator`, `Value`, `ValueType`, `SequenceNumber`. |

The 5 objects are **Tooling API only** — they are not on the normal REST
`/sobjects` surface. All 5 are independently queryable.

### The `DecisionTable.Metadata` complexvalue — ✅ live-verified

A Tooling GET of `DecisionTable/{id}` returns `Metadata` with these keys (the
Metadata-API field names), children inlined:

```
collectOperator, conditionCriteria, conditionType, dataSourceType,
dataSpaceName, decisionTableFileImportVersions[], decisionTableParameters[],
decisionTableSourceCriterias[], description, doesConsiderNullValue,
downloadStatus, dtRowLevelOverrideType, executionType, filterResultBy,
hasIncrementalSyncFailed, isIncrementalSyncEnabled, isVersioned,
lastIncrementalSyncDate, lastSyncDate, refreshFailureReason, refreshStatus,
setupName, sourceConditionLogic, sourceObject, status, type, uploadStatus,
urls, usageType
```

Each `decisionTableParameters[]` entry: `dataType, decimalScale, domainObject,
fieldName, fieldPath, isGroupByField, isPriorityField, isRequired, length,
operator, sequence, sortType, usage`.

---

## Metadata API — `.decisionTable-meta.xml` — ✅ live-verified

Folder `decisionTables/`; MDAPI suffix `.decisionTable`; **source format
`.decisionTable-meta.xml`** (what this repo uses). Annotated shape (real repo
file `RLM_CostBookEntries`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DecisionTable xmlns="http://soap.sforce.com/2006/04/metadata">
    <conditionCriteria>1</conditionCriteria>          <!-- boolean logic over INPUT sequences -->
    <conditionType>All</conditionType>                <!-- All | Any | Custom -->
    <dataSourceType>SingleSobject</dataSourceType>     <!-- see enums -->
    <decisionTableParameters>                          <!-- one per column -->
        <dataType>String</dataType>
        <fieldName>ProductId</fieldName>
        <fieldPath>ProductId</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>true</isRequired>
        <operator>Equals</operator>                    <!-- INPUT only -->
        <sequence>1</sequence>                          <!-- INPUT only; referenced by conditionCriteria -->
        <usage>INPUT</usage>                            <!-- INPUT | OUTPUT | ROWCRITERIA -->
    </decisionTableParameters>
    <decisionTableParameters>
        <dataType>String</dataType>
        <fieldName>Cost</fieldName>
        <fieldPath>Cost</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>false</isRequired>
        <usage>OUTPUT</usage>                           <!-- no operator/sequence -->
    </decisionTableParameters>
    <doesConsiderNullValue>false</doesConsiderNullValue>
    <executionType>Hbase</executionType>               <!-- ⚠ MDAPI casing 'Hbase'; Tooling/Connect return 'HBASE' -->
    <filterResultBy>OutputOrder</filterResultBy>        <!-- hit policy -->
    <hasIncrementalSyncFailed>false</hasIncrementalSyncFailed>
    <isIncrementalSyncEnabled>false</isIncrementalSyncEnabled>
    <setupName>Cost Book Entries</setupName>
    <sourceObject>CostBookEntry</sourceObject>
    <status>Active</status>                             <!-- deploy-time status -->
    <type>MediumVolume</type>
    <usageType>DefaultPricing</usageType>
</DecisionTable>
```

> ⚠ **`executionType` casing is representation-specific.** Source XML uses
> `Hbase`; Tooling `Metadata` and Connect return `HBASE`. Do not "correct" the
> XML casing to match the API read — keep each representation's native form.

---

## Enum catalog — 📄 doc-grounded (values in **bold** ✅ observed live)

| Field | Values |
|---|---|
| `dataSourceType` (MD/Tooling) / `sourceType` (Connect) | ContextDefinition, **CsvUpload**, **MultipleSobjects**, **SingleSobject** |
| `executionType` | **DLO** (v67.0+, replaces DMO), **HBASE**/`Hbase`, HBPO, SOLR, SOQL |
| `conditionType` | **All**, Any, Custom |
| `filterResultBy` (MD) / `decisionResultPolicy` (Connect) | AnyValue, CollectOperator, FirstMatch, **OutputOrder**, Priority, RuleOrder, UniqueValues |
| `type` | Advanced, HighScaleExecution, HighVolume, LowVolume, **MediumVolume**, RealTime |
| `status` | ActivationInProgress, **Active**, Draft, Inactive |
| `usageType` (ExpsSetProcessType) | Bre (default), **DefaultPricing**, **DefaultRating**, **PricingDiscovery**, **RatingDiscovery**, **RevenueStandardTax**, ProductCategoryQualification, ProductQualification, RecordAlert, … |
| `DecisionTableParameter.usage` | **INPUT**, **OUTPUT**, ROWCRITERIA |
| `DecisionTableParameter.dataType` | **Boolean**, **Currency**, **Date**, **DateTime**, **Number**, **Percent**, **String** (all 7 round-tripped live through a CsvUpload — per-cell CSV encoding in *CSV Based tables*; DateTime needs `…T…:….sssZ`, Boolean only `true`/`false`) |
| `DecisionTableParameter.operator` | **Equals**, NotEquals, GreaterThan, **GreaterOrEqual**, LessThan, **LessOrEqual**, ExistsIn, Matches, IsNull, … |
| `DecisionTableSourceCriteria.valueType` | Formula, **Literal**, Lookup, Parameter, Picklist |
| `collectOperator` | **None**, … (used when `filterResultBy=CollectOperator`) |
| `dtRowLevelOverrideType` (MD/Tooling) / `rowLevelOverrideType` (Connect) | **None**, … |

**v67.0 additions:** `decisionTableFileImportVersions[]` (per-import activation
windows / rank / refresh; observed empty on SObject-backed tables),
`isVersioned` (default true per docs; observed **false** on shipped
SObject-backed tables and **null** via Connect).

---

## Field-name divergence (the three paths) — ✅ live-verified

| Concept | Metadata / Tooling `Metadata` | Connect Definitions |
|---|---|---|
| data source | `dataSourceType` | **`sourceType`** |
| hit policy | `filterResultBy` | **`decisionResultPolicy`** |
| columns | `decisionTableParameters[]` | **`parameters[]`** |
| source criteria | `decisionTableSourceCriterias[]` | **`sourceCriteria[]`** |
| row override | `dtRowLevelOverrideType` | **`rowLevelOverrideType`** |
| column `usage` value | `INPUT` / `OUTPUT` (upper) | **`Input` / `Output`** (title) |
| api name | `fullName` (MD) / `DeveloperName` (Tooling) | `fullName` |
| id | 18-char record Id | **15-char** id |

Connect GET returns `dataSourceType: null` (it populates `sourceType`) and
`isVersioned: null` — do not read Metadata-API keys off a Connect response.

---

## Connect API — Decision Table Definitions — ✅ live-verified (full CRUD)

Base: `connect/business-rules/decision-table/definitions`.

| Verb | Path | Status |
|---|---|---|
| **GET** by-id | `.../definitions/{id}` → `{ "code":"200", "decisionTable": {…} }` | ✅ verified |
| **GET** collection | `.../definitions` | ✅ verified → **405** (POST-only; no list) |
| **POST** create | `.../definitions` (flat body, NOT wrapped in `decisionTable`) | ✅ verified |
| **PATCH** update | `.../definitions/{id}` (same flat body) | ✅ verified |
| **DELETE** | `.../definitions/{id}` (empty body on stdin — `-b -`) | ✅ verified |

**POST create — required fields** (learned by iteration on a scratch org): the
create body is **flat** (no `decisionTable` wrapper). The label field is
**`setupName`** — `label` and `masterLabel` are both rejected
(`JSON_PARSER_ERROR: Unrecognized field`). **`status` is required**
(`MISSING_ARGUMENT: Specify a valid value for status parameter` without it; the
toolkit defaults it to `Draft`). Every column needs a **`columnMapping`**
(set == `fieldName` when the author omits it) and title-case `usage`
(`Input`/`Output`).

> ⚠ **GET-vs-POST shape gap.** The create response echoes
> `"parameters": [], "sourceCriteria": []` (empty) **even though the columns
> persist** — a GET-back confirms both columns. Never trust the POST echo for the
> column set; **GET-back to confirm**. `describe_decision_table.py --connect` and
> the `create`/`update` CLIs follow this.

**PATCH update** takes the same flat body and returns `{"isSuccess": true,
"code": "200"}`. A benign `@`-suffixed advisory can ride along on success (e.g.
`"After removing the row level override … will become redundant.@DecisionTable"`)
— treat any `@`-suffixed message as **non-fatal** when `isSuccess` is true.
Unlike the atomic Tooling PATCH, a **failed** full-body Connect PATCH can leave a
**half-applied** definition (why the guarded update leaves a Connect-path table
DEACTIVATED on failure rather than reactivating it).

### Other Connect resources — 📄 doc-grounded (capture from `lookup_table_resources.htm`)

- Decision Table **Lookup** / **Invocation** / **Execution** — runtime evaluation
  (secondary; not exercised by the setup/admin toolkit).
- **Lookup Tables** GET; **Decision Matrix Lookup** POST; **DMN Export** POST.

---

## CSV Based tables — data upload + read — ✅ live-verified

A `CsvUpload` (CSV Based) table's rows are not on a queryable SObject — they are
loaded from an uploaded CSV and read back through Connect sub-resources.
`sourceObject` is the literal string `"CSV"` (no backing object) but is still
required on create.

### Write — the two-phase upload

`upload_decision_table_data.py` performs both phases (preview by default,
`--confirm` to write):

1. **Insert a `ContentVersion`** holding the CSV as base64. The CSV's first row
   must be the column headers, matching the table's INPUT/OUTPUT `fieldName`s.
   Body `{"Title", "PathOnClient", "VersionData"}` → returns a `068…` id.
2. **POST the file id** to the table's Connect `/file` sub-resource:

   | Verb | Path | Body |
   |---|---|---|
   | **POST** | `connect/business-rules/decision-table/{0lD…}/file[?versionNumber=N]` | `{"fileId":"068…","deleteAllRows":false}` |

   Response: `{"message":"We are uploading and processing the CSV file."}`.

- `deleteAllRows:false` **appends** to existing rows — the **only reliable write**.
- The import is **asynchronous**. The POST returns immediately; rows become
  queryable via the data GET within ~5s. `uploadStatus`
  (`UploadInProgress` → `Completed` / `CompletedWithErrors` / `Failed`) **lags**
  the data landing (~1 min to go terminal). `upload_decision_table_data.py
  --wait-for-status` (`--max-wait N`, default 120s) opts into polling
  `Metadata.uploadStatus` to a terminal state and exits non-zero on
  `CompletedWithErrors`/`Failed` — the only signal the fire-and-forget POST hides.

> ⚠ **`deleteAllRows:true` (overwrite) is BROKEN on 262 / v67.0 (✅ live-verified).**
> Every overwrite variant — Active table, Draft table, empty table, with or without
> `?versionNumber` — returns `uploadStatus = Failed` and loads **0 rows**; the
> intended delete does not happen and pre-existing rows are **left intact**
> (safe-fail). The **same CSV appended succeeds**, so `deleteAllRows:true` itself is
> the culprit (pilot-gated or bugged). **The reliable "replace all rows" path is to
> create a fresh version/table and append.** `--overwrite` carries this warning.

**Per-column CSV encoding (✅ live-verified — all 7 `dataType`s round-tripped).**
Each cell is coerced to the column's `dataType`; a cell that fails coercion drops
that **row silently** (below). Confirmed encodings:

| `dataType` | CSV cell that lands | Returned `rowData` | Notes |
|---|---|---|---|
| **String** | any text; `"quoted, comma"`; UTF-8 (`café ☕`) | JSON string | UTF-8 preserved |
| **Number** | `42`, `-3.5`, `0` | JSON number | decimals + negatives OK |
| **Currency** | `1234.56`, `0.99` | JSON number | verbatim, no rounding |
| **Percent** | `0.15`, `50`, `0.5` | JSON number | **stored VERBATIM — no ×100 / ÷100** |
| **Boolean** | `true`, `false`, `TRUE` | JSON bool | **case-insensitive `true`/`false` ONLY — `1`/`0` REJECTED** (row drops) |
| **Date** | `2026-07-10` (`YYYY-MM-DD`) | JSON string `YYYY-MM-DD` | date-only ISO |
| **DateTime** | `2026-07-10T14:30:00.000Z` | JSON string, same form | **milliseconds + `Z` MANDATORY** — no-ms / space-for-`T` / date-only all drop the row |

**Per-row validation — bad rows drop silently → `CompletedWithErrors` (✅ live).**
A mixed valid/invalid upload loads **only the valid rows** and finishes
`uploadStatus = CompletedWithErrors`; the dropped rows surface **no per-row error**
(neither the `/data` GET nor the `Metadata` reports which failed, only the aggregate
status). This is why `--wait-for-status` is worth the wait.

> ⚠ **The `/data` POST (row-by-row edit) is non-functional** on the probed
> release — load and replace rows through the `/file` upload, not a data POST.

### Version lifecycle

A create auto-mints a **Draft version 1**. Activate the version before activating
the table:

| Verb | Path | Body |
|---|---|---|
| **PATCH** | `connect/business-rules/decision-table/definitions/{id}/versions/{N}` | `{"versionStatus":"Active"}` |

`upload_decision_table_data.py --activate-version N` does this in the same run.

> **No v2 on re-upload (✅ live-verified).** Create auto-mints Draft version 1;
> re-uploading (append or overwrite, with or without `--version-number`) does **not**
> mint a v2 — the version list stays `[{versionNumber:1}]` and every upload targets
> v1. Uploading to a **non-existent** version (`?versionNumber=2` when only v1 exists)
> → `INVALID_API_INPUT`.

`refreshDecisionTable` requires an **Active** table, so the order is:
upload → activate version → activate table → refresh. For a **versioned** CSV
table the refresh's `VersionNumber` input is **required** (not optional as the
action-describe implies), and the two version failures differ (live-verified):

| Refresh `VersionNumber` | Error |
|---|---|
| **absent** | `INVALID_API_INPUT: Enter a valid versionNumber for versioned CSV-based decision tables.` |
| **non-existent** (e.g. `99`) | `INVALID_ID_FIELD: The decision table version number is invalid. Specify a valid version number of an active decision table…` |

Pass a real `refresh_decision_table.py --version-number N`.

### Read — the data GET

| Verb | Path | Returns |
|---|---|---|
| **GET** | `connect/business-rules/decision-table/{id}/data[?versionNumber=N][&filter=Field:Value][&limit=N]` | `{"rows":[{"id":"1FI…","rowData":{…}}], "totalRows":N}` |

Row ids are `1FI`-prefixed; `rowData` values are typed. `dump_decision_table_data.py`
reads this branch for a `CsvUpload` table, exposing `--filter FIELD:VALUE` and
`--version-number N` (both **CsvUpload-only**; against a non-CsvUpload table they
degrade to a note).

- **`filter=Field:Value`** is an **exact, case-sensitive equality** on the stored
  value (✅ live): `Region:North` ≠ `Region:north`, and there is **no substring /
  prefix** match. A **field name that doesn't exist returns 0 rows with no error**
  (silently empty — the caller must know the column is real).
- **`versionNumber`** defaults to the current/active version; a **non-existent
  version** on the read → `INVALID_API_INPUT`.

> ⚠ **`filter` + `limit` throw `UNKNOWN_EXCEPTION` (✅ live).** Combining them errors
> whenever `limit` is **not strictly greater** than the matched-row count (i.e.
> whenever `limit` would truncate the filtered set). `dump_decision_table_data.py`
> therefore **drops `--limit` (with a note) when `--filter` is given** and returns
> the full matched set.

> ⚠ **Pagination gotcha.** `totalRows` is the count **in the response**, not a
> grand total, and `offset` is unreliable — do **not** build an offset pager. Use
> `filter` to narrow and `limit` to cap; read once. A disabled endpoint or a table
> with no uploaded version degrades to a note (mirroring the SObject-branch
> fallbacks).

---

## Lifecycle — ✅ live-verified

- **Create** — three paths, all live-verified:
  - **Tooling POST** `…/tooling/sobjects/DecisionTable` with
    `{"FullName": …, "Metadata": {…}}` → `{"id":"0lD…","success":true}`. Required
    inside `Metadata`: `dataSourceType`, `sourceObject`, `usageType`,
    `filterResultBy`, `conditionType`, `conditionCriteria`, `status`, `type`,
    `decisionTableParameters[]` (`executionType` accepted as API-casing `HBASE`).
  - **Connect POST** — the flat-body path above.
  - **Metadata deploy** `.decisionTable-meta.xml`. The toolkit generates the XML
    into an **OS temp SFDX project outside the repo**, runs `sf project deploy
    start` **with cwd = the temp project root** (`--source-dir force-app`;
    deploying an absolute/`..`-laden path from the repo cwd trips
    `UnsafeFilepathError`), passes **`--ignore-conflicts`** (a brand-new component
    can report a source-tracking `Conflict` on a scratch org), and `rm -rf`s the
    temp project after — **no generated churn in `git status`**.
- **Update (Tooling PATCH)** `…/DecisionTable/{id}` with `{"Metadata": {…}}` →
  **204 No Content**. The `decisionTableParameters[]` array is a **full replace**
  (send the complete column set, not a delta). A PATCH is **atomic** — a rejected
  PATCH leaves the record byte-identical (why the guarded update reactivates a
  Tooling-path table on failure). ⚠ The Tooling `Metadata` complexvalue is
  **replaced wholesale** — a sparse body drops the omitted fields — so the toolkit
  always sends the full definition body. ⚠ **`status` is a required field on a
  Tooling `Metadata` PATCH** — a status-free body is rejected with
  `FIELD_INTEGRITY_EXCEPTION: Required field is missing: status` (live-verified on
  a Draft scratch table). To keep the spec from driving the lifecycle on an
  *update*, the `update` CLI drops the spec's `status` and stamps the table's
  **current live** `status` instead (read at PATCH time via
  `LifecycleEngine.get_status`; during a deactivate-first sequence that is the
  already-deactivated `Inactive`). The Connect PATCH, whose `status` is optional,
  simply drops it. Either way the lifecycle engine solely owns activate/deactivate.
- **Activate / deactivate** by setting `Metadata.status` (Active ↔
  Inactive/Draft). The repo build does this via Apex + the
  `exclude_active_decision_tables` (`.skip/`) pattern and
  `manage_decision_tables --operation activate|deactivate`. **Asymmetry
  (live-verified):** **activate is ASYNC** — the 204 is followed by
  `Status = "ActivationInProgress"` for ~10–15s before settling to `"Active"`, so
  a caller must **poll past `ActivationInProgress`** (the toolkit's `activate`
  does); **deactivate is SYNCHRONOUS** — `Status` flips to `"Inactive"`
  immediately, no `InactivationInProgress`.
- **Active-edit restriction** — ✅ an Active table's definition cannot be modified
  in place. A PATCH of an Active table's `Metadata` returns:
  ```json
  [{"message": "Can't edit an active Decision Table",
    "errorCode": "FIELD_NOT_UPDATABLE", "fields": []}]
  ```
  Deactivate first (analogous to Context Service's `RECORD_UPDATE_FAILED`
  deactivate-first rule, but DT uses `FIELD_NOT_UPDATABLE`). The `update` /
  `delete` mutators refuse an Active table up front unless `--deactivate-first`
  runs the guarded deactivate → mutate → reactivate sequence.
- **Delete** — Tooling (`…/tooling/sobjects/DecisionTable/{id}`) or Connect
  (`…/definitions/{id}`) DELETE with an **empty body piped on stdin** (`-b -`);
  `-b ""` / `-b "@file"` / an `-f` request-spec all fail with "No 'mode' found in
  'body' entry". GET-back → `NOT_FOUND`.

## Refresh (data sync) — ✅ live-verified

The `refreshDecisionTable` **standard invocable action** syncs source rows into
the engine cache. Action describe
(`GET /services/data/v67.0/actions/standard/refreshDecisionTable`) — inputs:

| Input | Type | Required |
|---|---|---|
| `DecisionTableApiName` | STRING | **true** |
| **`isDecisionTableIncremental`** | BOOLEAN | false |
| `VersionNumber` | INTEGER | false * |

> \* `VersionNumber` is action-describe-optional but **required for versioned
> CSV-based tables** — omitting it there fails `INVALID_API_INPUT: Enter a valid
> versionNumber for versioned CSV-based decision tables.` (live-verified). See
> *CSV Based tables → Version lifecycle* above.

> ⚠ **Use `isDecisionTableIncremental`.** ✅ Live-confirmed: both `false` (full)
> and `true` (incremental) return `isSuccess: true`, `outputValues.Status:
> "Queued"`. The action's accepted incremental flag is
> `isDecisionTableIncremental` — **not** `isIncremental`, which the existing CCI
> tasks (`rlm_refresh_decision_table.py`, `rlm_manage_decision_tables.py`)
> currently send; that name is silently ignored, so those tasks always do a full
> refresh. The toolkit's `refresh_decision_table.py` uses the correct flag; the
> CCI tasks are a candidate follow-up fix (behavioral — verify live before merge).

- Refresh is **async** and **rate-limited to ~100 refreshes/hour**.
- **Response is fire-and-queue:** `outputValues.Status: "Queued"`, no synchronous
  result and **no `AsyncOperationTracker` row** (that table holds
  ContextPersistence / AssetizationAsyncJob only). The DT's own
  `Metadata.refreshStatus` / `Metadata.lastSyncDate` / `Metadata.downloadStatus`
  are the completion signal — they advance when a real sync lands. (On a throwaway
  table with no matching source rows they stayed `null` — nothing to sync;
  expected.)
- 📄 The ~100/hr cap is doc-grounded; its exact rejection text was not exercised
  (probing stayed under the cap). `refresh_decision_table.py` surfaces the cap in
  help text.

## Recipe table mappings (trace) — ✅ live-verified

`PricingRecipeTableMapping` (normal REST) links a pricing recipe to a decision
table. Fields: `PricingRecipeId`, `PricingComponentType` (ListPrice,
VolumeDiscount, VolumeTierDiscount, AttributeDiscount, BundleDiscount, …),
`LookupTableId`, `IsInternal`, `FileBasedDecisionTableName`.

> ⚠ **There is no `DecisionTableId` field.** For SObject-backed tables,
> **`LookupTableId` == `DecisionTable.Id`** (confirmed live). For file/CSV-backed
> tables, correlate via **`FileBasedDecisionTableName`**.

`trace_decision_table.py` therefore resolves the DT via **Tooling**, queries
`PricingRecipeTableMapping` via **normal REST** filtering on `LookupTableId` /
`FileBasedDecisionTableName`, and correlates in Python — no single cross-surface
SOQL join. See also `pricing-wiring` and the `validate_lists` operation.

---

## Error → resolution — ✅ live-verified

Errors observed during scratch-org CRUD probing, with the fix each toolkit path
encodes.

| Error (code / message) | Path & trigger | Resolution |
|---|---|---|
| `FIELD_NOT_UPDATABLE` — "Can't edit an active Decision Table" | Tooling/Connect PATCH of an **Active** table | Deactivate first. `update`/`delete` refuse an Active table unless `--deactivate-first` runs the guarded deactivate → mutate → reactivate. |
| `MISSING_ARGUMENT` — "Specify a valid value for status parameter" | Connect POST create without `status` | `status` is **required** on a Connect create; the toolkit defaults it to `Draft`. |
| `FIELD_INTEGRITY_EXCEPTION` — "Required field is missing: status" | Tooling `Metadata` PATCH with a status-free body | `status` is **required** on a Tooling PATCH too. `update` drops the spec's `status` and stamps the table's **current live** status (via `LifecycleEngine.get_status`) so the edit never re-activates the table — in a deactivate-first sequence that live status is the already-deactivated `Inactive`. |
| `JSON_PARSER_ERROR` — `Unrecognized field "label"` / `"masterLabel"` | Connect POST/PATCH using the wrong label key | The Connect label field is **`setupName`** (not `label`/`masterLabel`). |
| `JSON_PARSER_ERROR: Unexpected character ('/' …)` | Any POST/PATCH passing a file path without the `@` prefix | Use `--body "@/abs/file.json"` (or `-` for stdin); a bare path is read as literal JSON. |
| "No 'mode' found in 'body' entry" | DELETE with `-b ""` / `-b "@file"` / an `-f` request-spec | Pipe an **empty body on stdin** via `-b -` (`printf '' \| sf api request rest … -X DELETE -b -`). The client already does this. |
| `UnsafeFilepathError` — "contains unsafe character sequences" | Metadata deploy with an absolute/`..`-laden `--source-dir` from the repo cwd | Run the deploy **with cwd = the temp SFDX project root**, then `--source-dir force-app`. |
| `Conflict` — "changes in the org that conflict" | Metadata deploy of a brand-new component to a scratch org (source tracking) | Pass **`--ignore-conflicts`** (the temp project has no local tracking history). |
| Stale `Status = "ActivationInProgress"` after a 204 | Reading status immediately after an activate PATCH | Activate is **async** — poll past `ActivationInProgress` (raise `--max-wait` for slow orgs). |
| Empty `"parameters": []` in a Connect POST/PATCH response | Trusting the Connect echo for the column set | **GET-back** to confirm; the columns persist despite the empty echo. |
| Benign `…@DecisionTable` advisory alongside `isSuccess: true` | Connect PATCH that removes a row-level override | Non-fatal — treat any `@`-suffixed message as advisory when `isSuccess` is true. |
| `uploadStatus = Failed`, 0 rows loaded | CsvUpload `/file` POST with `deleteAllRows:true` (`--overwrite`) | **Broken on 262/v67.0** — overwrite always fails safe (existing rows kept). Replace rows by creating a fresh version/table and appending. |
| `uploadStatus = CompletedWithErrors` | CsvUpload `/file` POST where some rows fail their column's `dataType` coercion | Only the valid rows land; bad rows drop **silently** (no per-row error). Fix the CSV encoding (DateTime needs `.sssZ`, Boolean only `true`/`false`) and re-append; use `--wait-for-status` to catch it. |
| `INVALID_API_INPUT` — "Enter a valid versionNumber for versioned CSV-based decision tables." | `refreshDecisionTable` on a versioned CSV table **without** `VersionNumber` | Pass `refresh_decision_table.py --version-number N`. |
| `INVALID_ID_FIELD` — "The decision table version number is invalid…" | `refreshDecisionTable` with a **non-existent** `VersionNumber` | Pass a real, existing version number (a distinct error from the absent case). |
| `INVALID_API_INPUT` | CsvUpload `/data` GET or `/file` POST targeting a `versionNumber` that doesn't exist (only v1 is minted) | Re-upload does not mint a v2 — target v1 (or omit `versionNumber` for the current version). |
| `UNKNOWN_EXCEPTION` | CsvUpload `/data` GET combining `filter` + a `limit` not strictly greater than the match count | The dump CLI drops `--limit` when `--filter` is given; don't combine them by hand. |

---

## Related references

- `.cursor/skills/decision-tables/SKILL.md` — task-level entry point.
- `.cursor/skills/decision-tables/authoring-and-data-model.md` — setup objects,
  metadata shape, enum tables, the two-layer model in depth.
- `.cursor/skills/decision-tables/lifecycle-and-refresh.md` — deploy, activate/
  deactivate, refresh, recipe mappings.
- `docs/references/decision-table-examples.md` — CCI `manage_decision_tables`
  ops examples.
- `scripts/decision_tables/README.md` — the standalone toolkit.
- `.cursor/skills/pricing-wiring/SKILL.md` — recipes → table mappings layering.
