# Decision Tables — Authoring & Data Model

> Sub-file of `.cursor/skills/decision-tables/SKILL.md`. **Pinned to Release 264 /
> API v68.0.** Read this when you need the setup-object model, the metadata XML
> shape, the enum catalog, the supported authoring paths, or the
> definition-vs-data model in depth. The exhaustive
> object/ID/enum/error reference is
> `docs/references/decision-table-api-reference.md`.

## The two-layer model in depth

A Decision Table is **definition** + **data** — two independently-managed layers.

### Layer 1 — Definition

The structure the engine evaluates: **columns** (a.k.a. parameters), the **source
binding**, the **hit policy**, and optional **row-filter criteria**. It is
authored/deployed and lives in metadata and the Tooling setup objects. Nothing in
this layer holds row values.

- **Columns** (`decisionTableParameters` · Connect `parameters`) each have a
  `usage`:
  - **INPUT** — a match condition. Carries an `operator` (Equals, GreaterThan, …)
    and a `sequence` number that `conditionCriteria` boolean logic references.
  - **OUTPUT** — a returned value. No operator/sequence.
  - **ROWCRITERIA** — a per-row filter column (less common than the standalone
    `DecisionTableSourceCriteria` objects).
- **Condition** — `conditionType` (**All** / Any / Custom) + `conditionCriteria`
  (e.g. `1 AND 2 AND 3`, referencing INPUT `sequence` numbers) decides how INPUT
  columns combine.
- **Hit policy** — `filterResultBy` · Connect `decisionResultPolicy` decides which
  matching row(s) win (OutputOrder, FirstMatch, Priority, …).
- **Source binding** — `dataSourceType` + `sourceObject` (and, for
  `MultipleSobjects`, the dataset links) name where the rows come from.

### Layer 2 — Data

The rows the engine actually evaluates. **Where** they live is decided by
`dataSourceType`:

| `dataSourceType` | Where the rows are | How to sample (`dump`) |
|---|---|---|
| **SingleSobject** | Records in the one `sourceObject` | SOQL the `sourceObject` (normal REST) |
| **MultipleSobjects** | Records across the dataset-link `SourceObject`s, joined | One SOQL sample per dataset link |
| **CsvUpload** | An uploaded CSV, held by the platform | Connect `.../{id}/data` (v62+; see **CSV Based tables** below) |
| **ContextDefinition** | Hydrated at runtime by a Context Definition | No static table — nothing to sample |

**Editing the definition ≠ refreshing the data.** A definition change is
deployed; row changes are picked up by the **async `refreshDecisionTable`
action**. Full-refresh pools are separate: **40 Standard + 60 Advanced per
org/hour**; CSV-based tables inherit Advanced limits. See
`lifecycle-and-refresh.md`. A definition
change is not live to the engine until a refresh completes. This is why the
toolkit separates `describe`/`diff` (definition) from `dump` (data).

### CSV Based tables — the data layer

A `CsvUpload` (a.k.a. **CSV Based**) table's rows do **not** live on a queryable
SObject — they are loaded from an uploaded CSV and read back through Connect
sub-resources. `sourceObject` is the literal string `"CSV"` (there is no backing
object), but it is still **required** on create like every other source type.

**Write — the two-phase upload** (`upload_decision_table_data.py`):

1. Insert a `ContentVersion` holding the CSV as base64 — its first row must be
   the column headers, matching the table's INPUT/OUTPUT `fieldName`s. Body
   `{"Title", "PathOnClient", "VersionData"}` → returns a `068…` id.
2. POST that id to the table's Connect `/file` sub-resource:
   `POST connect/business-rules/decision-table/{0lD…}/file`
   with a bare `{"fileId":"068…"}`. Response:
   *"We are uploading and processing the CSV file."*

The upload **appends** to the current version and completes asynchronously. The
loader waits for `uploadStatus` (`UploadInProgress` → `Completed` /
`CompletedWithErrors` / `Failed`) and succeeds only on `Completed`. Use
`dump_decision_table_data.py` when row-level inspection is needed.

> ⚠ **Do not use `deleteAllRows:true`.** It can finish with `uploadStatus=Failed`
> while leaving existing rows intact. Observed on Release 262 / API v67.0 and
> **not re-tested on 264** — assume it still holds until proven otherwise. The
> toolkit is append-only; replace CSV data with a fresh table and a new upload.

