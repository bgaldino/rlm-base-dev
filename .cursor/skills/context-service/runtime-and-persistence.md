# Context Service — Runtime Instances & Persistence

Companion to `SKILL.md`. Where `data-model-and-api.md` and
`authoring-and-lifecycle.md` cover the **design-time** Context *Definition*
(nodes / attributes / tags / mappings and their lifecycle), this sub-file covers
the **runtime** context *instance*: hydrating one from live records, querying /
inspecting the hydrated attribute values, updating them, reading / writing tags,
and persisting them back to the mapped SObjects.

> **Pinned to Release 262 / API v67.0.** Endpoint paths and the
> create / query-record / persist / query-tags-leaner request shapes are confirmed
> against the public **Runtime Context Instance Management** and **Persistence
> Context Management** REST references. The two PATCH bodies
> (`/contexts/attributes`, `/contexts/write-through-tags`) are grounded in internal
> sources and are **verify-live** — re-confirm on a live org before relying on them.

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
They are **EXPERIMENTAL / verify-live**, matching `apply/delete/mutate_context.py`.

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

Consequences:

- A `contextId` minted by one `sf`/CLI invocation is **not guaranteed** to be
  usable by a later, separate invocation. Cross-invocation reuse works **only**
  when the org setting **"Runtime Context Instance Reuse to Improve Response
  Times"** is on *and* the call is within `contextTtl` (definition-level;
  ~10 min default, 45 max).
- Therefore the **primary entry point is `context_session.py`**, which does
  create → use → persist → delete back-to-back in one process, so the handle
  never has to survive across calls.
- The standalone `create/query/persist/delete` scripts accept `--context-id` for
  the reuse-enabled or step-by-step-debugging case, and each print a one-line
  stderr warning to that effect. If one of them fails *not-found*, the instance
  expired between calls — use `context_session.py` or enable the org setting.

> `contextTtl` is a **definition** property. Do **not** try to send a per-instance
> TTL on the runtime create body — TTL is not a documented create field and an
> unexpected key risks a `JSON_PARSER_ERROR` (the same failure mode as
> `primaryDomainObject` on a definition create).

## Live-verified reality: REST create works, REST query is gated, Apex is the inspection path

Live testing (v67.0, against both a scratch org **and** a production/demo org — so
these are **platform behaviors, not instance quirks**) established the actual
runtime surface:

- **`POST /connect/contexts` (create) works** over REST. It mints a `contextId`
  (request scope) and returns Context Info. This is the un-gated entry.
- **`POST /connect/contexts/query-record` and `query-tags[-leaner]` are
  pilot-gated.** They return `API_DISABLED_FOR_ORG` — *"Looks like you don't have
  permission to call Query Record."* This is an **org-level gate**
  (`ContextServicePilot` org perm / `SessionScopeContext` user perm) that gates the
  **SESSION** scope those reads need. **Confirmed identical on scratch AND
  production/demo** → it is not something you can flip on with a permission set on
  a normal org; it is a pilot enablement.
