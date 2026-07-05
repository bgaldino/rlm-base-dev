# Context Service — Runtime Instances & Persistence

Companion to `SKILL.md`. Where `data-model-and-api.md` and
`authoring-and-lifecycle.md` cover the **design-time** Context *Definition*
(nodes / attributes / tags / mappings and their lifecycle), this sub-file covers
the **runtime** context *instance*: hydrating one from live records, querying /
inspecting the hydrated attribute values, updating them, reading / writing tags,
and persisting them back to the mapped SObjects.

> **Pinned to Release 262 / API v67.0.** Endpoint paths and the create /
> query-record / persist / query-tags-leaner request shapes are confirmed against
> the public **Runtime Context Instance Management** and **Persistence Context
> Management** REST references, cross-checked against near-core Java source and
> CS engineering. The runtime REST endpoints are all implemented and resolve, but
> the create `contextId` is **REQUEST-scoped by default** and does not survive
> across separate `sf api request` calls, and `query-record`/`query-tags` are
> **pilot-gated**. On a normal org, drive the whole lifecycle from one Apex
> transaction or one Flow. Re-verify edge behavior on the target release at merge.

## Start here — which runtime path works on your org

Pick the path by what the org has enabled. **On a normal GA org, use Apex or a
single Flow — the stateless multi-call REST scripts will not complete the
lifecycle** (see the roadblock table).

| Org capability | Working runtime path | Perm needed |
|----------------|----------------------|-------------|
| **Normal GA org** (no pilot) | **Apex `Context.IndustriesContext`** (scripted / debugging) **or one Flow** chaining the invocable actions (no-code). Whole lifecycle in **one request/transaction.** | just GA **`IndustriesContext`** |
| SESSION-scope pilot (`SessionScopeContext` via `ContextServicePilot`) and/or "Runtime Context Instance Reuse" (`ContextReuse`) | The REST scripts / multi-call REST — `contextId` survives across calls | pilot / reuse setting |

**On an org with `ContextServicePilot` enabled (262 / v67.0), the REST path
completes end-to-end:**

| REST step | Status | Notes |
|-----------|--------|-------|
| `POST /contexts` with `contextScope: "SESSION"` | ✅ works | contextId survives across separate CLI calls |
| `POST /contexts/query-record` | ✅ works | Pilot gate lifted — returns full attribute tree |
| `POST /contexts/query-tags-leaner` | ✅ works | Pilot gate lifted — returns tag values by name |
| `PATCH /contexts/attributes` | ✅ accepted | Flat body `{contextId, nodePathAndAttributes}` — NOT the `updateContextAttributesInput` wrapper |
| `PATCH /contexts/write-through-tags` | ✅ accepted | Flat body `{contextId, nodePathAndTagValues}` |
| `POST /contexts/persist-records` | ✅ end-to-end | Flat body `{contextId, targetMappingId}` — returns `referenceId` (16P) that **equals the `AsyncOperationTracker.Id`**. Both a no-op persist (`savedNodes={}`, OK) and a **dirty** persist (`Status=Completed` + populated `errorNodes`, FAILED) occur over this REST path — see *Persistence* |
| `DELETE /contexts/{id}` | ✅ works | Evicts the session-scoped instance |

**CLI flag:** `--context-scope SESSION` on `context_session.py` / `create_context_instance.py`.

**Why REST multi-call is not an option on a normal org** (both gates, not one):

| REST step | Status without pilot | Reason |
|-----------|----------------------|--------|
| `POST /contexts` (create) | ✅ works | GA |
| `query-record` / `query-tags` | ❌ `API_DISABLED_FOR_ORG` | pilot-gated (`ContextServicePilot`) |
| `persist-records` (and the PATCHes) | ❌ `RECORD_NOT_FOUND` | GA endpoint, but the REQUEST-scoped `contextId` from the create call is already gone by the next `sf api request` — surviving it needs **SESSION scope** (pilot) |

So without SESSION scope **and** `ContextServicePilot`, **Apex (or a single Flow)
is the only working path** — and it needs no pilot permission, only GA
`IndustriesContext`. Both keep create → query → (update) → persist in one request,
where the `contextId` never expires and the query methods aren't behind the REST
pilot gate.

**Copy-paste Apex — the full lifecycle in one transaction** (`sf apex run --file`).
Replace the `<…>` placeholders (`describe_context.py` gives you the ids and the
mapped SObject / tag names):

