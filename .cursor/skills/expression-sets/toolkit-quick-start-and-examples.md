# Toolkit quick start, CCI tasks, timings and example overlays

Progressive-disclosure sub-file of `.cursor/skills/expression-sets/SKILL.md`. Worked command sequence, the CCI task table, measured run times and the shipped overlay examples.

## <a name="running-the-tools"></a>Running the tools (agents, sandboxes, long procedures)

- **Run times.** Read tools take seconds. `import_expression_set.py`, `set_step_formula.py`
  and `apply_expression_set_overlay.py` take minutes on a large procedure (the overlay
  apply ran past two minutes on a 124-step clone and past 110 seconds on the 121-step
  default [Measured: 2026-11-26, 264, ent-sb0 harness build]). By default they block
  until the version is active again, so run them in the background with a timeout of 600
  seconds or more, then read the output.
- **Submit, then wait (for a foreground limit such as 120 s).** Add `--no-wait` to
  `import_expression_set.py`, `set_step_formula.py` or `apply_expression_set_overlay.py`.
  The run still waits for the deactivation (the write needs it), reactivates any cascaded
  procedure plans, submits the version's reactivation and exits 0 without polling it. It
  prints the exact `activate_expression_set.py ... --wait` command that confirms it. If
  the version already reads active at that point the run just carries on as usual and
  prints no follow-up. `--wait` is read-only: it polls `IsActive` (default `--timeout
  600`), and exits 1 with the state reached if the version is still off at the timeout
  (re-run it to keep waiting; no `--confirm`). While the version is unconfirmed, the
  overlay and import tools skip the step-label restore (they print a relabel command
  that reactivates the version) and the overlay and formula tools skip their read-back,
  so repeat those after the wait:

  ```bash
  python scripts/expression_sets/set_step_formula.py --target-org <sf_alias> \
    --expression-set <Set> --step <Step> --formula '<expr>' --confirm --no-wait
  # prints: Wait for it with: python scripts/expression_sets/activate_expression_set.py \
  #   --target-org <sf_alias> --expression-set <Set> --version <Set_V1> --wait --timeout 600
  python scripts/expression_sets/activate_expression_set.py --target-org <sf_alias> \
    --expression-set <Set> --version <Set_V1> --wait --timeout 100   # repeat until exit 0
  python scripts/expression_sets/set_step_formula.py --target-org <sf_alias> \
    --expression-set <Set> --step <Step> --show                      # read the formula back
  ```
- **Check the end state.** `apply_expression_set_overlay.py` reads the version back after
  `--confirm`, prints `Final ExpressionSetVersion ... IsActive=<bool>` and exits 1 when
  activation was requested and the version is off (`finalIsActive` in `--json`) [Repo:
  `scripts/expression_sets/apply_expression_set_overlay.py`]. A structural rejection
  mid-PATCH (for example removing the last step of a group: "<step> can't be the last
  step in a group") leaves the version inactive and recoverable only by a full re-import
  [Measured: 2026-11-26, 264, ent-sb0 harness build]. The overlay
  pre-check now refuses that removal before any write, and `removeSteps` entries are
  objects (`{"name": "<step>"}`), not bare strings [Repo: `scripts/expression_sets/_schema.py`].
  After any run, confirm with `list_expression_sets.py --versions`.
- **Previews.** Without `--confirm` every lifecycle line carries a `[preview]` prefix; none
  of them ran.
- **Sandboxed `sf`.** The scripts set `SF_DISABLE_LOG_FILE=true` for the `sf` child, so a
  read-only home no longer surfaces as an alias or auth error. The harmless
  `failed to copy trust settings` line goes to stderr; use `2>/dev/null` when you parse
  `sf ... --json` yourself.
- **Tool gaps.** `set_step_formula.py` changes formulas only: there is no tool that edits
  a list-group filter's criteria, so that change is a full re-import (or an overlay
  `updateSteps`). To label a clone, export with
  `export_expression_set.py --for-import --with-labels` (adds a top-level `labels` block read from
  the Tooling metadata), rename it, and import: the importer applies the block through Tooling
  after the create (119 labels on a clone of the default pricing procedure, version left
  active) [Measured: 2026-11-26, 264, ent-sb0 harness build; run time several minutes]. A
  replace layers the block onto the target version's captured labels. `--no-preserve-labels`
  skips it.

## <a name="quick-start"></a>Quick Start

Export → trace → slice a validated overlay → apply to a **disposable clone** —
using the standalone toolkit (`--target-org` is the *SF CLI* alias, never the CCI
alias):

