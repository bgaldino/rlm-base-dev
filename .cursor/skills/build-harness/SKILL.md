---
name: build-harness
description: Run, resume, report, test, or update the local build harness for prepare_rlm_org profiling and the CCI Build Manager TUI. Use when working with scripts/build_harness, .harness run artifacts, harness scenarios, checkpoint resume behavior, TUI scratch org creation, or build-harness tests.
---

# Build Harness

Use this skill when working with the local build harness for:

- automated profiling/testing runs of `prepare_rlm_org`
- investigation of `.harness/runs/<run_id>/` artifacts
- implementation or test changes under `scripts/build_harness/`
- creating a scratch org for an end user through the harness/TUI path

## Trigger Conditions

Use this skill when the request includes any of the following:

- run, resume, or report a build harness run
- profile `prepare_rlm_org` behavior across `dev`/`ent` scenarios
- investigate harness artifacts in `.harness/runs/<run_id>/`
- modify `scripts/build_harness/`, `scripts/build_harness/tui/`, or `tests/build_harness/`
- explain or change harness scenario flags, checkpointing, failure classification, or TUI behavior
- create a scratch org for a user using the harness TUI

## Non-Trigger Conditions

Do **not** use this skill when:

- running normal one-off CCI tasks/flows without harness orchestration
- editing SFDMU plans, Robot tests, or metadata not related to harness usage
- deploying metadata or managing scratch orgs outside the harness/TUI path

## Quick Rules

1. Use stable harness commands from repo root: `python scripts/build_harness/harness.py run|resume|report`.
2. Prefer scenario-based runs from `scripts/build_harness/scenarios.json`.
3. For resume, keep scenario id and flags consistent with checkpoint.
4. Use JSON mode (`--format json`) when another agent or script needs structured output.
5. Run focused harness tests after implementation changes: `.harness/tui-venv/bin/python -m pytest tests/build_harness/`.
6. For end-user org creation, default to shape `ent`, days `30`, alias auto-generated.
7. **Before creating the org, ask the user to confirm or override all three defaults** (shape, days, alias).
8. Cleanup semantics differ by entrypoint: harness CLI keeps failed orgs for resume; TUI auto-deletes on failure by default only if the org was created in the current run. Set `delete_org_on_failure: false` in `scripts/build_harness/tui/settings.local.json` to preserve failed TUI orgs.

## DO NOT

- **DO NOT** delete scratch orgs without clear user intent.
- **DO NOT** run destructive cleanup steps (`scratch_delete`) on ambiguous aliases.
- **DO NOT** attempt resume when scenario flags changed from checkpoint; re-run instead.
- **DO NOT** bypass the TUI/CLI materialized `cci_project` path when validating runtime flag overrides.
- **DO NOT** edit generated per-scenario `.harness/**/cci_project/cumulusci.yml` as source of truth; edit repo-root `cumulusci.yml` or scenario config instead.

---

## Harness Mental Model

The CLI harness profiles `prepare_rlm_org` by running scenarios from `scripts/build_harness/scenarios.json` against scratch orgs and writing structured artifacts under `.harness/runs/<run_id>/`.

Current scenario matrix:

- `dev-default`
- `ent-default`
- `dev-lightweight`
- `ent-lightweight`

`flag_overrides` are merged with `project.custom` defaults from `cumulusci.yml`. The CLI materializes each scenario into `scenarios/<scenario_id>/cci_project/` with an override-aware `cumulusci.yml`, then runs CCI from that project root so nested `when:` checks see the scenario flags.

Key modules:

- `scripts/build_harness/harness.py` - CLI entrypoint
- `scripts/build_harness/harness/config.py` - CCI/scenario loading, flag composition, safe `when:` evaluation, scenario project materialization
- `scripts/build_harness/harness/scenario_runner.py` - scenario execution and checkpointing
- `scripts/build_harness/harness/execution.py` - subprocess execution and run ids
- `scripts/build_harness/harness/failure.py` - transient/deterministic failure signatures
- `scripts/build_harness/harness/provenance.py` - stamp parsing and provenance output
- `scripts/build_harness/harness/reporting.py` - reports and analysis artifacts
- `scripts/build_harness/harness/io.py` - JSON/JSONL/time/directory helpers
- `scripts/build_harness/tui/` - Textual CCI Build Manager TUI