```apex
Context.IndustriesContext ctx = new Context.IndustriesContext();
Map<String,String> md = new Map<String,String>{
    'contextDefinitionId' => '<contextDefinitionId>',   // 11O…
    'mappingId'           => '<hydrationMappingId>'};    // 11j… a HYDRATION-intent mapping
// id-only payload — the engine hydrates parent + children from the org, server-side.
// NOTE businessObjectType = the MAPPED SObject name ("Quote"), NOT the node name.
Map<String,Object> bi = new Map<String,Object>{'metadata' => md,
    'data' => '{"SalesTransaction":[{"id":"<recordId>","businessObjectType":"Quote"}]}'};
String cid = (String) ctx.buildContext(bi).get('contextId');            // 0 SOQL — lazy

// READ by tag (tag names, not attribute/field names):
Map<String,Object> q = ctx.leanerQueryTags(new Map<String,Object>{
    'contextId' => cid, 'tags' => new List<String>{'SalesTransactionName','LineItemQuantity'}});
System.debug(q.get('recordIds'));          // [] means nothing hydrated → check businessObjectType
System.debug(q.get('leanerQueryTagResult'));

// (optional) UPDATE an attribute so persist sees it as dirty, then PERSIST:
// ⚠ dataPath MUST contain RECORD IDs [parentId, childId], NOT node names.
//   e.g. [quoteId] for root, [quoteId, qliId] for a child line.
//   Live-verified: node-name or empty dataPath silently no-ops (isSuccess=true,
//   value unchanged); record-ID path stages the edit for real.
// ⚠ Key is "nodePathAndAttributes" (NATIVE List<Map>) — NOT the stringified
//   "nodePathAndUpdatedValues" (which ALWAYS throws UnexpectedException in direct Apex).
List<String> dp = new List<String>{'<recordId>'};      // root-level: just the record id
// For child: new List<String>{'<parentRecordId>', '<childRecordId>'}
Map<String,Object> np = new Map<String,Object>{'dataPath' => dp};
List<Map<String,Object>> attrs = new List<Map<String,Object>>{
    new Map<String,Object>{'attributeName' => 'Quantity', 'attributeValue' => '5'}};
List<Map<String,Object>> npa = new List<Map<String,Object>>{
    new Map<String,Object>{'nodePath' => np, 'attributes' => attrs}};
ctx.updateContextAttributes(new Map<String,Object>{
    'contextId' => cid, 'nodePathAndAttributes' => npa});
Object refId = ctx.persistContext(new Map<String,Object>{
    'contextId' => cid, 'contextMappingId' => '<persistMappingId>'});   // returns referenceId (16P…)
System.debug(refId);
// persist is ASYNC — confirm via AsyncOperationTracker (see Persistence below), not refId.
```

The **Flow equivalent** is `buildContext → updateContextAttributes →
persistContextData` (+ `queryContextTags`) as invocable actions in one Flow — same
one-request guarantee, zero Apex, only the GA perm. Build it as a reusable subflow.

> **One caveat that no path escapes:** a **dirty** persist through the default
> `QuoteEntitiesMapping` fails on non-updateable fields (see *Persistence* → the
> `errorNodes` mechanism) — this is a field-updateability limit of the mapping, not
> a permission gate, so it affects Apex, Flow, and REST identically. A **no-op**
> persist (hydrate → persist unchanged) succeeds. Hydration and in-memory
> query/update are fully working on the Apex/Flow path.

## What these scripts are for (and are not)

**Purpose: debugging, understanding, and validating runtime behavior.** Reach for
the runtime scripts to answer questions like *does this definition actually
hydrate the fields it maps? does persist write the updated values back? does a
tag read resolve to the value I expect? what does the engine see for this record?*
They give you a hands-on, inspectable lens on the runtime that complements the
static inspection tools (`describe_context.py`, `trace_context.py`,
`diff_context.py`).

**They are not a production runtime or a build step.** In real usage the
consuming engines — pricing, DocGen, BRE / expression sets, the configurator,
billing, DRO — hydrate their own contexts as part of their own flows. Nothing in
the org build calls these scripts, and they are **not** wired into any CCI flow.
They carry **pilot caveats** the design-time `apply/delete/mutate_context.py` do
not: on a GA org `query`/`persist` need `ContextServicePilot`, and Apex
`Context.IndustriesContext` is the GA runtime path (see **Start here** below).

## The runtime lifecycle

```
build_hydration_data.py   →  a `data` payload — fillable skeleton, or
                             --from-record <id> for a ready-to-run id-only payload
        │
        ▼
POST /connect/contexts        create (hydrate)  →  Context Info { contextId, … }
        │
        ├─ PATCH /contexts/attributes            update attribute values
        ├─ PATCH /contexts/write-through-tags    write values by tag
        ├─ POST  /contexts/query-record          read the hydrated node/attr tree
        ├─ POST  /contexts/query-tags[-leaner]   read values by tag
        │
        ▼
POST /connect/contexts/persist-records   persist  →  { referenceId }  (→ ContextPersistenceEvent)
        │
        ▼
DELETE /connect/contexts/{contextId}     evict the instance
```

`context_session.py` runs this whole sequence in **one process** (see below);
the individual scripts each do one step.

## `contextId` is request-scoped — the fact that shapes everything

A runtime `contextId` is an **opaque, request-scoped cache handle** — a UUID / hex
string, **not** a 15/18-char SObject id, and **never** prefix-typed (do not
validate it like `11O…`/`11j…`). The create reference is explicit that a context
object *"applies only to a single request and cannot pass data across multiple
requests."*

This is governed by **`metadata.contextScope`** on the create body (near-core
enum `DataPersistenceScope { REQUEST, SESSION }`):

- **`REQUEST` (default)** — the instance is **thread/request-local** (the near-core
  builder puts it in a thread-local store, guardrail TTL capped at ~15 s). It
  **cannot** be looked up by a later, separate stateless HTTP call →
  `RECORD_NOT_FOUND` "doesn't exist or expired." This is by design.
