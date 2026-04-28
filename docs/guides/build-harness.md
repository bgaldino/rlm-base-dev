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
- Scenario matrix: `scripts/build_harness/scenarios.json`
- TUI package: `scripts/build_harness/tui/`
- Artifacts root: `.harness/runs/<run_id>/`

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

### JSON output mode (AI-friendly)

```bash
python scripts/build_harness/harness.py run --format json
python scripts/build_harness/harness.py resume --run-id <run_id> --scenario dev-default --format json
python scripts/build_harness/harness.py report --run-id <run_id> --format json
```

### Launch the full-screen TUI

Fast path from project root:

```bash
./run-build-tui.sh
```

Manual path:

Create a scoped TUI virtual environment and install dependency:

```bash
python -m venv scripts/build_harness/tui/.venv
scripts/build_harness/tui/.venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt
```

Start the TUI:

```bash
scripts/build_harness/tui/.venv/bin/python -m scripts.build_harness.tui
```

TUI behavior:

- Reads scratch org shapes from `orgs.scratch` in `cumulusci.yml`
- Provides a 4-step wizard (org shape → alias/days → flags/start → output)
- Reads default boolean feature flags from `project.custom`
- Groups and orders flags by `project.custom` comment headers and key order
- Shows inline per-flag descriptions from `project.custom` inline comments
- Applies flag changes as runtime-only overrides (no file writes to `cumulusci.yml`)
- Creates the scratch org and then runs top-level `prepare_rlm_org` steps with live elapsed time, current step, command output, and pass/fail status
- Supports an optional default selection via `scripts/build_harness/tui/settings.json` (`default_org_shape`)

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
- `scenarios/<scenario_id>/scenario.log`

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