## Command Recipes

### Run all scenarios

```bash
python scripts/build_harness/harness.py run
```

### Run selected scenarios

```bash
python scripts/build_harness/harness.py run --scenario dev-default --scenario ent-default
```

### Keep successful orgs for debugging

```bash
python scripts/build_harness/harness.py run --scenario ent-default --keep-orgs
```

### Resume a failed scenario

```bash
python scripts/build_harness/harness.py resume --run-id <run_id> --scenario <scenario_id>
```

### Render report

```bash
python scripts/build_harness/harness.py report --run-id <run_id>
```

### Prune old run artifacts (opt-in)

```bash
python scripts/build_harness/harness.py prune --prune-older-than 7d
python scripts/build_harness/harness.py run --prune-older-than 7d
python scripts/build_harness/harness.py report --run-id <run_id> --prune-older-than 7d
```

### JSON mode for agent automation

```bash
python scripts/build_harness/harness.py run --format json
python scripts/build_harness/harness.py resume --run-id <run_id> --scenario <scenario_id> --format json
python scripts/build_harness/harness.py report --run-id <run_id> --format json
```

### Run harness tests

```bash
.harness/tui-venv/bin/python -m pytest tests/build_harness/
```

If the repo-scoped TUI venv is missing:

```bash
python -m venv .harness/tui-venv
.harness/tui-venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt
.harness/tui-venv/bin/python -m pytest tests/build_harness/
```

## Run Artifacts to Inspect

CLI harness runs:

