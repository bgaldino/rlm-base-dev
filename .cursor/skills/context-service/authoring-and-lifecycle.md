# Context Service — Authoring & Lifecycle

Read this when deciding **extend vs clone**, reasoning about **activation /
deactivation**, understanding **versioning** and **upgrade/Sync** across a
release, or debugging a lifecycle gotcha.

> **Provenance / pin.** Sourced from `tasks/rlm_context_service.py`,
> `tasks/rlm_extend_stdctx.py`, `docs/references/context-service-utility.md`,
> the `datasets/context_plans/` examples, Core UDD, the Connect OAS, and
> Salesforce Help. **Pinned to Release 262 / API v67.0.** Behaviors below are
> live-confirmed on 262 / v67.0 unless marked *(verify live)* (inferred from
> code/docs, not yet confirmed against a live org).

## The three definition types

| Type | Origin | Suffix / marker | Upgradable via Sync? | Edit? |
|------|--------|-----------------|----------------------|-------|
| **Standard** | Ships OOTB, file-based | `__stdctx` | n/a (is the base) | **No** — extend it |
| **Extended** | Custom layer on a standard base | `inheritedFrom` set | **Yes** — auto-upgrades, preserves mandatory mappings | Yes (additive) |
| **Custom / Cloned** | From scratch (`create: true`) or `clonedFrom` | neither | **No** | Yes |

**Extend, don't clone** (documented best practice): extending preserves the
base's mandatory mappings and keeps **Sync** working across releases; a clone
freezes at its point-in-time copy and must be re-reconciled by hand. Only
create-new when no standard base fits — e.g. `RLM_QuoteDocGenContext`
(`datasets/context_plans/DocGen/`, `"create": true`), which models a Quote →
Line hierarchy that no standard context provides.

## Node vs. attribute vs. tag vs. mapping — the authoring decision

The four building blocks map onto data-model concepts. Grounding in the
**Sales Transaction context** (`SalesTransactionContext__stdctx` → extended
`RLM_SalesTransactionContext`) — the most-used context in Revenue Cloud, and the
one nearly every additive plan in this repo targets:

| Block | Data-model analogue | In Sales Transaction |
|-------|---------------------|----------------------|
| **Node** | an **entity / record level** in a hierarchy | `SalesTransaction` (the header) → `SalesTransactionItem` (the line) → `SalesTransactionItemDetail` → `SalesTrxnItemRateCardEntry` — a real **4-level**, 44-node tree |
| **Attribute** | a **value on that entity** | `SalesTransactionItem` carries **144 attributes** (132 `INPUTOUTPUT`, 9 `INPUT`, 3 `OUTPUT`) |
| **Tag** | the **name a consumer binds by** | every attribute a pricing procedure reads/writes is tagged; the tag name is the seam, not the SObject field |
| **Mapping (rule)** | the **binding to one SObject/field, per lens** | the `SalesTransaction` node binds to **6 different SObjects** across mappings — `Quote` (`QuoteEntitiesMapping`), `Order` (`OrderEntitiesMapping`), `SalesAgreement` (`SalesAgreementEntitiesMapping`), etc. |

### Which do I add?

- **New value on an entity that is already a node → add an *attribute* (+ tag +
  mapping).** This is the overwhelmingly common case. Example: the **RampMode**
  plan adds `RampMode__c` to the *existing* `SalesTransactionItem` node — **no new
  node**. You almost never add a node to Sales Transaction; its entity hierarchy
  already models the whole quote/order/agreement/asset/contract surface.
- **New entity / hierarchy level not yet modeled → add a *node*** (nested via
  `parentNodeName` for a child), **then** its attributes + tags + node/attribute
  mappings. This is the create-new path — e.g. DocGen's `Line` under `Quote`.
  Nodes must be created **parent-first**; depth is capped at **5** (Sales
  Transaction uses 4).
- **Make an existing attribute referenceable by an engine → add a *tag*** on it.
  An untagged attribute is invisible to expression sets / docgen.
