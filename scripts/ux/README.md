# `scripts/ux/` — UX assembly and drift tooling (no CCI)

Assembles feature-conditional UX metadata from `templates/` into
`unpackaged/post_ux/`, deploys it, and captures/applies drift between a live org
and the templates. Architecture, template layout and patch format:
[`docs/features/dynamic-ux-assembly.md`](../../docs/features/dynamic-ux-assembly.md).

The build still assembles through CCI: `prepare_ux` runs `assemble_and_deploy_ux`
(`tasks/rlm_ux_assembly.py`), a thin wrapper over this package. Drift capture and
writeback exist only here.

Requirements: Python 3 with PyYAML, and the `sf` CLI for the org-facing commands
(`retrieve`, `deploy`, `capture-drift`).

## Commands

```bash
python scripts/ux/ux_tool.py <command> [options]
```

| Command | Does | Org? |
|---------|------|------|
| `flags` | Print the resolved UX feature flags as JSON | no |
| `assemble [--type T] [--name F] [--output-path P]` | `templates/` → `unpackaged/post_ux/` | no |
| `deploy --target-org X [--output-path P]` | `sf project deploy start` the assembled output | yes |
| `retrieve --target-org X [--name F]` | Org flexipages → `unpackaged/post_ux/flexipages/` | yes |
| `diff [--name F] [--fail-on-drift]` | Org state in `post_ux/` vs. templates → `<output-path>/drift_report.json` | no |
| `writeback [--name F] [--apply]` | Reverse-apply patches: org flexipages → `templates/` | no |
| `capture-drift --target-org X [--fail-on-drift]` | `retrieve`, then `diff` | yes |
| `apply-drift [--fail-on-drift]` | `writeback --apply` (flexipages), `diff` against the org state, then `assemble` (no deploy) | no |

`--type` for `assemble` is one of `all`, `flexipages`, `layouts`, `applications`,
`profiles`, `objects`. `--name` takes the full source filename including its
type suffix, e.g. `RLM_Quote_Record_Page.flexipage-meta.xml`. Commands compose
rather than chain through options: `assemble && deploy --target-org X` assembles and
deploys.

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

Where a command's flags start depends on what it compares:

- `flags` and `assemble` start from `project.custom` in `cumulusci.yml`.
- The org-facing commands (`retrieve`, `diff`, `writeback`, `capture-drift`,
  `apply-drift`) start from the flags recorded in `<output-path>/assembly_manifest.json`
  by the last assembly, so an org built with runtime overrides is compared against
  what was really deployed. Without a manifest they fall back to `cumulusci.yml`.
  A `--type` or `--name` assemble with flags that differ from the last full one
  marks the manifest partial, and these commands then refuse it until a full
  `assemble` is run.
  The manifest records the last local assembly, not what a given org has
  deployed: after assembling with other flags, or deploying elsewhere, pass
  `--flag` for the target org's real flags (the command logs which manifest it read).

`--flag NAME=true|false` (repeatable) overrides either; unknown flag names are
rejected. `python scripts/ux/ux_tool.py flags` prints the `cumulusci.yml` view.

## Safety

- `writeback` is a **dry run** unless `--apply` is given. It keeps no backup
  copies: review with `git diff templates/` and revert with git.
- Never hand-edit `unpackaged/post_ux/`; change `templates/` and reassemble.
- `writeback` is all-or-nothing: if any active patch cannot be reversed out of
  the org page, it exits with an error before changing any template or patch file.
  A page in the org but not in the active templates is saved as a new base
  template, unless an inactive standalone feature owns it: that is a flag
  mismatch, and writeback aborts the same way.
- `deploy` treats `SucceededPartial` as a failure.
- `writeback --apply` rewrites a patch file only when the org changed what the
  patch produces, but that rewrite drops the file's YAML comments. Restore any
  rationale comments from `git diff` before committing.
- `retrieve` and `capture-drift` overwrite `unpackaged/post_ux/flexipages/` with
  org state. Run `assemble` (or `git checkout unpackaged/post_ux/`) afterwards if
  you do not mean to commit that state.

## Modules

| Module | Contents |
|--------|----------|
| `ux_tool.py` | argparse CLI (`main(argv)` is importable for tests) |
| `_context.py` | `UxContext`, `UxError`, `UxOptionError` |
| `_flags.py` | Known flags, `_STANDALONE_ORDER`, `FLEXIPAGE_PATCH_ORDER`, `LAYOUT_TIERS`, source suffixes, flexipage source resolver, flag loading/precedence |
| `_xml.py` | Salesforce metadata XML helpers: namespace, `write_xml`, element and valueList lookups |
| `_patch_ops.py` | One entry per flexipage patch type (apply, reverse, describe, refresh); add a patch type here |
| `_assemble.py` | `UxAssembler` (`run`, `assemble_flexipages`), selection validation, profile/app/object patches |
| `_sf.py` | `run_sf_json`: one `sf … --json` runner shared by retrieve and deploy |
| `_deploy.py` | `deploy()` via `sf project deploy start` |
| `_retrieve.py` | `retrieve()` via `sf project retrieve start` |
| `_diff.py` | `diff()` and the drift report |
| `_writeback.py` | `writeback()`: reverse the patches, then refresh the patch files from the org |

Tests: `tests/test_ux_tool.py` (offline; sf calls are stubbed).
