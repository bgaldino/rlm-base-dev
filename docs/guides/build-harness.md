# Build Harness Guide

This guide describes the local build harness for profiling `prepare_rlm_org` against the primary scratch org shapes:

- `orgs/dev.json`
- `orgs/ent.json`

The harness is designed for both human operators and AI agents.

## Goals

- Profile build duration and failure hotspots by scenario
- Compare `dev` vs `ent` behavior under the same flag bundles
- Persist checkpoint data for step-level resume
- Emit machine-readable run artifacts for automated analysis

## Files

- Runner: `scripts/build_harness/harness.py`
- Harness modules: `scripts/build_harness/harness/`
- Scenario matrix: `scripts/build_harness/scenarios.json`
- TUI package: `scripts/build_harness/tui/`
- TUI launcher: `./tui-cci`
- Artifacts root: `.harness/runs/<run_id>/`

`harness.py` is the CLI entrypoint (`run`, `resume`, `report`).
Execution, config loading, reporting, and provenance logic live under
`scripts/build_harness/harness/` for easier maintenance.
Notable shared modules:

- `harness/io.py` — JSON/JSONL/UTC/directory helpers and run pruning helpers
- `harness/failure.py` — shared transient/deterministic signature classification for CLI + TUI

## Scenario Model

Each scenario includes:

- `scenario_id`
- `org_shape` (`dev` or `ent`)
- `org_alias_prefix`
- `days`
- `flag_overrides`
- `notes`

`flag_overrides` are merged with `project.custom` defaults in `cumulusci.yml`.
The harness materializes each scenario into a scenario-scoped CCI project root with
an overridden `cumulusci.yml`, so CCI `when:` evaluation (including nested
sub-flows/tasks) uses the scenario's effective flags at execution time.

## Commands

### Run all scenarios

```bash
python scripts/build_harness/harness.py run
```

### Run a subset

```bash
python scripts/build_harness/harness.py run --scenario dev-default --scenario ent-default
```

### Resume from checkpoint

```bash
python scripts/build_harness/harness.py resume --run-id <run_id> --scenario dev-default
```

### Render report

```bash
python scripts/build_harness/harness.py report --run-id <run_id>
```

### Prune old run artifacts (opt-in)

```bash
python scripts/build_harness/harness.py prune --prune-older-than 7d
```

Optional prune can also run before `run` or `report`:

```bash
python scripts/build_harness/harness.py run --prune-older-than 7d
python scripts/build_harness/harness.py report --run-id <run_id> --prune-older-than 7d
```

`report` also (re)writes analysis artifacts and backfills
`build_provenance.json` for each scenario in that run.

### JSON output mode (AI-friendly)

```bash
python scripts/build_harness/harness.py run --format json
python scripts/build_harness/harness.py resume --run-id <run_id> --scenario dev-default --format json
python scripts/build_harness/harness.py report --run-id <run_id> --format json
```

### Launch the full-screen TUI

Fast path from project root:

```bash
./tui-cci
```

Manual path:

The wrapper creates and reuses a repo-scoped venv at `.harness/tui-venv`.
Use `--upgrade` to force a dependency refresh:

```bash
./tui-cci --upgrade
```

TUI behavior:

- Reads scratch org shapes from `orgs.scratch` in `cumulusci.yml`
- Provides a 4-step wizard (org shape → alias/days → flags/start → output)
- Reads default boolean feature flags from `project.custom`
- Groups and orders flags by `project.custom` comment headers and key order
- Shows inline per-flag descriptions from `project.custom` inline comments
- Applies flag changes as runtime-only overrides (no file writes to `cumulusci.yml`)
- Uses pill-style runtime toggles (`○ OFF` / `ON ●`) for boolean flag overrides
- Supports optional local settings in `scripts/build_harness/tui/settings.json`:
  - `default_org_shape`: preselect shape in Step 1
  - `theme_mode`: `auto`, `light`, or `dark`
