---
name: overlay-pack
description: >-
  Define and run an overlay pack: a private folder outside the public tree that
  holds one build's data plans, constraint models, procedure overlays and metadata,
  loaded onto a Foundations base build by a manifest (pack.yml) and a loader. Covers
  the manifest format and its step kinds (run, deploy, assign, check, fresh), how a
  loader stages the pack and runs Foundations' CCI tasks and sf deploys with explicit
  paths, the post-deploy component check, resume, dry run, rerun and idempotency
  checks, gate reruns, and what to do when a step fails. The repo ships no loader
  code; this documents the format and the behaviour a loader must have. Use when
  writing or extending a pack's manifest or loader, loading a pack onto a new org,
  or deciding why a pack step failed. Planning when a build repeats:
  implementation-planning. Data plans: sfdmu-data-plans. Aliases and flows:
  cci-orchestration.
---

# Overlay Pack — Manifest Format and Loader Behaviour

An overlay pack is how a finished customer build is loaded again onto a new org. It is
a private folder, kept outside this public repository, that holds the build's data
plans, constraint models (CML), procedure overlays, context plans and metadata. A
manifest, `pack.yml`, lists the steps in build order. A loader reads the manifest and
runs each step onto an org that already has a Foundations base build.

**The repo ships no pack format and no loader code.** This skill documents the format
and the behaviour a loader must have, as one private build wrote and proved them: a
fresh-org load of 32 steps, every one exit 0 in 36 minutes, and a second load that
changed nothing except one schedule its plan switches off and on by design and the
constraint records the CML import rewrites (**Rerun and idempotency**)
[Measured: 2026-11-17, 264, harness scratch org]. Each build writes its own loader against this contract.
[implementation-planning](../implementation-planning/SKILL.md) step 7 decides whether a
build repeats as a pack, a feature flag or a single task.

## Quick Rules

1. **The pack lives outside the public tree.** It is private customer content. Nothing
   from it is copied into this repo; promoting it to a public feature flag is a separate
   path (`implementation-planning` step 7, `repo-integration`).
2. **Load onto a base build.** Build the org with Foundations first (`build-harness`),
   then load the pack. Name the base scenario and release in the manifest.
3. **Run every step from a staged copy, never from the pack.** The copy has no `.git`,
   no SFDMU output and no source workbook, so a load never writes into the pack and no
   deploy reads from an ignored path.