```bash
ORG=rlm-base__beta

# 1. What's in the org, grouped by Revenue Cloud type.
python scripts/expression_sets/list_expression_sets.py --target-org $ORG

# 2. Export a procedure (import-ready: stripped + HTML-unescaped).
python scripts/expression_sets/export_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --for-import --out /tmp/pp.json

# 3. Trace a variable: who produces it, who consumes it (safe-removal view).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --variable NetUnitPrice

# 3b. Or draw it — a kind-shaped Mermaid dependency graph (or --mermaid flow).
#     --labels titles step nodes with their readable Tooling label (Connect has none).
python scripts/expression_sets/trace_expression_set.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --mermaid deps --labels --out /tmp/pp.deps.mmd

# 4. Slice a step into a validated overlay (three scopes pre-classified).
python scripts/expression_sets/export_expression_set_overlay.py --target-org $ORG \
    --developer-name RLM_DefaultPricingProcedure --step "Apply Discount" \
    --out /tmp/apply_discount.overlay.json

# 5. Preview applying it to a clone (no --confirm = no write), then apply.
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json

# 6. Apply for real. Wait for "Successfully applied overlay" message — label
#    restoration runs a second cycle, taking 30-60s for large procedures.
python scripts/expression_sets/apply_expression_set_overlay.py --target-org $ORG \
    --expression-set RLM_MyClone --overlay /tmp/apply_discount.overlay.json --confirm

# 7. Verify labels were preserved
python scripts/expression_sets/describe_expression_set.py --target-org $ORG \
    --developer-name RLM_MyClone --labels
```

## The CCI tasks

`tasks/rlm_expression_set_connect.py` wraps
`/connect/business-rules/expression-set` and handles the activation lifecycle,
HTML-entity normalization, version-id rules, and the procedure-plan cascade.

| Task | Verb | Use |
|---|---|---|
| `export_expression_set` | GET | Export a definition to JSON (`-o expression_set_api_name <DevName> -o output_file <path>`). |
| `import_expression_set` | POST create / PATCH replace | Create a new ES or replace an existing one whole (`-o input_file <path>`). Auto-detects create vs replace from whether the ES already exists. |
| `apply_expression_set_overlay` | declarative PATCH | Add/remove/update/reorder steps & variables without rewriting the whole definition (`-o overlay_file <path>`). |
| `delete_expression_set` | DELETE | Destructive; requires `-o confirm true`. Whole ES, or one version via `-o version_api_name`. |
| `validate_expression_set` | — (org-less) | Pre-flight a JSON file offline: `-o file <path> -o kind definition\|overlay`. CLI form: `python scripts/ai/validate_expression_set.py <file> [--definition\|--overlay]`. |

Common options on the mutation tasks: `dry_run` (log without mutating),
`skip_validation` (bypass the pre-flight — avoid), `normalize_html_entities`
(default true — leave on), `activate_after_import`/`activate_after_apply`,
`cascade_deactivate_procedure_plan`, `max_wait_seconds`/`poll_interval_seconds`.

## Performance Expectations

For reference, a 93-step pricing procedure (live-tested 2026-07-08):
- **Read operations** (list, describe, export, trace, Mermaid): 3-5 seconds
- **Import (CREATE):** ~45 seconds
- **Overlay application (with label preservation):** ~60 seconds
- **Overlay application (--no-preserve-labels):** ~30 seconds

The bulk of time is spent in version activation polling and large payload
transmission (129KB+ JSON for 93 steps). Use `--no-preserve-labels` if speed is
critical, then run a manual `relabel_expression_set.py` batch later.

## Examples

Shipped overlays in `datasets/expression_set_overlays/` are generally
applicable examples. Environment-specific examples live under
`docs/references/expression-set-overlay-examples/` so they remain available for
study without looking like safe default overlays. Capture each from a live GET,
HTML-unescape, validate, cross-check, then apply to a **disposable clone** before
any real target.

| Overlay | Shape | Dependency scopes demonstrated |
|---|---|---|
| `map_line_item.json` | flat, single step (`actionType: BreakdownLineMapping`; maps `SalesTransactionItem` → `SalesTransactionItemDetail`, 18 `sectionJsonStringN` field-mappings) | standard context only — no `addVariables`, no `externalDependencies` |
| `discount_distribution.json` | **nested** — 3 `ListGroup` parents (each with an `AdvancedListFilter` + `AssignmentElement` child) feeding a `DiscountDistributionService` element | ships 4 `Constant_DDS_*` constants in `addVariables`; rest standard context (incl. `__std` discount fields) → no `externalDependencies` |
| `docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json` | **Environment-specific reference** — 2 `ListGroup` blocks, incl. a `FormulaBasedPricing` child computing `SalesTransaction_Hospitals__c - ItemStartQuantity` | **all three scopes**: `HospitalPrice` in `addVariables`; the custom field `SalesTransaction_Hospitals__c` (mapped into `RLM_SalesTransactionContext`) in `externalDependencies`; `ItemProductCode`/`ItemStartQuantity`/etc. standard context |

The facility-quantity example is intentionally not in
`datasets/expression_set_overlays/`: it depends on an org-specific custom field,
context mapping, and procedure-shape anchor. It also shows that a custom field
can be referenced inside a `Formula` string, not just a `Parameter`, so the
dependency scan must tokenize formula text, which the validator does.

### Map Line Item — special case

How to configure the Map Line Item element (`BreakdownLineMapping`), where it sits and its
`sectionJsonStringN` encoding is in
[`../pricing-procedures/elements/map-line-item.md`](../pricing-procedures/elements/map-line-item.md).
For the overlay mechanics here: author the `sectionJsonStringN` values **unescaped**, or
deploy the same shape as an `expressionSetDefinition` `<steps>` block.
