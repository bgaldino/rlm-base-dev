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
python -m venv .harness/tui-venv
.harness/tui-venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt
```

## Launch

```bash
.harness/tui-venv/bin/python -m scripts.build_harness.tui
```

Or use the root wrapper:

```bash
./tui-cci
```

## Settings

The TUI reads `scripts/build_harness/tui/settings.json` on startup.

Set `default_org_shape` to preselect a shape in step 1.
Set `theme_mode` to control the palette:

- `auto` (default): use terminal/Textual default light-vs-dark mode
- `light`: force Salesforce-inspired light palette
- `dark`: force Salesforce-inspired dark palette

Set `persistent_logging` to control run artifact capture:

- `true` (default): write each TUI build run to `.harness/tui-runs/<run_id>/`
- `false`: disable persistent run artifacts (UI log still works)

Example:

```json
{
  "default_org_shape": "ent",
  "theme_mode": "auto",
  "persistent_logging": true
}
```

If the value does not match a known `orgs.scratch` key from `cumulusci.yml`,
the TUI falls back to the first shape in the list.

## Controls

- Step 1: choose scratch org shape, then `Next`
- Step 2: set alias and days, then `Next`
- Step 3: toggle runtime flag pill switches (`○ OFF` / `ON ●`), then `Start Build`
- Step 4: watch output, use `Stop Build` while running; after completion it becomes `New Build`
- Command Palette (`Ctrl+P`): run `Set Default Org` to persist the highlighted/current org shape to `settings.json`
- `Ctrl+X`, `Esc`, or `Exit` to quit (`Exit` is available on every screen)

## Notes

- The TUI materializes a run-scoped `cci_project` workspace under `.harness/tui-runs/` and executes `cci` commands from that workspace so runtime flag overrides affect CCI `when:` behavior.
- `prepare_rlm_org` execution uses top-level step parsing and `when` evaluation from the harness runner (`scripts/build_harness/harness.py` and `scripts/build_harness/harness/` modules).
- Flag groups and inline descriptions are sourced dynamically from `project.custom` comments/order in `cumulusci.yml`.
- Step 2 pre-fills a valid alias using shape + 4-char random suffix and retries on alias collisions.
- If a run fails after scratch org creation, the TUI automatically attempts to delete that org (only if it was created in the current run).
- Output screen behavior:
  - `Total Elapsed` freezes on success/failure/cancel
  - active step duration updates live in the table
  - step table auto-scrolls to newly started rows
  - a large completion banner is shown for success/failure/cancel
