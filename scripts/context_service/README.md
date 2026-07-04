# Context Service helper scripts

Tooling for Salesforce Revenue Cloud **Context Service**, covering both halves of
the lifecycle: **design-time** Context *Definitions* (author / inspect / validate /
apply / delete) **and** the **runtime** context *instance* (hydrate from records →
query/inspect → persist back to SObjects). These complement the CCI tasks
(`apply_context_*`, `extend_context_*`, `manage_context_definition`,
`deploy_context_definitions`) with the read/inspect/validate and runtime-execution
work that does not fit the "apply-a-plan-to-an-org" task mold.

Full guidance lives in the **context-service skill**:
`.cursor/skills/context-service/SKILL.md` (+ `data-model-and-api.md`,
`authoring-and-lifecycle.md`, `runtime-and-persistence.md`).

**How these fit the lifecycle** (what to reach for, and when):

| Lifecycle stage | Production path | These helpers |
|-----------------|-----------------|---------------|
| **Author / apply / deploy** a definition | CCI tasks (`manage_context_definition`, `extend_context_*`, `deploy_context_definitions`) | `apply_context_plan.py`, `mutate_context.py`, `delete_context.py` — EXPERIMENTAL mirrors, not build-critical |
| **Inspect / validate / diff / export** a definition | — | the read-only design-time scripts below (safe anytime) |
| **Run** a context *instance* (hydrate → query → persist) | — (no build task; runtime is not part of org setup) | the runtime scripts below — EXPERIMENTAL / verify-live, for debugging & validating hydration |

So: the CCI tasks own the build; the **read-only** scripts are always safe; the
**EXPERIMENTAL** ones (design mutators + all runtime scripts) are for
exploration/validation, not the setup path.

**Design-time (Context Definitions):**

| Script | Org? | Purpose |
|--------|------|---------|
| `validate_context_plan.py` | No (offline) | Lint this repo's context **plan JSON** (`datasets/context_plans/`). |
| `list_contexts.py` | Read-only | List context definitions in an org. |
| `describe_context.py` | Read-only | Pretty-print one definition: version → nodes → attrs → mappings → hydration. |
| `trace_context.py` | Read-only | Trace how SObject fields link to tags/attributes (hydration) and back (persistence); find unmapped attributes. |
| `diff_context.py` | Read-only | Diff a definition org-vs-org or plan-vs-org (drift): added / removed / changed. |
| `patch_context.py` | Read-only | Extract a diff into an applicable **plan-JSON patch** (adds & updates; never mutates). |
| `export_context.py` | Read-only | Serialize a live definition back into repo **plan JSON** (round-trips with the validator). |
| `apply_context_plan.py` | **Mutates** | Apply an additive plan (or create a new definition) — EXPERIMENTAL mirror of `manage_context_definition`. |
| `delete_context.py` | **Destructive** | Deactivate (default) or hard-delete a definition / custom artifacts — EXPERIMENTAL, `--confirm-delete` required. |
| `mutate_context.py` | **Mutates** | One granular in-place edit (`--set-transient` / `--set-default-mapping` / `--add-tag` / `--remove-tag`) — EXPERIMENTAL, `--confirm` required. |

**Runtime (context instances — EXPERIMENTAL / verify-live; see
`runtime-and-persistence.md`):**

| Script | Org? | Purpose |
|--------|------|---------|
| `build_hydration_data.py` | Read-only | Build the nested `data` hydration payload for a definition — fillable **skeleton**, or `--from-record <id>` for a ready-to-run **id-only** payload (parent + children hydrate server-side). |
| `context_session.py` | **Mutates** | **Primary runtime entry point** — one process: create → update-attr/write-tag → query → persist → delete. |
| `create_context_instance.py` | **Mutates** | `POST /connect/contexts` — hydrate an instance; returns the Context Info (`--id-only` for `$(...)` capture). |
| `query_context_instance.py` | Read-only | `query-record` (flatten + decode compound) / `query-tags[-leaner]` against a live `contextId`. |
| `persist_context_instance.py` | **Mutates** | `persist-records` — write attribute values back to a target mapping's SObjects (FK caveat). |
| `delete_context_instance.py` | **Mutates** | Evict one instance, or `--clear-schema-cache` for a definition (runtime cache, not the definition). |
| `list_context_interfaces.py` | Read-only | List (or GET one) context **definition interface** — not tied to a specific definition. |