**Per-column CSV encoding.** Generic BRE CSV tables accept all seven Metadata
`dataType` values. That does **not** widen Salesforce Pricing's supported
contract: Pricing Help limits
CSV tables to DateTime/Text, Boolean, and Number, and doesn't support Currency
as an input rule variable. Apply the table below to transport/debugging; validate
the consuming product's supported subset separately.
Each row's CSV cell is coerced to the column's `dataType`; a cell that fails
coercion drops that **row** silently (see below). Confirmed encodings:

| `dataType` | CSV cell that lands | Returned `rowData` | Notes |
|---|---|---|---|
| **String** | any text; `"quoted, comma"`; UTF-8 (`café ☕`) | JSON string | UTF-8 preserved end-to-end |
| **Number** | `42`, `-3.5`, `0` | JSON number | decimals + negatives OK |
| **Currency** | `1234.56`, `0.99`, `1000000` | JSON number | stored verbatim, no rounding |
| **Percent** | `0.15`, `50`, `0.5` | JSON number | **stored VERBATIM — no ×100 / ÷100 normalization** |
| **Boolean** | `true`, `false`, `TRUE` | JSON bool | **case-insensitive `true`/`false` ONLY — `1`/`0` are REJECTED** (row drops) |
| **Date** | `2020-01-02` (`YYYY-MM-DD`) | JSON string `YYYY-MM-DD` | date-only ISO |
| **DateTime** | `2020-01-02T03:04:05.000Z` | JSON string, same form | **milliseconds + `Z` required** |

**Per-row validation — bad rows produce `CompletedWithErrors`.**
An upload with a mix of valid + invalid rows loads **only the valid rows** and
finishes `uploadStatus = CompletedWithErrors`. The dropped rows surface **no
per-row error** — neither the `/data` GET nor the `Metadata` reports which rows
failed, only the aggregate status. Dump the rows back after the load and compare
the count against the CSV to detect silent drops.

**Read — the data GET** (`dump_decision_table_data.py`):
`GET connect/business-rules/decision-table/{id}/data[?filter=Field:Value][&limit=N]`
→ `{"rows":[{"id":"1FI…","rowData":{…}}], "totalRows":N}`. Row ids are
`1FI`-prefixed; `rowData` values are typed. The dump CLI exposes `--filter` for
CSV-backed tables.

- **`filter=Field:Value`** is an **exact, case-sensitive equality** on the stored
  value: `Region:North` ≠ `Region:north`, and there is **no substring /
  prefix** match. A **field name that doesn't exist returns 0 rows with no error**
  (silently empty — the caller must know the column is real).

> ⚠ **`filter` + `limit` can throw `UNKNOWN_EXCEPTION`.** Combining them errors
> whenever `limit` is **not strictly greater** than the matched-row count (i.e.
> whenever `limit` would truncate the filtered set). The dump CLI therefore
> **drops `--limit` (with a note) when `--filter` is given** and returns the full
> matched set. Use `--limit` for an unfiltered peek; use `--filter` alone to narrow.

> ⚠ **Pagination gotcha.** `totalRows` is the count **in the response**, not a
> grand total, and `offset` is unreliable — do **not** build an offset pager.
> Use `filter` to narrow and `limit` to cap; read once.

**Versions.** Creating a CSV table creates its initial file-import version;
re-uploading appends to that version rather than creating another one. The
toolkit therefore does not expose an upload-version selector.

**Row-level edit is not supported.** Load rows through `/file`; the toolkit does
not use `/data` POST.

---

## The 5 Tooling setup objects

The definition is assembled across **five Tooling API objects**. `DecisionTable`,
`DecisionTableParameter`, `DecisionTableDatasetLink`, and
`DecisionTblDatasetParameter` are available in **v51.0+**;
`DecisionTableSourceCriteria` is **v59.0+**. They
are **Tooling only** — not on the normal REST `/sobjects` surface — read via
`/tooling/query` and `/tooling/sobjects/<Object>`.