- **`SESSION`** — the instance is written to a **distributed cache**, so the
  `contextId` **survives across separate calls** (subject to `contextTtl`). But
  SESSION is **pilot-gated**: sending `contextScope:"SESSION"` on a non-pilot org
  returns `API_DISABLED_FOR_ORG` *"you don't have permission to call Session
  Scope."* Enabled by the **`SessionScopeContext`** user permission (shipped via
  `ContextServicePilot`, PM-approval — not GA). Per CS engineering, only REQUEST
  scope is openly available; SESSION scope is limited to specific pilot teams,
  and REQUEST is the recommended scope for customer use cases.

Consequences:

- On a normal (non-pilot / REQUEST-scope) org a `contextId` from one `sf`/CLI
  invocation is **not** usable by a later, separate invocation. Cross-call REST use
  needs **SESSION scope** (pilot) and/or the RLM setting **"Runtime Context
  Instance Reuse to Improve Response Times"** (internal id **`ContextReuse`**, under
  Revenue Lifecycle Management Setup), within `contextTtl`.
- Therefore the **primary entry point is `context_session.py`** for the
  reuse/pilot case; but on a normal org even it can't keep a REQUEST contextId
  alive across its own steps (each shells out to a separate `sf api request`) — use
  the **Apex bridge or a Flow** to keep the whole lifecycle in one request.
- The standalone `create/query/persist/delete` scripts accept `--context-id` for
  the reuse-enabled or step-by-step-debugging case, and each print a one-line
  stderr warning to that effect. If one of them fails *not-found*, the instance
  expired between calls — use SESSION scope, the Apex bridge, or a single Flow.

> **`contextTtl` is a ContextDefinition property, in minutes** (near-core
> `contextTtlInMinutes`; default **10 min**, org max raised to **45 min** at R254+
> via `ContextMaxTtlInMinutes`/`NccsMaxTtlInMinutes`). It only matters for SESSION
> scope; REQUEST contexts are hard-capped at ~15 s. **Do not send a TTL on the
> runtime create body** — TTL is definition/org-driven, not a create field; the
> create-body scope control is **`contextScope`**, not a TTL. An unexpected key
> risks a `JSON_PARSER_ERROR` (the same failure mode as `primaryDomainObject` on a
> definition create).

## The REST endpoints resolve — the wall is REQUEST scope, not broken routes

The runtime REST surface is fully implemented at v67.0. Two facts govern what
works from stateless CLI calls:

> **⚠ ALWAYS use the fully versioned path with `sf api request rest`.** Call
> `sf api request rest "/services/data/v67.0/connect/contexts/attributes" …`, **not**
> the bare `connect/contexts/attributes`. A bare (un-versioned) path is NOT
> auto-prefixed for these resources — it misroutes to an HTML **"URL No Longer
> Exists"** page (an edge 404, and a **501 for `PATCH`**). That 501 is the *edge
> server rejecting an unrouted PATCH*, **not** the Context endpoint being
> unimplemented — the endpoints ARE implemented at v67.0 (the core system of
> record marks the PATCH ops `status: implemented`; core fit-tests PATCH them
> expecting 200). With the versioned path they resolve correctly.
> `_client.connect_request` already prepends the version, so the Python scripts are
> fine; the artifact only bites hand-run `sf api request` probes.

Endpoint map (v67.0, platform-wide — the same on scratch and production/demo):

- **`POST /connect/contexts` (create) works** and mints a `contextId`. The create
  `metadata` accepts **`contextScope`** (`REQUEST` | `SESSION`) — **this is the
  knob that governs cross-call survival, and it defaults to `REQUEST`.**
- **`contextScope: SESSION` is pilot-gated** (`API_DISABLED_FOR_ORG`, user
  permission `SessionScopeContext` via `ContextServicePilot`). SESSION scope is
  what persists the instance to a distributed cache so a `contextId` survives
  across separate HTTP calls; default REQUEST scope is request-local (~15 s
  guardrail TTL), so a REQUEST `contextId` is `RECORD_NOT_FOUND` on any *separate*
  `sf api request` call. This is **by design**: each CLI call is its own request,
  and the near-core builder writes REQUEST contexts only to a thread-local,
  SESSION contexts to the durable store.
- **`GET /connect/contexts/{id}` returns `200` but `isSuccess:false`** for an
  expired REQUEST id (a *soft* not-found that echoes the id back). The mutating
  ops return a *hard* 400 `RECORD_NOT_FOUND`.
- **`POST /connect/contexts/query-record` and `query-tags[-leaner]` are
  pilot-gated** — `API_DISABLED_FOR_ORG` *"…call Query Record"*, even on a fresh
  in-TTL contextId, on scratch and production alike (`ContextServicePilot`; the
  write endpoints are GA).
- **`PATCH /connect/contexts/attributes`, `PATCH …/write-through-tags`, and
  `POST …/persist-records` all resolve and reach contextId validation** (400
  `RECORD_NOT_FOUND` on a dead REQUEST id) — i.e. they are **implemented and
  GA-consumable**; they only fail from CLI because a REQUEST-scoped `contextId`
  can't survive to a *second* call. On a **SESSION-enabled** org (or from one
  transaction) they work.

**Net: the REST runtime API is not broken — it is scope-gated.** On a normal GA
org the contextId is REQUEST-scoped, so the multi-call REST sequence (create in
one call, then query/patch/persist in *separate* calls) cannot work — the instance
is request-local. Genuine cross-call REST use requires **SESSION scope** (pilot:
`SessionScopeContext`) and/or the RLM **"Runtime Context Instance Reuse"** setting
(`ContextReuse`). Separately, `query-record`/`query-tags` need the
`ContextServicePilot` gate regardless of scope.