**Shared modules (imported, not run directly):**

| Module | Purpose |
|--------|---------|
| `_client.py` | Shared `sf api request rest` wrapper. |
| `_model.py` | GET/plan → comparable-model normalizer + `model_to_plan` serializer. |
| `_resolve.py` | Neutral read-only definition/mapping resolution (developerName → id, default/named mapping) — shared by the runtime path. |
| `_runtime.py` | Runtime client, `RuntimeSession`, pure body-builders + query-result shaping + hydration-skeleton builder. |
| `_runtime_cli.py` | Shared argparse / data-parsing / mapping-resolution helpers for the runtime CLIs. |
| `_apply.py` / `_payload.py` / `_endpoints.py` / `_delete.py` / `_mutate.py` | Shared apply/delete/mutate orchestration, pure payload lib, REST paths. |

## `validate_context_plan.py` — offline plan linter

Static check of the plan JSON consumed by `manage_context_definition` /
`ExtendStandardContext`. **No org, no network.** Modeled on
`scripts/validate_sfdmu_v5_datasets.py`.

```bash
# canonical: validate the 6 active (non-archive) plans
python scripts/context_service/validate_context_plan.py

# explicit paths
python scripts/context_service/validate_context_plan.py \
  datasets/context_plans/DocGen/manifest.json

# include the archive/ plans; treat warnings as failures
python scripts/context_service/validate_context_plan.py --include-archive --strict
```

Discovery skips `datasets/context_plans/archive/` unless `--include-archive` is
passed. Exit code is non-zero if any **ERROR** is found (or any warning under
`--strict`). The 6 active plans are known-good (0 errors, 0 warnings).

Checks: JSON well-formedness; manifest → plan-file resolution; canonical
`dataType`/`fieldType` enums (Core UDD, v67.0); required keys on
attrs/nodes/rules/tags; `mappingType ∈ {SOBJECT, CONTEXT}` with matching keys;
guardrail limits (nodes ≤30, attrs/node ≤50, total attrs ≤250, depth ≤5, and
distinct referenced context definitions ≤2 — all ERROR); tag↔attribute
alignment; `primaryDomainObject`/`primaryObject` → error; all-traversal rules →
info. Tags per node has a recommended guideline (≤10) surfaced as **INFO only**
— a shipped plan (DocGen) exceeds it and works, so it never fails the build.

### `__c`-suffix rule (scoped, to avoid false positives)

The `__c` convention only distinguishes **custom artifacts added to a
standard/extended base** from inherited standard names. So the suffix check is
an **ERROR** only when the plan targets a standard/extended base (no
`create: true`), and it is **skipped entirely for create-new custom
definitions** (`create: true`), whose names are wholly author-chosen and collide
with nothing inherited (e.g. `RLM_QuoteDocGenContext`'s `AccountName`,
`GrandTotal`). Definition `developerName`s are always exempt — those are
legitimately `RLM_*Context`, not `__c`.

## `list_contexts.py` / `describe_context.py` — read-only inspectors

```bash
python scripts/context_service/list_contexts.py --target-org rlm-base__beta
python scripts/context_service/list_contexts.py --target-org rlm-base__beta --json

python scripts/context_service/describe_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext
python scripts/context_service/describe_context.py --target-org rlm-base__beta \
  --id 11Og... --json
```

## `trace_context.py` — field↔tag↔attribute tracer (read-only)

Answers the two questions `describe_context.py` can't: **how does a specific
SObject field get *hydrated* into the context** (field → attribute/tag), and **how
does a context attribute/tag get *persisted* back to a field** (the same binding,
run backward). Context Service has **no separate persistence structure** —
`ContextAttrHydrationDetail` (`sObjectDomain` + `queryAttribute`) is the single
binding used for both read and write; direction is gated by the mapping's
`intents` (`HYDRATION`/`PERSISTENCE`) and the attribute's `fieldType`
(`INPUT` read-only / `OUTPUT` write-only / `INPUTOUTPUT` both / `AGGREGATE`
computed; `isTransient` skips persist). The trace is a pure join on
`contextAttributeId`, so the same abstract attribute resolves to a *different*
field per mapping (the reuse-lens: `Quote.AccountId` in `QuoteEntitiesMapping`,
`Order.AccountId` in `OrderEntitiesMapping`).

