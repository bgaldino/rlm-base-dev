---
name: expression-sets
description: >-
  Inspect and author Revenue Cloud BRE Expression Sets through Connect or Metadata APIs,
  including step and variable overlays and activation lifecycle. Use for pricing,
  qualification, discovery, rating, or constraint procedures; use pricing-procedures
  for pricing element configuration and pricing-wiring for integration sequencing.
---

# Expression Sets — Programmatic CRUD & Overlay Authoring

Use this skill when reading or mutating a BRE **Expression Set** (pricing
procedure, constraint procedure, qualification/discovery/rating procedure, …)
programmatically — via the **Connect API** (runtime/programmatic CRUD) or the
**Metadata API** (source-controlled authoring) — including building declarative
overlays that add/remove/update steps and variables. It is consumable by any AI
agent (Cursor, Claude Code, Copilot, Codex, Windsurf, Aider).

Expression Sets back more than pricing — Revenue Cloud uses **six**
`interfaceSourceType` values (see [Expression Set types](#expression-set-types)),
so this skill is generic to the Expression Set engine. For where Expression Set
CRUD fits into the **pricing** layering model (recipes, recipe-table mappings,
procedure plans, context definitions), read
`.cursor/skills/pricing-wiring/SKILL.md`. To configure the **elements** inside a pricing
procedure (what each computes, its parameters, ordering rules, troubleshooting), read
`.cursor/skills/pricing-procedures/SKILL.md`. A procedure can **consume a decision
table**'s output via a `GetOutputsFromDecisionTable` step (with a `DecisionTable`
parameter) — to inspect, author, or manage those tables see
`.cursor/skills/decision-tables/SKILL.md`.

## Quick Rules

1. **Choose the path by use case.** **Metadata API** (`expressionSetDefinition`
   XML + deploy) for source-controlled, git-tracked changes; **Connect API**
   (`tasks/rlm_expression_set_connect.py`) for runtime/programmatic CRUD. The
   step/param/variable shapes are identical, so a step authored once works for
   both.
2. **Every Connect mutation must HTML-unescape the payload before sending**
   (`normalize_html_entities`, default on). Raw GET output is HTML-escaped
   (`&quot;`/`&#39;`) and the engine rejects the entities. The Metadata path
   needs no equivalent — the XML parser decodes entities before the engine sees
   them.
3. **Run the pre-flight validator on any payload before a Connect call**
   (`validate_expression_set`, or `python scripts/ai/validate_expression_set.py`).
4. **The step graph is flat.** One `steps[]` array; hierarchy is encoded by
   `parentStep` (a step **name**), not nested arrays. Read `sequenceNumber` for
   execution order — GET returns top-level steps **alphabetically by name**, and
   `sequenceNumber` is **scoped per parent** (children restart at 1).
5. **Build `addSteps` overlays by capturing from a live GET**, not hand-authoring.
   Slice top-level steps and child steps differently (see `authoring-and-overlays.md`).
6. **Capture a step's dependencies, not just the step** — classify every
   referenced name into one of three scopes (version variable → `addVariables`;
   custom external dep → `externalDependencies`; standard context → nothing).
7. **Mutations run deactivate → modify → reactivate**, in a guarded `finally`;
   the tasks enforce this, including the procedure-plan cascade. The CCI task
   restores labels before reactivation in that same inactive window; its Connect
   PATCH sends `enabled:false` so the PATCH cannot reactivate first. The
   standalone toolkit still restores labels in a second lifecycle cycle. In
   `tasks/rlm_expression_set_connect.py`, preservation lives in
   `_run_connect_mutation`, so every Connect PATCH gets it. Opt out with
   `--no-preserve-labels` (toolkit) or `-o preserve_labels false` (CCI). Give an
   overlay's new or updated steps readable labels with a per-step `label` (or a top-level
   `labels` map); without one they show the spaceless `name`.
8. **Test Connect CRUD on a disposable clone** (POST-create a renamed copy),
   never the shipped procedure — except for an intentional, approved change.
9. **Step `name` ≠ `label`.** `name` is the spaceless API-Name identifier (and the
   `parentStep` FK); `label` is the readable UI text. **Connect has no `label`
   field and clobbers it to `name` on every full-graph PATCH**, so Connect-built
   steps read as run-on names. Labels live only in the **Metadata XML `<label>`**
   and the **Tooling `Metadata`** path. Read/write them with
   `describe_expression_set.py --labels` / `relabel_expression_set.py`, and run
   any relabel **last** (after all Connect work). See
   `metadata-vs-connect.md` → *Step names vs. labels*.