- **Populate an attribute from org data → add a *mapping rule*** — **one per lens
  (mapping) you want it hydrated in.** RampMode adds `RampMode__c` twice: to
  `QuoteEntitiesMapping` → `QuoteLineItem.RLM_RampMode__c` **and** to
  `OrderEntitiesMapping` → `OrderItem.RLM_RampMode__c`. Same attribute, two
  lenses, because a quote line and an order line are different SObjects.

### Combinations — what yields *working* functionality

The blocks are independent, so a partial combo is the usual reason a change
"doesn't do anything":

| What you declared | Result |
|-------------------|--------|
| Attribute only | Inert — declared, but never hydrated and not referenceable |
| Attribute + mapping, **no tag** | Hydrated into the cache but **unreachable** by the expression set (no name to bind) |
| Attribute + tag, **no mapping** | Referenceable but **never populated** from data (runtime-input only) |
| **Attribute + tag + mapping (× each lens)** | ✅ Working recipe for *"surface a new field to pricing / docgen"* — what **RampMode** does |
| **Node + its attributes + tags + node-mapping + attribute-mappings** | ✅ Working recipe for *"model a new (child) entity"* — what **DocGen's `Line`** does |

**On the parent-child linkage:** the node **hierarchy** itself lives in Layer 1
(`parentNodeId` / `childNodes`). At the binding layer, traversal from a parent
record to its children is carried by **relationship-typed attributes** (e.g.
`SalesTransactionItemParent` on the item node, whose `parentNodeMappingId` points
back at the parent node mapping) — not by a field on the node-mapping shell. You
do not hand-author those on the standard base; they come with it. When you add a
plain value attribute, you are **not** creating a relationship — just a field
binding.

Standard RC contexts this repo extends (see the `extend_context_*` tasks):
Sales Transaction, Product Discovery, Cart, Billing, Fulfillment Asset,
Collection Plan Segment, Rate Management, Rating Discovery, Contracts, Contracts
Extraction, Asset. **Availability varies by edition** — the foundational ones
(Sales Transaction, Product Discovery) are always present; **Cart** and **plain
Contracts** (non-extraction) are the ones most likely to be absent on a lean
edition and skip. Confirm what a given org actually provisioned with
`list_contexts.py` before assuming a base exists.

**Edition-optional vs. always-present (`allow_skip_if_unavailable`).** Most
`extend_context_*` tasks set `allow_skip_if_unavailable: true` so they no-op
gracefully when the standard base context is not provisioned on the target
edition: Cart, Billing, Fulfillment Asset, Collection Plan Segment, Rate
Management, Rating Discovery, Contracts, Contracts Extraction. Three do **not**
set the flag and will hard-fail if their base is missing:
`extend_context_sales_transaction` and `extend_context_product_discovery` (both
foundational — always present, so the flag is unnecessary) and
`extend_context_asset` (`cumulusci.yml:698`). The Asset omission is an
**asymmetry**: Asset availability varies by edition, so if an Asset extend fails
on a lean edition, that is the likely cause — add `allow_skip_if_unavailable:
true` there to match the others, or gate the task with a `when:` edition guard.
This bites only on lean editions that lack an Asset context — on editions where
Asset is provisioned the omission is harmless.

## Task sequence (extend → apply → deploy)

The typical order when standing up context configuration on an org:

1. **`extend_context_*`** (live, Connect/SObject REST) — establish the extended
   layer on each standard base first. Run via the **`extend_context_definitions`**
   flow (`cumulusci.yml:3794`).
2. **`apply_context_*` / `manage_context_definition`** (live) — apply this repo's
   additive plans (attributes, mappings, tags, traversal hydration) onto those
   bases. These are standalone tasks, not currently bundled into a flow.
3. **`deploy_context_definitions`** (MDAPI, `cumulusci.yml:925`) — deploy the
   file-based `.contextDefinition` metadata under
   `force-app/main/default/contextDefinitions/`. Also a **standalone task**, not
   in a flow. Note: activation state and default-mapping designation are **not
   packageable**, so an MDAPI deploy still needs a follow-up activation step.

