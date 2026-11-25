# Expression Set helper scripts

A self-contained, full-lifecycle toolkit for Salesforce Revenue Cloud **BRE
Expression Sets** — pricing / discovery / rating / rating-discovery /
qualification procedures and constraint rules. It covers the whole lifecycle:
**inspect / export / trace / diff** (read-only), and the guarded
**create / replace / overlay / activate / delete** mutators.

Auth is delegated to the **`sf` CLI** (`sf api request rest --target-org …`), so
**no access token is ever handled or passed**. `--target-org` is always the
**SF CLI alias** (e.g. `rlm-base__beta`), **never** the CCI alias.
Pinned to Release 264 / API v68.0.

Full guidance lives in the **expression-sets skill**:
`.cursor/skills/expression-sets/SKILL.md` (+ `authoring-and-overlays.md`,
`metadata-vs-connect.md`), with the exhaustive object/ID/enum/error reference in
`docs/references/expression-set-connect-api-reference.md`.

## Independent of CumulusCI

This package imports **nothing** from `tasks/`; the toolkit is its own program over
the `sf` CLI. Two modules are shared with the CCI task
`tasks/rlm_expression_set_connect.py`, which imports them (both are stdlib-only, no
CumulusCI): `_engine.py`, the one deactivate → mutate → recover state machine both
sides run, and `_guards.py`, so both importers apply one multi-version rule.
Everything else is separate; the validator is **vendored** here as `_schema.py` (a
mirror of `tasks/expression_set_schema.py`) rather than imported.

**Known, deliberate differences between the two adapters.** The engine runs the same
state machine for both, but two behaviours differ by design:

- **Failure recovery for a non-definition mutation.** The toolkit's Tooling
  `Metadata` mutations (`relabel_expression_set.py`, `set_step_formula.py`, the
  label auto-restore) call `run_mutation(reactivate_on_failure=True)`: when one
  fails, the version and the cascaded plans are reactivated and the error is still
  raised. The CCI task has no such path; every CCI mutation is a Connect PATCH, and
  after a failed one it leaves the version off and fails loudly. After a failed
  Connect PATCH the toolkit does the same.
- **Label restore.** The CCI task sends the Connect PATCH with `enabled: false` and
  restores step labels in the same inactive window, before reactivating; a restore
  failure is logged and the task still succeeds. The toolkit reactivates first and
  restores labels in a second deactivate → Tooling PATCH → reactivate cycle; a
  restore failure makes the CLI exit 1 (`labelRestore.ok=false` in `--json`).

**How these fit the lifecycle** (what to reach for, and when):

| Lifecycle stage | Production path | These helpers |
|-----------------|-----------------|---------------|
| **Author / apply** an expression set in the build | CCI tasks (`import_expression_set`, `apply_expression_set_overlay`, `manage_expression_sets`) + Metadata API source | the mutating CLIs below — live-proven, for one-off exploration & updates **outside** the build |
| **Inspect / trace / diff / export** a definition | — | the read-only CLIs below (safe anytime) |
| **Slice a step into a portable overlay** | — | `export_expression_set_overlay.py` (read-only; writes a local file only) |

So: the CCI tasks + Metadata API own the build; the **read-only** CLIs are always
safe; the **mutators** (`import` / `apply_expression_set_overlay` / `set_step_formula` / `activate` / `delete`) are
**preview-by-default** and require `--confirm` to write — use them for one-off
exploration and updates on a **disposable clone**, never a shipped procedure
(Quick Rule 8).

## Scripts

**Read-only inspectors (safe anytime):**

