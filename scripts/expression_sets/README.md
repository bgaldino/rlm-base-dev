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
| **`trace_expression_set.py`** | Read-only | **Flagship** — variable producer→consumer graph + three-scope classifier (version / custom / standard). `--variable` (safe-removal view), `--step` (dependency closure + capture guidance), `--field`, `--orphans`. `--mermaid deps\|flow` renders a diagram (`--out` to a `.mmd` file); `--step` scopes `deps` to one step's neighborhood. |
| `diff_expression_set.py` | Read-only | Added / removed / changed / reordered steps + variables, org-vs-org or org-vs-JSON. |
| `export_expression_set_overlay.py` | Read-only (writes local file) | Slice step(s) from a live GET into a **validated** `addSteps` overlay with the three dependency scopes pre-classified (version deps → `addVariables`; custom refs → `externalDependencies`). |

**Mutators (preview by default; `--confirm` to write — never on a shipped procedure):**

| Script | Org? | Purpose |
|--------|------|---------|
| `import_expression_set.py` | **Mutates** | Create (POST) or replace (PATCH) a whole set from a JSON file; **auto-detects** create-vs-replace; runs the full deactivate→mutate→reactivate lifecycle. |
| `apply_expression_set_overlay.py` | **Mutates** | Merge a declarative overlay (`addSteps` / `removeSteps` / `updateSteps` / `reorderSteps` / `addVariables` / `removeVariables`) into a live version; **all local pre-flights run BEFORE any deactivation**. |
| `activate_expression_set.py` | **Mutates** | `--activate` / `--deactivate` a version (+ the procedure-plan cascade), standalone. Use to re-enable a version left off by a failed apply. |
| `relabel_expression_set.py` | **Mutates** | Set readable step **labels** via the Tooling `Metadata` PATCH (the ONLY place labels live — Connect has no `label` and clobbers it on every PATCH). `--auto` (lossy derive for drift steps), `--labels-file` (`{name: label}` JSON), `--set NAME=LABEL` (repeatable). Runs the same deactivate→PATCH→reactivate lifecycle. **Run LAST** — any later Connect import/overlay clobbers the labels. |
| `delete_expression_set.py` | **Destructive** | Delete a whole set (Connect DELETE + cascade) or one version (`--version`). `--confirm` REQUIRED (absence of `--confirm` IS the preview). |

**Shared modules (imported by the CLIs, not run directly):**

| Module | Purpose |
|--------|---------|
| `_client.py` | The `sf api request rest` wrapper; Connect base `connect/business-rules/expression-set/{9QL}`; SOQL with `nextRecordsUrl` paging; the injectable `Transport` seam (binds `target_org` / `api_version` / `dry_run` / `logger`, short-circuits mutating verbs under dry-run). |
| `_resolve.py` | api-name → `ExpressionSetDefinition` (9QA) / `ExpressionSet` (9QL) / active `ExpressionSetVersion`; the "prefer active version" ordering. |
| `_schema.py` | **Vendored** validator + enums (mirror of `tasks/expression_set_schema.py`): `validate_definition` / `validate_overlay` / `validate_overlay_against_definition`, `_step_variable_refs` / `_step_all_refs`, `_is_custom_ref`, `INTERFACE_SOURCE_TYPES` / `USAGE_TYPES`. Stdlib-only. |
| `_payload.py` | Verb-specific field rules (strip top-level `id`; keep-and-rewrite vs strip version `id`); HTML-entity normalization (`unescape_value` / `normalize_html_entities`). Pure. |
| `_overlay.py` | Declarative step / variable merge (`add_steps` / `remove_steps` / `update_steps` / `reorder_steps` / `add_variables` / `remove_variables` / `renumber_top_level_steps`). Pure. |
| `_graph.py` | Flat `steps[]` → producer/consumer dependency graph + three-scope classifier. Imports `_schema` (in-package). Pure. |
| `_tooling.py` | Tooling-API access for step **labels** — the one thing Connect can't touch. Pure helpers (`step_labels` / `label_drift` / `readable_labels` / `humanize_name` / `derive_labels` / `apply_labels` / `strip_metadata_readonly`) + I/O over the `Transport` (`resolve_esdv` (9QB) / `fetch_metadata` / `patch_metadata`, dropping the read-only `urls` key) + `warn_label_clobber` (best-effort, non-fatal pre-PATCH warning the Connect mutators call). The active-version guard applies to the Metadata PATCH exactly as to a Connect mutation. |
| `_lifecycle.py` | The `LifecycleEngine`: deactivate → PATCH/POST → reactivate sequencer, the `ProcedurePlanDefinitionVersion` cascade (with rollback), version-state polling, `ResourceInitializationType` alignment, and delete-with-rollback — all on the `Transport` seam. A failed PATCH leaves the version **DEACTIVATED** and re-raises (never reactivated over a half-mutated definition). Drives both the Connect and the Tooling-`Metadata` (relabel) mutations. |

**Tests:** `tests/test_expression_sets_toolkit.py` — offline unit tests (no org,
no `sf`, no pytest) for `_graph` / `_payload` / `_overlay` / `_tooling` /
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

# 6. Apply it for real.
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json --confirm

# 7. LAST — restore readable step labels (Connect mutations above clobber them to
#    the spaceless names). Inspect drift, then relabel via the Tooling Metadata PATCH.
python scripts/expression_sets/describe_expression_set.py --target-org $ORG \
    --developer-name RLM_MyClone --labels          # shows label==name drift
python scripts/expression_sets/relabel_expression_set.py --target-org $ORG \
    --expression-set RLM_MyClone --labels-file /tmp/labels.json --confirm
```

## Visualizing a procedure (Mermaid)

`trace_expression_set.py --mermaid` emits a [Mermaid](https://mermaid.js.org/)
diagram to stdout (or a `.mmd` file with `--out`). Paste it into any Mermaid
renderer — `mermaid.live`, a GitHub Markdown ` ```mermaid ` fence, or the VS Code
Mermaid preview. Two views:

- **`--mermaid flow`** — execution order: top-level steps chained by their
  `sequenceNumber`, each `ListGroup`/parent's children hanging off it by a dashed
  `child` edge. The "what does this procedure do, in order" view.
- **`--mermaid deps`** (the default) — the data-dependency graph: steps are boxes,
  every referenced variable is a rounded node **colored by scope** (green =
  version variable → ship in `addVariables`; red = custom `__c`/`__r` →
  `externalDependencies`; blue = standard context → declare nothing). Edge labels
  carry the role symbol (`>` produces, `<` consumes, `?` filter criterion,
  `~` best-effort Formula token). Add `--step "<name>"` to scope the diagram to
  that step plus the variables it touches and their immediate neighbor steps —
  the drawn form of the `--step` text closure.

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
- **Labels are Connect-clobbered; relabel LAST.** Step labels live only in the
  Tooling `Metadata`; every Connect PATCH (`import` / `apply_expression_set_overlay`)
  rebuilds them from the spaceless `name`. Those two mutators now **warn**
  (best-effort, non-fatal) before the PATCH — "N readable labels will be reset" —
  in both preview and confirm, so the loss is never silent. Run
  `relabel_expression_set.py` as the final step, after all Connect mutations —
  anything Connect afterward wipes the labels again. `--auto` is best-effort/lossy;
  prefer an explicit `{name: label}` map (`--labels-file`) when the true labels
  are known. See `.cursor/skills/expression-sets/metadata-vs-connect.md` →
  *Step names vs. labels*.
- **`--target-org` is the SF CLI alias**, never the CCI alias. CCI alias `beta`
  → SF CLI alias `rlm-base__beta`.
