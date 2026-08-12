# Decision Table Programmatic Management

> Release 262 / API v67.0 reference for managing Business Rules Engine (BRE)
> Decision Table definitions and data. Runtime lookup and execution APIs are
> outside this toolkit's scope.

Use the [Decision Tables skill](../../.cursor/skills/decision-tables/SKILL.md)
for task routing and [the toolkit README](../../scripts/decision_tables/README.md)
for commands.

## Model

A Decision Table has two independently managed layers:

1. **Definition** — columns, source binding, criteria, and hit policy. Author
   through Metadata API or the Tooling `DecisionTable.Metadata` complex value.
2. **Data** — source-object rows, uploaded CSV rows, or runtime context data.
   Synchronize data into the BRE cache with `refreshDecisionTable`.

Changing a definition does not refresh its data. Active definitions must be
deactivated before update or deletion.

## API boundaries

| Surface | Toolkit use |
|---|---|
| Metadata API | Source-controlled definition create/update |
| Tooling API | Definition inspect/create/update/delete |
| Connect API | CSV file upload, version activation, and row read |
| REST API | Source-row reads and recipe-mapping trace |
| Standard Actions API | Data refresh |

The toolkit intentionally does not expose raw Connect definition CRUD. It adds
a second definition vocabulary without adding a required capability.

## Tooling object model

| Object | Prefix | Purpose |
|---|---|---|
| `DecisionTable` | `0lD` | Definition and `Metadata` complex value |
| `DecisionTableParameter` | `0lP` | Input, output, or row-criteria column |
| `DecisionTableDatasetLink` | `0lX` | Source-object binding for `MultipleSobjects` |
| `DecisionTblDatasetParameter` | `0lZ` | Dataset-field to parameter mapping |
| `DecisionTableSourceCriteria` | `0VT` | Source-row filter |

These records are available through Tooling API, not normal REST `/sobjects`.
`DecisionTableSourceCriteria` requires API v59.0 or later; the other four
objects require v51.0 or later.

The `DecisionTable.Metadata` complex value uses Metadata API field names and
inlines parameters, source criteria, and file-import versions. Important keys
include:

```text
conditionCriteria, conditionType, dataSourceType,
decisionTableFileImportVersions[], decisionTableParameters[],
decisionTableSourceCriterias[], executionType, filterResultBy,
isIncrementalSyncEnabled, isVersioned, refreshStatus, setupName,
sourceObject, status, type, usageType
```

## Metadata source format

Decision Table components live in `decisionTables/` with the
`.decisionTable-meta.xml` suffix.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DecisionTable xmlns="http://soap.sforce.com/2006/04/metadata">
    <conditionCriteria>1</conditionCriteria>
    <conditionType>All</conditionType>
    <dataSourceType>SingleSobject</dataSourceType>
    <decisionTableParameters>
        <dataType>String</dataType>
        <fieldName>ProductId</fieldName>
        <fieldPath>ProductId</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>true</isRequired>
        <operator>Equals</operator>
        <sequence>1</sequence>
        <usage>INPUT</usage>
    </decisionTableParameters>
    <decisionTableParameters>
        <dataType>Currency</dataType>
        <fieldName>Cost</fieldName>
        <fieldPath>Cost</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>false</isRequired>
        <usage>OUTPUT</usage>
    </decisionTableParameters>
    <doesConsiderNullValue>false</doesConsiderNullValue>
    <executionType>HBASE</executionType>
    <filterResultBy>OutputOrder</filterResultBy>
    <isIncrementalSyncEnabled>false</isIncrementalSyncEnabled>
    <setupName>Cost Book Entries</setupName>
    <sourceObject>CostBookEntry</sourceObject>
    <status>Active</status>
    <type>MediumVolume</type>
    <usageType>DefaultPricing</usageType>
