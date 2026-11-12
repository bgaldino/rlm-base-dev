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

1. Use stable harness commands from repo root: `python scripts/build_harness/harness.py run|resume|report`. Run builds from the main checkout or a regular `git clone`, never a git worktree (see **Where to run a build**).
2. Prefer scenario-based runs from `scripts/build_harness/scenarios.json`.
3. For resume, keep scenario id and flags consistent with checkpoint.
4. Use JSON mode (`--format json`) when another agent or script needs structured output.
5. Run focused harness tests after implementation changes: `.harness/tui-venv/bin/python -m pytest tests/build_harness/`.
6. For end-user org creation (TUI), default to shape `ent`, days `30`, alias auto-generated. Harness CLI scenarios take `days` from the scenario instead (`1` today); see **Keep an org for a multi-day build**.
7. **Before creating the org, ask the user to confirm or override all three defaults** (shape, days, alias).
8. Cleanup semantics differ by entrypoint: harness CLI keeps failed orgs for resume; TUI auto-deletes on failure by default only if the org was created in the current run. Set `delete_org_on_failure: false` in `scripts/build_harness/tui/settings.local.json` to preserve failed TUI orgs.

## DO NOT

- **DO NOT** delete scratch orgs without clear user intent.
- **DO NOT** run destructive cleanup steps (`scratch_delete`) on ambiguous aliases.
- **DO NOT** attempt resume when scenario flags changed from checkpoint; re-run instead.
- **DO NOT** bypass the TUI/CLI materialized `cci_project` path when validating runtime flag overrides.
- **DO NOT** edit generated per-scenario `.harness/**/cci_project/cumulusci.yml` as source of truth; edit repo-root `cumulusci.yml` or scenario config instead.
- **DO NOT** start a harness or TUI build from a git worktree. CCI resolves past it to the enclosing checkout, or finds no project at all (see **Where to run a build**).
- **DO NOT** kill a run while an SFDMU load is in progress; it can leave the org's access token in a tracked `export.json` (see **Stopping a run**).

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

### Where to run a build

Start harness and TUI builds from the main checkout or from a regular `git clone`. Do not start them from a git worktree.

- The workspace links `.git` into `cci_project/`, and CumulusCI takes as its project root the first folder, from the working directory upward, whose `.git` is a **directory** (`BaseProjectConfig.repo_root`, `cumulusci/core/config/project_config.py`). In a git worktree `.git` is a file.
- From a worktree nested under a checkout (for example `<checkout>/.claude/worktrees/<name>`), the root resolves to that enclosing checkout. The build loads its `cumulusci.yml` instead of the scenario's generated one, imports its `tasks/`, runs its Robot suites, and writes into its `robot/rlm-base/results/` and `datasets/`. The run's own `robot_results/` stays empty, and the worktree's code is never exercised. Measured 2026-11-11: a worktree build's Robot step wrote the enclosing checkout's `robot/rlm-base/results/output.xml` at the same moment as a harness build there that predated per-run Robot output, and both failed with exit 252.
- From a worktree outside any checkout, no parent has a `.git` directory, so CCI finds no project.
- `cci project info` run from a worktree's root looks normal and does not reveal this. Check the folder you start from instead: `test -d .git` must succeed there.
- CCI's root override (`CUMULUSCI_AUTO_DETECT=1` with `CUMULUSCI_REPO_ROOT`, which `tests/test_doc_build_steps.py` uses to read flows from a worktree) is not a fix for builds. The root must be each run's own `cci_project/`; pointing it at the worktree skips the scenario's generated `cumulusci.yml` and the per-run Robot output.
- Harness unit tests (`tests/build_harness/`) mock their subprocesses and run fine from a worktree. Only builds are affected.

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

### Keep an org for a multi-day build

An org's lifetime is the `--days` passed to `cci org scratch <shape> <alias> --days <n>` when the harness or TUI registers it (both then run `cci org info <alias>` to materialize it). No other harness or TUI code passes `--days` or changes an existing org's lifetime. The two entrypoints take `<n>` from different places:

| Entrypoint | Source of `days` | Current value |
|------------|------------------|---------------|
| Harness CLI `run` | the scenario's `days` in the scenarios file (`harness/scenario_runner.py`; `1` when absent) | `1` in all four scenarios in `scripts/build_harness/scenarios.json` |
| TUI | `orgs.scratch.<shape>.days` in `cumulusci.yml` (`tui/runner.py::load_tui_config`), prefilled when a shape is picked and editable in wizard step 2 | `30` on every shape |