## Activation & deactivation

- **`IsActive` is version-level.** One version active at a time; a version needs
  a **default mapping** to activate. Each extended definition exposes exactly one
  active `ContextDefinitionVersion`.
- **In-place by default — but only for *inserts*.** `manage_context_definition`
  and `apply_context_*` run with `deactivate_before: false` (`rlm_context_service.py`).
  **Adding a new artifact** (POST a node, attribute, or tag) applies **without** a
  deactivate cycle on an active version. But **modifying or deleting an *existing*
  artifact is blocked while the version is active** (`RECORD_UPDATE_FAILED`
  "Cannot modify/delete an active context definition") — this covers an
  `IsTransient` PATCH, an `isDefault` mapping PATCH, and any DELETE. The platform
  rule is literal in that error text: **insert-new = OK on active;
  modify/delete-existing = deactivate first.** So an *additive* plan (the normal
  case) needs no deactivate; a plan that flips `isTransient` or re-points the
  default mapping does. Pass `deactivate_before: true` for those, or use
  `mutate_context.py --deactivate-first` for a one-off.
- **Deactivation is blocked while an active consumer references the definition**
  — ExpressionSet, ContextRules, PricingActionParameters, or a decision table.
  The deactivate PATCH fails with **`RECORD_UPDATE_FAILED`**; a definition with
  no active consumer deactivates cleanly. **Only *active* consumers block** —
  deactivating the consumer first unblocks the definition. There is **no API/SOQL
  that names the blocking record**, so trace consumers by type (below).
  Deactivating a definition a **pricing procedure** uses **breaks that
  procedure** — unlink/deactivate consumers first, in dependency order.
- **Activation requires a default mapping.** A version will not flip active
  unless one `ContextMapping` is flagged `isDefault:true`; otherwise the
  `isActive:"true"` PATCH fails with **`DATA_MAPPING_NOT_FOUND`**. Set it with a
  `PATCH .../context-mappings {"contextMappings":[{"contextMappingId":…,
  "isDefault":"true","name":…}]}` **before** activating — this is what
  `ExtendStandardContext._update_context_mappings` does, and what the standalone
  `apply_context_plan.py --default-mapping <name>` / `_ensure_default_mapping`
  do in the create + activate flow. The designation is **not packageable** (must
  be set via API/UI after an MDAPI deploy).

### Debugging a blocked deactivation

When a deactivate fails, an active consumer still references the definition.
To find it, look at each consumer type (deep SOQL is out of scope here — start
with the likely one for your change):

- **ExpressionSet / pricing procedure** — the most common blocker. A pricing
  procedure binds to the context via its tags; deactivating the definition
  breaks the procedure. See `.cursor/skills/pricing-wiring/SKILL.md` and
  `.cursor/skills/expression-sets/SKILL.md` to trace which expression set
  consumes the context, then deactivate/unlink it first.
- **ContextRules / decision table** — a decision table whose input maps to a
  context node, or ContextRules referencing it.
- **PricingActionParameters** — pricing actions that name the context.

Fix order: unlink/deactivate consumers in dependency order (consumer → context),
then deactivate the definition. Reactivate the definition before re-linking.

## Versioning

**The model supports multiple retained versions — one active at a time.**
`ContextDefinitionVersion` is a **1-to-many child** of `ContextDefinition`
(`contextDefinitionVersions` is typed `ContextDefinitionVersion[]` in the MDAPI;
the SObject exposes a `ContextDefinitionVersions` child relationship). The
current-vs-retained distinction is carried by **`IsActive`** (plus effective
dating via **`StartDate` / `EndDate`**) — there is **no `IsLatest` and no
`Status` field**, so do not assert one. *(Confirmed from the MDAPI type and the
`ContextDefinitionVersion` SObject field list, v67.0.)*