- `.harness/runs/<run_id>/run_manifest.json`
- `.harness/runs/<run_id>/run_summary.json`
- `.harness/runs/<run_id>/report.md`
- `.harness/runs/<run_id>/agent_summary.md`
- `.harness/runs/<run_id>/compatibility_summary.json`
- `.harness/runs/<run_id>/dependency_summary.json`
- `.harness/runs/<run_id>/optimization_recommendations.json`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/scenario_manifest.json`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/step_results.jsonl`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/checkpoint.json`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/build_provenance.json`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/scenario.log`

TUI runs, when `persistent_logging` is enabled:

- `.harness/tui-runs/<run_id>/run_manifest.json`
- `.harness/tui-runs/<run_id>/events.jsonl`
- `.harness/tui-runs/<run_id>/command-output.log`
- `.harness/tui-runs/<run_id>/run_summary.json`

## Resume and Failure Policy

The harness executes top-level `prepare_rlm_org` steps in order. On success it writes `checkpoint.json` with:

- `last_successful_step`
- `last_successful_target`
- `org_alias`
- `effective_flags`

On failure, it also records `failed_step` and failure metadata. `resume` starts from the failed step, but blocks if current scenario effective flags differ from checkpoint `effective_flags`.

Exit codes:

- `0` - success
- `10` - scenario/build failure
- `20` - harness configuration/validation error
- `30` - resume blocked

`run_summary.json` includes an agent-facing policy per scenario:

- `recommended_action`: `none`, `resume`, `rerun_full`, `manual_fix_required`
- `confidence`: `high`, `medium`, `low`
- `operator_message`: suggested next command

Failure classes are heuristic:

- `transient`: timeout, network, or platform availability patterns
- `deterministic`: configuration, schema, validation, or metadata patterns
- `unknown`: not clearly classified

---

## End-User Scratch Org Creation (Harness/TUI Path)

Use this path when the user wants a guided scratch org create + build flow.

### Step 1: Confirm defaults and ask for overrides

Before opening the TUI, ask the user to confirm these defaults:

- org shape: `ent`
- days: `30`
- alias: auto-generated

Ask explicitly and allow override of **all three** before creation.

Suggested prompt:
"I can create this with shape `ent`, days `30`, and an auto-generated alias. Do you want to override shape, days, or alias before I start?"

### Step 2: Launch TUI

```bash
./tui-cci
```

If startup exits unexpectedly, run:

```bash
./tui-cci --debug-launch
```

Fallback manual launch:

```bash
python -m venv .harness/tui-venv
.harness/tui-venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt
.harness/tui-venv/bin/python -m scripts.build_harness.tui
```

### Step 3: Apply values in wizard

- Step 1: choose org shape (default `ent`, unless user overrode)
- Step 2: set alias and days (default `30`; alias can be generated, then user-approved)
- Step 3: review runtime flag overrides
- Step 4: monitor build output and status

### Current TUI fidelity behavior

The TUI now materializes a per-run `cci_project/` via
`prepare_scenario_project_root`, executes all `cci` subprocesses with `cwd`
set to that workspace, and cleans it up with
`cleanup_scenario_project_root` in `finally`. Step 3 overrides therefore affect
actual CCI `when:` behavior, not just TUI display logic.

### Alias auto-generation guidance

If user accepts auto-generated alias, generate a unique, readable alias (<= 60 chars) with short random suffix, for example:

- `ent-tui-a3f9`

Always share the generated alias with the user before creation.

---

## Safety and Cleanup Behavior

- Scratch org deletion is destructive; confirm intent before manual delete actions.
- Harness CLI default behavior:
  - successful run orgs are deleted automatically
  - failed run orgs are kept for resume
- TUI behavior:
  - failed runs trigger scratch delete only if the org was created in that same TUI run
  - `delete_org_on_failure` defaults to `true`; set it to `false` in `scripts/build_harness/tui/settings.local.json` to preserve the org for inspection
  - alias defaults use `<shape>-tui-<4char>` and retry on collisions
- Use `--keep-orgs` when you need to retain successful orgs for debugging.
- Resume is blocked when checkpoint prerequisites are missing or flags changed; perform a full re-run after fixing blockers.

## Implementation Notes

### `when:` evaluation

`harness/config.py::evaluate_when` implements a safe AST evaluator for the small CCI `when:` grammar observed in `cumulusci.yml`:

- `project_config.project__custom__<flag>` references
- `org_config.scratch` and `org_config.name`
- `and`, `or`, `not`, parentheses
- `==` and `!=` against string/boolean literals

Unsupported expressions fail open (`True`) to avoid silently skipping steps, matching CCI's defensive behavior.

### `tui-cci` wrapper behavior

`./tui-cci` creates a cache-backed venv at
`.harness/tui-venv` (repo-scoped), and supports
`--upgrade` to force dependency refresh. It sets `TERM=xterm-256color` only
for interactive TTY launches when `TERM` is missing or `dumb`, and always
`cd`s to repo root before launching `python -m scripts.build_harness.tui`.

### Scenario workspaces

`prepare_scenario_project_root` creates a temporary `cci_project/` under a run-scoped directory (CLI scenario run dirs, or TUI workspace dirs under `.harness/tui-runs/`). It symlinks most repo entries, copies `scripts/`, and writes a generated `cumulusci.yml` with scenario/effective flags. The cleanup guard refuses to delete paths not named `cci_project`.

### Tests to extend

- `tests/build_harness/test_io.py` - JSON/JSONL/time/directory helpers
- `tests/build_harness/test_failure.py` - failure signature classification
- `tests/build_harness/test_config.py` - flags, aliases, safe `when:`, project materialization, cleanup guard
- `tests/build_harness/test_execution.py` - subprocess streaming, cancellation, and org existence checks
- `tests/build_harness/test_provenance.py` - stamp parsing and provenance extraction
- `tests/build_harness/test_reporting.py` - report composition and analysis artifact generation
- `tests/build_harness/test_scenario_runner.py` - policy recommendations and scenario orchestration behavior
- `tests/build_harness/test_tui_app.py` - TUI pure helpers and app-level behavior
- `tests/build_harness/test_tui_launcher.py` - `tui-cci` launcher behavior
- `tests/build_harness/test_tui_runner.py` - TUI build runner wiring and flag-group parser behavior
- `tests/build_harness/test_harness_cli.py` - run/resume/report CLI guardrails and path safety

Use tests first for parser, evaluator, cleanup, and resume-safety changes. Mock subprocesses for TUI runner coverage instead of creating real orgs.

## Known Follow-Ups

- Operational hygiene: keep `.harness/runs/` pruning opt-in; avoid automatic deletion without explicit operator intent.
- Larger refactors should stay separate: `tui/app.py` decomposition and replacing remaining CLI `print()` calls with structured logging if that becomes useful.

## Related Docs

- `README.md` - human-facing quick entry point for the build harness and TUI
- `docs/guides/build-harness.md`
- `scripts/build_harness/tui/README.md`
- `.cursor/skills/cci-orchestration/SKILL.md`