</DecisionTable>
```

Use `HBASE`, matching the Metadata API spelling. The toolkit accepts `Hbase`
when reading specifications for compatibility.

## Common enums

| Field | Values |
|---|---|
| `dataSourceType` | `ContextDefinition`, `CsvUpload`, `MultipleSobjects`, `SingleSobject` |
| `executionType` | `DLO`, `HBASE`, `Hbase`, `HBPO`, `SOLR`, `SOQL` |
| `conditionType` | `All`, `Any`, `Custom` |
| `filterResultBy` | `AnyValue`, `CollectOperator`, `FirstMatch`, `OutputOrder`, `Priority`, `RuleOrder`, `UniqueValues` |
| `type` | `Advanced`, `HighScaleExecution`, `HighVolume`, `LowVolume`, `MediumVolume`, `RealTime` |
| `status` | `ActivationInProgress`, `Active`, `Draft`, `Inactive` |
| parameter `usage` | `INPUT`, `OUTPUT`, `ROWCRITERIA` |
| parameter `dataType` | `Boolean`, `Currency`, `Date`, `DateTime`, `Number`, `Percent`, `String` |
| parameter `operator` | `Contains`, `DoesNotExistIn`, `DoesNotMatch`, `Equals`, `ExistsIn`, `GreaterOrEqual`, `GreaterThan`, `IsNotNull`, `IsNull`, `LessOrEqual`, `LessThan`, `Matches`, `NotEquals` |

`DLO` replaces `DMO` as an execution type in API v67.0. Availability of table
types and usage types depends on installed products and entitlements; return
platform validation errors to the caller instead of maintaining a local
entitlement matrix.

## Definition lifecycle

### Create

Tooling create uses:

```text
POST /services/data/v67.0/tooling/sobjects/DecisionTable
{"FullName":"...","Metadata":{...}}
```

Required metadata includes source type/object, usage type, hit policy,
condition type/criteria, status, table type, and the full parameter list.

For source-controlled create/update, the same definition can also be deployed
through the Metadata API `.decisionTable-meta.xml` source (see *Metadata source
format* above). The toolkit itself creates through the single Tooling POST shown
here.

### Update

Tooling update sends the complete `Metadata` body:

```text
PATCH /services/data/v67.0/tooling/sobjects/DecisionTable/{id}
```

The complex value and its parameter array use replacement semantics. Sparse
payloads can remove omitted values. `status` is required, so the toolkit copies
the current platform status into the full update payload rather than allowing a
specification to drive lifecycle state.

The toolkit sends one update request. If the table is active or the payload is
invalid, the platform error is returned to the caller.

### Activate and deactivate

SObject-backed tables change `Metadata.status`. Activation may pass through
`ActivationInProgress`, so the toolkit polls until a terminal state.
Deactivation normally settles immediately.

CSV-backed tables activate their file-import version through Connect:

```text
PATCH connect/business-rules/decision-table/definitions/{id}/versions/{number}
{"versionStatus":"Active"}
```

The version must resolve unambiguously. The table status then follows the
version lifecycle.

### Delete

Tooling delete requires an empty request body on stdin:

```text
DELETE /services/data/v67.0/tooling/sobjects/DecisionTable/{id}
```

Active or referenced tables are rejected by the platform. The toolkit returns
those errors without predicting dependencies locally.

## CSV-backed data

`CsvUpload` tables use `sourceObject: "CSV"`. They do not have source rows that
can be queried through normal REST.

### Upload

1. Insert a `ContentVersion` containing the base64-encoded CSV.
2. Submit its `068...` id:

```text
POST connect/business-rules/decision-table/{id}/file
{"fileId":"068..."}
```

The operation is asynchronous. The toolkit waits for the submitted import's
`uploadStatus` and succeeds only on `Completed`. It returns
`CompletedWithErrors` and `Failed` as errors.

Uploads append rows. The toolkit does not expose `deleteAllRows` because that
overwrite path is not reliable for the pinned release. Replace a CSV table by
creating a fresh table and appending its rows.

CSV headers must match definition field names. Values are coerced by the
platform:

| Type | Accepted form |
|---|---|
| `Boolean` | `true` or `false`, case-insensitive |
| `Date` | `YYYY-MM-DD` |
| `DateTime` | ISO timestamp with milliseconds and `Z` |
| `Number`, `Currency`, `Percent` | JSON-compatible numeric text |
| `String` | UTF-8 text; use CSV quoting where needed |

Rows that fail coercion can be omitted while the import ends as
`CompletedWithErrors`. Salesforce does not return per-row rejection details;
inspect the rows that landed, correct the input, and retry against a fresh table
when replacement semantics are required.

### Read

```text
GET connect/business-rules/decision-table/{id}/data
GET connect/business-rules/decision-table/{id}/data?filter=Field:Value
GET connect/business-rules/decision-table/{id}/data?limit=N
```

`filter` is exact and case-sensitive. An unknown field returns no rows rather
than a validation error. The toolkit omits `limit` when a filter is supplied
because the combined parameters can fail when the limit truncates the matched
set.

Treat the response as a single page. `totalRows` describes returned rows, and
offset pagination is not reliable on this resource.

## Refresh

Call the standard `refreshDecisionTable` action with:

| Input | Required |
|---|---|
| `DecisionTableApiName` | yes |
| `isDecisionTableIncremental` | no |
| `VersionNumber` | for versioned CSV tables |

Use the exact `isDecisionTableIncremental` field name. A successful request
queues asynchronous work; it does not mean the refresh has completed.

**Input-name casing.** The action describe declares `DecisionTableApiName`
(initial capital), while the Salesforce doc sample
(`docs/salesforce/262/dev-guide-industries/articles/dt_actions_refresh_decision_table.htm.md`)
shows `decisionTableApiName`. Both are accepted — the invocable-action REST
layer matches input names **case-insensitively**, verified live on v67.0 by
running each spelling and confirming `LastSyncDate` advanced with
`RefreshStatus=Completed`. This is why the repo carries both: the flows and
`scripts/decision_tables/` use the describe spelling, `tasks/rlm_*.py` use the
doc spelling, and both refresh correctly. Prefer the describe spelling in new
code. Casing tolerance does **not** extend to using a wrong *name* —
`isIncremental` is a different key and is silently ignored.

Full refresh completion is reflected by `Metadata.refreshStatus` and
`Metadata.lastSyncDate`. Incremental refresh completion advances
`Metadata.lastIncrementalSyncDate`. Full-refresh hourly pools are 40 Standard
and 60 Advanced; CSV-backed tables use the Advanced pool.

## Recipe mappings

`PricingRecipeTableMapping` is a normal REST object. For SObject-backed tables,
`LookupTableId` identifies the `DecisionTable`; for CSV-backed tables, use
`FileBasedDecisionTableName`. There is no `DecisionTableId` field.

The trace command therefore resolves the table through Tooling, queries recipe
mappings through REST, and correlates the results locally.

## Common platform errors

| Error | Meaning / response |
|---|---|
| `FIELD_NOT_UPDATABLE: Can't edit an active Decision Table` | Deactivate, perform the update, then activate explicitly. |
| `INVALID_OPERATION` or `DEPENDENCY_EXISTS` on delete | Deactivate and remove references before retrying. |
| `FIELD_INTEGRITY_EXCEPTION: Required field is missing: status` | Send the complete Tooling metadata body with current status. |
| `CompletedWithErrors` after CSV upload | Some rows failed platform coercion; inspect landed rows and correct the CSV. |
| `INVALID_API_INPUT` for CSV refresh without a version | Pass an existing active `--version-number`. |
| `UNKNOWN_EXCEPTION` for filtered CSV reads | Do not combine a truncating `limit` with `filter`. |

## Related references

- [Decision Tables skill](../../.cursor/skills/decision-tables/SKILL.md)
- [Authoring and data model](../../.cursor/skills/decision-tables/authoring-and-data-model.md)
- [Lifecycle and refresh](../../.cursor/skills/decision-tables/lifecycle-and-refresh.md)
- [Toolkit README](../../scripts/decision_tables/README.md)
- [Operational examples](decision-table-examples.md)
