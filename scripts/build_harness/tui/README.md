# CCI Build Manager TUI

This package provides a full-screen terminal UI for:

- choosing a scratch org shape from `cumulusci.yml`
- setting org alias and scratch org duration
- reviewing and overriding `project.custom` boolean flags for the current run
- creating the scratch org
- running top-level `prepare_rlm_org` steps with live status and command output

Flag overrides are runtime-only and are never written back to `cumulusci.yml`.

## Create scoped virtual environment

```bash
python -m venv scripts/build_harness/tui/.venv
scripts/build_harness/tui/.venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt
```

## Launch

```bash
scripts/build_harness/tui/.venv/bin/python -m scripts.build_harness.tui
```

Or use the root wrapper:

```bash
./run-build-tui.sh
```

## Default org shape setting

The TUI reads `scripts/build_harness/tui/settings.json` on startup.

Set `default_org_shape` to preselect a shape in step 1:

```json
{
  "default_org_shape": "ent"
}
```

If the value does not match a known `orgs.scratch` key from `cumulusci.yml`,
the TUI falls back to the first shape in the list.

## Controls

- Step 1: choose scratch org shape, then `Next`
- Step 2: set alias and days, then `Next`
- Step 3: toggle flag `Switch` values, then `Start Build`
- Step 4: watch output, use `Stop Build` to request cancellation
- `Exit` is available on every screen

## Notes

- The TUI executes `cci` commands from the repository root.
- `prepare_rlm_org` execution uses top-level step parsing and `when` evaluation from `scripts/build_harness/harness.py`.
- Flag groups and inline descriptions are sourced dynamically from `project.custom` comments/order in `cumulusci.yml`.
