# Context Service — Data Model & API Reference

Read this when you need the object model, the canonical enums, the Connect /
SObject-REST endpoint split, the three mapping types, the repo plan-file format,
the guardrail limits, or the MDAPI type schema.

> **Provenance / pin.** Sourced from `tasks/rlm_context_service.py`,
> `tasks/rlm_extend_stdctx.py`, the plans in `datasets/context_plans/`,
> `docs/references/context-service-utility.md`, Core UDD, the Connect OAS, and
> Salesforce Help. **Pinned to Release 262 / API v67.0** — re-verify enums and
> response shapes against a live org if the platform changes.

## Object model (version-centric)

A version has **two layers that cross-link by id**, not one containment tree:

**Layer 1 — the abstract schema (SObject-agnostic).** Nodes, their attribute
lists, and the tags on those attributes. Nothing here names an SObject or a
field — it is the vocabulary an engine reasons over.

**Layer 2 — the SObject binding (the "lens").** A mapping projects the *same*
abstract schema onto a concrete set of SObjects/fields. The binding objects
**reference** the schema objects by id (`ContextNodeMapping.contextNodeId`,
`ContextAttributeMapping.contextAttributeId`) — they do **not** own their own
nodes/attributes.

```
ContextDefinition                     (developerName, label; NO IsActive here)
└─ ContextDefinitionVersion           (IsActive lives HERE; one active at a time)
   │
   ├─ LAYER 1 — abstract schema (no SObject)
   │  └─ ContextNode                  (hierarchy via childNodes / parentNodeName)
   │     └─ ContextAttribute          (name, dataType, fieldType, isTransient, isKey)
   │        └─ ContextTag (attributeTags)  ── the join key to expression sets
   │
   └─ LAYER 2 — SObject bindings (many mappings, each a lens over Layer 1)
      └─ ContextMapping               (e.g. QuoteEntitiesMapping; exactly one isDefault)
         └─ ContextNodeMapping        (contextNodeId → sObjectName)
            └─ ContextAttributeMapping (contextAttributeId → mappedField)
               └─ ContextAttrHydrationDetail  (query hop; ≤1 per attribute mapping)
```

**Record-ID key prefixes (live v67.0).** Passing an id to the wrong endpoint
returns a misleading `"The requested resource does not exist"` — check the
prefix first:

| Prefix | Object | Prefix | Object |
|--------|--------|--------|--------|
| `11O` | ContextDefinition | `11b` | ContextNodeMapping |
| `11o` | ContextNode | `11R` | ContextAttributeMapping |
| `11n` | ContextAttribute | `11P` | ContextAttrHydrationDetail |
| `11j` | ContextMapping | `11k` | ContextTag |

`11O`/`11o`/`11n` differ only by **case** — an easy transposition bug. Note the
attribute DELETE/PATCH endpoint is **node-scoped**
(`connect/context-nodes/{11o…}/context-attributes/{11n…}`); a bare
`connect/context-attributes/{id}` DELETE returns "resource does not exist."

**The reuse insight — one node, many SObject lenses.** Because a mapping only
*references* the shared node tree, the *same* abstract node is bound to a
*different* SObject by each mapping. In the standard Sales Transaction context,
the single `SalesTransaction` node resolves to a different object per mapping:

```
SalesTransaction node ─┬─ QuoteEntitiesMapping          → Quote
                       ├─ SalesAgreementEntitiesMapping → SalesAgreement
                       ├─ OrderEntitiesMapping          → Order
                       └─ QuoteToContractSlsTrxnMapping → Quote (a to-Contract lens)
```

Consequences that fall out of this:
- **Adding an attribute is a Layer-1 edit** (one `ContextAttribute` under a node);
  **mapping it to a field is a Layer-2 edit** (one `ContextAttributeMapping` per
  mapping you want it hydrated in). The two are separate steps — an attribute can
  exist with **no** binding in a given mapping (`mappedField: null`).
- **Which mapping activates is the default mapping** (`isDefault:true`) — that is
  the lens the engine uses unless told otherwise, hence the activation gate.
- **`ASSOCIATION`-only mappings carry zero node mappings** — they link two
  definitions (e.g. `SalesTransactionToAssetMapping`) without binding fields.

### Referenced definitions (cross-context links)

A definition can **reference another whole definition** so an engine can cross
between them. In Setup this is the **"Referenced Definitions"** field on the
Details tab; in the GET it is `referenceContextDefinitions[]` (each entry:
`referenceContextDefinition` = the target developerName, `inheritedFrom`,
`contextDefinition` id). Live example: `RLM_SalesTransactionContext` references
**`AssetContext__stdctx`** — so pricing a quote/order line can reach the related
**Asset** (renewals, amendments, asset-state lookups). This link is **inherited
from the standard base**, not hand-authored.