- `run` and `resume` have no `--days` option. For a longer-lived harness org, give the scenario a larger `days` in a copy of the manifest and pass `--scenarios-file <copy>`; pass the same file to `resume`, which reloads the scenario from it. Editing `scripts/build_harness/scenarios.json` changes the shared matrix.
- `--keep-orgs` only skips the `cci org scratch_delete` that follows a successful `run` or `resume`; it does not lengthen the org's life. Pass it on `resume` too, or a successful resume deletes the org.
- A failed run keeps its org for `resume`, but resume works only while the org exists: `execution.py::org_exists` runs `cci org info <alias>` with a 30-second timeout, and resume reports `resume_blocked` with target `org_missing` when that command exits non-zero or times out. Do not check an expired org by hand with `cci org info`: CumulusCI's `check_org_expired` (`cumulusci/cli/runtime.py`) recreates an expired scratch org under the same alias, with the same `days`, so you get a new, unbuilt org instead of an error. The harness probe can start that recreation too before its timeout kills it.
- The TUI rejects days outside 1–30 (`tui/app.py::_validate_alias_and_days`); the harness CLI applies no range check to a scenario's `days`.

### Run several builds at once

Concurrent harness runs are supported for Robot output only. Give each `run` its own `--run-id` (`run` refuses an existing run directory). The org alias is the scenario's `org_alias_prefix` (default `harness-<scenario_id>`) plus the **last 12 characters** of the run id after every `run-` is removed and the rest lowercased (`config.py::alias_for_scenario`). Two runs of the same scenario therefore need ids whose tails differ ignoring case, or both build the same scratch org. Starting two runs without `--run-id` in the same second can pick the same generated id.

Each workspace copies `robot/` and links `robot/rlm-base/results` to that run's own `robot_results/` folder, so Robot-backed steps no longer share `output.xml`. Before this, overlapping runs corrupted it and passing steps failed with exit 252 (`ParseError: not well-formed`), seen on `enable_document_builder_toggle` and `reorder_app_launcher`. Measured 2026-11-11 from a regular clone: two concurrent `ent-sb0` builds both completed all `prepare_rlm_org` steps while their Robot steps overlapped. The same failure now means two writers still shared a checkout's `robot/rlm-base/results/`: builds started from git worktrees under it (see **Where to run a build**), a plain `cci` run in it, or a harness build on code from before this isolation.

To build several orgs at once, put every scenario in one copy of the scenarios file, each with its own `org_alias_prefix` (or none, so the default `harness-<scenario_id>` applies), and start one `run` per scenario with a run id derived from its scenario id:

```bash
python scripts/build_harness/harness.py run --scenarios-file <copy> --scenario <scenario_a> --run-id <scenario_a>-r1 --keep-orgs
python scripts/build_harness/harness.py run --scenarios-file <copy> --scenario <scenario_b> --run-id <scenario_b>-r1 --keep-orgs
```

Distinct prefixes keep the aliases apart even when two run ids share their last 12 characters. Each run gets a predictable alias and run folder, and `resume` takes the same `--scenarios-file`, `--scenario` and `--run-id`, plus `--keep-orgs`. A rebuild after a failed run needs a new id, such as `<scenario_id>-r2`.

