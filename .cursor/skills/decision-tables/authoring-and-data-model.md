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
| **CsvUpload** | An uploaded CSV, held by the platform | Connect `.../{id}/data` (v62+) — 📄 doc-grounded, unverified (no such table on probed orgs) |
| **ContextDefinition** | Hydrated at runtime by a Context Definition | No static table — nothing to sample |

**Editing the definition ≠ refreshing the data.** A definition change is
deployed; row changes are picked up by the **async `refreshDecisionTable`
action** (rate-limited ~100/hr — see `lifecycle-and-refresh.md`). A definition
change is not live to the engine until a refresh completes. This is why the
toolkit separates `describe`/`diff` (definition) from `dump` (data).

---

## The 5 Tooling setup objects

The definition is assembled across **five Tooling API objects** (v59.0+). They
are **Tooling only** — not on the normal REST `/sobjects` surface — read via
`/tooling/query` and `/tooling/sobjects/<Object>`.

| Object | Key prefix | Role & key fields |
|---|---|---|
| `DecisionTable` | **`0lD`** | The definition head. `DeveloperName` (api name), `Status`, `UsageType`, `SourceObject`, `LastSyncDate`, and the **`Metadata`** complexvalue (inlines the children). |
| `DecisionTableParameter` | **`0lP`** | A column. `DecisionTableId`, `FieldName`, `Usage` (INPUT/OUTPUT/ROWCRITERIA), `Operator`, `Sequence`, `DataType`, `FieldPath`, `IsRequired`, `IsGroupByField`, `SortType`, `DomainObject`. |
| `DecisionTableDatasetLink` | **`0lX`** | Binds a source SObject for `MultipleSobjects`. `DecisionTableId`, `SourceObject`, `SetupName`, `IsDefault`, `Metadata`. |
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
    <executionType>Hbase</executionType>               <!-- ⚠ MDAPI casing 'Hbase'; APIs return 'HBASE' -->
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

> ⚠ **`executionType` casing is representation-specific.** Source XML uses
> `Hbase`; the Tooling `Metadata` complexvalue and Connect return `HBASE`. Do
> **not** "correct" the XML to match an API read — keep each representation's
> native casing (a repeated DO NOT in the parent skill).

---

## The three authoring paths — decision guide

| You want to… | Use | Vocabulary |
|---|---|---|
| **Ship a table in the build**, source-controlled, reviewable | **Metadata API** (`.decisionTable-meta.xml`) — the primary path | `dataSourceType`, `filterResultBy`, `decisionTableParameters`, `usage=INPUT` |
| **Inspect / one-off edit** the whole definition in one REST call | **Tooling API** — PATCH the `DecisionTable.Metadata` complexvalue | same as Metadata (Metadata-API field names) |
| **CRUD from an external/Connect client** | **Connect Definitions** `connect/business-rules/decision-table/definitions[/{id}]` | **`sourceType`, `decisionResultPolicy`, `parameters`, `usage=Input`, 15-char id** |

The toolkit's `create_decision_table.py --path metadata|tooling|connect`
selects the path; a canonical author-facing spec is translated to each path's
vocabulary by `_payload.py`. **Read the divergence table before writing
across paths.**

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
`_schema.py`'s `FIELD_NAME_MAP` encodes this mapping (concept → (metadata/tooling,
connect)) and the offline tests assert it.

---

## Enum catalog

Values in **bold** were observed live (`rlm-base__beta` / scratch, 2026-07-09);
the rest are 📄 doc-grounded from `meta_decisiontable.htm`. Re-verify on the
target release at merge time.

| Field (MD/Tooling · Connect) | Values |
|---|---|
| `dataSourceType` · `sourceType` | ContextDefinition, CsvUpload, **MultipleSobjects**, **SingleSobject** |
| `executionType` | **DLO** (v67.0+, replaces DMO), **HBASE**/`Hbase`, HBPO, SOLR, SOQL |
| `conditionType` | **All**, Any, Custom |
| `filterResultBy` · `decisionResultPolicy` | AnyValue, CollectOperator, FirstMatch, **OutputOrder**, Priority, RuleOrder, UniqueValues |
| `type` | Advanced, HighScaleExecution, HighVolume, **LowVolume**, **MediumVolume**, RealTime |
| `status` | ActivationInProgress, **Active**, Draft, Inactive |
| `usageType` (ExpsSetProcessType) | Bre (default), **DefaultPricing**, **DefaultRating**, **PricingDiscovery**, **RatingDiscovery**, **RevenueStandardTax**, ProductCategoryQualification, **ProductQualification**, RecordAlert, … |
| `DecisionTableParameter.usage` | **INPUT**, **OUTPUT**, ROWCRITERIA |
| `DecisionTableParameter.dataType` | Boolean, Currency, Date, DateTime, Number, Percent, **String** |
| `DecisionTableParameter.operator` | **Equals**, NotEquals, GreaterThan, GreaterOrEqual, LessThan, LessOrEqual, ExistsIn, Matches, IsNull, … |
| `DecisionTableSourceCriteria.valueType` | Formula, **Literal**, Lookup, Parameter, Picklist |
| `collectOperator` | **None**, … (used when `filterResultBy=CollectOperator`) |
| `dtRowLevelOverrideType` · `rowLevelOverrideType` | **None**, … |

**v67.0 additions:** `decisionTableFileImportVersions[]` (per-import activation
windows / rank / refresh; observed empty on SObject-backed tables) and
`isVersioned` (docs default true; observed **false** on shipped SObject-backed
tables, **null** via Connect).

These enum sets are the source of truth for `_schema.py` (`DATA_SOURCE_TYPES`,
`EXECUTION_TYPES`, `FILTER_RESULT_BY`, `PARAM_USAGE`, `SETUP_OBJECT_PREFIXES`, …)
and `validate_spec()`, which the offline tests exercise with no org.

---

## Related

- Parent skill: `.cursor/skills/decision-tables/SKILL.md`.
- Companion sub-file: `lifecycle-and-refresh.md` (deploy, activate/deactivate,
  refresh, recipe mappings).
- Exhaustive reference: `docs/references/decision-table-api-reference.md`.
- Toolkit: `scripts/decision_tables/README.md` (`_schema.py` encodes these
  enums + the divergence map).