Mechanically the reference is realized by the **`ASSOCIATION`-intent mappings**
(above): the 6 link mappings (`SalesTransactionToAssetMapping`,
`AssetToSalesTransactionMapping`, `ContractToSalesTxnMapping`,
`SalesTxnItmToAssetStatePrdMap`, `AssetStatePrdToSalesTxnItmMap`,
`ProductDiscoveryContextMapping`) bridge a node of one context to a node of
another, carry **no** SObject/field bindings, and do **not** hydrate (the
consuming service hydrates). Two related definition-level flags:
`canBeReferenceDefinition` (Setup **"Reference Definition"** — whether *this* def
may be referenced by another; `false` on Sales Transaction) and the validator's
cap of **≤ 2 distinct referenced definitions**. Do not confuse "Reference
Definition = false" (a capability flag) with "has referenced definitions" (the
`AssetContext` link above).

Key facts:
- **`IsActive` is on the version**, not the definition. Confirmed live via
  `SELECT Id, ContextDefinition.DeveloperName, IsActive FROM
  ContextDefinitionVersion`.
- A **default mapping** (a `ContextMapping` flagged `isDefault:true`) must exist
  for a version to activate — otherwise the `isActive:"true"` PATCH fails with
  **`DATA_MAPPING_NOT_FOUND`** (live-confirmed, v67.0). See
  `authoring-and-lifecycle.md` → *Activation & deactivation*.
- Engines (Pricing/BRE/DRO/Billing) bind to the active version, **hydrate** an
  instance by running SOQL against the mapped SObjects (honoring FLS), then
  read/write attributes **by ContextTag**. The direction of data movement per
  mapping is set by its **`intents`** (`HYDRATION` read / `PERSISTENCE`
  write-back / `ASSOCIATION` link / `TRANSLATION` transform — since v61) **and**
  each attribute's `fieldType`; see `authoring-and-lifecycle.md` → *Hydration,
  persistence & the mapping intents* for the full gate table.
- **One binding serves both read and write.** `ContextAttrHydrationDetail`
  (`sObjectDomain` + `queryAttribute`) is the **single** object describing an
  attribute↔SObject.field binding — there is **no** `ContextAttrPersistenceDetail`.
  Persistence reuses the same detail, run backward, gated by the `PERSISTENCE`
  intent + a write-eligible `fieldType` (`OUTPUT`/`INPUTOUTPUT`, not `transient`).
- **The source field name lives in `queryAttribute`, not `mappedField`.** On any
  inherited/standard attribute mapping `mappedField` is **empty**; the concrete
  SObject field is `contextAttrHydrationDetailList[].queryAttribute` (+
  `sObjectDomain`). Join field↔attribute↔tag on **`contextAttributeId`** (present
  on the Layer-1 attribute, its tags, *and* every Layer-2 attribute mapping) —
  `trace_context.py` does exactly this.
  **Two phantom modes** (both look like "the mapping didn't take"):
  (1) **field ABSENT** → the hydration write returns `success:true` but persists
  nothing (phantom no-op) — check `FieldDefinition` before trusting a green
  result; (2) **field PRESENT but the running user lacks FLS** → the write
  *persists* (`ContextAttributeMapping` + `ContextAttrHydrationDetail` rows
  exist at the SObject layer) but the **Connect aggregated GET honors FLS and
  filters the binding out**, so the GET (and any tool reading it, incl.
  `trace_context.py`) shows `contextAttrHydrationDetailList: []` / "no field
  bound." Granting FLS surfaces it **immediately — no activate/deactivate cycle
  and no definition change** (live-verified v67.0). So "(no field bound)" when a
  data-layer row exists means **missing FLS**, not a failed mapping. (This is
  the real cause of the Setup-UI "cycle + refresh before the new field appears"
  behavior — an FLS/describe-cache effect, not a version recompile: the bind
  itself lands in place on the *active* version.)
