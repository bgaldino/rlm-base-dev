# Context Service — PATCH payload shapes

> Live-verified accept-shapes for the Context Service Connect and SObject REST
> mutation endpoints (Salesforce Release 262 / API v67.0). Each rule below is
> grounded in an observed platform error and its resolution — re-verify edge
> behavior on the target release at merge time.
>
> **Audience:** authors of `scripts/context_service/*`, the production
> `manage_context_definition` task, and anyone hand-crafting Context Service
> API payloads. This file complements [context-service-utility.md](./context-service-utility.md)
> (which documents the plan-file surface) and
> [expression-set-connect-api-reference.md](./expression-set-connect-api-reference.md)
> (companion for Expression Sets).
>
> **Not authoritative for GET / read shapes** — see the platform GET response
> directly; this doc covers only what the *mutation* endpoints accept.

## Table of contents

- [The GET vs PATCH shape gap](#the-get-vs-patch-shape-gap)
- [Endpoint accept-shapes](#endpoint-accept-shapes)
  - [Connect PATCH `context-mappings/{id}/context-node-mappings`](#connect-patch-context-mappingsidcontext-node-mappings) — the destructive PATCH surface
  - [Connect PATCH `context-definitions/{id}/context-mappings`](#connect-patch-context-definitionsidcontext-mappings)
  - [SObject REST PATCH `sobjects/ContextAttribute/{id}`](#sobject-rest-patch-sobjectscontextattributeid)
  - [SObject REST PATCH `sobjects/ContextNodeMapping/{id}`](#sobject-rest-patch-sobjectscontextnodemappingid)
  - [SObject REST POST `sobjects/ContextAttributeMapping` / `ContextAttrHydrationDetail`](#sobject-rest-post-sobjectscontextattributemapping--contextattrhydrationdetail)
- [Active-version per-endpoint behavior matrix](#active-version-per-endpoint-behavior-matrix)
- [Common rejections and how to resolve them](#common-rejections-and-how-to-resolve-them)
- [Where the fixes live in code](#where-the-fixes-live-in-code)

---

## The GET vs PATCH shape gap

The Context Service Connect API is **not shape-symmetric**: the JSON a GET
returns is **not** the JSON the same URL's PATCH accepts. Concretely:

- **GET response** carries *response-only* fields the PATCH rejects
  (`baseReference`, `contextAttributeName`, `parentNodeMappingId`, `dataType`,
  `sourceObject`, `mappedContextTag`, …).
- **GET response** flattens hydration into top-level lists
  (`contextAttrHydrationDetailList`, `contextAttrContextHydrationDetailList`);
  the PATCH expects them **nested** under `hydrationDetails` with a different
  key name (`contextAttrHydrationDetails`, `contextAttrContextHydrationDetails`).
- **GET response** exposes SObject-REST-style fields (`mappedField`) even on
  the Connect surface; the Connect PATCH rejects them.

Rebroadcasting a GET row unchanged as the PATCH body will fail with
`JSON_PARSER_ERROR: Unrecognized field "<name>"` on the first response-only
field the parser encounters.

**Implication for callers doing a read-modify-write:** you must **project**
the GET row down to the PATCH accept-shape before re-emitting it. See
[`_project_attribute_mapping_for_patch`](../../scripts/context_service/_apply.py)
for the reference implementation.

---

## Endpoint accept-shapes

### Connect PATCH `context-mappings/{id}/context-node-mappings`

The primary "update node mapping" surface — and the one with the
**whole-body-replace hazard**: any `contextAttributeMappings` list that omits
an existing sibling row is interpreted as a request to delete that sibling
(the platform still returns `isSuccess: true`). Live-verified silent-destroy
on active versions.

**Body:**

```json
{
  "contextNodeMappings": [
    {
      "contextNodeId":         "11a…",
      "contextNodeMappingId":  "11b…",
      "sObjectName":           "QuoteLineItem",
      "mappedContextNodeId":   "11a…",
      "attributeMappings": {
        "contextAttributeMappings": [
          {
            "contextAttributeId":          "11c…",
            "contextInputAttributeName":   "MyAttr__c",
            "contextAttributeMappingId":   "11d…",   /* PATCH one; omit for POST */
            "mappedContextAttributeName":  null,
            "mappedContextTagName":        null,
            "isKey":                       false,
            "isValue":                     true,
            "sequence":                    1,
            "hydrationDetails": {
              "contextAttrHydrationDetails": [
                { "sObjectDomain": "QuoteLineItem", "queryAttribute": "Description" }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

**Node-mapping shell required fields (all four):** `contextNodeId`,
`contextNodeMappingId` (for PATCH), `sObjectName`, `mappedContextNodeId`.
Omitting any raises `INVALID_DEFINITION: "Invalid mapping for given context"`
(a generic message that *does not name the missing field*).

**Attribute-mapping accept-list** (fields the endpoint accepts; every other
key raises `JSON_PARSER_ERROR: Unrecognized field`):

- `contextAttributeMappingId` — required for PATCH; omit for POST of a new mapping
- `contextAttributeId`
- `contextInputAttributeName` (writable form; **not** `contextAttributeName`)
- `mappedContextAttributeName`
- `mappedContextTagName`
- `isKey`, `isValue`, `sequence`
- `hydrationDetails` (nested — see below)

**Response-only fields (never emit these back):** `baseReference`,
`contextAttributeName`, `parentNodeMappingId`, `dataType`, `sourceObject`,
`mappedContextTag`, `contextAttrHydrationDetailList` (flat),
`contextAttrContextHydrationDetailList` (flat), `mappedField`.

**Hydration nesting:** the GET returns hydration as *flat* top-level lists;
the PATCH expects them *nested* under `hydrationDetails` with different keys:

| GET (response) shape                                | PATCH (accept) shape                                          |
|-----------------------------------------------------|----------------------------------------------------------------|
| `contextAttrHydrationDetailList: [{...}]`           | `hydrationDetails.contextAttrHydrationDetails: [{...}]`        |
| `contextAttrContextHydrationDetailList: [{...}]`    | `hydrationDetails.contextAttrContextHydrationDetails: [{...}]` |

Per-hydration-entry accept-list:

- SObject-domain entries (`contextAttrHydrationDetails`): `sObjectDomain`,
  `queryAttribute` only.
- Context-source entries (`contextAttrContextHydrationDetails`):
  `queryAttribute` (source `ContextAttribute` id), `parentAttributeMappingId`
  (source `ContextAttributeMapping` id) only.

All other entry keys (`baseReference`, `contextAttrHydrationDetailId`,
`mappedAttributeDataTypeInfo`, `childDetails`, …) are response-only.

**Inherited-row rule:** GET rows with `baseReference` containing `__stdctx/`
are inherited from the standard base. Re-emitting them raises
`INVALID_INPUT: "An Inherited mapping for ContextAttribute: <name> already
exists…"`. Filter them out before the merge. See `_is_inherited_row`.

**Verb rule:** the endpoint accepts both `POST` (new node mappings) and
`PATCH` (existing ones). The primary caller inspects each node mapping —
if *any* has a `contextNodeMappingId` the write becomes a `PATCH`; otherwise
a `POST`.

**Many-to-one plan constraint (not a payload-shape issue but a common
follow-on error):** binding a custom attr to a `QuoteLineItem` field that is
already bound by a standard inherited attribute raises
`INVALID_DEFINITION: "Many-to-one mapping isn't allowed"`. Pick a field the
inherited base doesn't already map.

---

### Connect PATCH `context-definitions/{id}/context-mappings`

Used for mapping-level metadata (`description`, `isDefault`, etc.) — **not**
for attribute-mapping edits. The typical fields:

```json
{
  "contextMappings": [
    {
      "contextMappingId": "11j…",
      "isDefault":        true,
      "description":      "…"
    }
  ]
}
```

Active-version behavior: **BLOCKED**. Setting `isDefault` on an active
version fails with `RECORD_UPDATE_FAILED: "Cannot modify/delete an active
context definition"`. Deactivate first.

---

### SObject REST PATCH `sobjects/ContextAttribute/{id}`

Used to flip `IsTransient` on an existing `ContextAttribute`:

```json
{ "IsTransient": true }
```

Active-version behavior: **BLOCKED** — same
`RECORD_UPDATE_FAILED` error as the Connect mapping PATCH. Deactivate first.

---

### SObject REST PATCH `sobjects/ContextNodeMapping/{id}`

Used to set/clear `MappedContextDefinition` on a node mapping:

```json
{ "MappedContextDefinition": "11O…" }   /* or null to clear */
```

Active-version behavior: **ALLOWED** (silent success on null→value,
value→value, value→null).

---

### SObject REST POST `sobjects/ContextAttributeMapping` / `ContextAttrHydrationDetail`

Used by the traversal-hydration flow (`_apply_traversal_hydration`). Body is
the standard SObject REST create shape:

```json
{
  "ContextNodeMappingId":  "11b…",
  "ContextAttributeId":    "11c…",
  "MappedField":           "Account.Name",
  "IsKey":                 false,
  "IsValue":               true
}
```

Note the **SObject REST uses `MappedField`** (SObject-REST-style) — this is
the same-domain concept the Connect PATCH expresses via nested
`hydrationDetails.contextAttrHydrationDetails[].queryAttribute`. **Do not
confuse the two.** Emitting `mappedField` on the Connect endpoint raises
`JSON_PARSER_ERROR`.

Active-version behavior: **ALLOWED** (POST of new artifacts is on the
active-version allow-list, universally).

---

## Active-version per-endpoint behavior matrix

Live-verified on an active version (v67.0).

| Endpoint                                                                    | On active           | Notes                                                                 |
|-----------------------------------------------------------------------------|---------------------|-----------------------------------------------------------------------|
| Connect `PATCH context-mappings/{id}/context-node-mappings` (attr-mappings) | ⚠ SILENTLY DESTRUCTIVE | `isSuccess:true` + wipes sibling `ContextAttributeMapping` rows not re-emitted. **Mitigated** by the sibling-merge in `_apply.py`. |
| Connect `PATCH context-definitions/{id}/context-mappings` (mapping metadata) | BLOCKED             | `RECORD_UPDATE_FAILED`. Deactivate first.                             |
| SObject REST `PATCH sobjects/ContextAttribute/{id}` (`IsTransient`)          | BLOCKED             | `RECORD_UPDATE_FAILED`. Deactivate first.                             |
| SObject REST `PATCH sobjects/ContextNodeMapping/{id}` (`MappedContextDefinition`) | ALLOWED         | Silent success.                                                       |
| Connect `POST context-definitions/{id}/context-tags` (add tag)               | ALLOWED             | INSERT of a new artifact.                                             |
| SObject REST `POST sobjects/ContextAttributeMapping`                         | ALLOWED             | INSERT of a new artifact.                                             |
| SObject REST `POST sobjects/ContextAttrHydrationDetail`                      | ALLOWED             | INSERT of a new artifact.                                             |
| SObject REST `DELETE sobjects/ContextAttributeMapping/{id}`                  | ALLOWED             | Leaf-row delete.                                                      |
| Connect `POST context-definitions/{id}/context-node-mappings` (new NM shell)| ALLOWED             | INSERT of a new artifact.                                             |
| Connect `POST context-definitions/{id}/context-attributes` (new attr)       | ALLOWED             | INSERT of a new artifact.                                             |

**Rule of thumb:** the platform lets you **INSERT** new artifacts on an
active version (POST of nodes, attributes, mappings, tags, hydration-detail
leaves), but **MODIFY / DELETE** an existing one is blocked — with two
exceptions:

1. `SObject REST PATCH sobjects/ContextNodeMapping/{id}` is silently
   allowed (independent of the Connect PATCH block).
2. The Connect node-mapping PATCH is not blocked — but its
   whole-body-replace semantics turn a partial payload into a silent delete
   of the omitted rows. This is worse than a hard block.

---

## Common rejections and how to resolve them

Every error below was observed live against the mutation endpoints. `<field>` /
`<name>` are placeholders for the platform's actual token.

| Symptom                                                                 | Root cause                                                        | Resolution |
|-------------------------------------------------------------------------|-------------------------------------------------------------------|-------------|
| `JSON_PARSER_ERROR: Unrecognized field "baseReference"`                 | Response-only field re-emitted on PATCH                           | Project the row down via `_project_attribute_mapping_for_patch`; strip all response-only fields |
| `JSON_PARSER_ERROR: Unrecognized field "contextAttributeName"`          | Response-only mirror of `contextInputAttributeName`               | Use `contextInputAttributeName` on writes |
| `JSON_PARSER_ERROR: Unrecognized field "mappedField"`                   | SObject REST field emitted on Connect PATCH                       | Use nested `hydrationDetails.contextAttrHydrationDetails[{sObjectDomain,queryAttribute}]` on Connect |
| `JSON_PARSER_ERROR: Unrecognized field "contextNodeName"`               | Response-only field on node-mapping shell                         | Use `contextNodeId` + `sObjectName` |
| `INVALID_DEFINITION: "Invalid mapping for given context"`               | Node-mapping shell missing required id or the payload references an artifact the definition doesn't know about | Include all four: `contextNodeId`, `contextNodeMappingId`, `sObjectName`, `mappedContextNodeId`. Verify ids against a fresh `fetch_detail`. |
| `INVALID_INPUT: "An Inherited mapping for ContextAttribute: <name> already exists…"` | Re-emitted an inherited (`baseReference` contains `__stdctx/`) attribute mapping row | Filter inherited rows via `_is_inherited_row` before the merge |
| `INVALID_DEFINITION: "Many-to-one mapping isn't allowed"`               | Two attributes binding to the same SObject field                  | Plan-authoring issue, not a payload issue — pick a different `sObjectField` or repurpose the existing binding |
| `RECORD_UPDATE_FAILED: "Cannot modify/delete an active context definition"` | Modify/delete of an existing artifact on an active version    | Deactivate first (see A2 shared lifecycle guard); reactivate after |
| `MAX_LIMIT_EXCEEDED: "Version already exists for this Context Definition"` | Attempted to insert a second `ContextDefinitionVersion`         | The version is a 1:1 singleton — deactivate/reactivate bumps `VersionNumber` in place; do not create a second version |
| PATCH returns `isSuccess: true` but siblings vanish                     | Whole-body-replace semantics on Connect node-mapping PATCH        | Re-emit ALL existing children (P2 fix) or migrate to `ATTR_MAPPING_COLLECTION` granular writes |

---

## Where the fixes live in code

- **Read-shape → write-shape projection:** `_project_attribute_mapping_for_patch`
  in `scripts/context_service/_apply.py` — the read side of the P2 fix.
  Emits the accept-shape (allow-listed keys + nested hydration).
- **Field allow-lists:** `_ATTR_MAPPING_PATCH_FIELDS`,
  `_SOBJECT_HYDRATION_ENTRY_FIELDS`, `_CONTEXT_HYDRATION_ENTRY_FIELDS` in
  `_apply.py`. Keep in sync with the [Attribute-mapping accept-list](#connect-patch-context-mappingsidcontext-node-mappings)
  section above.
- **Inherited-row detection:** `_is_inherited_row` in `_apply.py`.
- **Sibling merge:** `_merge_existing_attribute_mappings` in `_apply.py` —
  the write side of the P2 fix. Given a plan payload with `contextMappings`
  and a `detail` snapshot, folds every existing non-inherited sibling back
  into the PATCH so the whole-body-replace endpoint sees a complete child
  set.
- **Primary builder (write-shape source of truth):**
  `_payload.translate_mapping_rules` — the plan→PATCH translator, whose
  emitted shape is what this doc describes. Any change to accept-shape rules
  must be reflected in both `translate_mapping_rules` and the projection
  helpers.
- **Active-version guard:** `_guard_active_for_patch` in `_apply.py` — routes
  the two Connect/SObject PATCH hazard points through a deactivate-first
  wrapper when `deactivate_before=True` was passed to `apply_plan`.

---

## Runtime instance mutation shapes (live-verified 2026-07-04, ContextServicePilot org)

These are the **runtime** (context-instance) mutation bodies, distinct from the
design-time definition-management PATCHes above. All are flat (no wrapper object).

### `PATCH /connect/contexts/attributes` — update attribute values

```json
{
  "contextId": "<opaque-hex-contextId>",
  "nodePathAndAttributes": [
    {
      "nodePath": {"dataPath": ["<recordId>"]},
      "attributes": [
        {"attributeName": "SalesTransactionName", "attributeValue": "New Value"},
        {"attributeName": "Status", "attributeValue": "InReview"}
      ]
    }
  ]
}
```

- `dataPath` contains **record IDs** from root to target, NOT node names.
  `["<quoteId>"]` = root record; `["<quoteId>", "<qliId>"]` = child.
  An empty `[]` or node-name-based dataPath silently no-ops (returns
  `isSuccess:true` but no value changes). Live-verified: both REST and Apex
  confirm **only record IDs mutate values** (262 / v67.0, pilot + non-pilot).
- Uses **attribute names** (not tag names).
- **NOT** wrapped in `updateContextAttributesInput` — the wrapper is rejected:
  `JSON_PARSER_ERROR: Unrecognized field "updateContextAttributesInput"`.
- **REST and Apex use the SAME key and shape**: `nodePathAndAttributes`
  (parsed JSON for REST; native `List<Map<String,Object>>` for Apex). The
  stringified `nodePathAndUpdatedValues` key ALWAYS throws
  `UnexpectedException` in direct Apex — it is only for the Flow invocable
  adapter (which deserializes it internally and uses tag names, not attribute
  names).

### `PATCH /connect/contexts/write-through-tags` — write values by tag

```json
{
  "contextId": "<opaque-hex-contextId>",
  "nodePathAndTagValues": [
    {
      "nodePath": {"dataPath": []},
      "tagValues": [
        {"tagName": "SalesTransactionName", "tagValue": "Written via Tag"}
      ]
    }
  ]
}
```

- Uses **tag names** (distinct namespace from attribute names).

### `POST /connect/contexts/persist-records` — persist to mapped SObjects

```json
{"contextId": "<opaque-hex-contextId>", "targetMappingId": "11j…"}
```

- Flat — **NOT** wrapped in `contextPersistInput`.
- Returns `{"referenceId": "16P…"}` (async; confirm via `AsyncOperationTracker`).

### `POST /connect/contexts` — create (hydrate)

```json
{
  "metadata": {
    "contextDefinitionId": "11O…",
    "mappingId": "11j…",
    "contextScope": "SESSION"
  },
  "data": "<stringified JSON payload>"
}
```

- `contextScope` is optional (omit → `REQUEST` default, thread-local ~15 s).
- `SESSION` requires `ContextServicePilot` permission; persists to distributed cache.
- `data` is a **JSON string** (not a nested object).

---

## Related references

- [`context-service-utility.md`](./context-service-utility.md) — plan-file
  surface (`manage_context_definition` task options, plan JSON shape).
- [`expression-set-connect-api-reference.md`](./expression-set-connect-api-reference.md)
  — sister doc for Expression Sets, same style.
- `.cursor/skills/context-service/data-model-and-api.md` — Connect vs
  SObject REST endpoint split at the model level.
- `.cursor/skills/context-service/runtime-and-persistence.md` — runtime
  context-instance API (separate surface; not the design-time PATCH shapes).
- `.claude/plans/context-service-followup-fixes.md` — P2 fix plan, live
  verification ledger.