**Therefore, on a normal (non-pilot) org, drive the whole lifecycle inside ONE
request** — Apex `Context.IndustriesContext` (`sf apex run`) or a single Flow
chaining the invocable actions. This is Salesforce's documented **design intent**,
not a workaround: internal engine call sites (pricing
`PricingRuntimeContextServiceImpl`, expression sets
`NearCoreExpressionSetRESTController`) all resolve context via the in-process
`ContextRuntimeService.getContext(...)`, never by chaining outbound
`/connect/contexts/*` calls; and CS engineering states that the REST APIs do not
support querying in REQUEST-scope context, with Apex and Flow the recommended
alternatives.

### The invocable-actions path (fourth surface) — same request-scope wall

Context Service also ships **standard invocable actions** (Flow-/REST-invocable,
[doc](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/context_service_invocable_actions_parent.htm)).
Action names on the org (`GET /services/data/v67.0/actions/standard`, filtered):
**`buildContext`**, **`updateContextAttributes`**, **`persistContextData`**,
**`queryContextTags`**, **`deleteContextCache`**, plus `addContextRecords` /
`deleteContextRecords` / `getAgentContext`. Input schemas (via
`GET /actions/standard/{name}`):

| Action | Required inputs | Optional | Outputs |
|--------|-----------------|----------|---------|
| `buildContext` | `contextDefinitionId` | `contextMappingId`, `contextData` (stringified JSON), `isTaggedData` | `contextId`, `contextDefinitionId`, `contextMappingId` |
| `updateContextAttributes` | `contextId`, `nodePathAndUpdatedValues` (stringified JSON — **invocable only**; direct Apex uses key `nodePathAndAttributes` as native `List<Map>`) | — | — |
| `persistContextData` | `contextId` | `contextMappingId`, `trackingId` | `referenceId` |
| `queryContextTags` | `contextId`, `tagsList` (**real `String[]`**, not stringified) | — | `queryResult` (stringified JSON) |

Over REST as *separate* calls the invocable actions hit the **exact same
request-scope wall** as raw Connect: `buildContext` works (`isSuccess:true`,
returns a `contextId`), but a *separate* REST `queryContextTags`/`persistContextData`
call with that `contextId` fails **`RECORD_NOT_FOUND` "doesn't exist or expired"** —
each REST invocation is its own request, and the instance is evicted between them.
(Gotcha: `tagsList` must be a genuine JSON array; a stringified array →
`INVALID_ARGUMENT_TYPE "expected String[]"`.)

**Where invocable actions win:** inside a **single Flow**, all the actions run in
**one transaction/request**, so a Flow `buildContext → updateContextAttributes →
persistContextData` keeps the `contextId` alive — the declarative equivalent of the
Apex bridge, with **zero Apex and only the GA `IndustriesContext` perm**. That
makes them the best *composable, low-dependency, no-code* runtime path (a reusable
subflow). They are **not** usable as separate `sf api request` CLI steps.

### The viable inspection path is Apex

`Context.IndustriesContext` does build + query **in one Apex transaction** (same
app server), so the `contextId` survives and the query methods are reachable
without the REST pilot gate:

```apex
Context.IndustriesContext ctx = new Context.IndustriesContext();
Map<String,String> md = new Map<String,String>{
    'contextDefinitionId' => '<contextDefinitionId>',  // 11O… ContextDefinitionId
    'mappingId'           => '<mappingId>'};            // 11j… a HYDRATION-intent ContextMapping
Map<String,Object> bi = new Map<String,Object>{'metadata' => md,
    // NOTE businessObjectType = the MAPPED SObject name ("Quote"), not the node name
    'data' => '{"SalesTransaction":[{"id":"<recordId>","businessObjectType":"Quote"}]}'};
String cid = (String) ctx.buildContext(bi).get('contextId');   // 0 SOQL — lazy
Map<String,Object> out = ctx.leanerQueryTags(new Map<String,Object>{
    'contextId' => cid, 'tags' => new List<String>{'SalesTransactionName','LineItemQuantity'}});
// out.leanerQueryTagResult → {tagName: [{tagValue, recordIdIndexesForPath, isNodeLevelTag}]}
// out.recordIds → the hydrated parent + child record ids
```

Method map on `Context.IndustriesContext`:

| Method | Works? | Notes |
|--------|--------|-------|
| `buildContext(input)` | ✅ | Returns Context Info (`contextId` + the 5 metadata keys). **0 SOQL** — hydration is lazy; the engine queries the org server-side on read. |
| `queryTags(input)` | ✅ | `{queryResult:{tag:[…]}, isSuccess, isDone}`. Empty arrays when the payload's `businessObjectType` is wrong (see the gotcha below). |
| `leanerQueryTags(input)` | ✅ | Lower-heap shape: `{leanerQueryTagResult, recordIds[], recordsInfo[], isSuccess}`. **The clearest signal** — `recordIds:[]` means *nothing hydrated*. |
| `getContext(input)` | ⚠ | Returns only the Context Info metadata (not hydrated data); its values are non-serializable proxies (`JSON.serialize` → `"null"`). Not a data-read path. |
| `queryContextRecordsAndChildren` | ❌ | Uncatchable `System.UnexpectedException` — effectively not exposed. Use `queryTags`. |
| build with `metadata.eagerHydration = 'true'` | ❌ | Uncatchable `System.UnexpectedException` at build — eager hydration is unsupported on this path; rely on lazy (default). |