| Script | Org? | Purpose |
|--------|------|---------|
| `list_expression_sets.py` | Read-only | One row per set: `interfaceSourceType` (the RC type), `usageType`, active version, IsActive — grouped by type. |
| `describe_expression_set.py` | Read-only | Pretty-print one set: version → steps in execution (per-parent `sequenceNumber`) order → params / variables. `--params` for the full parameter dump; `--labels` joins the readable step **labels** from the Tooling API (Connect has none) and flags `label==name` drift. |
| `export_expression_set.py` | Read-only | GET a definition → JSON file (the read half of the round trip). `--for-import` strips read-only fields + HTML-unescapes so the output is import-ready. |
| **`trace_expression_set.py`** | Read-only | **Flagship** — variable producer→consumer graph + three-scope classifier (version / custom / standard). `--variable` (safe-removal view), `--step` (dependency closure + capture guidance), `--field`, `--orphans`. `--mermaid deps\|flow` renders a diagram (`--out` to a `.mmd` file) where each node is **shaped & colored by kind** (step / version constant / version variable / custom / `__std` field / context tag); `--step` scopes `deps` to one step's neighborhood; `--labels` titles step nodes with their readable Tooling label. |
| `diff_expression_set.py` | Read-only | Added / removed / changed / reordered steps + variables of one version per side, org-vs-org or org-vs-JSON. An org side uses `--left-version` / `--right-version`, else the executing version; a JSON file with several versions needs the option. |
| `export_expression_set_overlay.py` | Read-only (writes local file) | Slice step(s) from a live GET into a **validated** `addSteps` overlay with the three dependency scopes pre-classified (version deps → `addVariables`; custom refs → `externalDependencies`). `--with-labels` joins each sliced step's readable **label** (from the Tooling Metadata — Connect can't serialize it) into a top-level `labels` block, so the overlay is self-describing and `apply_expression_set_overlay` restores the label after the Connect PATCH clobbers it. |

**Mutators (preview by default; `--confirm` to write — never on a shipped procedure):**