- **A `contextId` does not survive across separate HTTP calls.** Each
  `sf api request` is a distinct HTTP request that can land on a different app
  server, so a `contextId` from one call is `RECORD_NOT_FOUND` ("doesn't exist or
  expired") on the next — even from a single Python process, because the scripts
  shell out to a fresh `sf api request` per call. Request-scope reuse across calls
  needs the org's Instance-Reuse setting (pilot-adjacent), so in practice the
  standalone `query`/`persist`/`delete` scripts will fail not-found on most orgs.

**The viable inspection path is Apex.** `Context.IndustriesContext` does
build + query **in one Apex transaction** (same app server), so the `contextId`
survives and the query methods are reachable without the REST pilot gate:

```apex
Context.IndustriesContext ctx = new Context.IndustriesContext();
Map<String,String> md = new Map<String,String>{
    'contextDefinitionId' => '11O…',        // ContextDefinitionId
    'mappingId'           => '11j…'};        // a HYDRATION-intent ContextMapping
Map<String,Object> bi = new Map<String,Object>{'metadata' => md,
    // NOTE businessObjectType = the MAPPED SObject name ("Quote"), not the node name
    'data' => '{"SalesTransaction":[{"id":"0Q0…","businessObjectType":"Quote"}]}'};
String cid = (String) ctx.buildContext(bi).get('contextId');   // 0 SOQL — lazy
Map<String,Object> out = ctx.leanerQueryTags(new Map<String,Object>{
    'contextId' => cid, 'tags' => new List<String>{'SalesTransactionName','LineItemQuantity'}});
// out.leanerQueryTagResult → {tagName: [{tagValue, recordIdIndexesForPath, isNodeLevelTag}]}
// out.recordIds → the hydrated parent + child record ids
```

Live-verified method map on `Context.IndustriesContext`:

| Method | Works? | Notes |
|--------|--------|-------|
| `buildContext(input)` | ✅ | Returns Context Info (`contextId` + the 5 metadata keys). **0 SOQL** — hydration is lazy; the engine queries the org server-side on read. |
| `queryTags(input)` | ✅ | `{queryResult:{tag:[…]}, isSuccess, isDone}`. Empty arrays when the payload's `businessObjectType` is wrong (see the gotcha above). |
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

> **Why the scripts still exist.** The REST runtime scripts remain the documented,
> tool-agnostic contract (and work fully on a pilot-enabled / reuse-enabled org),
> but on a normal org the **Apex snippet above is the reliable way to validate
> that a definition actually hydrates**. This is exactly the debugging/validation
> purpose these scripts serve — not a production runtime.

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
      "id": "0Q0O9000005sX7NKAU",
      "businessObjectType": "Quote",        // ← MAPPED SObject name, NOT the node name
      "SalesTransactionName": "ACME-0001",
      "TotalAmount": 1200,
      "SalesTransactionItem": [             // child node → nested array (node name)
        { "id": "0QL...", "businessObjectType": "QuoteLineItem", "Quantity": 3 }
      ]
    }
  ]
}
```

> **⚠ The #1 hydration gotcha (live-verified, v67.0).** `businessObjectType` must
> be the **mapped SObject name** for that node under the chosen mapping (e.g. the
> `SalesTransaction` node maps to `Quote` under `QuoteEntitiesMapping`), **not**
> the context-node name. A payload whose `businessObjectType` is the node name
> hydrates **zero records** — the engine silently returns empty tag results
> (`recordIds: []`) with `isSuccess: true`, which *looks* like a
> permission/definition problem but is really a node-name-vs-SObject-name
> mismatch. The array **key** stays the node name; only `businessObjectType`
> changes. The node→SObject map lives on the mapping's `contextNodeMappings`
> (`contextNodeName` → `sObjectName`).

This shape is easy to get wrong by hand, so **`build_hydration_data.py`** fetches
the definition (one Connect GET), resolves the mapping's node→SObject lookup, and
emits a correctly-shaped skeleton with typed placeholders (empty string / `0` /
`false` / `null` by `dataType`) whose `businessObjectType` is already the mapped
SObject name; you fill in real `id`s and values. Leave `businessObjectType` and
the child-array names as emitted. `--mapping-name` picks the mapping to shape
against (default = the definition's default mapping); `--node NAME` (repeatable)
restricts output to a subtree.

**Hydration sourcing (live-verified).** With only `id` + `businessObjectType` set,
the engine **queries the org itself** for the mapped fields — and does so
**server-side, invisible to the Apex SOQL governor** (0 `Limits.getQueries()`
consumed at build). Any attribute values you *do* include in the payload
**override** the org-queried values for that record. So an id-only payload is the
normal case (hydrate live data); inline values are for what-if / test overrides.

The server-side query also **cascades to child nodes**: a payload with only the
**root** record's `id` (no child arrays) hydrates the parent *and* its children —
the engine walks the mapping's node tree and queries each child SObject itself
(live-verified: one root Quote id → the Quote + all its QuoteLineItems, no child
ids listed). That is why **`build_hydration_data.py --from-record <rootId>`** emits
just `{nodeName: [{"id": <rootId>, "businessObjectType": <mapped SObject>}]}` — no
placeholders, no child arrays — and it is ready to hydrate as-is (pass `--node` to
name the root node when the definition has more than one top-level node). Use the
default skeleton mode only when you want to hand-author attribute *overrides*.

`metadata` = `{contextDefinitionId (11O…), mappingId (11j…)}`. `taggedData`
(Boolean) is included **only** when you pass `--tagged-data` — it is on the
Context MetaData Input rep per internal sources; omit it otherwise (verify live).

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
maps to a `ContextPersistenceEvent`). Body:
`{"contextPersistInput": {"contextId", "targetMappingId (11j…)"}}`.

> **FK caveat.** Reference / lookup **foreign-key** changes are **not reliably
> saved** by persist — scalar field updates are the supported path. `persist_context_instance.py`
> emits this caveat on every run; confirm any FK write directly on the target
> SObject.

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
definition selector).

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

Live (EXPERIMENTAL — required before merging any behavioral change here), against a
scratch org with an active definition (e.g. `RLM_SalesTransactionContext`):

1. `build_hydration_data.py … --out /tmp/records.json`; fill in real ids (values
   optional — id-only hydrates from the org) — or use `--from-record <rootId>
   [--node NAME]` for a ready-to-run id-only payload. Confirm each record's
   `businessObjectType` is the **mapped SObject name** (e.g. `Quote`), which the
   builder emits.
2. `context_session.py … --data-file /tmp/records.json --query` — on a
   **pilot-enabled** org this returns a `contextId` and the hydrated values. On a
   normal org expect `API_DISABLED_FOR_ORG` on the query (see "Live-verified
   reality" above) and/or a not-found `contextId` between calls; fall back to the
   Apex path below to validate hydration.
3. Add `--persist --target-mapping-name <mapping>` → returns a `referenceId`;
   confirm the scalar attributes wrote back to the mapped SObject (note the FK
   caveat). Also pilot/reuse-gated.
4. `list_context_interfaces.py` → lists interfaces; `--interface <name>` → one.
   (This one is **not** gated — a plain Connect GET; verified on scratch + prod.)
5. **Apex validation (the reliable path on a normal org):** run the
   `Context.IndustriesContext` `buildContext` + `leanerQueryTags` snippet from
   "Live-verified reality" above via `sf apex run`. `recordIds` non-empty and real
   `tagValue`s confirm the definition + mapping hydrate; `recordIds:[]` means the
   payload's `businessObjectType` doesn't match the mapping's SObject.

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