**Tag names are a distinct namespace from attribute names.** `queryTags` /
`leanerQueryTags` take **tag** names, and an unknown one throws
`ContextModificationException: Invalid tag attribute name key: […]`. The tag name
often differs from the attribute name it fronts (e.g. attribute `Quantity` →
tag `LineItemQuantity`; attribute `Pricebook` → tag `PriceBooks`). Read the tag
names off the definition (`describe_context.py`, or the node/attribute
`tags`/`attributeTags[].name`), not the SObject field names.

> **Why the scripts still exist.** The REST runtime scripts are the documented,
> tool-agnostic contract (and work fully on a pilot-enabled / reuse-enabled org),
> but on a normal org the **Apex snippet above is the reliable way to validate
> that a definition actually hydrates** — the debugging/validation purpose these
> scripts serve, not a production runtime.

## The `data` hydration payload

The create body is `{"metadata": {…}, "data": "<stringified JSON>"}`. The `data`
field is a **JSON string** (not a nested object) whose decoded value is an object
**keyed by the context-node name**; each record carries `id`,
`businessObjectType`, its attribute values, and any child nodes as **nested
arrays named by the child node**:

```jsonc
{
  "SalesTransaction": [                     // ← array key = context NODE name
    {
      "id": "<quoteId>",
      "businessObjectType": "Quote",        // ← MAPPED SObject name, NOT the node name
      "SalesTransactionName": "ACME-0001",
      "TotalAmount": 1200,
      "SalesTransactionItem": [             // child node → nested array (node name)
        { "id": "<lineId>", "businessObjectType": "QuoteLineItem", "Quantity": 3 }
      ]
    }
  ]
}
```

> **⚠ The #1 hydration gotcha.** `businessObjectType` must be the **mapped SObject
> name** for that node under the chosen mapping (e.g. the `SalesTransaction` node
> maps to `Quote` under `QuoteEntitiesMapping`), **not** the context-node name. A
> payload whose `businessObjectType` is the node name hydrates **zero records** —
> the engine silently returns empty tag results (`recordIds: []`) with
> `isSuccess: true`, which *looks* like a permission/definition problem but is
> really a node-name-vs-SObject-name mismatch. The array **key** stays the node
> name; only `businessObjectType` changes. The node→SObject map lives on the
> mapping's `contextNodeMappings` (`contextNodeName` → `sObjectName`).