```bash
# everything that touches a field, across all lenses (hydration + persistence)
python scripts/context_service/trace_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --field RLM_RampMode__c

# every field a tag reads/writes; scope to one lens with --mapping
python scripts/context_service/trace_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --tag RampMode__c \
  --mapping QuoteEntitiesMapping

# one attribute (node.attr or bare name)
python scripts/context_service/trace_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext \
  --attribute SalesTransactionItem.RampMode__c

# gaps: tagged-but-unbound (never populated), bound-but-untagged (unreachable by
# an ES), inert (neither). Drop --mapping for the never-anywhere signal.
python scripts/context_service/trace_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --unmapped

# no selector → per-mapping (lens) binding summary; --json on any mode
python scripts/context_service/trace_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext
```

Direction symbols read field-relative: `->` the field hydrates the context, `<-`
the context persists the field, `<->` both (an `INPUTOUTPUT` attribute in a
mapping carrying both intents), `(agg)` computed, `(x)` no active direction.
`--unmapped` scoped to one `--mapping` reports *per that lens* (an attribute bound
in another lens shows as "not populated by this lens" — expected, not a defect);
unscoped it is the true never-populated-anywhere signal.

**Relationship traversals show the full chain.** When an attribute hydrates
across a lookup (the GET nests the hop under `childDetails`), the trace renders
the whole path — `QuoteLineItem.Product2 -> Product2.ProductCode` — so you see
both the intermediate lookup and the **terminal source field**. `--field` matches
on *any* hop, so `--field ProductCode` finds a traversal whose terminal field is
`Product2.ProductCode`, and `--field Product2` finds the same via the lookup hop.
Context-sourced attributes (from `contextAttrContextHydrationDetailList`, another
context rather than an SObject field) render as `context:<attr>` so they are not
mislabeled unbound.

### The three selectors match on different axes (not interchangeable)

The selectors are *not* three spellings of one lookup — each keys on a different
thing, so the same string can return different result sets:

| Selector | Matches on | Match rule | Answers |
|----------|-----------|-----------|---------|
| `--field X` | **SObject field** names, at *any* traversal hop | case-insensitive substring of `Object.field` | reverse: "given a field, which attributes/tags read/write it" |
| `--tag X` | **tag** names | case-insensitive **substring** | forward: "which tagged attributes (and their field bindings) carry this tag" |
| `--attribute X` | **attribute** name | `node.attr` or bare `attr`, **exact** (ci) | forward, keyed on the attribute itself (its tag is incidental) |

The consequence to expect: `--field ProductCode` and `--tag ProductCode` overlap
but are **not** equal. `--field` returns only field-bound rows named `ProductCode`
(e.g. `... -> Product2.ProductCode`). `--tag`, being a *substring* over tag names,
also matches `ItemProductCode`, `FulfillmentItemProductCode__std`, and
`RootItemProductCode` — and surfaces lenses where the attribute carries the tag
but binds **no field** (`(no field bound)`), including transient/computed
attributes that never read a `ProductCode` field at all. For the exact forward
mirror of a `--field` result, prefer `--attribute Node.Attr` (exact) over the
fuzzy `--tag`. The substring behavior on `--tag`/`--field` is deliberate — it lets
`--tag Account` find every account tag — so it is kept, not "fixed."

## `diff_context.py` — drift diff (read-only)

Compares one definition (or all) between two orgs, or a repo plan against an
org, and reports **added / removed / changed** nodes, attributes, mappings,
hydration, and tags. Both sides normalize through `_model.py` to a common shape.

The **target org is always the examined (right) side**; the baseline is the
source org or the plan on the left.

