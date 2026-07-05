# Expression Set helper scripts

A self-contained, full-lifecycle toolkit for Salesforce Revenue Cloud **BRE
Expression Sets** — pricing / discovery / rating / rating-discovery /
qualification procedures and constraint rules. It covers the whole lifecycle:
**inspect / export / trace / diff** (read-only), and the guarded
**create / replace / overlay / activate / delete** mutators.

Auth is delegated to the **`sf` CLI** (`sf api request rest --target-org …`), so
**no access token is ever handled or passed**. `--target-org` is always the
**SF CLI alias** (e.g. `rlm-base__july4_ctxPilot`), **never** the CCI alias.
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
| **Slice a step into a portable overlay** | — | `export_overlay.py` (read-only; writes a local file only) |

So: the CCI tasks + Metadata API own the build; the **read-only** CLIs are always
safe; the **mutators** (`import` / `apply_overlay` / `activate` / `delete`) are
**preview-by-default** and require `--confirm` to write — use them for one-off
exploration and updates on a **disposable clone**, never a shipped procedure
(Quick Rule 8).

## Scripts

**Read-only inspectors (safe anytime):**

| Script | Org? | Purpose |
|--------|------|---------|
| `list_expression_sets.py` | Read-only | One row per set: `interfaceSourceType` (the RC type), `usageType`, active version, IsActive — grouped by type. |
| `describe_expression_set.py` | Read-only | Pretty-print one set: version → steps in execution (per-parent `sequenceNumber`) order → params / variables. `--params` for the full parameter dump. |
| `export_expression_set.py` | Read-only | GET a definition → JSON file (the read half of the round trip). `--for-import` strips read-only fields + HTML-unescapes so the output is import-ready. |
| **`trace_expression_set.py`** | Read-only | **Flagship** — variable producer→consumer graph + three-scope classifier (version / custom / standard). `--variable` (safe-removal view), `--step` (dependency closure + capture guidance), `--field`, `--orphans`. |
| `diff_expression_set.py` | Read-only | Added / removed / changed / reordered steps + variables, org-vs-org or org-vs-JSON. |
| `export_overlay.py` | Read-only (writes local file) | Slice step(s) from a live GET into a **validated** `addSteps` overlay with the three dependency scopes pre-classified (version deps → `addVariables`; custom refs → `externalDependencies`). |

**Mutators (preview by default; `--confirm` to write — never on a shipped procedure):**

| Script | Org? | Purpose |
|--------|------|---------|
| `import_expression_set.py` | **Mutates** | Create (POST) or replace (PATCH) a whole set from a JSON file; **auto-detects** create-vs-replace; runs the full deactivate→mutate→reactivate lifecycle. |
| `apply_overlay.py` | **Mutates** | Merge a declarative overlay (`addSteps` / `removeSteps` / `updateSteps` / `reorderSteps` / `addVariables` / `removeVariables`) into a live version; **all local pre-flights run BEFORE any deactivation**. |
| `activate_expression_set.py` | **Mutates** | `--activate` / `--deactivate` a version (+ the procedure-plan cascade), standalone. Use to re-enable a version left off by a failed apply. |
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
| `_lifecycle.py` | The `LifecycleEngine`: deactivate → PATCH/POST → reactivate sequencer, the `ProcedurePlanDefinitionVersion` cascade (with rollback), version-state polling, `ResourceInitializationType` alignment, and delete-with-rollback — all on the `Transport` seam. A failed PATCH leaves the version **DEACTIVATED** and re-raises (never reactivated over a half-mutated definition). |

**Tests:** `test_expression_sets_toolkit.py` — offline unit tests (no org, no
`sf`, no pytest) for `_graph` / `_payload` / `_overlay` / `export_overlay` +
shipped-fixture validator parity. Run:
`python scripts/expression_sets/test_expression_sets_toolkit.py`.

## Quick start — export → trace → slice → apply-to-clone

```bash
ORG=rlm-base__july4_ctxPilot

# 1. See what's in the org, grouped by Revenue Cloud type.
python scripts/expression_sets/list_expression_sets.py --target-org $ORG

# 2. Export a procedure to a local JSON file (import-ready).
python scripts/expression_sets/export_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --for-import --out /tmp/pp.json

# 3. Trace a variable — who produces it, who consumes it (safe-removal view).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --variable NetUnitPrice

# 4. Slice a step into a validated overlay (three scopes pre-classified).
python scripts/expression_sets/export_overlay.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --step "Apply Discount" \
    --out /tmp/apply_discount.overlay.json

# 5. Preview applying that overlay to a DISPOSABLE CLONE (no --confirm = no write).
python scripts/expression_sets/apply_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json

# 6. Apply it for real.
python scripts/expression_sets/apply_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json --confirm
```

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
- **`--target-org` is the SF CLI alias**, never the CCI alias. CCI alias `beta`
  → SF CLI alias `rlm-base__beta`.
