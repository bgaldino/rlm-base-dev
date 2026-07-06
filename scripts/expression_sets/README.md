# Expression Set helper scripts

A self-contained, full-lifecycle toolkit for Salesforce Revenue Cloud **BRE
Expression Sets** — pricing / discovery / rating / rating-discovery /
qualification procedures and constraint rules. It covers the whole lifecycle:
**inspect / export / trace / diff** (read-only), and the guarded
**create / replace / overlay / activate / delete** mutators.

Auth is delegated to the **`sf` CLI** (`sf api request rest --target-org …`), so
**no access token is ever handled or passed**. `--target-org` is always the
**SF CLI alias** (e.g. `rlm-base__beta`), **never** the CCI alias.
Pinned to Release 262 / API v67.0.

Full guidance lives in the **expression-sets skill**:
`.cursor/skills/expression-sets/SKILL.md` (+ `authoring-and-overlays.md`,
`metadata-vs-connect.md`), with the exhaustive object/ID/enum/error reference in
`docs/references/expression-set-connect-api-reference.md`.

## Independent of the CCI tasks

This package imports **nothing** from `tasks/`, and nothing under `tasks/`
imports from it. The CCI task `tasks/rlm_expression_set_connect.py` (and
`tasks/expression_set_schema.py`) is **reference-only**: the toolkit mirrors its
live-verified Connect/lifecycle rules but runs as its own program. The validator
is therefore **vendored** here as `_schema.py` rather than imported (the task
imports the canonical copy; a standalone CLI must not share an import with a CCI
task). The two encode the same platform truths independently.

**How these fit the lifecycle** (what to reach for, and when):

| Lifecycle stage | Production path | These helpers |
|-----------------|-----------------|---------------|
| **Author / apply** an expression set in the build | CCI tasks (`import_expression_set`, `apply_expression_set_overlay`, `manage_expression_sets`) + Metadata API source | the mutating CLIs below — live-proven, for one-off exploration & updates **outside** the build |
| **Inspect / trace / diff / export** a definition | — | the read-only CLIs below (safe anytime) |
| **Slice a step into a portable overlay** | — | `export_expression_set_overlay.py` (read-only; writes a local file only) |

So: the CCI tasks + Metadata API own the build; the **read-only** CLIs are always
safe; the **mutators** (`import` / `apply_expression_set_overlay` / `activate` / `delete`) are
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
| `diff_expression_set.py` | Read-only | Added / removed / changed / reordered steps + variables, org-vs-org or org-vs-JSON. |
| `export_expression_set_overlay.py` | Read-only (writes local file) | Slice step(s) from a live GET into a **validated** `addSteps` overlay with the three dependency scopes pre-classified (version deps → `addVariables`; custom refs → `externalDependencies`). `--with-labels` joins each sliced step's readable **label** (from the Tooling Metadata — Connect can't serialize it) into a top-level `labels` block, so the overlay is self-describing and `apply_expression_set_overlay` restores the label after the Connect PATCH clobbers it. |

**Mutators (preview by default; `--confirm` to write — never on a shipped procedure):**