Other build steps still write into folders the workspace links to the shared repo, so overlapping runs can still collide there. Not isolated yet: SFDMU loads (`tasks/rlm_sfdmu.py` rewrites the plan's `export.json` with the target org and restores it), the `.forceignore` edit in `tasks/rlm_cleanup_settings.py`, the network and payments site XML patch/revert in `tasks/rlm_community.py`, and UX assembly output in `unpackaged/post_ux/` (`tasks/rlm_ux_assembly.py`).

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
- `.harness/runs/<run_id>/scenarios/<scenario_id>/robot_results/` - Robot `output.xml`, `log.html` and `report.html` of the scenario's last Robot-backed step

TUI runs, when `persistent_logging` is enabled:

- `.harness/tui-runs/<run_id>/run_manifest.json`
- `.harness/tui-runs/<run_id>/events.jsonl`
- `.harness/tui-runs/<run_id>/command-output.log`
- `.harness/tui-runs/<run_id>/run_summary.json`
- `.harness/tui-runs/tui-workspace-<UTC stamp>-<alias>-<suffix>/robot_results/` - Robot output of a failed or cancelled build (kept whatever `persistent_logging` says)

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

### Resumable UI flakes on fresh orgs

These Robot-backed steps have failed on a freshly created `ent-sb0` org and then passed on `resume` with no change. The harness classed each failure `unknown`, so `run_summary.json` recommends `resume`. Resume once before investigating; if the same step fails again, open its Robot log and treat it as a real failure.

| Step | Robot task | Symptom in `scenario.log` | Seen |
|------|------------|---------------------------|------|
| 10 `prepare_docgen` | `enable_document_builder_toggle` | `Keyword '_EnsureToggleByLabel' failed after retrying`, the locator for the `Document Builder` switch not found; the suite's other tests pass | twice |
| 27 `prepare_pricing_discovery` | `configure_product_discovery_settings` | `Default Catalog "<catalog>" could not be set within 90s`, last error `page_not_ready` (combobox or its shadow elements not yet rendered) | once |

Exit 252 with `ParseError: not well-formed` after the tests passed is not a flake: two builds wrote the same `output.xml`. See **Run several builds at once**.

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
- Use `--keep-orgs` when you need to retain successful orgs for debugging. It prevents the delete only; the org still expires after its `days`, and a later `cci org info <alias>` recreates a new, unbuilt org under the alias (see **Keep an org for a multi-day build**).
- Resume is blocked when checkpoint prerequisites are missing or flags changed; perform a full re-run after fixing blockers.

### Stopping a run

An SFDMU load (`tasks/rlm_sfdmu.py`) writes the target org's access token into the plan's tracked `export.json` and restores the file when the load finishes. A process killed mid-load never restores it. Measured 2026-11-11: stopping a build during step 8 left the org's token in a tracked `datasets/sfdmu/**/export.json`.

- Don't stop a run while an SFDMU load is in progress. Let the step finish, or stop before it starts.
- After any interrupted run, check the checkout the build ran from, before committing anything:

  ```bash
  git grep -l accessToken -- datasets/sfdmu
  git diff --stat -- datasets/sfdmu
  ```

  Tracked plans hold no `accessToken`, so the first command prints nothing on a clean tree. For each file listed that you did not edit yourself, run `git restore -- <file>`. If you did edit it, `git restore` would discard your edits: set `"orgs": []` by hand instead, then review the whole diff, because the load also rewrote the file's formatting (trailing newline, non-ASCII escapes).

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
Before launch it loads gitignored `.env.local` (dotenv: `KEY="value"`, `$VAR`
expansion, no command substitution) for any variable the shell has not already
set, so Chrome for Testing overrides apply even when the direnv hook never
exported them.

### Scenario workspaces

`prepare_scenario_project_root` creates a temporary `cci_project/` under a run-scoped directory (CLI scenario run dirs, or TUI workspace dirs under `.harness/tui-runs/`). It symlinks most repo entries, copies `scripts/` and `robot/`, and writes a generated `cumulusci.yml` with scenario/effective flags. The `robot/` copy leaves out the repo's `robot/rlm-base/results/` and links that path to `robot_results/` beside `cci_project/`, so Robot logs are private to the run and outlive `cci_project/` cleanup and the clean rebuild on resume. The CLI keeps `robot_results/` in the scenario run dir. The TUI (`tui/runner.py::_remove_workspace_dir`) discards it after a successful build; after a failed or cancelled build that wrote Robot output it keeps `.harness/tui-runs/tui-workspace-<UTC stamp>-<alias>-<suffix>/robot_results/`. Nothing prunes those folders. A Robot wrapper's error names `.../cci_project/robot/rlm-base/results/log.html`; the TUI deletes `cci_project/`, so open the sibling `robot_results/log.html` instead. The cleanup guard refuses to delete paths not named `cci_project`.

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
- `tests/build_harness/test_harness_cli.py` - run/resume/report/prune CLI guardrails and path safety

Use tests first for parser, evaluator, cleanup, and resume-safety changes. Mock subprocesses for TUI runner coverage instead of creating real orgs.

## Known Follow-Ups

- Operational hygiene: keep `.harness/runs/` pruning opt-in; avoid automatic deletion without explicit operator intent.
- Open: the platform's maximum scratch-org duration is not recorded in this repo. `30` is the TUI's own cap and the `days` on every `cumulusci.yml` shape; whether a harness scenario with `days` above 30 is accepted has not been run.
- Larger refactors should stay separate: `tui/app.py` decomposition and replacing remaining CLI `print()` calls with structured logging if that becomes useful.

## Related Docs

- `README.md` - human-facing quick entry point for the build harness and TUI
- `docs/guides/build-harness.md`
- `scripts/build_harness/tui/README.md`
- `.cursor/skills/cci-orchestration/SKILL.md`