4. **Use Foundations' own tasks with explicit paths.** `cci task run <task> --org <cci
   alias>` with pack paths as options, run from a Foundations checkout; `sf` commands
   take `--target-org <sf alias>`. Never put an access token on a command line.
5. **A deploy passes only when every component landed.** Each `package.xml` member must
   be in the deploy's `componentSuccesses` and on the org afterwards. Refuse wildcards
   and empty manifests.
6. **Stop at the first failing step and resume from it.** Log each step, record its
   exit, and print the step id to pass to `--from`.
7. **A second load changes nothing.** Prove it with a count of records each data plan
   owns, modified since the second load started, and with each script's own report of
   what it changed. Explain every nonzero count.
8. **A person's step is a `check`, not a comment.** Setup-only work the loader can't do
   is a step that queries for its result and stops with instructions when it's missing.

## DO NOT

- **DO NOT** commit pack content, customer names, prices, record IDs or org aliases to
  this repo, including in skills, examples or test fixtures.
- **DO NOT** deploy or load from the pack folder itself. A deploy from a path the
  project ignored (under a dot-folder) reported success with an empty package
  [Measured: 264, prior build, date not recorded]; SFDMU writes its reports and target files beside the plan.
- **DO NOT** use `operation: Insert` with `deleteOldData: true` in a pack's data plans.
  Plans use Upsert so a rerun matches instead of duplicating or deleting
  (`sfdmu-data-plans`; `AGENTS.md` → SFDMU v5 rules).
- **DO NOT** pass a CCI alias to `sf`, an sf alias to `cci`, or an access token to
  either (`cci-orchestration` → Org Identity: CCI vs SF CLI).
- **DO NOT** run the loader's CCI steps from a git worktree of Foundations. CCI takes
  as its project root the first folder whose `.git` is a directory, so a worktree runs
  the enclosing checkout's code or none (`build-harness` → Where to run a build).
- **DO NOT** list `*` in a deployed `package.xml`. The check can't verify a wildcard.
- **DO NOT** edit `unpackaged/post_ux/` to carry a pack's page changes. Patch the org's
  page from a pack step that retrieves, patches, deploys and re-retrieves it.
- **DO NOT** stage per-org runtime state (result files, replay state) as pack content.
  A restaged pack that carried another org's state sent that org's account to the new
  org and failed with `INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY` [Measured:
  2026-11-18, 264].

## Entry Conditions

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Write or extend a pack's `pack.yml` or loader | Yes | Start from **Manifest** and **Loader behaviour**. |
| Load a pack onto a new or replacement org | Yes | Base build first, then **Running a load**. |
| A pack step failed, or a deploy "succeeded" with missing components | Yes | **When a step fails**. |
| Decide whether a build repeats as a pack or a feature flag | No | `implementation-planning` step 7. |
| Write or fix a data plan the pack loads | No | `sfdmu-data-plans`. |
| Build the base org | No | `build-harness`, `cci-orchestration`. |
| Add public content behind a feature flag | No | `repo-integration`, `cci-orchestration`. |

## What a pack holds

One folder per build area, each with its own README: for example `catalog/` (an SFDMU
plan and its picklist metadata), `cml/`, `pricing/` (metadata, a context plan, a data
plan, a procedure overlay script), `billing/`, `approvals/`, `dro/`. Beside them:
`pack.yml`, the loader, a gate runner, and the build plan with its golden tests. The
pack's folders read Foundations through a `foundations` link next to the pack
(`<pack>/../foundations`), which the stage recreates.

## Manifest (`pack.yml`)

Top-level keys:

| Key | Holds |
|-----|-------|
| `version`, `name` | Manifest format version and the pack's name. |
| `base` | The base build the pack expects: the harness scenarios file, the scenario name, the release. |
| `stage.exclude` | Paths and `**/<name>` patterns left out of the staged copy: `.git`, SFDMU `reports` and `target`, the source workbook, generated output, `__pycache__`. |
| `stage.metadata_copies` | `<name>: <pack path>`: a metadata folder copied again to `<stage>/meta/<name>`, for folders that hold more than the deploy should. |
| `stage.metadata_copy_drop` | `<name>: [files]` removed from that copy (a build script kept beside the metadata). |
| `layers` | Ordered list of `{id, phase, steps}`. `phase` names the plan phase and gate the layer serves. |

Each step has a unique `id` (across the manifest; the loader refuses duplicates), a
`kind`, and an optional `note` recording its side effects or a known wait. String
fields take placeholders: `{cci}` (the cci executable), `{py}` (a Python with PyYAML,
CCI's own), `{org}` (CCI alias), `{sf}` (sf alias), `{foundations}` (the Foundations
checkout), `{pack}` (the staged pack), `{meta}` (the staged metadata copies).

| Kind | Fields | Passes when | On failure |
|------|--------|-------------|------------|
| `run` | `cmd` (argument list, no shell); `cwd`: `foundations` (default) or `pack`; `env` map | the command exits 0 | stops the load with the command's exit |
| `deploy` | `dir` (a Metadata API folder with `package.xml`); `wait` (minutes, default 30); `tests` (list: runs `RunSpecifiedTests`) | the deploy succeeded, and every `package.xml` member is in `componentSuccesses` and on the org | exit 1 with the component failures, or exit 4 naming each member not deployed or not on the org |
| `assign` | `permset` | the permission set is assigned; "already assigned" counts | stops the load |
| `check` | `soql` + `expect_rows`, optionally `soql2` + `expect_rows2`; `instructions` | each query returns the expected row count | prints the misses and `instructions`, exit 3 |
| `fresh` | none | no decision table is Stale ("Not comparable" passes) | exit 1 after the time limit |

A `fresh` step polls `check_decision_table_freshness` (every 30 seconds in the proved
loader), runs the `refresh_all_decision_tables` flow once if tables are still Stale
after 5 minutes, and fails after 15. "Not comparable" passes because the check declines
to guess on some tables (`decision-tables` Quick Rule 6); a fulfillment fallout table
read that way on both measured orgs once its rules were loaded [Measured: 2026-11-17, 264].

### Illustrative manifest

Names are placeholders. Use your own pack's folders, models and permission sets.

```yaml
version: 1
name: mypack
base: {harness_scenarios: harness/scenarios.json, scenario: mypack-base, release: "264"}
stage:
  exclude: [".git", "**/reports", "**/target", "**/source", "**/__pycache__"]
  metadata_copies: {fulfillment: fulfillment/metadata}
  metadata_copy_drop: {fulfillment: [build_fulfillment.py]}