| Script | Org? | Purpose |
|--------|------|---------|
| `import_expression_set.py` | **Mutates** | Create (POST) or replace (PATCH) a whole set from a JSON file; **auto-detects** create-vs-replace; runs the full deactivate→mutate→reactivate lifecycle. On a REPLACE it **auto-preserves step labels** (captures them before the clobbering PATCH, restores the survivors after — `--no-preserve-labels` to skip). |
| `apply_expression_set_overlay.py` | **Mutates** | Merge a declarative overlay (`addSteps` / `removeSteps` / `updateSteps` / `reorderSteps` / `addVariables` / `removeVariables`) into a live version; **all local pre-flights run BEFORE any deactivation**. **Auto-preserves step labels** (captures the survivors before the PATCH + honors any labels the overlay carries for its new steps, restores after — `--no-preserve-labels` to skip). |
| `activate_expression_set.py` | **Mutates** | `--activate` / `--deactivate` a version (+ the procedure-plan cascade), standalone. Use to re-enable a version left off by a failed apply. |
| `relabel_expression_set.py` | **Mutates** | Set readable step **labels** via the Tooling `Metadata` PATCH (the ONLY place labels live — Connect has no `label` and clobbers it on every PATCH). Label source: `--auto` (lossy derive for drift steps), `--labels-file` (`{name: label}` JSON), `--set NAME=LABEL` (repeatable), or **`--from-metadata <file>`** (read the authoritative `{name: label}` map straight from a `*.expressionSetDefinition-meta.xml` — the source-controlled `force-app/…/expressionSetDefinition/` files, or a target-org retrieve). Runs the same deactivate→PATCH→reactivate lifecycle. The Connect mutators now auto-restore labels, so this is mainly for a manual fix or a bulk relabel from the repo XML. |
| `delete_expression_set.py` | **Destructive** | Delete a whole set (Connect DELETE + cascade) or one version (`--version`). `--confirm` REQUIRED (absence of `--confirm` IS the preview). |

**Shared modules (imported by the CLIs, not run directly):**

| Module | Purpose |
|--------|---------|
| `_client.py` | The `sf api request rest` wrapper; Connect base `connect/business-rules/expression-set/{9QL}`; SOQL with `nextRecordsUrl` paging; the injectable `Transport` seam (binds `target_org` / `api_version` / `dry_run` / `logger`, short-circuits mutating verbs under dry-run). |
| `_resolve.py` | api-name → `ExpressionSetDefinition` (9QA) / `ExpressionSet` (9QL) / active `ExpressionSetVersion`; the "prefer active version" ordering. |
| `_schema.py` | **Vendored** validator + enums (mirror of `tasks/expression_set_schema.py`): `validate_definition` / `validate_overlay` / `validate_overlay_against_definition`, `_step_variable_refs` / `_step_all_refs`, `_is_custom_ref`, `INTERFACE_SOURCE_TYPES` / `USAGE_TYPES`. Stdlib-only. |
| `_payload.py` | Verb-specific field rules (strip top-level `id`; keep-and-rewrite vs strip version `id`); HTML-entity normalization (`unescape_value` / `normalize_html_entities`). Pure. |
| `_overlay.py` | Declarative step / variable merge (`add_steps` / `remove_steps` / `update_steps` / `reorder_steps` / `add_variables` / `remove_variables` / `renumber_top_level_steps`) + `overlay_labels` (harvest the `{name: label}` map an overlay carries — top-level `labels` block and/or per-`addSteps` `label`, per-step wins) + `OVERLAY_ONLY_STEP_KEYS` (`placement` / `label` — stripped from a step before the Connect send). Pure. |
| `_graph.py` | Flat `steps[]` → producer/consumer dependency graph + three-scope classifier. Imports `_schema` (in-package). Pure. |
| `_tooling.py` | Tooling-API access for step **labels** — the one thing Connect can't touch. Pure helpers (`step_labels` / `label_drift` / `readable_labels` / `humanize_name` / `derive_labels` / `apply_labels` / `strip_metadata_readonly` / `labels_from_metadata_xml` (read `{name: label}` from a `*.expressionSetDefinition-meta.xml`)) + I/O over the `Transport` (`resolve_esdv` (9QB) / `fetch_metadata` / `patch_metadata`, dropping the read-only `urls` key). **Label-preservation trio:** `capture_labels` (best-effort snapshot of the readable labels a Connect PATCH will clobber), `relabel_version` (the shared deactivate→Tooling PATCH→reactivate core, used by both `relabel_expression_set.py` and auto-restore), and `restore_labels_after_clobber` (non-fatal re-apply after a Connect mutation — re-resolves the version, restores survivors, never fails the mutation). Plus `warn_label_clobber` (best-effort pre-PATCH warning). The active-version guard applies to the Metadata PATCH exactly as to a Connect mutation. |
| `_lifecycle.py` | The `LifecycleEngine`: deactivate → PATCH/POST → reactivate sequencer, the `ProcedurePlanDefinitionVersion` cascade (with rollback), version-state polling, `ResourceInitializationType` alignment, and delete-with-rollback — all on the `Transport` seam. A failed PATCH leaves the version **DEACTIVATED** and re-raises (never reactivated over a half-mutated definition). Drives both the Connect and the Tooling-`Metadata` (relabel) mutations. |