> **Pinned to Release 264 / API v68.0.** Re-verify enums and behavior on the
> target release at merge time. This `SKILL.md` is the task-level entry point;
> deep detail lives in companion files (read on demand):
> - **`authoring-and-overlays.md`**: building/applying overlays, capturing a
>   step's three dependency scopes, safe step removal.
> - **`metadata-vs-connect.md`**: the two authoring paths, the Connect mutation
>   lifecycle, verb-specific field rules, GET serializer gotchas, Metadata API
>   authoring, create-with-content.
> - **`multi-version-orgs.md`**: which version executes, and editing, re-ranking,
>   overlaying, importing and deploying on a set with several versions.
> - **`expression-set-types.md`**: the six Revenue Cloud types, the full enum, and why
>   Constraint sets (CML) fall outside this skill's tooling.
> - **`toolkit-quick-start-and-examples.md`**: the worked command sequence, the CCI task
>   table, run times, running the tools from an agent sandbox, and example overlays.
> - **`docs/references/expression-set-connect-api-reference.md`**: the
>   exhaustive object/ID model, OAS-confirmed schema enums, every known error +
>   resolution, and the verification checklist.
>
> The standalone helper toolkit lives at **`scripts/expression_sets/`** (see its
> `README.md` and the [script routing table](#script-routing) below).

## <a name="expression-set-types"></a>Expression Set types (Revenue Cloud)

Revenue Cloud uses **six** `interfaceSourceType` values: PricingProcedure, DiscoveryProcedure, RatingProcedure, RatingDiscoveryProcedure, QualificationProcedure (step graphs, this skill) and Constraint (**CML**, not a step graph: use [`constraint-models`](../constraint-models/SKILL.md); the overlay tooling and the activation rules here do not apply to it). The table, the shipped examples, the full 11-member enum and the two rules that mislead for Constraint sets are in [`expression-set-types.md`](expression-set-types.md).

<a name="the-full-enum"></a>


## DO NOT

- **DO NOT** send raw Connect GET output back in a PATCH/POST without
  HTML-unescaping it first — the escaped `&quot;`/`&#39;` values make engine parsing fail
  (flat: `Syntax error. Found '&'`; nested: opaque `INVALID_INPUT: Error
  processing JSON`). The mutation tasks do this automatically; only set
  `normalize_html_entities: false` to reproduce the failure.
- **DO NOT** keep the version-level `id` on a POST-create payload, and DO NOT
  drop it on a PATCH-replace. Create omits it; replace keeps it (the tasks
  handle this — `import_expression_set` strips it on create).
- **DO NOT** drop `contextDefinitions[].id` on a POST-create — context-node
  parameter data types fail to resolve without it (`Specify a valid data type
  for the … variable`).
- **DO NOT** change `resourceInitializationType` on an existing ES — it is
  **immutable once set**. Set it correctly at POST-create time (`Default` is
  common).
- **DO NOT** mutate a shipped/production Expression Set to experiment — test
  Connect CRUD against a disposable clone, except for an intentional, approved
  change.
- **DO NOT** treat a `removeSteps` (or any PATCH) that reactivates as proof it
  is correct — engine validation is **structural, not functional**. Removing a
  producer element can leave its consumers/filters orphaned and **silently
  misbehave** with no error. See `authoring-and-overlays.md` → *Removing steps*.
- **DO NOT** attempt to clone an Expression Set by changing only the version
  `apiName` — the script detects create-vs-replace by querying for the
  **top-level `apiName`**, not the version name. For a POST-create, change
  all three: top-level `apiName`, top-level `name`, and version `apiName`.
  Otherwise the script will attempt REPLACE mode and fail with "You can't modify
  the apiName of an expression set version."
- **DO NOT** ship an `addSteps` overlay without accounting for **all three**
  dependency scopes (see `authoring-and-overlays.md`). The
  validator warns on an undeclared **custom** (`__c`/`__r`) reference — declare
  it rather than suppressing the signal. Don't put `__std`/standard fields in
  `externalDependencies`; they aren't custom.
- **DO NOT** append a step to an existing version via a Tooling `Metadata`
  PATCH — it returns `FIELD_INTEGRITY_EXCEPTION`. Use create-with-content or a
  Metadata API deploy.
- **DO NOT** send a `label` field to Connect (`JSON_PARSER_ERROR: Unrecognized
  field "label"`) or put spaces in a step `name` (`INVALID_INPUT` — `name` is an
  API Name). Readable labels are a **Tooling `Metadata`** concern only.
- **DO NOT** relabel a version and then run a Connect import/overlay on it — the
  Connect full-graph PATCH resets every `label` to `name`. Relabel is always the
  **last** step; re-run it after any later Connect mutation. A Tooling `Metadata`
  PATCH on an **active** version is rejected (`INVALID_ID_FIELD:
  LatestVersionSnapshotId not found …`) — deactivate first, PATCH, reactivate.

- **DO NOT** run an overlay apply, import or step-formula edit in a foreground call
  with a short timeout: they block for minutes on a large procedure and stop half way
  when the caller gives up. See *Running the tools* in
  [`toolkit-quick-start-and-examples.md`](toolkit-quick-start-and-examples.md).

## Entry Conditions

| Situation | Use |
|---|---|
| Export, create, replace, overlay, or delete an Expression Set at runtime | This skill → [script routing](#script-routing) / Connect API tasks |
| Inspect / trace / diff a live procedure without mutating it | The read-only toolkit CLIs → [script routing](#script-routing) |
| Author/modify a procedure in git (source-controlled) | `metadata-vs-connect.md` → Metadata API authoring |
| The Connect mutation lifecycle, verb-specific field rules, GET gotchas | `metadata-vs-connect.md` |
| Capture a known-good element from one org and add it to another | `authoring-and-overlays.md` |
| Configure a **pricing element** (Aggregate Price, Price Revision / compound ramp uplift, discounts, DDS, …), element ordering, pricing operations | `.cursor/skills/pricing-procedures/SKILL.md` |
| Classify a step's dependency scopes; remove a step safely | `authoring-and-overlays.md` |
| Where ES CRUD fits in the **pricing** setup order (recipes, plans, context) | `.cursor/skills/pricing-wiring/SKILL.md` |
| The **decision table** a `GetOutputsFromDecisionTable` step consumes (inspect / author / lifecycle) | `.cursor/skills/decision-tables/SKILL.md` |
| Object/ID model, full schema enums, **every error + resolution**, verification checklist | Detail file: `docs/references/expression-set-connect-api-reference.md` |
| An opaque Connect failure (a code/message you don't recognize) | Reference doc → **Known errors & conditions** section |
| Writing the Python task class itself | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |

## <a name="quick-start"></a>Quick Start

Export, trace, slice a validated overlay, preview, apply to a **disposable clone**, verify labels, with the standalone toolkit (`--target-org` is the *SF CLI* alias, never the CCI alias). The command sequence is in [`toolkit-quick-start-and-examples.md`](toolkit-quick-start-and-examples.md); the CCI task table, run times (overlay apply takes minutes on a large procedure: run it in the background) and the shipped example overlays are there too.


## <a name="script-routing"></a>Task + script routing

Two independent surfaces cover Expression Set CRUD — the **CCI tasks** (build
work) and the standalone **`scripts/expression_sets/` toolkit** (inspection +
one-off lifecycle, `sf`-CLI transport, no access token). They share the
deactivate → mutate → recover engine (`scripts/expression_sets/_engine.py`) and the
version guards (`_guards.py`), both stdlib-only; everything else is separate.
Full toolkit detail:
`scripts/expression_sets/README.md`.

| I need to… | Use |
|---|---|
| List every ES in an org by type / active version | `python scripts/expression_sets/list_expression_sets.py --target-org <sf_alias>` (read-only) |
| Pretty-print one procedure's steps in execution order | `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name>` (read-only) |
| Export a definition to JSON (snapshot, or `--for-import`) | `python scripts/expression_sets/export_expression_set.py --target-org <sf_alias> --developer-name <name> --out <path>` (read-only) |
| **Trace** who produces/consumes a variable; classify a step's dependency scopes; find orphans | `python scripts/expression_sets/trace_expression_set.py --target-org <sf_alias> --developer-name <name> --variable <v> \| --step <s> \| --field <f> \| --orphans` (read-only) |
| **Visualize** a procedure as a Mermaid diagram — data-dependency (nodes shaped & colored by kind: step / version constant / version variable / custom / `__std` field / context tag) or execution-flow (top-down; ListGroups drawn as subgraph boxes containing their children in sequence order); `--labels` titles steps with their readable Tooling label | `python scripts/expression_sets/trace_expression_set.py --target-org <sf_alias> --developer-name <name> --mermaid deps\|flow [--step <s>] [--labels] [--out <path.mmd>]` (read-only) |
| Diff a procedure org-vs-org or org-vs-JSON | `python scripts/expression_sets/diff_expression_set.py --target-org <sf_alias> --developer-name <name> --right-org <sf_alias2> \| --right-file <path>` (read-only) |
| Slice step(s) into a validated overlay with scoped deps | `python scripts/expression_sets/export_expression_set_overlay.py --target-org <sf_alias> --developer-name <name> --step <s> --out <path>` (read-only; writes a local file) |
| Create/replace a whole ES from JSON | `import_expression_set` (CCI, build) **or** `python scripts/expression_sets/import_expression_set.py --target-org <sf_alias> --input-file <path>` (preview; `--confirm` to write) |
| Apply a declarative overlay | `apply_expression_set_overlay` (CCI, build) **or** `python scripts/expression_sets/apply_expression_set_overlay.py --target-org <sf_alias> --expression-set <name> --overlay <path>` (preview; `--confirm`) |
| Change one step's formula on one version (the executing one by default), with read-back | `python scripts/expression_sets/set_step_formula.py --target-org <sf_alias> --expression-set <name> --step <s> \| --parent-step <p> --formula '<text>'` (preview; `--confirm`; `--show` reads only) — see [Multi-version orgs](#multi-version-orgs) |
| Activate / deactivate a version (+ procedure-plan cascade) | `python scripts/expression_sets/activate_expression_set.py --target-org <sf_alias> --expression-set <name> --activate \| --deactivate` (preview; `--confirm`) |
| Delete a whole ES or one version | `delete_expression_set` (CCI) **or** `python scripts/expression_sets/delete_expression_set.py --target-org <sf_alias> --expression-set <name> [--version <v>] --confirm` (destructive) |
| Price lines through one procedure with no quote (headless; golden numbers for a clone) | `python scripts/expression_sets/run_headless_pricing.py --target-org <sf_alias> --procedure <name> --request <file> --pricebook <id>` (read-only; adds the Pricebook, currency and end-date inputs pricing needs; see [`../pricing-procedures/runtime-and-observability.md`](../pricing-procedures/runtime-and-observability.md)) |
| Pre-flight a JSON file offline (no org) | `python scripts/ai/validate_expression_set.py <path> [--definition\|--overlay]` |

---


---

## Mutation lifecycle & authoring paths (summary)

Every Connect mutation runs **deactivate → PATCH/POST → reactivate** in a guarded
`finally` (an enabled version can't be modified/deleted), including the
`ProcedurePlanDefinitionVersion` cascade; a failed PATCH is **left deactivated and
raised** (non-atomic), but the cascaded procedure plans are **reactivated** — an
inactive plan silently skips its procedures — once the version is confirmed off.
They stay off under `activate_after=false`, or when the version can't be
confirmed off (the tool treats a failed PATCH as possibly leaving a half-written or
active version, a precaution not traced to platform behaviour; don't restore a plan
over it). Each record the run left inactive is reported with its
restore command, except a version a failed PATCH may have half-written: re-import
it before reactivating. Verb-specific field rules (version `id` omit-on-create /
keep-on-replace, `contextDefinitions[].id`, immutable `resourceInitializationType`,
`usageType`), the GET serializer gotchas (alphabetical top-level order,
per-parent `sequenceNumber`, HTML-escaped string leaves), and the **Metadata API**
source-controlled path (nested graphs, no lifecycle, create-with-content) all live
in **`metadata-vs-connect.md`** — read it before any Connect mutation or
source-controlled edit.

## <a name="multi-version-orgs"></a>Multi-version orgs

A set can hold several active versions; the runtime runs the **highest Rank** among enabled versions whose date window covers the call. Edit the executing version (`set_step_formula.py`), give a version a Rank before cycling it, and expect overlays, whole-set imports and deploy read-backs to refuse the shapes that fail on the platform. The measured rules, the version-list query and the open questions are in [`multi-version-orgs.md`](multi-version-orgs.md); toolkit detail in `scripts/expression_sets/README.md` → *Multi-version expression sets*.


## Overlays & dependency capture (summary)

Overlays declare placement by **anchor** (`afterStep`/`beforeStep`), not numeric
sequence; capture them from a live GET (don't hand-author) — the toolkit's
`export_expression_set_overlay.py` slices a step and pre-classifies its dependencies. Every
referenced name is one of **three scopes**: version variable → `addVariables`;
custom (`__c`/`__r`) → `externalDependencies` (the overlay can't create it);
standard context → nothing. Top-level and child steps are sliced differently
(placement vs `parentStep` + `sequenceNumber`). To put several overlays on one
procedure, merge them locally and import once: a second overlay applied to a
procedure that already carried one failed and left the version inactive (measured
on 264, cause not isolated). And **validation is structural,
not functional** — a `removeSteps` that reactivates can still leave a consumer
orphaned and silently misbehave. The full slicing table, the three-scope
classifier, the `externalDependencies` block shape, the local-merge recipe and
safe-removal guidance live in **`authoring-and-overlays.md`**.


## <a name="compound-ramp-uplift"></a>Compound ramp uplift

Moved to the pricing-procedures skill, which owns pricing element configuration:
[`../pricing-procedures/elements/price-revision-compound-uplift.md`](../pricing-procedures/elements/price-revision-compound-uplift.md)
(the five prerequisites, the ramp `PriceRevision` bindings, the tracked-default vs
264-template comparison and the compounding math); the read-only inspect commands are in
[`../pricing-procedures/elements/price-revision.md`](../pricing-procedures/elements/price-revision.md). Building the group-ramp quote itself is
[`../ramped-quotes/SKILL.md`](../ramped-quotes/SKILL.md).

---


---


---

## Validation Checks

Run before any Connect mutation and before a PR that touches overlays, the
tasks, or the validator:

```bash
# Pre-flight a payload offline (definition or overlay)
cci task run validate_expression_set -o file <path> -o kind overlay
python scripts/ai/validate_expression_set.py <path> --overlay   # CLI form

# Validator/schema unit tests (self-contained check() runner, no pytest)
python tests/test_expression_set_schema.py        # expect: all pass

# Token for manual API checks
yes | sf org auth show-access-token --target-org <sf_alias>
```

Checklist:

- [ ] Payload HTML-unescaped (or `normalize_html_entities` left on).
- [ ] Validator reports 0 errors; resolve or consciously accept warnings.
- [ ] Overlay `addSteps` account for all three dependency scopes; custom
      (`__c`/`__r`) refs declared in `externalDependencies`.
- [ ] Top-level vs child steps sliced correctly (placement vs `parentStep` +
      `sequenceNumber`).
- [ ] POST omits version `id` and keeps `contextDefinitions[].id`; PATCH keeps
      version `id`.
- [ ] `resourceInitializationType` matches the stored value (or set correctly at
      create).
- [ ] Applied + verified on a **disposable clone** before any real target; for a
      removal, verified functionally (test run), not just "it reactivated."
- [ ] After `cumulusci.yml` task/option edits:
      `python scripts/ai/generate_cci_reference.py` and commit the regenerated
      reference.

---

## Related References

- **Sub-files (progressive disclosure):** `authoring-and-overlays.md` (overlays,
  three-scope dependency capture, safe step removal) and `metadata-vs-connect.md`
  (authoring paths, mutation lifecycle, verb-specific field rules, GET gotchas,
  Metadata API authoring).
- **Standalone toolkit (inspect / trace / diff / export + guarded mutators, no
  access token):** `scripts/expression_sets/README.md`.
- **Exhaustive detail (object/ID model, OAS schema enums, every error +
  resolution, Metadata authoring, verification checklist):**
  `docs/references/expression-set-connect-api-reference.md`
- **Pricing element configuration (each element's parameters, ordering rules,
  compound ramp uplift, pricing operations and troubleshooting):**
  `.cursor/skills/pricing-procedures/SKILL.md`
- **Pricing layering model (recipes, recipe-table mappings, procedure plans,
  context definitions) — where ES CRUD fits in pricing setup:**
  `.cursor/skills/pricing-wiring/SKILL.md`
- **Decision tables a procedure consumes (`GetOutputsFromDecisionTable` step) —
  inspect / author / lifecycle + the async-refresh data layer:**
  `.cursor/skills/decision-tables/SKILL.md`
- **Connect CRUD tasks:** `tasks/rlm_expression_set_connect.py`; pre-flight
  validator `tasks/expression_set_schema.py`; tests
  `tests/test_expression_set_schema.py`.
- **External doc link index:**
  `docs/salesforce/262/dev-guide/expression-set-business-apis-links.md` (262 capture;
  not in the 264 snapshot).
- **Writing the Python task class:**
  `.cursor/skills/cci-orchestration/custom-task-authoring.md`.