layers:
  - id: catalog
    phase: P3
    steps:
      - {id: catalog-meta, kind: deploy, dir: "{pack}/catalog/metadata"}
      - {id: catalog-pass1, kind: run, cmd: ["{cci}", task, run, load_sfdmu_data, -o, pathtoexportjson, "{pack}/catalog", --org, "{org}"]}
      - {id: catalog-check, kind: run, cmd: ["{py}", scripts/check_classification_attrs.py, --target-org, "{sf}", --plan, "{pack}/catalog"], note: "exit 0 continues; a non-zero exit stops the step and the loader follows catalogs-and-loading.md step 5 (second pass, recheck)"}
      - {id: cml-import, kind: run, cmd: ["{cci}", task, run, import_cml, --org, "{org}", -o, data_dir, "{pack}/cml"]}
      - {id: cml-cycle, kind: run, cmd: ["{cci}", task, run, manage_expression_sets, --org, "{org}", -o, operation, deactivate_versions, -o, version_full_names, MyModel_V1], note: "a reload's changed model reaches the solver only after a cycle; skipped when inactive (Rerun and idempotency)"}
      - {id: cml-activate, kind: run, cmd: ["{cci}", task, run, manage_expression_sets, --org, "{org}", -o, operation, activate_versions, -o, version_full_names, MyModel_V1]}
  - id: pricing
    phase: P4
    steps:
      - {id: pricing-meta, kind: deploy, dir: "{pack}/pricing/metadata", tests: [MyPackPricingTest]}
      - {id: pricing-permset, kind: assign, permset: MyPack_Pricing}
      - {id: pricing-context, kind: run, cmd: ["{cci}", task, run, manage_context_definition, --org, "{org}", -o, plan_file, "{pack}/pricing/context/manifest.json"]}
      - {id: pricing-data, kind: run, cmd: ["{cci}", task, run, load_sfdmu_data, -o, pathtoexportjson, "{pack}/pricing", --org, "{org}"]}
      - {id: pricing-overlay, kind: run, cmd: ["{py}", -u, "{pack}/pricing/build_overlay.py", --target-org, "{sf}", --apply]}
      - {id: refresh, kind: run, cmd: ["{cci}", flow, run, refresh_all_decision_tables, --org, "{org}"]}
      - {id: search-index, kind: run, cmd: ["{cci}", task, run, rebuild_search_index, --org, "{org}"]}
      - {id: pricing-fresh, kind: fresh}
  - id: fulfillment
    phase: P6
    steps:
      - id: setup-done
        kind: check
        soql: "SELECT Id FROM DecisionTable WHERE DeveloperName = '<Table>' AND Status = 'Active'"
        expect_rows: 1
        instructions: |
          Sign in (sf org open -o {sf}) and do the Setup steps in fulfillment/README.md.
          Then rerun the load with --from setup-done.
      - {id: fulfillment-meta, kind: deploy, dir: "{meta}/fulfillment", wait: 20}