| Object | Key prefix | Role & key fields |
|---|---|---|
| `DecisionTable` | **`0lD`** | The definition head. `DeveloperName` (api name), `Status`, `UsageType`, `SourceObject`, `LastSyncDate`, and the **`Metadata`** complexvalue (inlines the children). |
| `DecisionTableParameter` | **`0lP`** | A column. `DecisionTableId`, `FieldName`, `Usage` (INPUT/OUTPUT/ROWCRITERIA), `Operator`, `Sequence`, `DataType`, `FieldPath`, `IsRequired`, `IsGroupByField`, `SortType`, `DomainObject`. |
| `DecisionTableDatasetLink` | **`0lX`** | Binds a source SObject for `MultipleSobjects`; supported only for **Standard** decision tables. `DecisionTableId`, `SourceObject`, `SetupName`, `IsDefault`, `Metadata`. |
| `DecisionTblDatasetParameter` | **`0lZ`** | Join layer: maps a dataset link's field to a parameter. `DecisionTableDatasetLinkId`, `DecisionTableParameterId`, `DatasetFieldName`, `DatasetSourceObject`. |
| `DecisionTableSourceCriteria` | **`0VT`** | Row-filter on the source. `DecisionTableId`, `SourceFieldName`, `Operator`, `Value`, `ValueType`, `SequenceNumber`. |

`describe_decision_table.py` resolves the head via Tooling, then loads the
children on `DecisionTableId` / `DecisionTableDatasetLinkId` and groups the
columns by `Usage`.

### The `DecisionTable.Metadata` complexvalue

A Tooling GET of `DecisionTable/{id}` returns a **`Metadata`** complexvalue that
inlines the parameters/criteria/import-versions with the **Metadata-API field
names** (not the Tooling column names). Keys:

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

Each `decisionTableParameters[]` entry carries: `dataType, decimalScale,
domainObject, fieldName, fieldPath, isGroupByField, isPriorityField, isRequired,
length, operator, sequence, sortType, usage`.

This is the seam a Tooling-path author writes through: PATCH the `Metadata`
complexvalue to inline the whole definition in one call.

---

## Metadata API — `.decisionTable-meta.xml`

Folder `decisionTables/`; MDAPI suffix `.decisionTable`; **source format
`.decisionTable-meta.xml`** — what this repo ships, under
`unpackaged/pre/5_decisiontables/` and
`unpackaged/post_prm_pricing/decisionTables/`. This is the **primary,
source-controlled** authoring path (deploy via `sf project deploy start` or CCI
`Deploy`).

Annotated real file (`RLM_CostBookEntries` — a `SingleSobject` with two INPUT
columns and one OUTPUT column). This is the file verbatim; comments are added:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DecisionTable xmlns="http://soap.sforce.com/2006/04/metadata">
    <collectOperator>None</collectOperator>            <!-- aggregate over hits; None | Sum | Min | Max | … -->
    <conditionCriteria>1 AND 2</conditionCriteria>     <!-- boolean logic over INPUT sequences -->
    <conditionType>All</conditionType>                <!-- All | Any | Custom -->
    <dataSourceType>SingleSobject</dataSourceType>     <!-- see enums -->
    <decisionTableParameters>                          <!-- one block per column -->
        <dataType>String</dataType>
        <fieldName>ProductId</fieldName>
        <fieldPath>ProductId</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>true</isRequired>
        <operator>Equals</operator>                    <!-- INPUT only -->
        <sequence>1</sequence>                          <!-- INPUT only; referenced by conditionCriteria -->
        <usage>INPUT</usage>                            <!-- INPUT | OUTPUT | ROWCRITERIA -->
    </decisionTableParameters>
    <decisionTableParameters>                          <!-- second INPUT column -->
        <dataType>String</dataType>
        <fieldName>CurrencyIsoCode</fieldName>
        <fieldPath>CurrencyIsoCode</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>true</isRequired>
        <operator>Equals</operator>
        <sequence>2</sequence>                          <!-- paired with sequence 1 by conditionCriteria "1 AND 2" -->
        <usage>INPUT</usage>
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
    <dtRowLevelOverrideType>None</dtRowLevelOverrideType>
    <executionType>HBASE</executionType>               <!-- storage/eval engine; see enums -->
    <filterResultBy>OutputOrder</filterResultBy>        <!-- hit policy -->
    <hasIncrementalSyncFailed>false</hasIncrementalSyncFailed>
    <isIncrementalSyncEnabled>false</isIncrementalSyncEnabled>
    <isVersioned>false</isVersioned>
    <setupName>Cost Book Entries</setupName>            <!-- human label (spaces OK) -->
    <sourceObject>CostBookEntry</sourceObject>
    <status>Active</status>                             <!-- deploy-time status -->
    <type>MediumVolume</type>
    <usageType>DefaultPricing</usageType>
