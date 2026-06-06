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
cci task run assemble_and_deploy_ux --deploy false                     # dry-run assembly: local only, no org needed
cci task run assemble_and_deploy_ux                                    # deploy: targets your DEFAULT cci org (no --org flag)
cci flow run capture_ux_drift --org <cci_alias>                        # retrieve + diff
cci flow run apply_ux_drift --org <cci_alias>                          # writeback to templates + verify
```

Use **`--org`** with the **CCI alias** on the *flows* above; for raw `sf` commands use **`--target-org`** with the SF CLI alias (e.g. `rlm-base__beta`). See `AGENTS.md` — Org Identity. **Note:** the `assemble_and_deploy_ux` *task* has no `--org` option — its deploy step uses your **default** cci org (and raises if none is set); `--deploy false` runs assembly locally with no org at all.

## DO NOT

- **DO NOT** edit `unpackaged/post_ux/` to “fix” UX — fix **`templates/`** and re-run assembly (or follow drift writeback).
- **DO NOT** add `EmailTemplatePage` flexipages to templates — they cannot deploy via Metadata API (`AGENTS.md`).
- **DO NOT** assume hand-copied org XML belongs in `post_ux` without going through retrieve + diff + writeback when aligning with templates.
- **DO NOT** reference a feature-gated custom field/component (e.g. a `post_<feature>`-only field) from a **base/always-on** template (`layouts/base`, `flexipages/base`, `profiles/base`). It assembles into the default build and **breaks deploy** on a flag-off org where that field/component was never deployed. Put it in the feature's patch path.

## Feature-gated metadata must not leak into always-on output

`post_ux` deploys for **every** build, gated only by `ux=true` — independent of feature
flags like `large_stx`/`tso`. So anything that references metadata which only exists when
a feature is on (custom fields/objects/components under `unpackaged/post_<feature>/`)
**must** live in that feature's patch path, not the base:

- Flexipages → `templates/flexipages/patches/<feature>/<Page>.yml` (applied when the flag is on).
- Layouts → the feature tier in `tasks/rlm_ux_assembly.py::_assemble_layouts` (base → billing →
  constraints …). Layouts use **full-file tier override** (no field-level layout patches); if a
  base layout must not carry a gated field, **remove it from base** and surface the field via the
  feature **flexipage** patch (the Lightning record page), which is usually where it belongs anyway.

The **committed** `post_ux` must reflect the **committed default flags** (`tso=false`,
`large_stx=false`, …) — not your local build. To regenerate + verify:

```bash
# 1. cumulusci.yml at committed defaults (don't commit local flag flips)
cci task run assemble_and_deploy_ux --deploy false        # local assembly only, no org needed
# 2. confirm the assembled output is a false/false build
python3 -c "import json;d=json.load(open('unpackaged/post_ux/assembly_manifest.json'));print(d['feature_flags'])"
grep -rl '<post_feature_field>' unpackaged/post_ux/        # must be empty for gated fields
# 3. optional: diff vs the org (a flag-on org) — the ONLY diffs should be the gated patch content
```

A clean way to find leaks: list each `post_<feature>` custom field, then grep the base/standalone
templates (excluding that feature's patch dir) for references — any hit is a leak.
