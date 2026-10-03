# `scripts/ux/` — UX assembly and drift tooling (no CCI)

Assembles feature-conditional UX metadata from `templates/` into
`unpackaged/post_ux/`, deploys it, and captures/applies drift between a live org
and the templates. Architecture, template layout and patch format:
[`docs/features/dynamic-ux-assembly.md`](../../docs/features/dynamic-ux-assembly.md).

The build still assembles through CCI: `prepare_ux` runs `assemble_and_deploy_ux`
(`tasks/rlm_ux_assembly.py`), a thin wrapper over this package. Drift capture and
writeback exist only here.

Requirements: Python 3 with PyYAML, and the `sf` CLI for the org-facing commands
(`retrieve`, `deploy`, `capture-drift`, `assemble --deploy`).

## Commands

```bash
python scripts/ux/ux_tool.py <command> [options]
```

| Command | Does | Org? |
|---------|------|------|
| `flags` | Print the resolved UX feature flags as JSON | no |
| `assemble [--type T] [--name F] [--output-path P] [--deploy --target-org X]` | `templates/` → `unpackaged/post_ux/` | only with `--deploy` |
| `deploy --target-org X [--output-path P]` | `sf project deploy start` the assembled output | yes |
| `retrieve --target-org X [--name F]` | Org flexipages → `unpackaged/post_ux/flexipages/` | yes |
| `diff [--name F] [--report-file P] [--fail-on-drift]` | Org state in `post_ux/` vs. templates → `drift_report.json` | no |
| `writeback [--name F] [--type flexipages\|layouts\|all] [--apply] [--no-backup]` | Reverse-apply patches: org state → `templates/` (flexipages by default; layouts need org layouts placed in `post_ux/layouts/` by hand, since `retrieve` fetches only flexipages) | no |
| `capture-drift --target-org X [--fail-on-drift]` | `retrieve`, then `diff` | yes |
| `apply-drift [--no-backup] [--fail-on-drift]` | `writeback --apply` (flexipages), `diff` against the org state, then `assemble` (no deploy) | no |

`--type` for `assemble` is one of `all`, `flexipages`, `layouts`, `applications`,
`profiles`, `objects`. `--name` takes the full source filename including its
type suffix, e.g. `RLM_Quote_Record_Page.flexipage-meta.xml`.

Relative paths resolve against the repository root, so the tool can run from any
directory. Exit codes: `0` success, `1` drift found with `--fail-on-drift`, `2`
a failed step or invalid option.

## Typical drift loop

```bash
python scripts/ux/ux_tool.py capture-drift --target-org <sf_alias>   # retrieve + diff
cat unpackaged/post_ux/drift_report.json | python3 -m json.tool       # review
python scripts/ux/ux_tool.py writeback                                # dry run: what would change
python scripts/ux/ux_tool.py apply-drift                              # write templates, re-diff, reassemble
git diff templates/                                                   # review, then commit
```

## Targeting an org

Orgs are addressed by their **sf CLI** alias or username (`--target-org`), never by
a CCI alias. A CCI org `beta` is usually the sf alias `rlm-base__beta`; check with
`sf org list`. All org access goes through the sf CLI
(`sf project retrieve start`, `sf project deploy start`), so this package never
reads or handles an access token.

`retrieve` runs `sf project retrieve start --metadata FlexiPage:<name> …
--target-metadata-dir <tmp> --unzip` and copies each raw `.flexipage` into
`flexipages/` under its source-format name. The scope is every flexipage the
assembler would deploy for the resolved flags (base pages plus active standalone
overrides). A failed retrieve leaves the existing files untouched; pages the org
does not have are reported as warnings.

## Feature flags

Flags default to `project.custom` in `cumulusci.yml`. Two options layer on top, in
this order:

1. `--flags-from-manifest [PATH]`: the flags recorded by the last assembly
   (default `<output-path>/assembly_manifest.json`). Use it when the org was built
   with runtime overrides, so the diff compares against what was really deployed.
2. `--flag NAME=true|false`: repeatable runtime overrides; these win. Unknown flag
   names are rejected.

`python scripts/ux/ux_tool.py flags` prints the result.

## Safety

- `writeback` is a **dry run** unless `--apply` is given. With `--apply` it keeps
  `*.bak` copies of overwritten templates unless `--no-backup` is set.
- Never hand-edit `unpackaged/post_ux/`; change `templates/` and reassemble.
- `retrieve` and `capture-drift` overwrite `unpackaged/post_ux/flexipages/` with
  org state. Run `assemble` (or `git checkout unpackaged/post_ux/`) afterwards if
  you do not mean to commit that state.

## Modules

| Module | Contents |
|--------|----------|
| `ux_tool.py` | argparse CLI (`main(argv)` is importable for tests) |
| `_context.py` | `UxContext`, `UxError`, `UxOptionError` |
| `_flags.py` | Known flags, `_STANDALONE_ORDER`, `FLEXIPAGE_PATCH_ORDER`, `LAYOUT_TIERS`, source suffixes, flexipage source resolver, flag loading/precedence |
| `_assemble.py` | `UxAssembler` and all patch helpers |
| `_sf.py` | `run_sf_json`: one `sf … --json` runner shared by retrieve and deploy |
| `_deploy.py` | `deploy()` via `sf project deploy start` |
| `_retrieve.py` | `UxRetriever` via `sf project retrieve start` |
| `_diff.py` | `UxDiff` and the drift report |
| `_writeback.py` | `UxWriteback` (reverse-patch, patch-file updates) |

Tests: `tests/test_ux_tool.py` (offline; sf calls are stubbed).