- Supports `Set Default Org` from Command Palette (`Ctrl+P`) to persist the currently highlighted/selected shape
- Auto-generates alias defaults as `<shape>-<4char>` and retries on alias collisions
- Separates scratch-org startup timing before top-level `prepare_rlm_org` steps:
  - runs `cci org scratch <shape> <alias> --days <n>` (register alias/config)
  - then runs `cci org info <alias>` (forces materialization/credential refresh)
  - then runs top-level `prepare_rlm_org` steps
- Runs top-level `prepare_rlm_org` steps with:
  - TUI runtime overrides materialized into a per-run `cci_project` so CCI subprocesses evaluate `when:` against the selected overrides
  - live `Total Elapsed` (freezes when run ends)
  - live per-step duration updates in the table
  - auto-scroll to newly started step rows
  - command output and pass/fail status
  - completion banner on success/failure/cancel
  - `Stop Build` button while running that switches to `New Build` after completion
- On run failure, attempts scratch delete only when the org was created in that same run

## `when:` evaluation semantics

`harness/config.py::evaluate_when` uses a safe AST evaluator for the subset of
CCI `when:` expressions used by this repo:

- `project_config.project__custom__<flag>`
- `org_config.scratch`
- `org_config.name`
- `and` / `or` / `not` and parentheses
- `==` / `!=` with string or boolean literals

Unsupported expression forms are treated as `True` (fail-open) to match CCI's
defensive behavior and avoid silent step skips.

## Tests

Run the harness unit test suite from repo root:

```bash
.harness/tui-venv/bin/python -m pytest tests/build_harness/
```

## Resume Behavior

The harness executes top-level `prepare_rlm_org` steps in order by reading `flows.prepare_rlm_org.steps` from `cumulusci.yml`.

On each successful step, it writes `checkpoint.json`:

- `last_successful_step`
- `last_successful_target`
- `org_alias`
- `effective_flags`

If a step fails, `failed_step` and failure metadata are written. `resume` continues from the failed step.

Resume safety guard:

- resume is blocked when current scenario effective flags do not match checkpoint `effective_flags`

Phase-1 resume scope is top-level `prepare_rlm_org` steps only. Nested sub-flow task-level resume is intentionally out of scope.

## Output Artifacts

Each run writes:

- `run_manifest.json` - run inputs and selected scenarios
- `run_summary.json` - status summary across scenarios
- `report.md` - human-readable report
- `agent_summary.md` - concise decision-oriented summary
- `compatibility_summary.json` - pass/fail matrix with failed signatures and flag involvement
- `dependency_summary.json` - observed step outcomes and failure predecessor hints
- `optimization_recommendations.json` - top slow steps ranked with effort/impact heuristics
- `scenarios/<scenario_id>/scenario_manifest.json`
- `scenarios/<scenario_id>/step_results.jsonl`
- `scenarios/<scenario_id>/checkpoint.json`
- `scenarios/<scenario_id>/build_provenance.json`
- `scenarios/<scenario_id>/scenario.log`

`build_provenance.json` includes:

- run-level provenance (`git_sha`, command, start time)
- scenario identity (`scenario_id`, `org_alias`, `org_shape`)
- effective flags snapshot
- checkpoint summary
- `stamp_git_commit` event details and parsed stamp output (when present)

`report.md` includes:

- per-scenario compatibility status
- failed step signatures
- flag involvement summary
- dependency hints from observed failed-step predecessors
- optimization recommendations (slowest observed steps)

## Exit Codes

- `0` - success
- `10` - scenario/build failure
- `20` - harness configuration/validation error
- `30` - resume blocked (missing run/checkpoint/org)

## Agent Policy

The harness applies policy metadata in `run_summary.json` per scenario:

- `recommended_action`: `none`, `resume`, `rerun_full`, `manual_fix_required`
- `confidence`: `high`, `medium`, `low`
- `operator_message`: suggested next command

Failure classes are heuristic:

- `transient`: timeout/network/platform availability patterns
- `deterministic`: configuration/schema/validation patterns
- `unknown`: not clearly classified

For failed runs, orgs are kept by default so resume can continue from checkpoint.
Use `--keep-orgs` if you also want to keep successful orgs for debugging.