**What this repo's apply path does:** an additive Connect PATCH (`apply_context_*`
/ `manage_context_definition`) **bumps `VersionNumber` in place on the single
active version** — it does *not* mint a new version record (the mutated row's
`CreatedDate` precedes its `LastModifiedDate`; each extended `RLM_*` definition
carries exactly one `ContextDefinitionVersion` row). Standard `__stdctx`
definitions expose **no queryable `ContextDefinitionVersion` rows** — only the
extended `RLM_*` layer does.

**Do not claim prior versions are deleted.** Observing one row reflects the
additive-PATCH path minting no new rows — **not** a platform guarantee that
history is discarded. The schema allows many rows; whether **Sync/upgrade** or an
MDAPI deploy of a new `versionNumber` creates additional (retained, inactive)
version records is **unverified** — treat multi-version history as *possible per
the schema* and re-verify live before relying on either rollback or its absence.
There is **no "save as new version" verb** in the Connect API (public REST
reference lists only create/clone/extend, PATCH-by-id, and Upgrade); the only
version-crossing operation is Upgrade/Sync (below).

## Upgrade / Sync (across a release)

- `PATCH /services/data/v67.0/connect/context-definitions/upgrades` with
  `upgradeMode` ∈ **`Sync`** (merge platform changes, preserve custom artifacts),
  **`Preview`** (report only), **`Override`** (**destructive** — deletes custom
  artifacts, resets to the standard base). One definition at a time.
- **Prefer `Sync`.** Use `Preview` to see the delta first. Never run `Override`
  expecting it to be non-destructive.
- **262 upgrade note:** a **BillingContext duplicate-mapping cleanup** is
  required before Sync succeeds on the Billing context — resolve the duplicate
  mapping, then Sync.
- Sandbox → prod: validate the upgrade in a sandbox (Preview, then Sync), confirm
  consumers still resolve, then repeat in prod.

## Hydration, persistence & the mapping intents

A context definition is a **schema**; at runtime an engine (Pricing/BRE/DRO/
Billing) creates a **context instance** and moves data between the mapped
SObjects and the instance's attribute cache. Which direction the data flows is
governed by the mapping's **`intents`** (Connect `contextMappings[].intents`, a
`List<String>`; MDAPI `contextMappingIntents[].mappingIntent`, since v61) **and**
each attribute's **`fieldType`**:

| Intent | Direction | Meaning |
|--------|-----------|---------|
| **HYDRATION** | source → cache (read) | Run SOQL against the mapped SObject/field (honoring FLS) to **load** attribute values into the instance ("load cache from a data source"). |
| **PERSISTENCE** | cache → sink (write-back) | **Write** computed attribute values back out to the mapped SObject ("load the *sink objects* from cache"). The persist API takes a `targetMappingId` — the **same** mapping used for hydration — and commits the record tree via the **Composite Graph API** (`ALL_OR_NONE`). |
| **ASSOCIATION** | link | Link records/definitions **without** validating a DB relationship and **without hydrating** (the consuming service supplies hydration). The *most permissive* shape — the only intent that allows many-node→one-SObject and cross-node mappings. This is the intent on **cross-context / definition-to-definition** links (`SalesTransactionToAssetMapping`, `ContractToSalesTxnMapping`), which carry **zero node mappings**. |
| **TRANSLATION** | transform | Re-express a hydrated context through **another target mapping** (context→context / SObject-graph reshaping). Invoked via a `translate(contextId, mappingId)` operation, analogous to persist; runs in the SObject-graph persistence subsystem; SObject-mapping-only (not DMOs). |

**One binding record, two directions — there is NO separate persistence
structure.** `ContextAttrHydrationDetail` (`sObjectDomain` + `queryAttribute`) is
the **single** object that describes an attribute↔SObject.field binding, used for
**both** read and write. There is no `ContextAttrPersistenceDetail` /
`persistenceDetailList` — confirmed against the MDAPI `ContextDefinition` type and
the live GET (only `contextAttrHydrationDetailList` +
`contextAttrContextHydrationDetailList`, nothing persistence-specific). Persist
reuses the same bindings, run backward.

