# Decision Tables — Authoring & Data Model

> Sub-file of `.cursor/skills/decision-tables/SKILL.md`. **Pinned to Release 262 /
> API v67.0.** Read this when you need the setup-object model, the metadata XML
> shape, the enum catalog, the field-name divergence across the three authoring
> APIs, or the definition-vs-data two-layer model in depth. The exhaustive
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
| **CsvUpload** | An uploaded CSV, held by the platform | Connect `.../{id}/data` (v62+) — ✅ live-verified (see **CSV Based tables** below) |
| **ContextDefinition** | Hydrated at runtime by a Context Definition | No static table — nothing to sample |

**Editing the definition ≠ refreshing the data.** A definition change is
deployed; row changes are picked up by the **async `refreshDecisionTable`
action**. Full-refresh pools are separate: **40 Standard + 60 Advanced per
org/hour**; CSV-based tables inherit Advanced limits. See
`lifecycle-and-refresh.md`. A definition
change is not live to the engine until a refresh completes. This is why the
toolkit separates `describe`/`diff` (definition) from `dump` (data).

### CSV Based tables — the data layer (✅ live-verified)

A `CsvUpload` (a.k.a. **CSV Based**) table's rows do **not** live on a queryable
SObject — they are loaded from an uploaded CSV and read back through Connect
sub-resources. `sourceObject` is the literal string `"CSV"` (there is no backing
object), but it is still **required** on create like every other source type.

**Write — the two-phase upload** (`upload_decision_table_data.py`):

1. Insert a `ContentVersion` holding the CSV as base64 — its first row must be
   the column headers, matching the table's INPUT/OUTPUT `fieldName`s. Body
   `{"Title", "PathOnClient", "VersionData"}` → returns a `068…` id.
2. POST that id to the table's Connect `/file` sub-resource:
   `POST connect/business-rules/decision-table/{0lD…}/file[?versionNumber=N]`
   with `{"fileId":"068…","deleteAllRows":false}`. Response:
   *"We are uploading and processing the CSV file."*

`deleteAllRows:false` **appends** to any existing rows. The import is
**asynchronous**: the POST returns immediately, the rows become queryable within
~5s, and `uploadStatus` (`UploadInProgress` → `Completed` / `CompletedWithErrors`
/ `Failed`) lags the data landing — it can take ~1 min to go terminal. Opt into
`upload_decision_table_data.py --wait-for-status` to poll `Metadata.uploadStatus`
to a terminal state; its value is surfacing `CompletedWithErrors`/`Failed` (a
terminal error exits non-zero), which the fire-and-forget POST response hides.

> ⚠ **`deleteAllRows:true` (overwrite) is BROKEN on 262 / v67.0 (✅ live-verified).**
> Every overwrite variant — Active table, Draft table, empty table, with or
> without `?versionNumber` — returns `uploadStatus = Failed` and loads **0 rows**;
> the intended delete does not happen and any pre-existing rows are **left intact**
> (safe-fail — nothing is lost). The **same CSV appended succeeds**, so
> `deleteAllRows:true` itself is the culprit (pilot-gated or bugged), not the
> CSV/table/version. **For Salesforce Pricing, the reliable replacement path is
> a fresh table + append**; Pricing does not support multiple CSV-table versions.
> `--overwrite` carries this warning in its help.

**Per-column CSV encoding (✅ live-verified for generic BRE).** A `usageType=Bre`
probe round-tripped all 7 Metadata `dataType`s through the CSV transport. That
does **not** widen Salesforce Pricing's supported contract: Pricing Help limits
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
| **Date** | `2026-07-10` (`YYYY-MM-DD`) | JSON string `YYYY-MM-DD` | date-only ISO |
| **DateTime** | `2026-07-10T14:30:00.000Z` | JSON string, same form | **milliseconds + `Z` MANDATORY** — `…T14:30:00Z` (no ms), a space instead of `T`, and date-only all drop the row |

**Per-row validation — bad rows drop silently → `CompletedWithErrors` (✅ live).**
An upload with a mix of valid + invalid rows loads **only the valid rows** and
finishes `uploadStatus = CompletedWithErrors`. The dropped rows surface **no
per-row error** — neither the `/data` GET nor the `Metadata` reports which rows
failed, only the aggregate status. This is why `--wait-for-status` is worth the
wait: it is the only signal that rows were silently dropped.

**Read — the data GET** (`dump_decision_table_data.py`):
`GET connect/business-rules/decision-table/{id}/data[?versionNumber=N][&filter=Field:Value][&limit=N]`
→ `{"rows":[{"id":"1FI…","rowData":{…}}], "totalRows":N}`. Row ids are
`1FI`-prefixed; `rowData` values are typed. Exposed as `--filter` /
`--version-number` on the dump CLI (both CsvUpload-only).