```bash
# org-vs-org (same developerName on both orgs)
python scripts/context_service/diff_context.py \
  --source-org rlm-base__A --target-org rlm-base__B \
  --developer-name RLM_SalesTransactionContext

# org-vs-org with differently-named defs across the two orgs
python scripts/context_service/diff_context.py \
  --source-org rlm-base__A --source-dev-name RLM_FooContext \
  --target-org rlm-base__B --target-dev-name RLM_BarContext

# plan-vs-org drift (directional — see caveat)
python scripts/context_service/diff_context.py \
  --target-org rlm-base__beta \
  --plan-file datasets/context_plans/RampMode/manifest.json

python scripts/context_service/diff_context.py ... --json   # structured output
```

**plan-vs-org is directional.** Repo plans are *additive* (they declare only
what they add onto a standard/extended base), so `+ (only in org)` items are
usually **inherited** base artifacts, not drift; `- (only in plan)` items are
the real signal that the plan is unapplied. CONTEXT-to-CONTEXT sources are
compared by raw `mappedContextDefinitionId` (not resolved to a developerName) —
confirm an apparent ID mismatch with `describe_context.py`.

## `patch_context.py` — extract a diff into an applicable patch (read-only)

> **Repo tooling, not a Salesforce-native feature.** Salesforce has no
> diff/patch primitive for Context Definitions and no context *import* format.
> This is our logic on top of standard platform APIs (it *reads* via Connect /
> SObject REST; a patch *applies* through our CCI task). A patch is only as
> correct as our normalizer + serializer — there is no platform round-trip
> guarantee — which is why the workflow lints every patch before applying and
> flags (rather than silently emits) CONTEXT-to-CONTEXT / traversal reversals.
> The only platform-native reconciliation is `upgradeMode: Preview`, and that
> only reconciles an *extended* definition against its *standard base* — not two
> orgs or an org vs a repo plan.

Computes the same diff, then serializes the **delta** as repo **plan JSON** —
the additive format `manage_context_definition` consumes and
`validate_context_plan.py` lints. It **never mutates an org**; it writes/prints a
patch for you to review, lint, then apply yourself.

