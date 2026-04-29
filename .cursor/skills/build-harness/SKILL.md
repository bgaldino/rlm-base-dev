# Build Harness Skill

Use this skill when working with the local build harness for:

- automated profiling/testing runs of `prepare_rlm_org`
- creating a scratch org for an end user through the harness/TUI path

## Trigger Conditions

Use this skill when the request includes any of the following:

- run, resume, or report a build harness run
- profile `prepare_rlm_org` behavior across `dev`/`ent` scenarios
- investigate harness artifacts in `.harness/runs/<run_id>/`
- create a scratch org for a user using the harness TUI

## Non-Trigger Conditions

Do **not** use this skill when:

- running normal one-off CCI tasks/flows without harness orchestration
- editing SFDMU plans, Robot tests, or metadata not related to harness usage
- writing harness implementation code (use repo integration/troubleshooting skills)

## Quick Rules

1. Use stable harness commands from repo root: `run`, `resume`, `report`.
2. Prefer scenario-based runs from `scripts/build_harness/scenarios.json`.
3. For resume, keep scenario id and flags consistent with checkpoint.
4. For end-user org creation, default to shape `ent`, days `30`, alias auto-generated.
5. **Before creating the org, ask the user to confirm or override all three defaults** (shape, days, alias).
6. Cleanup semantics differ by entrypoint: harness CLI keeps failed orgs for resume; TUI auto-deletes on failure only if the org was created in the current run.

## DO NOT

- **DO NOT** delete scratch orgs without clear user intent.
- **DO NOT** run destructive cleanup steps (`scratch_delete`) on ambiguous aliases.
- **DO NOT** attempt resume when scenario flags changed from checkpoint; re-run instead.

---

## Command Recipes (Run / Resume / Report)

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

### JSON mode for agent automation

```bash
python scripts/build_harness/harness.py run --format json
python scripts/build_harness/harness.py resume --run-id <run_id> --scenario <scenario_id> --format json
python scripts/build_harness/harness.py report --run-id <run_id> --format json
```

## Run Artifacts to Inspect

- `.harness/runs/<run_id>/run_manifest.json`
- `.harness/runs/<run_id>/run_summary.json`
- `.harness/runs/<run_id>/report.md`
- `.harness/runs/<run_id>/agent_summary.md`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/checkpoint.json`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/build_provenance.json`
- `.harness/runs/<run_id>/scenarios/<scenario_id>/scenario.log`

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

Fallback manual launch:

```bash
python -m venv scripts/build_harness/tui/.venv
scripts/build_harness/tui/.venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt
scripts/build_harness/tui/.venv/bin/python -m scripts.build_harness.tui
```

### Step 3: Apply values in wizard

- Step 1: choose org shape (default `ent`, unless user overrode)
- Step 2: set alias and days (default `30`; alias can be generated, then user-approved)
- Step 3: review runtime flag overrides
- Step 4: monitor build output and status

### Alias auto-generation guidance

If user accepts auto-generated alias, generate a unique, readable alias (<= 60 chars) with short random suffix, for example:

- `ent-a3f9`

Always share the generated alias with the user before creation.

---

## Safety and Cleanup Behavior

- Scratch org deletion is destructive; confirm intent before manual delete actions.
- Harness CLI default behavior:
  - successful run orgs are deleted automatically
  - failed run orgs are kept for resume
- TUI behavior:
  - failed runs trigger scratch delete only if the org was created in that same TUI run
  - alias defaults use `<shape>-<4char>` and retry on collisions
- Use `--keep-orgs` when you need to retain successful orgs for debugging.
- Resume is blocked when checkpoint prerequisites are missing or flags changed; perform a full re-run after fixing blockers.

## Related Docs

- `docs/guides/build-harness.md`
- `scripts/build_harness/tui/README.md`
- `.cursor/skills/cci-orchestration/SKILL.md`