```

## Loader behaviour

A loader must do the following. The proved loader is one Python file run with CCI's
Python, using only `cci` and `sf`.

**Stage.** Copy the pack to `<work>/stage/pack`, skipping `stage.exclude`. Create a
`foundations` link at `<work>/stage/foundations` pointing at a Foundations checkout
(a regular clone, not a worktree). Make each `metadata_copies` entry under
`<work>/stage/meta/<name>` and drop its listed files. The work folder is per org and
outside both repos. Restage on a load from the first step or with `--restage`; a
resume with `--from` reuses the existing stage.

**Resolve and run.** Flatten the layers into one ordered step list, fill the
placeholders, and run each step. `run` commands run with the Foundations checkout as
their working folder unless `cwd: pack`, so CCI finds its project. The sf alias is CCI's
prefixed form of the CCI alias (`<project>__<alias>`; `cci-orchestration`).

**Record.** Each step writes `<work>/logs/<NN>-<id>.log`, and `<work>/state.json`
records its exit, end time and seconds. On a nonzero exit, print the log's tail and
`resume with --from <id>`, then exit with the step's code.

**Options.**

| Option | Does |
|--------|------|
| `--org <cci alias>` | Target org; the sf alias is derived from it. |
| `--from <id>`, `--to <id>` | Run a slice of the step list; an unknown id is refused with the list of ids. |
| `--only <layer,...>` | Run only these layers, within the slice. |
| `--dry-run` | Print each resolved step (layer, id, kind, command or folder) and run nothing. |
| `--restage` | Restage before a `--from` resume, to pick up pack edits. |
| `verify` | The on-org half of the deploy check for every `deploy` step, without deploying. Exits 1 if any member is missing. |
| `changed --since <ISO time>` | The idempotency count (see **Rerun and idempotency**). |

## Post-deploy component check

A metadata deploy can report success without deploying what you meant. A deploy from
an ignored path reported success with an empty package [Measured: 264, prior build, date not recorded],
and an empty `package.xml` deploys nothing and succeeds. So a `deploy` step:

1. Reads `<dir>/package.xml` into (type, member) pairs. It refuses a `*` member and a
   manifest with no members before deploying.
2. Runs `sf project deploy start --metadata-dir <dir> --target-org <sf alias> --wait
   <wait> --json`, adding `--test-level RunSpecifiedTests --tests <name>` per listed test.
3. Fails with the component failures if the command or the deploy status is not
   Succeeded.
4. Compares the pairs with the result's `componentSuccesses` (type and full name).
5. Lists each type on the org with `sf org list metadata --metadata-type <type>
   --target-org <sf alias> --json` and matches members case-insensitively. A type the
   listing returns nothing for (`StandardValueSet` is not listable) is retrieved by
   name with `sf project retrieve start --metadata <type>:<member>
   --target-metadata-dir <tmp> --unzip --target-org <sf alias>`; a member with no retrieved
   file is missing. Name the target org on every `sf` call: without it the CLI falls back to
   its default org, which may not be the one the pack is loading.
6. Prints package.xml, deployed and on-org counts, names each `NOT DEPLOYED` and
   `NOT ON ORG` member, and exits 4 if any.

Fed wrong inputs, the check failed each way: an empty `package.xml` was refused before
deploying; a member expected but not shipped exited 4 as not deployed and not on the
org; an absent flow was listed missing. A member named in `package.xml` but missing
from the folder is refused by the platform itself ("named in package.xml, but was not
found in zipped directory") [Measured: 2026-11-18, 264]. `verify` found 93 components
from 7 deploy steps on two orgs, none missing [Measured: 2026-11-18, 264].

Run the deploy with `sf`, not CCI's `deploy` task, so the step reads the JSON result.
A page patch keeps its own retrieve-and-compare: a `run` step that retrieves the live
page, patches it, deploys, re-retrieves and checks every value.

## Rerun and idempotency

Every step must be safe to run twice. What the proved build learned:

- **Data plans:** Upsert on stable externalIds (`sfdmu-data-plans`). A plan that sent
  `Status = Draft` to records already Active was refused on the second load; status
  objects take `skipExistingRecords: true`, as `sfdmu-data-plans` prescribes
  [Measured: 2026-11-17, 264].
- **Catalog:** load the PCM plan, run `scripts/check_classification_attrs.py` and follow `catalogs-and-loading.md` step 5 for any second pass (one pass is enough for QuantumBit [Measured: 2026-11-23, 264]); a second pass applies classification-attribute values (PCM load fact a), and extract only after the check exits 0.
- **Procedure overlays:** skip the save when no step is new or changed. Re-saving an
  unchanged active version counted as a change on every run [Measured: 2026-11-17, 264].
- **CML:** on the proved second load, with the model's version Active, `import_cml` exited
  0. It deleted the model's constraint records and created them again with new Ids, and
  uploaded the blob. The activate step skipped the already-Active version and warned that
  the solver keeps the model it last deployed [Measured: 2026-11-17, 264]. So:
    - A rerun with an unchanged model passes, but rewrites those records on every load.
      Count the rewrite as designed when you prove a rerun.
    - A changed model reaches the solver only when its version is cycled after the
      import: deactivated, then activated, through `manage_expression_sets`
      (`constraint-models` Quick Rule 3). To make that hands-off, put a step
      `manage_expression_sets -o operation deactivate_versions -o version_full_names
      <version>` between the import and the activate step. The task skips a version that
      is already Inactive or not in the org, so the same step is harmless on a first load
      [Repo: `tasks/rlm_manage_expression_sets.py`; not run as a pack step].
- **Scripts that create records:** create what is missing and correct what differs on
  existing records. A script that only created missing products never applied its
  design's flag to the ten that already existed, so the org and the design disagreed
  until the script enforced the field [Measured: 2026-11-18, 264].

To prove a rerun, note the time, load again, then run `changed --since <time>`. Take the
SFDMU plans from the manifest (every `pathtoexportjson` a step loads), not from a folder
glob: the proved loader globbed `<pack>/*/export.json`, which misses a plan nested
deeper. For each plan and each object it writes (skip `Readonly`), count records with
`SystemModstamp` at or after the time, inside the plan's own `WHERE`. Expect 0, and
write down the reason for each nonzero count the plan designs. The proved second load
had one: a schedule switched off and on by design [Measured: 2026-11-17, 264].

The count covers data plans only. Every step that writes records another way (a build
script, a procedure overlay, a CML import, a context plan) must report what it changed
in its own log, and a rerun must report nothing changed, or only a designed rewrite such
as the CML import's (above). The proved build's fulfillment
script reported 0 changes on its rerun [Measured: 2026-11-17, 264].

## Gates

The load proves the build only when the gates' golden tests pass again on the new org.
A gate runner reruns them in the order they ran during the build:

- Run from the stage (`<work>/stage/pack`, with its `foundations` link), so result
  files land there, not in the pack. Refuse to run without a stage.
- Pass the IDs a later runner needs (an order, its root asset, quote IDs) from the
  earlier runner's result file, chosen by org and write time.
- Wait for decision-table freshness before pricing gates, and refresh first where a
  test needs data the previous one changed.
- Record each runner's exit and keep going; stop a runner only when an input it needs
  is missing (exit 2). A `summary` reads pass and fail per case from the result files.
- Start each per-org runner from empty state; delete replay state carried in the stage.

## Running a load

The loader and gate-runner commands show how the proved build laid them out
(`tools/load.py`, `tools/gate.py` in the pack); yours take whatever names and paths
your pack gives them.

```bash
# 1. Base build (from a Foundations checkout, not a worktree)
python scripts/build_harness/harness.py run --scenarios-file <pack>/harness/scenarios.json \
  --scenario <scenario> --run-id <run> --keep-orgs
# 2. Load
<cci python> <pack>/tools/load.py --org <cci_alias> --dry-run
<cci python> <pack>/tools/load.py --org <cci_alias>
# 3. Prove it
<cci python> <pack>/tools/load.py --org <cci_alias> verify
python3 <pack>/tools/gate.py --org <cci_alias>
# 4. Rerun: note the time, load again, then
<cci python> <pack>/tools/load.py --org <cci_alias> changed --since <ISO time>
```

A person can do Setup-only steps while the loader runs earlier layers, since they need
only the base build. On the proved load the `check` passed when the loader reached it.

## When a step fails

| Exit or symptom | Do |
|-----------------|----|
| 3 (`check` missed) | Do the printed instructions, then `--from <id>`. |
| `verify` exits 1 | A member isn't on the org: redeploy its step with `--from <id> --to <id>`; if you fixed its folder or `package.xml` in the pack, add `--restage`. |
| 4 (deploy unverified) | Read the `NOT DEPLOYED` / `NOT ON ORG` lines. Fix the folder or `package.xml` in the pack, then `--from <id> --restage`. |
| 1 on a deploy | Read the component failures; fix the metadata or deploy its dependency first. |
| 1 on a `run` step | Read the step's log. For a data plan, follow `sfdmu-data-plans` (never switch to Insert + `deleteOldData`). |
| `fresh` timed out | Run `check_decision_table_freshness` and read which table is Stale and why (`decision-tables`). |
| Place says it can't find a newly loaded product | Wait for the search index after `rebuild_search_index` (`product-catalog-modeling` → `catalogs-and-loading.md`, PCM load fact f). |
| A fix in the pack isn't picked up | The resume reused the stage: add `--restage`. |
| A CCI step runs the wrong code or finds no project | The Foundations path is a worktree; point it at a regular checkout. |

Fix the pack, not the stage: the stage is rebuilt from the pack. Resume from the failed
step rather than from the start, unless a fix changes an earlier step's output.

## Examples

**Add a metadata folder to a pack.** Put the source under `<area>/metadata/` with an
explicit `package.xml` (no `*`). Add a `deploy` step before the data step that needs it,
with `tests` if it carries Apex. Run `--dry-run`, then `--only <layer>`, then `verify`.

**Add a Setup-only step.** Find a query whose row count shows the step is done. Add a
`check` step with that query, `expect_rows` and the instructions, placed before the
first step that depends on it.

**Replace an expiring org.** Base-build a new org, load the pack from the first step,
run `verify` and the gate runner. The pack does not change; only the work folder and
aliases do.

## Validation Checks

Before calling a pack or loader change done:

- `--dry-run` resolves every step with no unfilled placeholder, and step ids are unique.
- Every `deploy` folder has a `package.xml` with explicit members; `verify` reports 0
  missing on a loaded org.
- A fresh-org load from the first step exits 0, and the gate runner's `summary` shows
  every golden passing.
- `changed --since` after a second load reports 0, or each nonzero count is designed and
  written down.
- No command passes an access token; every `cci` call takes `--org <cci alias>` and
  every `sf` call takes `--target-org <sf alias>`.
- For changes to this skill: `python scripts/ai/analyze_agent_tooling.py check` and
  `python scripts/ai/pr_gate.py --base origin/main`.
