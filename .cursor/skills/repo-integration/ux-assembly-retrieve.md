# UX Assembly, Retrieve, and Drift

Read this when changing **`templates/`** UX sources, **`tasks/rlm_ux_assembly.py`**, **`tasks/rlm_retrieve_ux.py`**, drift tasks, or anything under **`unpackaged/post_ux/`** output.

## Source of truth

| Location | Role |
|----------|------|
| `templates/` | **Edit here** — flexipage patches, layouts, apps, profiles, object bindings |
| `unpackaged/post_ux/` | **Generated** — assembled output; **do not hand-edit** (see `AGENTS.md`) |
| `docs/features/dynamic-ux-assembly.md` | Full drift capture / writeback / assembly behavior |

## Assembler (`assemble_and_deploy_ux`)

- **Purpose** — Merges base templates + YAML patches per feature flags, writes to `unpackaged/post_ux/`, optionally deploys.
- **Options** — Filter by `metadata_type` (e.g. `flexipages`, `profiles`) or single `metadata_name` (full filename including `.flexipage-meta.xml`).
- **App menus** — AppSwitcher / `appMenus` are **not** assembled here; launcher order is handled by **`reorder_app_launcher`** (Robot). The task **removes a stale `appMenus/`** directory if present from older runs.
- **Python changes** — Keep `_assemble_*` helpers internally consistent (return types, early exits). Drift flows assume predictable manifest and file layout.

## Retrieve (`retrieve_ux_from_org`)

- **Purpose** — Pulls live flexipages from the org into `unpackaged/post_ux/` for **drift comparison** (`capture_ux_drift` → `diff_ux_templates`).
- **Implementation** — Uses **Metadata API SOAP retrieve** inside CCI (not necessarily `sf` CLI) to avoid PATH/env issues in embedded runs.
- **Scope** — Defaults to the same flexipage set the assembler would deploy (base + standalone for active flags). Narrow with `metadata_name` when testing one page.
- **XML / namespace** — Retrieved XML must match parser expectations (namespace-aware parsing). If you change retrieve or strip logic, validate with a real org retrieve.

## Workflows (canonical commands)

```bash
cci task run assemble_and_deploy_ux -o deploy false --org <cci_alias>   # dry-run assembly
cci flow run capture_ux_drift --org <cci_alias>                        # retrieve + diff
cci flow run apply_ux_drift --org <cci_alias>                          # writeback to templates + verify
```

Use **`--org`** with the **CCI alias**; for raw `sf` commands use **`--target-org`** with the SF CLI alias (e.g. `rlm-base__beta`). See `AGENTS.md` — Org Identity.

## DO NOT

- **DO NOT** edit `unpackaged/post_ux/` to “fix” UX — fix **`templates/`** and re-run assembly (or follow drift writeback).
- **DO NOT** add `EmailTemplatePage` flexipages to templates — they cannot deploy via Metadata API (`AGENTS.md`).
- **DO NOT** assume hand-copied org XML belongs in `post_ux` without going through retrieve + diff + writeback when aligning with templates.