- **`filter=Field:Value`** is an **exact, case-sensitive equality** on the stored
  value (✅ live): `Region:North` ≠ `Region:north`, and there is **no substring /
  prefix** match. A **field name that doesn't exist returns 0 rows with no error**
  (silently empty — the caller must know the column is real).
- **`versionNumber`** — **omitting it** returns the current/active version's
  rows. ⚠ **Explicitly passing the current/active version's own number instead
  silently returns `{"rows": [], "totalRows": 0}`** (✅ live-verified — not lag,
  not param ordering; the version was independently confirmed current via the
  Connect versions-list endpoint). There is currently no way to *explicitly*
  request the current version's data by number — only the default
  (omitted-param) form works. A genuinely **non-existent** version on the read
  still correctly → `INVALID_API_INPUT`.

> ⚠ **`filter` + `limit` throw `UNKNOWN_EXCEPTION` (✅ live).** Combining them errors
> whenever `limit` is **not strictly greater** than the matched-row count (i.e.
> whenever `limit` would truncate the filtered set). The dump CLI therefore
> **drops `--limit` (with a note) when `--filter` is given** and returns the full
> matched set. Use `--limit` for an unfiltered peek; use `--filter` alone to narrow.

> ⚠ **Pagination gotcha.** `totalRows` is the count **in the response**, not a
> grand total, and `offset` is unreliable — do **not** build an offset pager.
> Use `filter` to narrow and `limit` to cap; read once.

**Versions — no v2 is auto-minted by re-upload (✅ live).** The generic BRE
API probe returned **Draft version 1** after create; Salesforce Pricing Help calls
the initial version **Inactive**, so preserve that product/surface distinction.
Uploading again (append or overwrite, with or without
`--version-number`) does **not** mint a v2 — every upload targets version 1.
Uploading to a **non-existent** version (`?versionNumber=2` when only v1 exists)
→ `INVALID_API_INPUT`.

**Row-level edit is not the `/data` POST.** On the probed release the `/data`
POST (row edit) is non-functional — load rows through the `/file` upload, not a
row-by-row POST.

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
names** (not the Tooling column names). Keys (live-verified):

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

Annotated real file (`RLM_CostBookEntries` — a `SingleSobject`, one INPUT + one
OUTPUT column):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DecisionTable xmlns="http://soap.sforce.com/2006/04/metadata">
    <conditionCriteria>1</conditionCriteria>          <!-- boolean logic over INPUT sequences -->
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
    <decisionTableParameters>
        <dataType>String</dataType>
        <fieldName>Cost</fieldName>
        <fieldPath>Cost</fieldPath>
        <isGroupByField>false</isGroupByField>
        <isRequired>false</isRequired>
        <usage>OUTPUT</usage>                           <!-- no operator/sequence -->
    </decisionTableParameters>
    <doesConsiderNullValue>false</doesConsiderNullValue>
    <executionType>Hbase</executionType>               <!-- repo XML accepted live; official enum/Tooling use HBASE -->
    <filterResultBy>OutputOrder</filterResultBy>        <!-- hit policy -->
    <hasIncrementalSyncFailed>false</hasIncrementalSyncFailed>
    <isIncrementalSyncEnabled>false</isIncrementalSyncEnabled>
    <setupName>Cost Book Entries</setupName>            <!-- human label (spaces OK) -->
    <sourceObject>CostBookEntry</sourceObject>
    <status>Active</status>                             <!-- deploy-time status -->
    <type>MediumVolume</type>
    <usageType>DefaultPricing</usageType>