| Script | Org? | Purpose |
|--------|------|---------|
| `import_expression_set.py` | **Mutates** | Create (POST) or replace (PATCH) a whole set from a JSON file; **auto-detects** create-vs-replace **by querying the org for an existing top-level `apiName`** (NOT the version name). For a clone/CREATE, change top-level `apiName`, top-level `name`, and version `apiName`. On a REPLACE it **auto-preserves step labels** (captures them before the clobbering PATCH, restores the survivors after — `--no-preserve-labels` to skip). On a set with several versions it imports only a one-version payload for the targeted version whose label no other version shares, and **refuses anything else before any write** (see [Multi-version expression sets](#multi-version-expression-sets)). |
| `set_step_formula.py` | **Mutates** | Set one step's formula (`formula-section-<N>-input`) on **one version** through the Tooling `Metadata` PATCH: the executing version by default (see [Multi-version expression sets](#multi-version-expression-sets)), or `--version-api-name`. Select the step by `--step`, or by `--parent-step` (the one child carrying the formula; stable when versions rename the child). Runs deactivate → PATCH → reactivate (an inactive target stays inactive), reads the formula, the version and every referencing plan back, and exits 1 on any mismatch. `--show` reads only. The tool for formula edits on a multi-version set. |
| `apply_expression_set_overlay.py` | **Mutates** | Merge a declarative overlay (`addSteps` / `removeSteps` / `updateSteps` / `reorderSteps` / `addVariables` / `removeVariables`) into a live version; **all local pre-flights run BEFORE any deactivation**. **Auto-preserves step labels** (captures the survivors before the PATCH + honors any labels the overlay carries for added or updated steps, restores after — `--no-preserve-labels` to skip). |
| `activate_expression_set.py` | **Mutates** | `--activate` / `--deactivate` a version (+ the procedure-plan cascade), standalone. Use to re-enable a version left off by a failed apply. |
| `relabel_expression_set.py` | **Mutates** | Set readable step **labels** via the Tooling `Metadata` PATCH (the ONLY place labels live — Connect has no `label` and clobbers it on every PATCH). Label source: `--auto` (lossy derive for drift steps), `--labels-file` (`{name: label}` JSON), `--set NAME=LABEL` (repeatable), or **`--from-metadata <file>`** (read the authoritative `{name: label}` map straight from a `*.expressionSetDefinition-meta.xml` — the source-controlled `force-app/…/expressionSetDefinition/` files, or a target-org retrieve). Runs the same deactivate→PATCH→reactivate lifecycle. The Connect mutators now auto-restore labels, so this is mainly for a manual fix or a bulk relabel from the repo XML. |
| `delete_expression_set.py` | **Destructive** | Delete a whole set (Connect DELETE + cascade) or one version (`--version`). `--confirm` REQUIRED (absence of `--confirm` IS the preview). |

**Shared modules (imported by the CLIs, not run directly):**

| Module | Purpose |
|--------|---------|
| `_client.py` | The `sf api request rest` wrapper; Connect base `connect/business-rules/expression-set/{9QL}`; SOQL with `nextRecordsUrl` paging; the injectable `Transport` seam (binds `target_org` / `api_version` / `dry_run` / `logger`, short-circuits mutating verbs under dry-run). |
| `_resolve.py` | api-name → `ExpressionSetDefinition` (9QA) / `ExpressionSet` (9QL) / `ExpressionSetVersion`. The mutators' default version (`resolve_version_by_es_id`) is the executing one from `_guards.executing_version` (then the highest-numbered active, then the highest-numbered), with a warning when several are active. |
| `_guards.py` | Pure, stdlib-only version guards, also imported by the CCI task: `executing_version` (the highest `Rank` among active versions whose date window covers now; earliest created among null Ranks; measured on 264), `rank_order_warning`, `target_version_warning`, `VERSION_FIELDS` (the fields every caller selects for it), `import_target_refusal` (the measured multi-version import rule), `version_name_collision_refusal` and `other_active_versions_refusal` (the overlay's multi-version refusals), and `null_rank_reactivation_refusal` / `null_rank_delete_refusal` (a version with no Rank cannot be reactivated). |
| `_schema.py` | **Vendored** validator + enums (mirror of `tasks/expression_set_schema.py`): `validate_definition` / `validate_overlay` / `validate_overlay_against_definition`, `_step_variable_refs` / `_step_all_refs`, `_is_custom_ref`, `INTERFACE_SOURCE_TYPES` / `USAGE_TYPES`. Stdlib-only. |
| `_payload.py` | Verb-specific field rules (strip top-level `id`; keep-and-rewrite vs strip version `id`); HTML-entity normalization (`unescape_value` / `normalize_html_entities`). Pure. |
| `_overlay.py` | Declarative step / variable merge (`add_steps` / `remove_steps` / `update_steps` / `reorder_steps` / `add_variables` / `remove_variables` / `renumber_top_level_steps`) + `overlay_labels` (harvest the `{name: label}` map an overlay carries — top-level `labels` block and/or per-`addSteps` or `updateSteps` `label`, per-step wins) + `OVERLAY_ONLY_STEP_KEYS` (`placement` / `label` — stripped from a step before the Connect send). Pure. |
| `_graph.py` | Flat `steps[]` → producer/consumer dependency graph + three-scope classifier. Imports `_schema` (in-package). Pure. |
| `_tooling.py` | Tooling-API access for step **labels** — the one thing Connect can't touch. Pure helpers (`step_labels` / `label_drift` / `readable_labels` / `humanize_name` / `derive_labels` / `apply_labels` / `strip_metadata_readonly` / `labels_from_metadata_xml` (read `{name: label}` from a `*.expressionSetDefinition-meta.xml`)) + I/O over the `Transport` (`resolve_esdv` (9QB) / `fetch_metadata` / `patch_metadata`, dropping the read-only `urls` key). **Label-preservation trio:** `capture_labels` (best-effort snapshot of the readable labels a Connect PATCH will clobber), `relabel_version` (the shared deactivate→Tooling PATCH→reactivate core, used by both `relabel_expression_set.py` and auto-restore), and `restore_labels_after_clobber` (non-fatal re-apply after a Connect mutation — re-resolves the version, restores survivors, never fails the mutation). `capture_version_labels` / `restore_version_labels` run the capture and restore over **every** version of the set, since the full-graph PATCH clobbers all of them. The active-version guard applies to the Metadata PATCH exactly as to a Connect mutation. |
| `_engine.py` | `LifecycleCore`, the one deactivate → mutate → recover state machine, shared with the CCI task: the `ProcedurePlanDefinitionVersion` cascade (with rollback), version-state transitions and polling, `ResourceInitializationType` alignment, failure recovery with the health report, and delete-with-rollback. Stdlib-only; an adapter supplies I/O, logging, the error class and the dry-run style. A failed PATCH leaves the version **DEACTIVATED** and re-raises (never reactivated over a half-mutated definition). |
| `_lifecycle.py` | `LifecycleEngine`, the toolkit's adapter over `_engine.LifecycleCore`: every call on the `Transport` seam, `LifecycleError`, the transport's dry-run, plus the Connect GET/PATCH/POST/DELETE. Drives both the Connect and the Tooling-`Metadata` (relabel, `set_step_formula`) mutations. |

**Tests:** `tests/test_expression_sets_toolkit.py` — offline unit tests (no org,
no `sf`, no pytest) for `_graph` / `_payload` / `_overlay` / `_tooling` (incl. the
label-preservation trio `capture_labels` / `relabel_version` /
`restore_labels_after_clobber`, `labels_from_metadata_xml`, and `overlay_labels`) /
`export_expression_set_overlay` + shipped-fixture validator parity, `_guards`
(the multi-version import rule over a version-chain table) and
`set_step_formula`. Run:
`python tests/test_expression_sets_toolkit.py`.

## Quick start — export → trace → slice → apply-to-clone

```bash
ORG=rlm-base__beta

# 1. See what's in the org, grouped by Revenue Cloud type.
python scripts/expression_sets/list_expression_sets.py --target-org $ORG

# 2. Export a procedure to a local JSON file (import-ready).
#    Works for Pricing, Rating, RatingDiscovery, Qualification procedures.
python scripts/expression_sets/export_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --for-import --out /tmp/pp.json

# 2b. Export a Rating procedure (same toolkit, same flags).
python scripts/expression_sets/export_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultRatingProcedure --for-import --out /tmp/rating.json

# 3. Trace a variable — who produces it, who consumes it (safe-removal view).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --variable NetUnitPrice

# 3a. Trace orphans (consumed-with-no-producer, candidate for removal).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultRatingProcedure --orphans

# 3b. Draw it — a Mermaid dependency diagram (scope-colored) or execution-flow
#     chart. --out writes a .mmd file; --step scopes the deps view to one step.
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --mermaid deps \
    --out /tmp/pricing.deps.mmd

# 4. Slice a step into a validated overlay (three scopes pre-classified).
python scripts/expression_sets/export_expression_set_overlay.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --step "Apply Discount" \
    --out /tmp/apply_discount.overlay.json

# 5. Preview applying that overlay to a DISPOSABLE CLONE (no --confirm = no write).
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json

# 6. Apply it for real. Step labels are auto-preserved: the surviving steps' labels
#    are captured before the clobbering PATCH and restored after (a second
#    deactivate→relabel→reactivate cycle); a NEW step keeps its label if the overlay
#    carries one (top-level "labels" block, or export --with-labels). --no-preserve-labels
#    opts out.
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json --confirm

# 7. (Optional) Manual relabel — only if you skipped preservation (--no-preserve-labels),
#    a restore failed, or you want to bulk-apply the authoritative labels from the repo XML.
python scripts/expression_sets/describe_expression_set.py --target-org $ORG \
    --developer-name RLM_MyClone --labels          # shows label==name drift
python scripts/expression_sets/relabel_expression_set.py --target-org $ORG \
    --expression-set RLM_MyClone \
    --from-metadata force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml \
    --confirm
```

## Visualizing a procedure (Mermaid)

`trace_expression_set.py --mermaid` emits a [Mermaid](https://mermaid.js.org/)
diagram to stdout (or a `.mmd` file with `--out`). Paste it into any Mermaid
renderer — `mermaid.live`, a GitHub Markdown ` ```mermaid ` fence, or the VS Code
Mermaid preview. Two views:

- **`--mermaid flow`** — execution order, top-down: top-level steps chained by
  their `sequenceNumber`, and each `ListGroup` drawn as a **subgraph box that
  contains** its children — chained inside in their own `sequenceNumber` order, so
  the diagram shows containment, not just a relationship edge. The group box takes
  the parent's slot in the top-level chain; nested ListGroups nest recursively. The
  "what does this procedure do, in order" view.
- **`--mermaid deps`** (the default) — the data-dependency graph: steps are
  rectangles, and every referenced name is drawn with a **shape + color keyed to
  its kind**, a finer split than the three scopes but grounded only in what the
  Connect GET reveals:

  | Node kind | Scope | Shape | Color | Capture meaning |
  |---|---|---|---|---|
  | step | — | rectangle `[ ]` | grey | a procedure step |
  | version **constant** | version | hexagon `{{ }}` | green | a `type: Constant` version variable → ship in `addVariables` |
  | version **variable** | version | rounded `( )` | green | a non-Constant version variable → ship in `addVariables` |
  | **custom** | custom | cylinder `[( )]` | red | a `__c`/`__r` field/relationship → `externalDependencies` (target org must define) |
  | **std** | standard | subroutine `[[ ]]` | blue | a `__std` standard-context field → declare nothing |
  | **context** | standard | stadium `([ ])` | blue | a bare context-supplied tag/attribute → declare nothing (the ES GET can't say tag-vs-attribute, so neither does the tool) |

  Edge labels carry the role symbol (`>` produces, `<` consumes, `?` filter
  criterion, `~` best-effort Formula token). Add `--step "<name>"` to scope the
  diagram to that step plus the variables it touches and their immediate neighbor
  steps — the drawn form of the `--step` text closure. The legend (`classDef`
  block) lists only the kinds actually drawn.

Add **`--labels`** (either view) to title each step node with its readable label
from the Tooling API — the Connect GET carries only the spaceless `name`, so labels
cost one extra Tooling GET. A step then shows its label over the small API name; a
step whose label is missing or equals the name (Connect-clobbered drift) shows the
name alone. Label-read failure only **warns** — the diagram still renders with names.

The diagram is built from the same `_graph.py` model as the text trace, so it is
read-only, offline after the GET, and deterministic (same definition → identical
output). Highly-coupled steps (those touching hot shared variables like
`NetUnitPrice`) produce large `deps` neighborhoods — that coupling is real; scope
to a leaf-ish step or use the full `deps` view with a renderer that pans/zooms.

## Known Limitations

### Constraint (CML) Type Support

Constraint expression sets are authored in **CML** (Constraint Modeling Language) via the
Configurator Constraint Builder, not as step graphs. The Connect-overlay toolkit in this
directory works with step-graph-based procedures (Pricing, Rating, RatingDiscovery,
Qualification). For Constraint sets:

- **list** — shows `interfaceSourceType=Constraint` and basic metadata
- **describe** — shows "0 step(s), 0 variable(s)" (expected)
- **trace** — produces empty dependency graph (no orphans, no unused outputs)
- **export** — captures `contextDefinitions` but empty `steps[]`/`variables[]`
- **import/apply_overlay** — NOT applicable (CML authoring uses Configurator UI + SFDMU data)

See `docs/salesforce/264/dev-guide/` (cml_* articles) for CML authoring guidance.

### <a name="multi-version-expression-sets"></a>Multi-version expression sets

An org can hold several versions of one set, several of them active, and the
runtime runs one. Which one (`_guards.executing_version`, over the active versions
whose window covers now; the platform uses the call's effective date):

- the **highest Rank** [Dev guide: `sforce_api_objects_expressionsetversion`]: Rank 2
  ran over Rank 1 whatever the VersionNumbers, and a numeric Rank ran over a null one
  [Measured: 2026-11-24, 264, QB scratch build, disposable sets];
- among **null Ranks, the earliest created**: VersionNumber 2 created before
  VersionNumber 1 ran, and in a one-deploy pair the first-created V1 ran [Measured:
  2026-11-25, 264, QB scratch build, disposable sets];
- **equal numeric Ranks**: a deploy is refused ("Assign a unique rank to expression
  set version …"), and activating a version through the sObject API needs a Rank
  ("Enter a valid rank to enable …"), so null Ranks only come from a Metadata API
  deploy [Measured: 2026-11-24/25, 264, QB scratch build, disposable sets]. [Open:
  which version runs when two active versions share a numeric Rank; settle it by
  setting an inactive version's Rank equal to the active one's with an sObject
  update, activating it, and invoking the set, or record that the activation is
  refused.]

The rules were measured by invoking the sets directly (Connect `POST
connect/business-rules/expressionSet/{name}`, 3 of 3 calls each). The tools note
when the version that runs is not the highest-numbered one. An upgraded org can
carry `RLM_DefaultPricingProcedure` as such a chain: v1 to v4, three active, v4 ran
[Measured: 2026-09-03, 264, upgraded org (ramp264)]. Consequences:

- **A whole-set import works on a multi-version set in one shape only.**
  `import_expression_set` (toolkit and CCI) rewrites the payload's first version id
  to the version it targets (the executing one). On two-version sets, two-version
  payloads failed: named alike, on the version-name collision; target first with the
  other version renamed in the payload, on a duplicate `CalculationProcedureId`
  [Measured: 2026-11-24, 264, QB scratch build, disposable sets]. A one-version
  payload for the target failed on the version-name collision when the other
  version's `Name` equalled its label, and succeeded when it did not, where that
  `Name` had been changed by an sObject update [Measured: 2026-11-24, 264, QB scratch
  build, disposable sets] and on versions deployed with their own labels, CLI and
  CCI, the other version left untouched [Measured: 2026-11-25, 264, QB scratch build,
  disposable sets]. Both importers allow only that last shape — exactly one payload
  version, the targeted one, no other version with its label — and refuse
  everything else before any write, naming the condition that failed. [Open: the
  platform's answer to a two-version import payload on versions with their own
  labels; the importers' guard refuses it first, so settle it with a raw Connect
  PATCH of that payload on a disposable set.] To change every version in one PATCH,
  an overlay sends each under its own id. Platform version chains share one label,
  so expect a refusal there.
- **Edit the version that executes.** A change to any other version changes no
  price: a constant written into `_V1` changed no price, written into the executing
  version, VersionNumber 4 (ApiName `…_v40`), it changed every price [Measured:
  2026-09-03, 264, upgraded org (ramp264)]. Use
  `set_step_formula.py` for formula edits; it defaults to the executing version and
  reads the result back.
- **No tool picks the first version.** A tool given no version works on the
  executing one (`describe`, `trace`, `export_expression_set_overlay`, `diff` org
  sides, the overlay and import), and finds it in the Connect GET by
  `VersionNumber`, since the GET can serve a stale clone `apiName`. A definition
  with one version uses that version when none is named; a name that matches
  nothing is refused. A JSON file with several versions needs the version named.
- **A version with no Rank cannot be cycled.** Activating a version through the API
  needs a Rank ("Enter a valid rank to enable …") [Measured: 2026-11-25, 264, QB
  scratch build, disposable sets], so a run that would end by activating a null-Rank
  version fails after its change is written: an active version would be left off, a
  draft changed but not activated. These tools refuse it before any write and say to
  give the version a Rank first: `set_step_formula`, `relabel_expression_set` and
  the label restore, `import_expression_set`, `apply_expression_set_overlay`,
  `activate_expression_set --activate` and `delete_expression_set` (whose rollback
  reactivates), and the CCI `import_expression_set`, `apply_expression_set_overlay`
  and `delete_expression_set` tasks. Other activation paths do not pre-check: the
  CCI `ManageExpressionSets` tasks (`activate_expression_sets`,
  `activate_prm_expression_sets`, `activate_procedure_plan_expression_sets`, and
  `manage_expression_sets` with `operation: activate_version` or
  `activate_versions`) only set the status, so a null-Rank version fails at the
  platform's refusal with nothing else written for it. Runs without
  activation (`--no-activate`; CCI `activate_after_apply` / `activate_after_import`
  false) are allowed; `activate_expression_set --deactivate` warns that the step is
  one-way. To give a version a Rank: an sObject update of `ExpressionSetVersion.Rank`
  works on an inactive version; on an active one it is refused ("An enabled
  Expression Set Version cannot be updated/deleted."), as is a redeploy, so
  deactivate it without cascading (`activate_expression_set.py --deactivate
  --no-cascade`; it does not run while off), set a numeric Rank, higher than every
  other active version's if it should execute (equal Ranks are refused), and
  activate it again (`--activate --no-cascade`) [Measured: 2026-11-25, 264, QB
  scratch build, disposable sets]. The refusals print the activate commands filled
  with the run's org and set, and describe the Rank step.
- **An overlay sends every version.** `apply_expression_set_overlay` (toolkit and
  CCI) PATCHes the whole definition its GET returned. On two-version sets, active
  and draft, it succeeded when the versions were deployed with their own labels, and
  was rejected ("An expression set version with the name … exists in this expression
  set") when the GET returned one name for both, whether the rows' `Name` was shared
  or had been made distinct by an sObject update, which does not change the name the
  GET returns; with no version named it edited the GET's first version, the draft
  [Measured: 2026-11-25, 264, QB scratch build, disposable sets]. So both surfaces
  edit the executing version when none is named (naming another warns that pricing
  does not run it), and refuse before any write when a version in the PATCH has no
  name, shares one with another, or carries another version's `Name`, and when any
  version other than the executing one is active: the run deactivates only the
  executing version, so the PATCH would rewrite an active one. [Open: whether a
  PATCH that rewrites an active version is accepted; settle it with an overlay on a
  disposable set with two active versions, each with its own label, with the guard
  bypassed.] Deactivate the other active versions first with
  `activate_expression_set.py --deactivate --no-cascade` (a cascade would also turn
  off the procedure plans the executing version serves), or use
  `set_step_formula.py`. Platform version chains share one label and keep several
  versions active, so expect a refusal there.

In the build, `activate_and_deploy_expression_sets` reads back which version each
deployed repo procedure executes and fails when it is not the deployed one. The
deploy handler matches versions by VersionNumber, and its code path suggests a
version found under another number can be skipped silently [Platform behaviour,
traced]; the one construction measured (lower version deleted, `_V1` redeployed at
the freed number) failed the deploy loudly instead [Measured: 2026-11-24, 264, QB
scratch build, disposable sets]. The read-back reports any VersionNumber mismatch
either way. Its two read-only queries are retried on a transient error (HTTP 5xx, a
connection reset, a timeout; up to 3 attempts), while an auth or SOQL error fails at
once; a failure then says the deploy succeeded and the read-back could not run. It
runs only after a successful deploy, and that step cannot be re-run
in place on a built org: the redeploy is refused ("You can't update the expression
set version … because it's active") [Measured: 2026-11-24, 264, QB scratch build].
When it fails, run the build's remaining steps after it, in order (`cci flow info
prepare_rlm_org` lists them; a build-harness `resume` restarts at the failed step,
so it would re-run it) and, if the wrong version executes, edit or re-rank the
executing version. For future builds on an org whose chain is known, set the check
to warn: `-o version_check warn` on `cci task run activate_and_deploy_expression_sets`,
or `-o activate_and_deploy_expression_sets__version_check warn` on `cci flow run
prepare_rlm_org`.

### Discovery Procedure "Unused" Outputs

Discovery procedures (RatingDiscovery, PricingDiscovery) will show many "produced but
unused" outputs in `--orphans` analysis — these are consumed by the paired execution
procedure (Rating, Pricing) at runtime, not within the discovery graph itself. This is
expected behavior; the outputs are not dead code.

## Safety model

- **Preview by default.** Every mutator runs its transport in dry-run unless
  `--confirm` is passed: reads execute, mutating verbs are logged and skipped.
  `delete_expression_set.py` has no separate `--dry-run` flag — absence of
  `--confirm` IS the preview.
- **Never mutate a shipped procedure** (Quick Rule 8). Import/overlay/activate/
  delete only against a disposable clone (POST-create a renamed copy first).
- **A failed Connect PATCH is not atomic.** The lifecycle engine leaves the
  version DEACTIVATED and re-raises rather than reactivating a half-mutated
  definition. Re-enable it with `activate_expression_set.py --activate` once
  you've inspected and restored it. A failure **during deactivation setup**, before the
  mutation callback starts (for example the deactivation poll timing out), wrote
  nothing, so the version is restored too,
  with a forced PATCH, since the stale read that timed the poll out would make an
  idempotent one a no-op. The version and the plans are restored independently,
  and every plan is attempted before any failure is raised.
  After a failed PATCH it first confirms the version is off (a failed full-graph
  PATCH can still apply `enabled: true`), then reactivates the procedure plans it
  cascaded off (unless `--no-activate`). If the version can't be confirmed off, the
  plans stay off, and (with cascade on) any other active referencing plan is
  turned off too, so pricing can't reach a half-written version. Restoring the
  plans matters because an inactive plan is silently skipped: pricing falls back to the Revenue Settings default procedure with plausible
  numbers, while an active plan over the inactive version fails loudly. After any
  failure, including a failed reactivation, it re-reads the version and every
  referencing plan. Records the run deactivated get a restore command, except a
  version a failed PATCH may have half-written (re-import it first); other
  inactive plan versions (which may be intentional drafts) are listed for
  inspection only. **A failed label-only Tooling `Metadata`
  PATCH (the relabel path) is different** — it never touches the definition
  graph, so the stored Metadata is byte-identical after a failure and only the
  cosmetic labels are stale. That path therefore **reactivates** the version even
  on failure (`run_mutation(reactivate_on_failure=True)`), so a cosmetic relabel
  error never knocks a live procedure offline; the error is still reported.
- **Row locks are retried.** Every sObject PATCH the engine sends (version and plan
  `IsActive`, `ResourceInitializationType`) retries `UNABLE_TO_LOCK_ROW` up to four
  attempts, waiting 2, 4 and 6 seconds, as the CCI task does, whether the code is
  the error's own or quoted in its message; any error that does not mention
  `UNABLE_TO_LOCK_ROW` fails at once.
- **Default reactivation.** Every mutator defaults to `activate_after=True`, so
  applying/importing/relabeling reactivates the version on success. If you are
  operating on an **intentionally inactive** version, pass `--no-activate` or it
  will be switched on. (`--no-activate` also skips the post-PATCH label restore,
  since a relabel needs its own deactivate→reactivate window.)
- **Labels are Connect-clobbered — and auto-restored.** Step labels live only in the
  Tooling `Metadata`; every Connect PATCH (`import` / `apply_expression_set_overlay`)
  rebuilds them from the spaceless `name`. Both mutators now **capture** the readable
  labels before the PATCH and **restore** them after, in a **second
  deactivate→Tooling-PATCH→reactivate cycle** (default-on; `--no-preserve-labels` to skip).
  **This adds 30-60 seconds for large procedures** (90+ steps) due to the second
  activation cycle.
  This covers two step populations: **survivors** (restored from the pre-PATCH
  target-org snapshot — a renamed/added step simply won't match, which is correct) and
  **added or updated steps** (labeled from the overlay's own `labels` block / per-step `label`, so a
  sliced step exported `--with-labels` lands readable). Restore is **non-fatal but
  surfaced**: the Connect mutation already succeeded, so a restore failure is never
  raised — but the mutator **exits non-zero** and emits `labelRestore.ok=false` in its
  `--json` summary (with a `relabel_expression_set.py` fix hint), so an operator/CI
  never reads plain success over a version whose labels are stale. It runs only when the
  version is reactivated (`activate_after`) — a relabel needs its own deactivate window;
  with `--no-activate` the labels are left for a manual relabel. The authoritative
  `{name: label}` map is source-controlled in
  `force-app/main/default/expressionSetDefinition/*.expressionSetDefinition-meta.xml`
  — feed it to `relabel_expression_set.py --from-metadata` for a bulk manual fix.
  `--auto` is best-effort/lossy; prefer an explicit map (`--from-metadata` / `--labels-file`)
  when the true labels are known. See
  `.cursor/skills/expression-sets/metadata-vs-connect.md` → *Step names vs. labels*.
- **`--target-org` is the SF CLI alias**, never the CCI alias. CCI alias `beta`
  → SF CLI alias `rlm-base__beta`.


### Existing steps and verification

`addSteps` creates missing steps. An existing name is accepted only when its
requested content already matches; a different formula, parameter, parent, or
other supplied field fails **before deactivation or PATCH**. Use `updateSteps`
to change an existing step, or `reorderSteps` to move it. An exported `addSteps`
overlay is therefore not a formula-edit operation: move the edited entry into
`updateSteps` (and remove its `placement` metadata).

After PATCH, both the CCI task and standalone CLI re-read the selected version
and compare the final step graph with the merged payload, including formula
parameters and sequence numbers, including for variable-only overlays. Missing,
unexpected, duplicate, or changed steps fail verification; removed steps must
be absent. Named parameter order, HTML entity encoding, and an empty string
that reads back as null (such as a blank step `description`) do not count as
content changes. This verifies stored step
configuration, not execution results or step labels. The CLI's `--no-verify`
option explicitly skips this read-back.
