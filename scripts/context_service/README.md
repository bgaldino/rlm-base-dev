# Context Service helper scripts

Introspection and offline-validation tooling for Salesforce Revenue Cloud
**Context Service / Context Definitions**. These complement the CCI tasks
(`apply_context_*`, `extend_context_*`, `manage_context_definition`,
`deploy_context_definitions`) with the read/inspect/validate work that does not
fit the "apply-a-plan-to-an-org" task mold.

Full guidance lives in the **context-service skill**:
`.cursor/skills/context-service/SKILL.md` (+ `data-model-and-api.md`,
`authoring-and-lifecycle.md`).

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
| `_client.py` | — | Shared `sf api request rest` wrapper (imported, not run directly). |
| `_model.py` | — | Shared GET/plan → comparable-model normalizer + `model_to_plan` serializer (imported). |
| `_apply.py` / `_payload.py` / `_endpoints.py` / `_delete.py` / `_mutate.py` | — | Shared apply/delete/mutate orchestration, pure payload lib, REST paths (imported). |

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