This shape is easy to get wrong by hand, so **`build_hydration_data.py`** fetches
the definition (one Connect GET), resolves the mapping's node→SObject lookup, and
emits a correctly-shaped skeleton with typed placeholders (empty string / `0` /
`false` / `null` by `dataType`) whose `businessObjectType` is already the mapped
SObject name; you fill in real `id`s and values. Leave `businessObjectType` and
the child-array names as emitted. `--mapping-name` picks the mapping to shape
against (default = the definition's default mapping); `--node NAME` (repeatable)
restricts output to a subtree.

**Hydration sourcing.** With only `id` + `businessObjectType` set, the engine
**queries the org itself** for the mapped fields — and does so **server-side,
invisible to the Apex SOQL governor** (0 `Limits.getQueries()` consumed at build).
Any attribute values you *do* include in the payload **override** the org-queried
values for that record. So an id-only payload is the normal case (hydrate live
data); inline values are for what-if / test overrides.

The server-side query also **cascades to child nodes**: a payload with only the
**root** record's `id` (no child arrays) hydrates the parent *and* its children —
the engine walks the mapping's node tree and queries each child SObject itself
(one root Quote id → the Quote + all its QuoteLineItems, no child ids listed).
That is why **`build_hydration_data.py --from-record <rootId>`** emits just
`{nodeName: [{"id": <rootId>, "businessObjectType": <mapped SObject>}]}` — no
placeholders, no child arrays — and it is ready to hydrate as-is (pass `--node` to
name the root node when the definition has more than one top-level node). Use the
default skeleton mode only when you want to hand-author attribute *overrides*.

`metadata` = `{contextDefinitionId (11O…), mappingId (11j…)}`. `taggedData`
(Boolean) is included **only** when you pass `--tagged-data` — it is on the
Context MetaData Input rep per internal sources; omit it otherwise (verify live).

> **⚠ Hydration is a sparse subset — you never get "all the tags."** A hydrated
> instance returns far fewer values than the definition defines, via a
> three-stage funnel (measured on `RLM_SalesTransactionContext` +
> `QuoteEntitiesMapping`):
> 1. **Definition ceiling** — the full attribute/tag count; `isTransient` attrs
>    never hydrate.
> 2. **Mapping ceiling** — only attributeMappings with a `queryAttribute` read a
>    field (the rest are computed/reference/derived). Field binding lives at
>    `attributeMappings[].contextAttrHydrationDetailList[].queryAttribute`
>    (+ `sObjectDomain`), **not** a `mappedField` key.
> 3. **Instance reality** — a tag only carries a value if the record it lives on
>    exists for *this* instance. A quote with no tax/recipient/rate-card/adjustment
>    children hydrates records for only a couple of the mapping's ~19 nodes; the
>    rest get **zero records**.
>
> **Querying a tag whose node hydrated 0 records THROWS** an uncatchable
> `System.UnexpectedException` (`ContextCoreRuntimeServiceAPIException`) — so a
> bulk "query every tag" call fails. Query tags only for nodes you know hydrated
> (check `recordIds` / `recordsInfo[].recordId` first, then query that node's
> tags). `leanerQueryTags` returns `{leanerQueryTagResult:{<tagName>:
> [{isNodeLevelTag, recordIdIndexesForPath:[…], tagValue}]}, recordIds[],
> recordsInfo[], isSuccess}` — the value field is **`tagValue`** (singular), and
> `recordIdIndexesForPath` (`[0]`=root, `[0,n]`=nth child) positions it in the
> tree. This sparse-hydrate / broad-writeback asymmetry is exactly why a dirty
> persist fails (see Persistence below).

## Query results: flattening + compound fields

`query-record` returns a **Query Context Record Result**: `contextId`, `isDone`,
`isSuccess`, and a recursive `queryRecords[]` where each record can carry
`childQueryRecords`. `query_context_instance.py` flattens that tree into rows with
a `depth` field (parent before child).

Each `record.attributesAndValues` may contain **stringified** compound values
(e.g. an Address serialized as a JSON blob). The human view **best-effort
decodes** any string value that looks like JSON (`{`/`[`) back into an object;
`--json` leaves everything raw (so machine consumers see exactly what the API
returned). A value that does not parse is left as the raw string, never dropped.

`--tags TAG …` switches to `query-tags` (or `query-tags-leaner` with `--leaner`,
API 66.0 — a lower-heap result shape for Apex / constrained clients). Both take
the same input: `{contextId, tags[]}`.

## Persistence

`persist-records` writes the instance's (possibly updated) attribute values back
to the SObjects of a **target** context mapping and returns a `referenceId` (which
maps to a `ContextPersistenceEvent`). Body (**flat form** — the public doc's
`contextPersistInput` wrapper is rejected at the parser;
`persist_context_instance.py` emits the flat form):
`{"contextId": "…", "targetMappingId": "11j…"}`.

Unlike `query-record`/`query-tags`, **`persist-records` is NOT pilot-gated** — a
live POST parses the body and reaches contextId validation (400 `RECORD_NOT_FOUND`
on a dead id, rather than `API_DISABLED_FOR_ORG`). The endpoint is implemented and
GA. But it's bounded by the **REQUEST-scoped** `contextId`, and
**`context_session.py --persist` does NOT survive this** — despite being "one
process," each step shells out to a *separate* `sf api request`, so the
REQUEST-scoped contextId minted by create is already `RECORD_NOT_FOUND` by the
persist call (and `--update-attr` PATCH hits the same wall). **The persist path
that works on a normal org is the Apex bridge:** `Context.IndustriesContext` doing
build → (`updateContextAttributes`) → `persistContext` in **one Apex transaction**
(`sf apex run --file`), which returns the `referenceId`. The REST `persist-records`
call works only when the instance survives — i.e. with **SESSION scope** (pilot)
or within a single request.

> **⚠ Persist is ASYNCHRONOUS — a `referenceId` is NOT proof the writeback
> landed.** `persistContext` returns `{referenceId:"16P…"}` immediately having done
> **zero synchronous DML**. The real success/failure lands asynchronously and is
> exposed in **two** places:
> 1. **`ContextPersistenceEvent`** platform event (`/event/ContextPersistenceEvent`,
>    key prefix `16P` — the referenceId IS the event handle; `RequestIdentifier` ==
>    the referenceId). Carries only a **`HasErrors`** boolean and is NOT queryable
>    (`describeSObjects` only) — subscribe with an `after insert` Apex trigger / Flow /
>    CometD to read it.
> 2. **`AsyncOperationTracker`** (SOQL-queryable! prefix `16P`, `queryable=true`) —
>    **this is THE diagnostic; read it first.** Every persist writes a row with
>    `JobType='ContextPersistence'`, a `Status`, and a **`Response`** long-text
>    field holding the node-level breakdown:
>    `{"contextDefinitionId","graphId","savedNodes":{…},"skippedNodes":[…recordIds…],"errorNodes":{"<recordId>":"<full DML error>"}}`.
>    **The returned `referenceId` IS the tracker's `Id` — exactly, not a
>    correlation key.** So poll it deterministically by primary key, not with a
>    "most-recent-row" heuristic:
>    ```bash
>    sf data query --query "SELECT Id,Status,Response FROM AsyncOperationTracker WHERE Id = '16P…referenceId…'" --target-org <sf-alias>
>    ```
>    `Status` picklist: `Submitted` / `InProgress` / `Completed` /
>    `CompletedWithFailures` / `Failure` (the first two are non-terminal — keep
>    polling). `savedNodes` = written; `skippedNodes` = eligible-but-DML-skipped;
>    `errorNodes` = recordId → the exact error. **So: never treat a returned
>    `referenceId` as confirmation — read `AsyncOperationTracker.Response` (detail)
>    and/or `ContextPersistenceEvent.HasErrors` (boolean), plus re-query the target
>    SObject.**
>
> **⚠ A dirty persist reports `Status='Completed'` WITH a populated `errorNodes`
> — "Completed" alone is NOT success.** Concretely (SESSION-scope REST,
> `QuoteEntitiesMapping`, a 1-line quote with `Quantity` edited on the QLI
> node): `Status='Completed'`, `savedNodes={}`, `skippedNodes=[<qliId>]`, and
> `errorNodes={<qliId>: "Unable to create/update fields: TotalPrice, Subtotal,
> NetUnitPrice, Product2Id, PricebookEntryId, …"}`. So the failure test is
> **`Status ∈ {CompletedWithFailures, Failure}` OR `errorNodes` non-empty** — a
> populated `errorNodes` on a `Completed` row is still a failure. This is exactly
> what `_runtime.summarize_persist_tracker` computes (`is_failure`).
>
> **The runtime scripts confirm this for you.**
> `context_session.py --persist` and `persist_context_instance.py` poll the
> tracker by `Id` after persist (`_runtime.confirm_persist`), print
> `persist outcome: OK …` / `persist outcome: FAILED …`, and **exit non-zero on a
> confirmed failure** — so a dirty persist is not reported as success. Control the
> poll with `--persist-poll-seconds` / `--poll-seconds` (default 30) and opt out
> with `--no-confirm-persist` / `--no-confirm` (reports only the `referenceId`).
> `create_context_instance.py` / the session likewise abort (non-zero, no
> `contextId` emitted) when create returns `isSuccess:false`.

> **⚠ Persist SKIPS a clean record and REJECTS a dirty record whose node carries
> non-updateable fields.** Two distinct outcomes, both visible in the tracker
> `Response`, both explained by near-core `DMLTypeResolver.java`:
> - **No-op / skip (`skippedNodes`, `HasErrors=false`).** A hydrated-but-unedited record
>   has DmlStatus `CREATED` + a **real Salesforce id**. `DMLTypeResolver.isDMLNoOp`
>   (real id + `CREATED` → no-op; `getHttpMethod` → null) skips it — "it already exists,
>   nothing to change." Only records that are `UPDATED` (real id → PATCH), or `CREATED`/
>   `UPDATED` with a **synthetic** id (→ POST), or `DELETED` are persisted. *This eligibility
>   gate was added in 254* (the 3-arg `isDMLNoOp` is `@Deprecated(since=254)`). A record
>   that never flipped `CREATED`→`UPDATED` (e.g. values supplied at build time rather than
>   via a post-hydration `updateContextAttributes`) silently no-ops.
> - **Reject (`errorNodes`, `HasErrors=true`).** A genuinely dirty record (`UPDATED`) IS
>   eligible → persist attempts an **atomic SObject-graph UPDATE over the FULL mapped
>   fieldset for that node — not just the changed column.** `removeRestrictedFields` strips
>   only **FLS**-restricted fields, NOT `updateable=false` ones, so every system-derived /
>   create-only field the mapping carries enters the graph. On the standard
>   QuoteEntitiesMapping SalesTransactionItem→QuoteLineItem node, the writeback set includes
>   **~29 `updateable=false` fields** (`TotalPrice`, `Subtotal`, `NetUnitPrice`,
>   `NetTotalPrice`, `ListPrice`, `TotalCost`, `Product2Id`, `PricebookEntryId`,
>   `StartDateTime`/`EndDateTime`, …). The whole node UPDATE is rejected atomically →
>   `errorNodes` = *"Unable to create/update fields: … Please check the security settings…"*.
>   The one field actually edited (e.g. `Quantity`, `updateable=true`) is **not** in the list —
>   it fails because of its non-updateable travelling companions. The "check security
>   settings" hint is **misleading**: no permission fixes `updateable=false`; the fix is a
>   PERSISTENCE mapping whose writeback set excludes non-updateable fields (and the Apex/REST
>   persist has **no** knob to narrow the fieldset — `removeRestrictedFields`/
>   `smartUpdatesEnabled` are not surfaced by the Apex bridge).
>
> This is a **field-updateability gate**, not a pilot entitlement — fully diagnosable from
> `AsyncOperationTracker.Response`, and it reproduces identically across the Apex
> attribute-path and the Flow tag-path (both funnel into the same near-core engine —
> `AbstractContextColumnarUpdateService.writeThroughTags` delegates to
> `updateContextAttributes` after tag→attribute resolution) and on a fresh single-line quote
> (so it is not record complexity). **Bottom line for tooling:** hydration + in-memory update
> are proven; a **no-op persist succeeds**; a **dirty persist through the default
> QuoteEntitiesMapping fails atomically** on non-updateable fields — read
> `AsyncOperationTracker.Response.errorNodes` for the exact list. A custom PERSISTENCE
> mapping restricted to updateable fields is the expected way to let a dirty write land.
> (Providing a child record inline in the create `data` payload throws an uncatchable
> `System.UnexpectedException` — unsupported, same class as eager hydration.)

> **FK caveat.** Reference / lookup **foreign-key** changes are **not reliably
> saved** by persist — scalar field updates are the supported path.
> `persist_context_instance.py` emits this caveat on every run; confirm any FK
> write directly on the target SObject.

Persistence reuses the same hydration binding, run backward: there is **no
separate persistence structure** — `ContextAttrHydrationDetail` is the single
field↔attribute binding, and direction is gated by the mapping's `intents`
(`HYDRATION` / `PERSISTENCE`) and the attribute's `fieldType`
(`INPUT` read-only / `OUTPUT` write-only / `INPUTOUTPUT` both; `isTransient`
skips persist). See `trace_context.py` (design-time) to see, per attribute, which
field a persist would target and whether the direction is active.

## Definition interfaces

`list_context_interfaces.py` reads `connect/context-definition-interfaces`
(GET; `--interface NAME` for one). A **definition interface** is an abstract
contract that context definitions can implement, used by engines to discover a
compatible definition. Interfaces are **not tied to a specific definition** — that
is why this is a separate script from `describe_context.py` (which requires a
definition selector). This endpoint is **not** gated (a plain Connect GET).

## Clearing the runtime schema cache

`DELETE /connect/context-runtime-schema/clear?contextDefinitionName=…[&contextMappingNames=…]`
evicts the **cached runtime schema** for a definition so the next hydration
re-reads the (possibly just-changed) mappings. Exposed as
`delete_context_instance.py --clear-schema-cache --developer-name <name>
[--mapping-names …]`. Useful while iterating on a definition's mappings during
debugging.

> **Two different deletes.** `delete_context_instance.py` touches the **runtime**
> (evict one instance, or clear the runtime schema cache). `delete_context.py`
> touches the **design-time definition** (deactivate / hard-delete a
> ContextDefinition). Don't confuse them.

## Dry-run contract (one consistent rule)

Under `--dry-run`, the runtime scripts behave exactly like the design-time ones on
the transport, with one deliberate refinement for the read-shaped POSTs:

- **Mutations only log, never execute:** `create` (POST), `persist-records`
  (POST), `attributes` PATCH, `write-through-tags` PATCH, and both DELETEs
  (instance + schema cache).
- **Reads always execute** — including the read-shaped POSTs `query-record` and
  `query-tags[-leaner]` — *when they have a valid target*. The runtime client
  forces `dry_run=False` on those calls so a supplied `--context-id` can still be
  inspected during a dry run (mirroring `_client`, where GET/HEAD and SOQL always
  run).
- **Session consequence:** because create is a mutation, a **dry-run session mints
  no `contextId`**. The dependent steps (attribute/tag update, query, persist,
  delete) are **skipped with a log line** rather than run against a fabricated id
  — there is no sentinel id. `RuntimeSession.run` returns
  `{dry_run: true, created: false, context_id: null, …}`. Passing an explicit
  `--context-id` lets the read steps run even under dry-run.

## Verification (before relying on the runtime scripts)

Offline (no org):

- `python tests/test_context_runtime.py` — body-builder shapes, mapping
  resolution, query flattening + compound decode, hydration skeleton, and the
  dry-run / reuse session contracts (all via a fake transport).
- `--help` and `--dry-run` on each script exercise import + argument wiring
  without touching an org.

Live (verify-live — required before merging any behavioral change here), against a
scratch org with an active definition (e.g. `RLM_SalesTransactionContext`):

1. `build_hydration_data.py … --out records.json`; fill in real ids (values
   optional — id-only hydrates from the org) — or use `--from-record <rootId>
   [--node NAME]` for a ready-to-run id-only payload. Confirm each record's
   `businessObjectType` is the **mapped SObject name** (e.g. `Quote`), which the
   builder emits.
2. `context_session.py … --data-file records.json --query` — on a
   **pilot-enabled** org this returns a `contextId` and the hydrated values. On a
   normal org expect `API_DISABLED_FOR_ORG` on the query (see "The REST endpoints
   resolve" above) and/or a not-found `contextId` between calls; fall back to the
   Apex path to validate hydration.
3. Add `--persist --target-mapping-name <mapping>` → the script polls
   `AsyncOperationTracker` by the returned `referenceId` (== the tracker `Id`) and
   reports `persist outcome: OK/FAILED`, exiting non-zero on a confirmed failure.
   Confirm the scalar attributes wrote back to the mapped SObject (note the FK
   caveat). A **no-op** persist (id-only hydrate → persist unchanged) reports OK
   with `savedNodes={}`; a **dirty** persist through `QuoteEntitiesMapping`
   (`--update-attr <parentId>.<qliId> Quantity N`) reports FAILED with populated
   `errorNodes`. Also pilot/reuse-gated (SESSION scope for the REST path).
4. `list_context_interfaces.py` → lists interfaces; `--interface <name>` → one.
   (Not gated — a plain Connect GET.)
5. **Apex validation (the reliable path on a normal org):** run the
   `Context.IndustriesContext` `buildContext` + `leanerQueryTags` snippet from
   "The viable inspection path is Apex" via `sf apex run`. `recordIds` non-empty
   and real `tagValue`s confirm the definition + mapping hydrate; `recordIds:[]`
   means the payload's `businessObjectType` doesn't match the mapping's SObject.

Record the actual v67.0 request/response shapes and adjust the two verify-live
PATCH builders (`build_update_attributes_body`, `build_write_tags_body`) and the
`taggedData` handling in `_runtime.py` if they differ.

## Related

- `SKILL.md` — routing, Quick Rules (rule 8 = runtime scoping), DO NOT, Entry
  Conditions.
- `data-model-and-api.md` — the Connect-vs-SObject endpoint split; the runtime
  resources row.
- `authoring-and-lifecycle.md` — activation/deactivation, `intents`, `fieldType`,
  `isTransient` (the design-time knobs that gate what persist can write).
- `scripts/context_service/README.md` — per-script flags, examples, caveats.
- `trace_context.py` — design-time field↔tag↔attribute tracer (the static
  companion to runtime `query-record` / `persist`).