**Tests:** `tests/test_expression_sets_toolkit.py` — offline unit tests (no org,
no `sf`, no pytest) for `_graph` / `_payload` / `_overlay` / `_tooling` (incl. the
label-preservation trio `capture_labels` / `relabel_version` /
`restore_labels_after_clobber`, `labels_from_metadata_xml`, and `overlay_labels`) /
`export_expression_set_overlay` + shipped-fixture validator parity. Run:
`python tests/test_expression_sets_toolkit.py`.

## Quick start — export → trace → slice → apply-to-clone

```bash
ORG=rlm-base__beta

# 1. See what's in the org, grouped by Revenue Cloud type.
python scripts/expression_sets/list_expression_sets.py --target-org $ORG

# 2. Export a procedure to a local JSON file (import-ready).
python scripts/expression_sets/export_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --for-import --out /tmp/pp.json

# 3. Trace a variable — who produces it, who consumes it (safe-removal view).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --variable NetUnitPrice

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

## Safety model

- **Preview by default.** Every mutator runs its transport in dry-run unless
  `--confirm` is passed: reads execute, mutating verbs are logged and skipped.
  `delete_expression_set.py` has no separate `--dry-run` flag — absence of
  `--confirm` IS the preview.
- **Never mutate a shipped procedure** (Quick Rule 8). Import/overlay/activate/
  delete only against a disposable clone (POST-create a renamed copy first).
- **A failed PATCH is not atomic.** The lifecycle engine leaves the version
  DEACTIVATED and re-raises rather than reactivating a half-mutated definition.
  Re-enable it with `activate_expression_set.py --activate` once you've inspected
  and restored it.
- **Labels are Connect-clobbered — and auto-restored.** Step labels live only in the
  Tooling `Metadata`; every Connect PATCH (`import` / `apply_expression_set_overlay`)
  rebuilds them from the spaceless `name`. Both mutators now **capture** the readable
  labels before the PATCH and **restore** them after, in a second
  deactivate→Tooling-PATCH→reactivate cycle (default-on; `--no-preserve-labels` to skip).
  This covers two step populations: **survivors** (restored from the pre-PATCH
  target-org snapshot — a renamed/added step simply won't match, which is correct) and
  **new steps** (labeled from the overlay's own `labels` block / per-step `label`, so a
  sliced step exported `--with-labels` lands readable). Restore is **non-fatal**: the
  Connect mutation already succeeded, so a restore failure is reported (with a
  `relabel_expression_set.py` fix hint), never raised. It runs only when the version is
  reactivated (`activate_after`) — a relabel needs its own deactivate window; with
  `--no-activate` the labels are left for a manual relabel. The authoritative
  `{name: label}` map is source-controlled in
  `force-app/main/default/expressionSetDefinition/*.expressionSetDefinition-meta.xml`
  — feed it to `relabel_expression_set.py --from-metadata` for a bulk manual fix.
  `--auto` is best-effort/lossy; prefer an explicit map (`--from-metadata` / `--labels-file`)
  when the true labels are known. See
  `.cursor/skills/expression-sets/metadata-vs-connect.md` → *Step names vs. labels*.
- **`--target-org` is the SF CLI alias**, never the CCI alias. CCI alias `beta`
  → SF CLI alias `rlm-base__beta`.