Why plan JSON (not a Connect payload or MDAPI `.contextDefinition`)? Connect /
SObject REST is the *runtime apply* path, but that write orchestration lives in
the CCI task (idempotency, dry-run, traversal hydration, verification) and needs
`access_token` handling the repo forbids on the `sf` CLI — so the patch targets
the task's *input*, not the wire protocol. MDAPI deploys a definition as one
atomic unit (no per-artifact granularity, can't set activation) — so a plan-JSON
delta is the granular, applicable-anywhere artifact. A patch therefore
round-trips: `patch_context.py` → `validate_context_plan.py` →
`cci task run manage_context_definition`.

```bash
# plan is truth → patch brings the org up to the plan (default --apply-to org)
python scripts/context_service/patch_context.py \
  --plan-file datasets/context_plans/RampMode/manifest.json \
  --target-org rlm-base__beta --out /tmp/ramp_patch.json

# source org is truth → patch makes the target org match it
python scripts/context_service/patch_context.py \
  --source-org rlm-base__A --target-org rlm-base__B \
  --developer-name RLM_SalesTransactionContext --out /tmp/patch.json

# org is truth → fold the org's *custom* (__c) state back into the repo plan
python scripts/context_service/patch_context.py \
  --plan-file datasets/context_plans/RampMode/manifest.json \
  --target-org rlm-base__beta --apply-to plan > /tmp/plan.json
#   add --include-inherited to also emit inherited (non-__c) artifacts
```

**v1 scope — adds & updates only.** The plan format and the CCI task are
additive (no per-artifact delete directive), so artifacts present in the
*target* but absent from the *source* (candidate deletions) are **reported, not
emitted** — removing them is a manual unlink/deactivate step (a documented
followup). CONTEXT-to-CONTEXT and multi-hop traversal reversals are best-effort
and flagged as `_caveats` / `_todo` in the output (both `_`-prefixed keys are
ignored by the task and the validator, so the patch stays consumable). Always
lint an emitted patch before applying.

## `export_context.py` — serialize a live definition to plan JSON (read-only)

Fetches one definition and emits it as repo **plan JSON** — the inverse of
applying a plan. Snapshot an org's config into source control, or seed a new
plan from a hand-configured org. Same "repo tooling, not a Salesforce-native
export" caveat as `patch_context.py`: correctness rests on our normalizer +
serializer, so **lint the output** and verify flagged reversals.

```bash
# Whole definition (a snapshot — includes inherited standard artifacts)
python scripts/context_service/export_context.py \
  --target-org rlm-base__beta --developer-name RLM_SalesTransactionContext \
  --out /tmp/export.json

# Just the custom (__c) layer — the repo-authoring plan for an extended base
python scripts/context_service/export_context.py \
  --target-org rlm-base__beta --developer-name RLM_SalesTransactionContext \
  --custom-only --out /tmp/plan.json
```

**Use `--custom-only` when seeding a repo plan.** A *full* export of a
standard/extended base includes every inherited standard artifact, and the
validator's `__c` rule (correctly) errors on those — a full export is a
*snapshot*, not an apply-ready extend plan. `--custom-only` drops the inherited
layer, leaving the custom artifacts a repo plan should own; that output lints
clean and round-trips. CONTEXT-to-CONTEXT and multi-hop traversal reversals are
flagged as `_caveats` / `_todo` (both `_`-prefixed, ignored by the task and
validator), not fabricated.

## `delete_context.py` — deactivate / hard-delete (EXPERIMENTAL, destructive)

> **No production delete task exists.** The supported lifecycle verb is
> *deactivation* (soft-disable), which this script does **by default**. A hard
> delete is **strictly opt-in** (`--confirm-delete`) and cannot be undone. Not
> wired into any CCI flow. Orchestration lives in `_delete.py`
> (`ContextDeleter`, reverse-order sequencer).

```bash
# safe default: deactivate only (reversible)
python scripts/context_service/delete_context.py --target-org rlm-base__beta \
  --developer-name RLM_QuoteDocGenContext

# preview a custom teardown (no mutation — delete modes without --confirm-delete
# only print the ordered plan)
python scripts/context_service/delete_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --custom-teardown

# strip every custom (__c) artifact, deactivating first (deletes are blocked while active)
python scripts/context_service/delete_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --custom-teardown \
  --deactivate-first --confirm-delete

# one custom attribute + its dependent tag/attr-mapping
python scripts/context_service/delete_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext \
  --delete-artifact attribute SalesTransactionItem.RampMode__c \
  --cascade --deactivate-first --confirm-delete

# whole definition (platform cascade)
python scripts/context_service/delete_context.py --target-org rlm-base__beta \
  --developer-name RLM_QuoteDocGenContext --delete-definition --confirm-delete
```

Three pre-flight guards refuse a bad delete up front (instead of surfacing an
opaque platform error mid-teardown), all **live-verified** on v67.0:

- **`baseReference` (inheritance) guard** — an inherited standard-base artifact
  (`baseReference` set) cannot be deleted; only custom (`baseReference: None`,
  the `__c` layer) artifacts are removable. The script refuses the target *and*
  refuses a cascade that would touch an inherited dependent.
- **Active-state guard** — the platform blocks **every** structural delete
  (whole-definition down to a single custom tag) while the version is active
  (`RECORD_UPDATE_FAILED`: "Cannot modify/delete an active context definition").
  Confirmed live: a custom leaf-tag DELETE was blocked while active and
  succeeded once deactivated. `--deactivate-first` deactivates then deletes in
  one run; otherwise an active definition is refused. (Note the asymmetry:
  *adds* apply in-place on an active version, but *deletes* do not.)
- **Dependents guard** — `--delete-artifact` refuses a target that still has
  custom dependents unless `--cascade` is given (then they delete first, in
  child→parent order).

Reverse-order teardown mirrors `_endpoints`: `attribute-mappings → node-mappings
→ mappings`, then `tags → attributes → nodes`; the whole-definition delete is a
single DELETE that the platform cascades. (`_client.py` note: `sf api request
rest` rejects a bodiless mutating verb — DELETE included — so the transport
pipes an empty `-b -` body on every non-GET/HEAD request.)

## `mutate_context.py` — granular in-place edit (EXPERIMENTAL)

> **Prefer a plan for build work.** The production path for context changes is a
> plan applied by `manage_context_definition` / `apply_context_plan.py`. This is
> a *granular* companion for a one-off edit to an **existing** definition, not a
> build step; orchestration lives in `_mutate.py` (`ContextMutator`).

Four mutually-exclusive ops; previews unless `--confirm`:

```bash
# flip a custom attribute's IsTransient (a modify → deactivate first, reactivate after)
python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext \
  --set-transient SalesTransactionItem.RampMode__c true \
  --deactivate-first --reactivate --confirm

# re-designate the default context mapping (a modify → deactivate first)
python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
  --developer-name RLM_QuoteDocGenContext \
  --set-default-mapping QuoteEntitiesMapping --deactivate-first --reactivate --confirm

# add a custom tag alias to an attribute (an insert → runs on the active version)
python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext \
  --add-tag SalesTransactionItem.RampMode__c RampModeAlias__c --confirm

# remove a custom tag (a delete → deactivate first)
python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext \
  --remove-tag RampModeAlias__c --deactivate-first --reactivate --confirm
```

Two op-specific guards, both **live-verified** on v67.0:

- **Inheritance guard (per-op).** `--set-transient` and `--remove-tag` refuse an
  inherited (standard-base) artifact — the platform blocks editing/deleting a
  base artifact in place. `--set-default-mapping` and `--add-tag` **do** target
  inherited artifacts legitimately (the standard default mapping is inherited; a
  custom `__c` tag attaches fine to an inherited attribute).
- **Active-state guard (per-op) — the insert-vs-modify/delete asymmetry.** The
  platform allows **inserting a new artifact** on an active version but blocks
  **modifying or deleting an existing one** (`RECORD_UPDATE_FAILED` "Cannot
  modify/delete an active context definition"). So `--add-tag` (a pure insert)
  runs on an active version, while `--set-transient`, `--set-default-mapping`,
  and `--remove-tag` require `--deactivate-first` (pair with `--reactivate` to
  restore active state after). No-op edits (setting a value that already holds)
  are detected and skipped.

## Runtime instance scripts (EXPERIMENTAL / verify-live)

> **The runtime half of Context Service.** Where the scripts above operate on a
> Context **Definition** (design-time schema), these operate on a runtime context
> **instance**: hydrate one from records, query/inspect the hydrated values,
> update them, read/write tags, and persist them back to the mapped SObjects.
>
> **Purpose: debugging, understanding, and validating runtime behavior** — *does
> this definition actually hydrate the fields it claims? does persist write them
> back? does a tag read resolve?* They are a diagnostic/inspection lens on the
> runtime, **not** a production runtime or a build step. In real usage the
> consuming engines (pricing, DocGen, BRE, the configurator) hydrate their own
> contexts; you reach for these to reproduce and verify what those engines see.
>
> All are **EXPERIMENTAL / verify-live (262 / v67.0)** and not wired into any CCI
> flow. Endpoint paths and the create/query-record/persist/query-tags-leaner body
> shapes are confirmed against the public REST references; the two PATCH bodies
> (`attributes`, `write-through-tags`) are grounded in internal sources — re-verify
> on a live org. Full narrative in
> `.cursor/skills/context-service/runtime-and-persistence.md`.

**A runtime `contextId` is request-scoped.** It is an opaque cache handle (a
UUID/hex string, **not** an SObject id — never prefix-validate it) that, per
Salesforce docs, "applies only to a single request and cannot pass data across
multiple requests" unless the org's *"Runtime Context Instance Reuse to Improve
Response Times"* setting is on and the call is within `contextTtl` (~10 min
default, 45 max). That is why the reliable entry point,
**`context_session.py`**, does create→use→persist→delete in one process. The
standalone scripts accept `--context-id` for the reuse-enabled / debugging case
and each print a one-line scope warning.

**Dry-run contract (consistent across the mutating runtime scripts).** Under
`--dry-run`, mutations (create, `persist-records`, the two PATCHes, both DELETEs)
only **log**; read-shaped POSTs (`query-record`, `query-tags[-leaner]`) and the
interface/schema reads still **execute**. Because create is a mutation, a dry-run
session mints **no** `contextId` and skips the steps that need one (with a log
line) — no fabricated id.

**On a normal GA org, use Apex — the stateless REST scripts can't complete the
lifecycle.** REST `create` is GA, but **`query-record` / `query-tags[-leaner]` are
pilot-gated** (`API_DISABLED_FOR_ORG`, scratch and production alike;
`ContextServicePilot`), and `persist-records`/the PATCHes are GA but need a
surviving `contextId` — which a REQUEST-scoped id is not across separate
`sf api request` calls (cross-call survival needs SESSION scope, the
`SessionScopeContext` pilot). So without both pilots the standalone
`query`/`persist` scripts fail not-found. **Without any pilot perm, keep the whole
hydrate → query → (update) → persist in one request** via **Apex
`Context.IndustriesContext`** (`buildContext` + `leanerQueryTags`
[+ `updateContextAttributes` + `persistContext`], one transaction) — it needs only
the GA `IndustriesContext` perm, the `contextId` survives, and the query isn't
behind the REST pilot gate. A single Flow chaining the invocable actions is the
no-code equivalent. The copy-paste snippet + method map are in
`runtime-and-persistence.md` → **Start here**. Tag names are a **distinct
namespace** from attribute names (attr `Quantity` → tag `LineItemQuantity`);
`list_context_interfaces.py` is *not* gated (plain Connect GET).

**Debugging a persist (`persist_context_instance.py` / `context_session.py --persist`):**
persist is **asynchronous** — the returned `referenceId` is not confirmation. The
per-record outcome is in **`AsyncOperationTracker`** (SOQL-queryable, richer than
the `ContextPersistenceEvent.HasErrors` boolean):

```bash
sf data query --query "SELECT AsyncOperationNumber,Status,Response FROM AsyncOperationTracker WHERE JobType='ContextPersistence' ORDER BY CreatedDate DESC LIMIT 5" --target-org <sf-alias>
```

`Response` is JSON with `savedNodes` (written), `skippedNodes` (eligible but
DML-skipped), and `errorNodes` (recordId → error text). A **no-op** persist
(hydrate → persist unchanged) succeeds; a **dirty** persist through the default
`QuoteEntitiesMapping` fails atomically with `errorNodes` = *"Unable to
create/update fields: TotalPrice, Subtotal, NetUnitPrice, Product2Id,
PricebookEntryId, …"* — the persist graph writes the **full mapped fieldset** for a
touched node, and that set includes ~29 `updateable=false` QLI fields;
`removeRestrictedFields` strips FLS only, not non-updateable fields, so **no
permission fixes it and it affects Apex, Flow, and REST identically** (a
field-updateability limit of the mapping, not a gate; reproduces on a fresh 1-line
quote). See `runtime-and-persistence.md` for the full mechanism + `DMLTypeResolver`
no-op matrix.

### `build_hydration_data.py` — hydration payload (read-only)

Emits the nested `data` payload shape that create/session expect — each array
**keyed by the context-node name**, `businessObjectType` = the node's **mapped
SObject**. Fetches the definition (one Connect GET), resolves the mapping's
node→SObject lookup, walks its active-version node tree. Two modes:

- **skeleton** (default) — each record carries `id`, `businessObjectType`, typed
  attribute placeholders, and child nodes as nested arrays. Fillable, for
  hand-authoring a payload (including what-if attribute *overrides*).
  `--mapping-name NAME` picks the mapping (default = the definition's default);
  `--node NAME` (repeatable) restricts to a subtree.
- **`--from-record ROOT_ID`** — the minimal **id-only** payload
  `{nodeName: [{"id": ROOT_ID, "businessObjectType": <mapped SObject>}]}`, ready
  to hydrate as-is. An id-only record hydrates the mapped SObject **and its child
  nodes** server-side (the runtime walks the mapping tree and queries children
  itself — live-verified: one root Quote id → parent + all child QuoteLineItems).
  Pass `--node NAME` to pick the root node when the definition has more than one
  top-level node.

> **`businessObjectType` = mapped SObject name (live-verified, the #1 gotcha).**
> The emitted `businessObjectType` is the node's **mapped SObject** (e.g.
> `SalesTransaction` node → `Quote` under `QuoteEntitiesMapping`), **not** the
> node name. A node-name `businessObjectType` hydrates **zero** records (silent
> empty result, `isSuccess: true`). The array *key* stays the node name — only
> `businessObjectType` is the SObject. Leave both as emitted. An id-only record
> hydrates live org data; inline attribute values override the org's.

```bash
# skeleton to hand-fill (values optional — id-only hydrates from the org)
python scripts/context_service/build_hydration_data.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --node SalesTransactionItem \
  --out /tmp/records.json

# id-only payload for a real record — ready to hydrate (parent + children)
python scripts/context_service/build_hydration_data.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext \
  --from-record <quoteId> --node SalesTransaction --out /tmp/records.json
# then feed either to create/session via --data-file
```

### `context_session.py` — full runtime round trip (primary entry point)

One process: create (or reuse `--context-id`) → `--update-attr NODEPATH NAME
VALUE` (repeatable) → `--write-tag NODEPATH TAG VALUE` (repeatable) → `--query` →
`--persist` (`--target-mapping-id`/`--target-mapping-name`) → auto-delete (unless
`--keep` or reusing an id). `NODEPATH` is a dot-joined node path from the root
(`-` or `""` = the root node).

```bash
python scripts/context_service/context_session.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --data-file /tmp/records.json \
  --query --persist --target-mapping-name QuoteEntitiesMapping
```

### `create_context_instance.py` / `query_context_instance.py` / `persist_context_instance.py` / `delete_context_instance.py`

The individual verbs, for the reuse-setting-on org or step-by-step debugging.
Data input (create) is mutually-exclusive `--data-file` / `--data '<json>'` /
`--data -` (stdin) — parsed and validated before the call (bad JSON → exit 2).
Mapping resolution is `--mapping-id`/`--target-mapping-id` directly, else
`--developer-name`/`--context-definition-id` [+ `--mapping-name`/`--target-mapping-name`]
→ default (or named) mapping.

```bash
# reuse-enabled org: create → capture id → query → persist → evict
CID=$(python scripts/context_service/create_context_instance.py --target-org rlm-base__beta \
  --developer-name RLM_SalesTransactionContext --data-file /tmp/records.json --id-only)
python scripts/context_service/query_context_instance.py --target-org rlm-base__beta --context-id "$CID"
python scripts/context_service/persist_context_instance.py --target-org rlm-base__beta \
  --context-id "$CID" --target-mapping-id 11j...
python scripts/context_service/delete_context_instance.py --target-org rlm-base__beta --context-id "$CID"

# clear a definition's cached runtime schema (not the definition)
python scripts/context_service/delete_context_instance.py --target-org rlm-base__beta \
  --clear-schema-cache --developer-name RLM_SalesTransactionContext
```

`query_context_instance.py` flattens the recursive `queryRecords` tree (with a
`depth`) and best-effort **decodes stringified compound values** (e.g. Address) in
the human view (`--json` leaves them raw). `--tags TAG …` switches to
`query-tags` (`--leaner` → `query-tags-leaner`). `persist_context_instance.py` prints the
returned `referenceId` and emits the **FK caveat** (reference/lookup writes are
not reliably saved by persist). `delete_context_instance.py` is the **runtime**
delete — distinct from `delete_context.py`, which deactivates / hard-deletes a
Context Definition.

### `list_context_interfaces.py` — definition interfaces (read-only)

`GET /connect/context-definition-interfaces` (or `--interface NAME` for one).
Interfaces are not tied to a specific definition, so no `--developer-name` is
required — which is why this is a separate script from `describe_context.py`.

```bash
python scripts/context_service/list_context_interfaces.py --target-org rlm-base__beta
```

### Auth — delegated to the `sf` CLI

These scripts **do not handle access tokens**. They shell out to
`sf api request rest '<path>' --target-org <alias>`, which authenticates with
the CLI's stored credentials — the same pattern as `scripts/erd/*`. Consequences:

- `--target-org` is always the **SF CLI alias/username** (e.g. `rlm-base__beta`),
  **never** the CCI alias (e.g. `beta`). CCI `beta` → SF CLI `rlm-base__beta`.
- Authenticate first with `sf org login web --alias <alias>` if a call fails.
- `sf api request rest` does not resolve a bare `connect/...` path (it 404s with
  "URL No Longer Exists"); `_client.py` always sends the fully versioned
  `/services/data/v67.0/…` path. Override the version with `--api-version`.

The GET response shapes are parsed the same way as
`tasks/rlm_context_service.py` and are pinned to **Release 262 / API v67.0** —
re-verify against a live org if the platform response shape changes.