- The GET response nests nodes under `childNodes` (a `{contextNodes: [...]}`
  wrapper *or* a bare list — the inspector's `iter_nodes` tolerates both) and
  attributes under `attributes` (wrapper `contextAttributes` or bare list).

### Attribute fields (the Structure grid)

The Setup **Structure** tab lists a node's attributes; each column maps to a
Layer-1 `ContextAttribute` field (live-confirmed, v67.0):

| Structure column | API field | Notes |
|------------------|-----------|-------|
| **Name** | `name` | The API name; also the join key spelling for `mappingRules.contextAttribute` and (usually) the tag name. |
| **Display Name** | `displayName` | UI label only. **Null on essentially all standard/inherited attributes** — the grid then shows the API name. Repo plans don't set it. |
| **Type** | `fieldType` | `INPUT`/`INPUTOUTPUT`/`OUTPUT`/`AGGREGATE` — governs read/write direction (see `authoring-and-lifecycle.md` → intents gate table). |
| **Data Type** | `dataType` | The canonical enum above (`STRING`, `LOOKUP`, `CURRENCY`, …). |
| **Key / Value** | `isKey` / `isValue` | A **matched pair for dynamic key-value *bag* nodes** — NOT a primary-key/uniqueness marker. On Sales Transaction only the 3 bag nodes (`SalesTransactionItemAttribute`, `FulfillmentLineAttribute`, `ASPAttribute`) carry them, as `…AttributeKey` (`isKey:true`) + `…AttributeValue` (`isValue:true`); every other attribute shows **"NA"** (both false). Record identity is `contextAttributeId`, not `isKey`. |
| **Transient** | `isTransient` | `true` → the attribute is computed in-cache and **skipped on persistence** (write-back opt-out) and not packaged. Set only via **SObject REST** (Connect PATCH ignores it); plan key `isTransient`. |

Other real attribute fields not shown in the grid: `contextAttributeId` (the join
key), `parentNodeId`, `attributeTags` (Layer-1 tags), `isCustomMappingAllowed`,
and `isLocalizationDisabled` (opts an attribute out of the **separate** 262
locale-translation feature — distinct from the `TRANSLATION` mapping intent).

### Tags — the expression-set contract

Tags are **Layer-1** (they hang off attributes via `attributeTags`, not off
mappings or SObjects). Each tag is `{contextTagId, name, contextAttributeId,
dynamic}`. **This is deliberate:** a pricing procedure / expression set reads and
writes context values **by tag name**, never by node path or SObject field — so
the tag vocabulary is the stable seam between a context definition and the
engines that consume it. Rename or drop a tag and you break the consuming
expression set; that is also *why* a definition with an active ES consumer cannot
be deactivated (see `authoring-and-lifecycle.md` → *Activation & deactivation*,
and `.cursor/skills/expression-sets/SKILL.md` for the consumer side). A standard
context carries hundreds of these (the Sales Transaction context tags the large
majority of its attributes).

**Tag names are unique per *definition*, not per attribute** (live-verified
v67.0). A tag row stores exactly one `contextAttributeId`, so tags are *stored*
per-attribute — but the **name** is a definition-wide key: POSTing a tag whose
`name` already exists anywhere in the definition (even onto a *different*
attribute) is rejected with **`DUPLICATE_VALUE` — "Tag name already exists for
this definition: <name>"**. Confirmed directly: the same `__c` tag name POSTed to
a custom attribute succeeded, then the identical name POSTed to a second,
unrelated inherited attribute was refused. Corollary observed on the standard
base — 717 tags carry 717 distinct names, zero reuse. **This is *why* an
expression set can reference a bare tag name with no node/attribute qualifier:
the name → attribute mapping is 1:1 across the whole definition, so the name is an
unambiguous global handle.** So you cannot use one tag name as a shared alias
across two attributes; pick distinct names.

**One attribute can carry multiple tags** (live-confirmed v67.0). `attributeTags`
is a list; POSTing a second `ContextTag` with the same `contextAttributeId` (and a
*different*, definition-unique `name`) yields `attributeTags: [{…tag1}, {…tag2}]` —
both sharing the `contextAttributeId`, each with its own `contextTagId`. Each tag
is an **independent by-name alias** for the same attribute value: an expression set
referencing either name resolves to the identical attribute (confirmed against
Core source + the Context Management architecture doc). There is **no documented
priority/ordering** among tags — the pricing pre-processor keys tags by name and
takes the first match — so treat multiple tags as parallel names, safe for reads,
not as a precedence list. The common use is adding a custom `__c` alias next to an
inherited standard tag so a consumer can reference a stable name you control.
**Multiplying tags does not change Layer-2**: the attribute's mapping/hydration
binds once regardless of tag count. Tooling: `trace_context.py` joins on
`contextAttributeId`, so every tag on an attribute resolves to the same field
bindings; `_delete.py` treats each tag as its own deletable artifact (distinct
`contextTagId`).

The `dynamic` boolean marks a **data-derived** tag/attribute (populated from
org records via a context dictionary tied to an entity object, surfaced by the
design-time `…/dynamic-attributes` typeahead) versus a fixed-schema one
(`dynamic:false`). It is an attribute-level property the tag payload mirrors.

### Also on the version (present but out of this repo's scope)

A `ContextDefinitionVersion` GET also returns `contextDefinitionFilters`
(criteria that refine data operations — see the Filters endpoint below),
`contextDefinitionTransformations`, and per-node-mapping `contextDictionaries`.
These are **empty on the standard bases this repo extends** and no task/plan key
touches them, but they are real model elements — do not assume the version is
just nodes + mappings + tags.

## Canonical enums (Core UDD, v67.0)

- **`dataType`** ∈ `STRING, NUMBER, BOOLEAN, DATE, DATETIME, PERCENT, PICKLIST,
  CURRENCY, REFERENCE, DOUBLE, INT, MAP, SELFREFERENCE, LOOKUP`
- **`fieldType`** ∈ `INPUT, INPUTOUTPUT, OUTPUT, AGGREGATE`
- **`mappingType`** ∈ `SOBJECT, CONTEXT`

> **Normalization note.** The file-based `.contextDefinition` MDAPI format /
> internal validator uses a slightly different allow-list (`INTEGER` instead of
> `INT`, lowercased intents). Treat the **Core enum above as canonical**; the
> offline plan validator (`scripts/context_service/validate_context_plan.py`) checks
> against it. Normalize to Core when authoring plan JSON.

## Connect API vs SObject REST

All Connect paths are relative to `/services/data/v67.0/` — `sf api request rest`
requires the **fully versioned path** (a bare `connect/...` 404s with
"URL No Longer Exists"; `_client.py` prepends it automatically).

| Resource / operation | API | Path (relative to `/services/data/v67.0/`) |
|----------------------|-----|---------------------------------------------|
| List definitions | Connect (GET) | `connect/context-definitions?includeInactive=true&includeUpgrade=true` |
| Read one definition | Connect (GET) | `connect/context-definitions/<id>` |
| Create definition; **clone**; **extend** a standard/file-based base; persist entire definition | Connect (GET/POST) | `connect/context-definitions` |
| Query / update / delete one definition | Connect (GET/PATCH/DELETE) | `connect/context-definitions/<id>` |
| Add nodes/attributes/tags; basic SOBJECT + CONTEXT mappings | Connect (POST/PATCH) | `connect/context-definitions/<id>/...` |
| Upgrade / Sync | Connect (PATCH) | `connect/context-definitions/upgrades` (`upgradeMode` ∈ Sync/Preview/Override) |
| **Context Definition Filters** — create / get / update / delete filters on a definition | Connect (GET/POST + by-id GET/PATCH/DELETE) | `connect/context-definitions/<id>/filters[/<filterId>]` |
| Context nodes / attributes / tags / node-mappings / mappings — granular create/update/**delete-by-id** | Connect (POST/PATCH/DELETE) | `connect/context-definitions/<id>/<subresource>[/<subId>]` |
| Query tags (memory-optimized) | Connect (POST) | `connect/context-definitions/.../query-tags` (leaner result for Apex / low-heap clients) |
| Runtime context instances — create / query / delete | Connect (POST/GET/DELETE) | Context Service **Runtime** resources (not used by this repo's build tasks) |
| **Relationship-traversal hydration** | **SObject REST** | (not settable via Connect PATCH — rejected) |
| **`MappedContextDefinition` (CONTEXT `mappedContextDefinitionName`)** | **SObject REST** | (Connect PATCH silently ignores it) |
| **`IsTransient` on an attribute** | **SObject REST** | (not honored by Connect PATCH) |

> **Source.** Verbs/resources above are from the public **Context Service API
> REST Reference** (`developer.salesforce.com` → industries_reference →
> context_service_apis) cross-checked against the internal MDAPI type + Connect
> endpoint inventory. Two notes for this repo: there is **no "save as new
> version" verb** — the only version-crossing operation is Upgrade/Sync (see
> *Versioning* in `authoring-and-lifecycle.md`); and the **granular delete-by-id**
> sub-resource endpoints exist at the API even though this repo's plan format /
> `manage_context_definition` task are **additive-only** and do not call them
> (relevant if a future "patch deletions" capability is built — the API can
> delete a node/attribute/tag/mapping by id).

The mutating tasks (`rlm_context_service.py`) apply SObject mappings **before**
CONTEXT-to-CONTEXT mappings so referenced IDs exist. On a Connect PATCH,
`isDeleteExistingHydrationDetail` defaults **true** — a re-run **wipes existing
hydration** unless you preserve it.

## The three mapping types

**1. SOBJECT** — attribute ↔ a field on the node's mapped object:

```json
{
  "mappingName": "QuoteEntitiesMapping",
  "contextNode": "SalesTransactionItem",
  "contextAttribute": "ConstraintEngineNodeStatus__c",
  "mappingType": "SOBJECT",
  "sObject": "QuoteLineItem",
  "sObjectField": "RLM_ConstraintEngineNodeStatus__c"
}
```

**2. Relationship-traversal (chained hydration)** — a SOBJECT rule that carries
`childSObject` / `childSObjectField` to hydrate across a relationship hop.
**Applied via SObject REST, not the Connect PATCH** (which rejects traversals);
the validator emits an INFO note when it sees `childSObjectField`.

**3. CONTEXT-to-CONTEXT** — one context attribute sourced from another:

```json
{
  "mappingType": "CONTEXT",
  "sourceContextNode": "AssetActionSource",
  "sourceContextAttribute": "AssetConstraintEngineNodeStatus__c"
}
```

## Repo plan-file format

A manifest (`datasets/context_plans/<Name>/manifest.json`) lists one or more
plans:

```json
{ "contexts": [
  { "developerName": "RLM_SalesTransactionContext",
    "planFile": "contexts/ramp_mode.json" } ] }
```

Each plan file (`contexts/<plan>.json`) is either **additive against an existing
base** or **create-new** (`"create": true`). Recognized keys:

| Key | Meaning |
|-----|---------|
| `create` | `true` → create a new definition if it does not exist (needs `developerName` + `label`) |
| `developerName` | Target/definition developer name (unsuffixed, e.g. `RLM_SalesTransactionContext`) |
| `label` / `description` | DisplayName + description (required on create) |
| `contextNodeDefinitions` | Nodes: `name`, optional `parentNodeName` (child of another node) |
| `contextAttributesByName` | Attributes: `nodeName`, `name`, `dataType`, `fieldType`, optional `isTransient` |
| `contextMappings` | Mapping shells (name/description) + `generateInputMappings` / `generateSObjectMappings` |
| `mappingRules` | The three mapping types above (`mappingName`, `contextNode`, `contextAttribute`, `mappingType`, `sObject`/`sObjectField` \| `sourceContext*` \| `childSObject*`) |
| `contextTagsByName` | Context tags (the expression-set contract) |
| `contextMappingUpdates` | In-place updates to existing mappings |
| `defaultMapping` | Name of the mapping to flag `isDefault:true` before activation (required to activate a freshly-created definition — else `DATA_MAPPING_NOT_FOUND`) |
| `activate` | Activate the version after applying |

**`__c`-suffix rule (scoped).** The `__c` convention distinguishes custom
artifacts *added to a standard/extended base* from inherited standard names, so
the offline validator makes the suffix an **ERROR only when the plan targets a
standard/extended base** (no `create: true`). For **create-new** definitions
(`create: true`) the check is **skipped** — names are wholly author-chosen and
collide with nothing inherited (e.g. DocGen's `AccountName`, `GrandTotal`).
Definition `developerName`s are always exempt (legitimately `RLM_*Context`).

## Guardrail limits

The offline validator enforces the **strict** numbers; Salesforce Help quotes
higher ceilings. Both are listed — flag the discrepancy when it matters.

| Limit | Strict (validator) | Help | Enforced? |
|-------|--------------------|------|-----------|
| Nodes per definition | ≤ 30 | up to 50 | ERROR |
| Attributes per node | ≤ 50 | — | ERROR |
| Total attributes | ≤ 250 | up to 1000 | ERROR |
| Hierarchy depth | ≤ 5 | ≤ 5 | ERROR |
| Tags per node | ≤ 10 (guideline) | — | INFO only |
| Distinct referenced context definitions | ≤ 2 | — | ERROR |
| Hydration entries per attribute mapping | ≤ 1 | ≤ 1 | — |

**Tags per node is a guideline, not a hard limit.** The shipped `DocGen` plan
declares 20 tags on its `Quote` node and works, so the validator surfaces
exceeding 10 as an **INFO note only** — it never fails the build (even under
`--strict`). Treat it as a "consider splitting the node" hint, not an error.

## MDAPI

`ContextDefinition` deploys as **one atomic unit** (`childXmlNames: []` — no
sub-components deploy independently) from
`force-app/main/default/contextDefinitions/` via `deploy_context_definitions`.
**Activation state and default-mapping designation are not packageable** — they
are manual/API steps after deploy. This directory is **tracked** metadata, not
auto-generated; prefer plans + tasks for additive changes.