</DecisionTable>
```

Important XML rules:

- INPUT `sequence` values, not XML element order, drive `conditionCriteria`.
- Use the Metadata/Tooling spelling `HBASE` for `executionType`.
- `setupName` is the human label; the file name is the `DeveloperName`.

---

## Definition authoring paths — decision guide

| You want to… | Use | Toolkit CLI | Vocabulary |
|---|---|---|---|
| **Ship a table in the build**, source-controlled, reviewable | **Metadata API** (`.decisionTable-meta.xml`) — the primary path | Standard `sf`/CCI deploy | `dataSourceType`, `filterResultBy`, `decisionTableParameters`, `usage=INPUT` |
| **Create or one-off edit** the whole definition in one REST call | **Tooling API** — POST/PATCH the `DecisionTable.Metadata` complexvalue | `create`, `update`, `delete` | same as Metadata (Metadata-API field names) |

The toolkit does not expose raw Connect definition operations because Connect
uses a different definition vocabulary. Connect remains necessary for CSV
`/file`, `/data`, and `/versions` resources.

---

## Enum catalog

This catalog was captured on Release 262 and is not yet re-verified on 264.
Unknown descriptive
values warn for forward compatibility; invalid structural values such as column
`usage` fail validation.

| Metadata/Tooling field | Values |
|---|---|
| `dataSourceType` | ContextDefinition, CsvUpload, MultipleSobjects, SingleSobject |
| `executionType` | DLO (v67.0+, replaces DMO), HBASE, HBPO, SOLR, SOQL (the toolkit also tolerates the mixed-case `Hbase` for forward-compat; `HBASE` is the canonical shipped/Tooling spelling) |
| `conditionType` | All, Any, Custom |
| `filterResultBy` | AnyValue, CollectOperator, FirstMatch, OutputOrder, Priority, RuleOrder, UniqueValues |
| `type` | Advanced, HighScaleExecution, HighVolume, LowVolume, MediumVolume, RealTime |
| `status` | ActivationInProgress, Active, Draft, Inactive |
| `usageType` (ExpsSetProcessType) | Bre, DefaultPricing, DefaultRating, PricingDiscovery, RatingDiscovery, RevenueStandardTax, ProductCategoryQualification, ProductQualification, RecordAlert, … |
| `DecisionTableParameter.usage` | INPUT, OUTPUT, ROWCRITERIA |
| `DecisionTableParameter.dataType` | Boolean, Currency, Date, DateTime, Number, Percent, String; Salesforce Pricing supports a narrower CSV subset |
| `DecisionTableParameter.operator` | Contains, DoesNotExistIn, DoesNotMatch, Equals, ExistsIn, GreaterOrEqual, GreaterThan, IsNotNull, IsNull, LessOrEqual, LessThan, Matches, NotEquals (full set of 13) |
| `DecisionTableParameter.sortType` | AscNullFirst, AscNullLast, DescNullFirst, DescNullLast, None |
| `DecisionTableSourceCriteria.valueType` | Formula, Literal, Lookup, Parameter, Picklist |
| `collectOperator` | Count, Maximum, Minimum, None, Sum |
| `dtRowLevelOverrideType` | None, Both, Condition, Operator |

API v67 adds `decisionTableFileImportVersions[]` and `isVersioned`. When a spec
omits `isVersioned`, the toolkit defaults it to `False` — except for `CsvUpload`
tables, which are versioned by nature and default to `True` unless the spec
explicitly sets `isVersioned: false`.

These Metadata/Tooling enum sets are the source of truth for canonical specs and
`validate_spec()`, which the offline tests exercise with no org.

---

## Related

- Parent skill: `.cursor/skills/decision-tables/SKILL.md`.
- Companion sub-file: `lifecycle-and-refresh.md` (deploy, activate/deactivate,
  refresh, recipe mappings).
- Exhaustive reference: `docs/references/decision-table-api-reference.md`.
- Toolkit: `scripts/decision_tables/README.md` (`_schema.py` encodes these enums).