</DecisionTable>
```

Notes from the shipped files:

- **Column order is not sequence order.** `RLM_ProductQualification` lists columns
  in file order `ParentProductId(seq2), IsQualified(OUTPUT), RootProductId(seq3),
  ProductId(seq1)` with `conditionCriteria` `1 AND 2 AND 3` — the `sequence`
  numbers, not the XML order, define the condition wiring.
- **`executionType` is optional in XML** — `RLM_ProductQualification` omits it
  (defaults) while `RLM_CostBookEntries` sets `Hbase`.
- **`setupName`** is the human label; the file base name is the `DeveloperName`
  (api name). Keep them consistent with the repo's existing naming.

> ⚠ **`executionType` casing needs context.** Official Metadata documentation
> and Tooling reads use `HBASE`; this repo's shipped XML uses `Hbase` and was
> accepted live. Preserve shipped XML for repo consistency, but don't generalize
> that spelling as the sole Metadata form.

---

## Definition authoring paths — decision guide

| You want to… | Use | Toolkit CLI | Vocabulary |
|---|---|---|---|
| **Ship a table in the build**, source-controlled, reviewable | **Metadata API** (`.decisionTable-meta.xml`) — the primary path | `create --path metadata` (default) | `dataSourceType`, `filterResultBy`, `decisionTableParameters`, `usage=INPUT` |
| **Inspect / one-off edit** the whole definition in one REST call | **Tooling API** — PATCH the `DecisionTable.Metadata` complexvalue | `create --path tooling`, `update`, `delete` | same as Metadata (Metadata-API field names) |
| **Compare a raw Connect representation** | Connect Definitions GET by id | `describe --connect` (read-only, optional) | `sourceType`, `decisionResultPolicy`, `parameters`, `usage=Input`, 15-char id |

The toolkit writes definitions only through **Metadata/Tooling**. Raw Connect
Definitions POST/PATCH/DELETE remain documented in the API reference for
platform context, but are not supported toolkit routes. Connect remains an
active toolkit dependency for CSV `/file`, `/data`, and `/versions`
sub-resources.

### Field-name divergence (Metadata/Tooling vs Connect)

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

Connect GET returns `dataSourceType: null` and `isVersioned: null` — it populates
its own (`sourceType`). **Never read a Metadata-API key off a Connect response.**
Treat this as a response-interpretation map, not a supported Connect mutation
contract.

---

## Enum catalog

Values in **bold** were observed live (`rlm-base__beta` / scratch, 2026-07-09);
the rest are 📄 doc-grounded from `meta_decisiontable.htm`. This is the
**Metadata/Tooling authoring catalog**; raw Connect Definitions has a narrower,
differently-spelled documented catalog and is read/reference-only in the toolkit.
Re-verify live observations on the target release at merge time.

| Metadata/Tooling field | Values |
|---|---|
| `dataSourceType` | ContextDefinition, **CsvUpload**, **MultipleSobjects**, **SingleSobject** |
| `executionType` | **DLO** (v67.0+, replaces DMO), **HBASE**/`Hbase`, HBPO, SOLR, SOQL |
| `conditionType` | **All**, Any, Custom |
| `filterResultBy` | AnyValue, CollectOperator, FirstMatch, **OutputOrder**, Priority, RuleOrder, UniqueValues |
| `type` | Advanced, HighScaleExecution, HighVolume, **LowVolume**, **MediumVolume**, RealTime |
| `status` | ActivationInProgress, **Active**, Draft, Inactive |
| `usageType` (ExpsSetProcessType) | Bre (default), **DefaultPricing**, **DefaultRating**, **PricingDiscovery**, **RatingDiscovery**, **RevenueStandardTax**, ProductCategoryQualification, **ProductQualification**, RecordAlert, … |
| `DecisionTableParameter.usage` | **INPUT**, **OUTPUT**, ROWCRITERIA |
| `DecisionTableParameter.dataType` | **Boolean**, **Currency**, **Date**, **DateTime**, **Number**, **Percent**, **String** (all 7 round-tripped on a generic `usageType=Bre` CsvUpload; Salesforce Pricing is narrower—see the **CSV Based tables** section) |
| `DecisionTableParameter.operator` | **Equals**, NotEquals, GreaterThan, GreaterOrEqual, LessThan, LessOrEqual, ExistsIn, Matches, IsNull, … |
| `DecisionTableSourceCriteria.valueType` | Formula, **Literal**, Lookup, Parameter, Picklist |
| `collectOperator` | Count, Maximum, Minimum, **None**, Sum |
| `dtRowLevelOverrideType` | **None**, Both, Condition, Operator |

**v67.0 additions:** `decisionTableFileImportVersions[]` (per-import activation
windows / rank / refresh; observed empty on SObject-backed tables) and
`isVersioned`. Its default is surface/product-specific: Metadata v67 documents
`true`; Tooling documents `false`; Pricing auto-versions CSV tables created
after the Usage 262 upgrade while older tables remain unversioned; raw Connect
GET returned `null` in the probe.

**Raw Connect catalog differences:** official Connect Definitions documents no
`ContextDefinition` `sourceType`, only title-case `Input`/`Output` usage, and
different source-criteria spellings (`GreaterThanOrEqual`, `LessThanOrEqual`,
`NotEqual`, `PickList`). Connect parameter docs omit `DateTime`, although it was
observed live. Do not assume Metadata enums are portable to Connect.

These Metadata/Tooling enum sets are the source of truth for canonical specs and
`validate_spec()`, which the offline tests exercise with no org.

---

## Related

- Parent skill: `.cursor/skills/decision-tables/SKILL.md`.
- Companion sub-file: `lifecycle-and-refresh.md` (deploy, activate/deactivate,
  refresh, recipe mappings).
- Exhaustive reference: `docs/references/decision-table-api-reference.md`.
- Toolkit: `scripts/decision_tables/README.md` (`_schema.py` encodes these
  enums + the divergence map).