**Direction is gated by intent AND `fieldType`:**

| `fieldType` | On HYDRATION | On PERSISTENCE |
|-------------|--------------|----------------|
| `INPUT` | read into cache | — (never written) |
| `INPUTOUTPUT` | read into cache | written back |
| `OUTPUT` | — | written back (computed) |
| `AGGREGATE` | — | computed/rollup (not a plain field write) |

`isTransient: true` is **skipped on persist** regardless of `fieldType` (the
explicit per-attribute opt-out of write-back). `trace_context.py` classifies each
binding using exactly this table — `->` hydrate, `<-` persist, `<->` both.

- **The intent is a *gate*, not a config payload.** Adding/removing an intent
  enables/disables that operation for the mapping (a read-only context ships
  `intents:["HYDRATION"]`; adding `"PERSISTENCE"` is what enables the persist
  API). Multiple intents coexist — the 8 entity mappings on Sales Transaction
  carry all four; the 6 link mappings carry `["ASSOCIATION"]` only. The intent
  also gates which mapping *shapes* are legal at design time (ASSOCIATION allows
  many:1 / cross-node; PERSISTENCE and TRANSLATION are one-to-one only).
- **`writeThroughTags` is a *runtime* API, not a definition/mapping field**
  (`PATCH /connect/contexts/write-through-tags`, and an Apex
  `context.writeThroughTags(...)`). It writes attribute values **by tag name**
  into a live context instance. A context is read-only because its mapping
  **lacks the PERSISTENCE intent** — not because a `writeThroughTags` field is
  empty.
- **`ContextAttrHydrationDetail`** is the hydration query hop (≤1 per attribute
  mapping). Simple SOBJECT hydration is one detail (`sObjectDomain` +
  `queryAttribute`); a **relationship traversal** chains a parent detail → child
  detail (`parentDetailId`/`childDetails`) and must be built via **SObject REST**,
  not the Connect PATCH.
- **Note — `mappedField` is empty on inherited/standard definitions.** The real
  source field on an attribute mapping lives in
  `contextAttrHydrationDetailList[].queryAttribute` (+ `sObjectDomain`), **not**
  in a `mappedField` column (which is blank on everything inherited from a
  standard base). Any field↔tag tooling must read the hydration detail; a join on
  `mappedField` returns zero rows. This is what `trace_context.py` and `_model.py`
  read.
- **Hydration silently no-ops when the mapped SObject field is absent** — the
  big gotcha. Writing a `ContextAttrHydrationDetail` — via either the inline
  Connect node-mapping PATCH **or** a direct `ContextAttrHydrationDetail`
  SObject-REST POST — returns `success:true` with an id **but persists nothing**
  when the target `sObjectField` does not exist on the org. The GET then reports
  `hasHydrationDetail:false` even though the write "succeeded", and this happens
  identically whether the write came from the standalone scripts or the CCI task
  (it is a platform behavior, not a mapping-code bug). **Lesson:** a "hydration
  didn't take" failure is almost always a **missing field / build-order** problem
  — query `FieldDefinition` for the mapped field before blaming the mapping.

## Gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| `JSON_PARSER_ERROR` on create | `primaryDomainObject` / `primaryObject` in the create payload — **or** a bare-date `startDate` | Remove the domain-object key; make `startDate` an **xsd:dateTime** (`"2020-01-01T00:00:00.000Z"`), not `"2020-01-01"` |
| `DATA_MAPPING_NOT_FOUND` on activate | No mapping is flagged `isDefault:true` on the version | PATCH the default mapping before `isActive:"true"` (see *Activation & deactivation*); with the scripts, pass `--default-mapping <name>` or set `defaultMapping` in the plan |
| Hydration write "succeeds" but no rows persist | Mapped `sObjectField` does not exist on the org (phantom no-op) | Deploy the field / fix build order; verify with `FieldDefinition` (see *Hydration, persistence & the mapping intents*) |
| New field binds (data-layer rows exist) but the Connect GET / trace / Setup picker shows **"(no field bound)"** / `contextAttrHydrationDetailList: []` | **Running user lacks FLS on the mapped field.** The bind *persists* on the active version in place, but the **Connect aggregated GET honors FLS** and filters it out (live-verified v67.0). This — not a version recompile — is what the Setup-UI "deactivate/activate + refresh before the new field appears" behavior actually is | **Grant FLS** (add the field to the permission set that already ships the context's fields, with read) → it surfaces **immediately, no cycle, no definition change.** A deactivate/activate cycle does **not** fix a missing-FLS binding, so don't chase version cycles — FLS is the actual lever. *(Whether an FLS-hidden binding also affects hydration at engine runtime, or is purely a read-view artifact, is worth confirming on the target org if the field is engine-consumed — but it is moot in practice once FLS is granted.)* |
| Hydration disappears after a re-run | Connect PATCH `isDeleteExistingHydrationDetail` defaults **true** | Re-send hydration, or apply traversal hydration via SObject REST |
| `mappedContextDefinitionName` never sets | Connect PATCH silently ignores it | Set via **SObject REST** |
| Relationship traversal rejected on PATCH | Connect does not accept traversals | Use **SObject REST** (`childSObject`/`childSObjectField`) |
| Deactivate fails | An active consumer (ExpressionSet/ContextRules/PricingActionParameters/DecisionTable) references it | Unlink/deactivate consumers first |
| Pricing procedure breaks | Its context definition was deactivated | Reactivate; don't deactivate a consumed definition |
| **`RECORD_UPDATE_FAILED` "Cannot modify/delete an active context definition"** on a delete **or an in-place edit** | **The version is active.** The platform blocks **modifying or deleting an *existing* artifact** while active — a DELETE (whole-definition down to a single custom `__c` tag), an `IsTransient` PATCH, or an `isDefault` mapping PATCH (all live-verified v67.0). **Inserting a new** node/attribute/tag is **allowed** on active — the asymmetry is *insert-new* vs *modify/delete-existing*, not *add* vs *delete* | **Deactivate first, then edit/delete.** `delete_context.py --deactivate-first` (delete) or `mutate_context.py --deactivate-first --reactivate` (edit) does this in one run; `manage_context_definition -o deactivate_before true` for a plan that edits existing artifacts |
| `TransactionType` mapping change ignored | Inherited from the standard base; the task skips it | Leave it; it comes from the base |
| Orphan definition after a failed create | Payload-create has **no full rollback** on partial failure | Inspect with `describe_context.py`; delete/clean up the orphan before retrying |
| Context tag rejected / collides | A tag equals a decision table's label/API name | Rename the tag |
| **`DUPLICATE_VALUE` "Tag name already exists for this definition"** on a tag POST | **Tag names are unique per *definition*, not per attribute** (live-verified v67.0) — the same name cannot be used on two different attributes, even as an intended shared alias | Pick a distinct name. (A bare tag name is therefore a globally unambiguous handle for an ES; that 1:1 name→attribute map is the whole point) |
| Definition `name` rejected | Spaces / special chars in `name` | Alphanumeric `name`; use a separate DisplayName |
| **`INVALID_API_INPUT` "the custom artifact name … must have an '\_\_c' suffix in an extended context definition"** at INSERT (POST of a node/attribute/tag on an extended base) | The `__c` suffix is **platform-enforced at creation on a standard/extended base**, not just a downstream/naming nicety — a suffix-less custom artifact is **rejected outright** | Add `__c` to the custom artifact name. The offline validator errors on this for non-create plans, so it is caught before you hit the API |

## See also

- `data-model-and-api.md` — object model, enums, endpoint split, plan format,
  limits, MDAPI.
- `SKILL.md` — Quick Rules, DO NOT, task/script routing.
- `docs/references/context-service-utility.md` — `manage_context_definition`
  options.
