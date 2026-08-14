# Documentation Consistency — Pre-Merge Doc Review

Use this skill **before marking a PR ready** to verify that all affected
documentation stays aligned with code changes. It replaces multi-round
review-loop fixes ("fix stale description", "update README task name",
"regenerate CCI reference") with a single lookup pass.

## Quick Rules

1. **If you changed `cumulusci.yml`** — run `python scripts/ai/generate_cci_reference.py` and commit the output. Verify `git diff` on `tasks-reference.md`, `flows-reference.md`, `feature-flags.md` shows only your intended changes.
2. **If you renamed or added a CCI task** — grep `README.md`, `AGENTS.md`, `docs/`, and `.cursor/skills/` for the **old name**; update or remove every stale reference.
3. **If you changed an SFDMU plan** (`export.json`, CSVs, objects, operations) — update the plan's `README.md` in the **same commit**, then run `python scripts/ai/check_plan_readme_consistency.py <plan_dir>` to confirm the README's object table and `# N records` listings still match the plan (record counts, operations, externalIds, object presence). Also run `python scripts/validate_sfdmu_v5_datasets.py`.
4. **If you changed feature flags** (added, removed, renamed, changed default) — update the flag table in `README.md` and verify `feature-flags.md` was regenerated (rule 1).
5. **If you changed a Python task class** (`tasks/*.py`) — check the task's `description` in `cumulusci.yml`, the `README.md` Custom Tasks table, and any `docs/` guide that names it.
6. **If you changed Robot test suites or resources** — check `robot-testing/SKILL.md` tables (Setup tasks / E2E tasks) and the `README.md` troubleshooting section.
7. **If you created a new skill or sub-file** — follow `.cursor/skills/skill-authoring/SKILL.md`: add top-level skills to `AGENTS.md`, `.cursor/skills/README.md`, and `.claude/skill-manifest.yml` when cross-repo discoverability applies; register sub-files in the parent `SKILL.md`, which is their only registry — `AGENTS.md` carries no second-level index.
8. **Quick verification** — run `python scripts/ai/generate_cci_reference.py` and then `git diff` to confirm only intended changes appear. Run `python scripts/validate_sfdmu_v5_datasets.py` (should pass).

## DO NOT

- **DO NOT** duplicate procedural content across `README.md`, `AGENTS.md`, and skill files — keep one source and add pointers.
- **DO NOT** re-add a hand-maintained task listing (e.g. the removed `docs/references/cci-task-reference.md`). The single source for project tasks is the generated `.cursor/skills/cci-orchestration/tasks-reference.md` (run `python scripts/ai/generate_cci_reference.py`); for CumulusCI built-in tasks use `cci task list` / `cci task info <name>`.
- **DO NOT** edit `CLAUDE.md` — it is a symlink to `AGENTS.md`.
- **DO NOT** skip the plan README when changing SFDMU plan behavior.

---

## Change-Surface Map

The core lookup: **when X changes, verify Y**.

| What changed | Docs to verify or update |
| ------------ | ------------------------ |
| `cumulusci.yml` (tasks, flows, flags) | Generated refs (run script), `README.md` task/flag tables, `AGENTS.md` Common Workflows |
| `tasks/*.py` (class, options, description) | `cumulusci.yml` description, `README.md` Custom Tasks table, relevant `docs/` guide |
| `datasets/sfdmu/**/export.json` or CSVs | Plan `README.md` in same directory, then `check_plan_readme_consistency.py` (README ↔ plan) **and** the SFDMU v5 validator (plan compliance) |
| Feature flag add/rename/default change | `README.md` Feature Flags tables, `AGENTS.md` edition flags, generated `feature-flags.md` |
| `robot/**` (new suite, renamed keyword) | `robot-testing/SKILL.md` task tables, `patterns.md`, `README.md` troubleshooting |
| `templates/` or UX assembly logic | `ux-assembly-retrieve.md`, `docs/features/dynamic-ux-assembly.md` |
| New `.cursor/skills/` file | Parent `SKILL.md` sub-file list (the only registry), and `.cursor/skills/README.md` Skill Router for a new *top-level* skill |
| `orgs/*.json` (scratch org definitions) | `README.md` Quick Start if it names specific configs |
| `scripts/apex/*.apex` | `troubleshooting/SKILL.md` if it references the script |
| `.forceignore` | No doc update, but verify retrieve/deploy intent is consistent |
| `scripts/ai/*.py` | The skill that owns the script (see `AGENTS.md` **Script Reference** for the owner). Only a brand-new script *directory* earns an `AGENTS.md` row |
| **New** `scripts/*.py` (top level) | `AGENTS.md` Repository Layout — top-level utilities are easy to add and never document |
| **New** `scripts/apex/*.apex` | `troubleshooting/SKILL.md` (if it diagnoses a failure) and `.cursor/rules/apex-scripts.mdc` (if it establishes a pattern) |
| **New** `docs/guides/*.md` | `README.md` **Primary Guides** table — an unindexed guide is invisible |
| `unpackaged/**/classes/*.cls` behavior change | `docs/references/revenue-cloud-permissions.md` if the class is permission-gated — especially when its **destructive scope** grows |
| A **product/SKU added** to any dataset | *Every* plan CSV that carries that SKU, and each of their READMEs — see below |
| `scripts/build_harness/harness/` or `harness.py` | `.cursor/skills/build-harness/SKILL.md`, `docs/guides/build-harness.md` |
| `scripts/build_harness/tui/` or `tui-cci` | `scripts/build_harness/tui/README.md`, `.cursor/skills/build-harness/SKILL.md` |
| **API version bump** for a new release | Every doc carrying a `vNN.0` — but see below: a verified capture is provenance, not a version to retarget |

### An API bump must not rewrite a verified capture

`bump_api_version.py` handles code; the docs are a **manual** pass, and that pass is
where provenance gets overwritten. A section headed `✅ VERIFIED LIVE` or
"verified against `<org>`, `<date>`" records what was actually *exercised*, and the
capture org's **maximum API version caps what could have been called at all** — so
retargeting the path inside it does not merely overstate the evidence, it asserts a
request that was impossible to make.

Retarget prose that answers "which endpoint do I call now"; leave captures alone. If
the body and sequencing are still the contract you want to publish at the new
release, keep the new path and **say so in the banner** — state the release and API
the capture was taken at, and that `VERIFIED LIVE` attests to the body, response
shape, and sequencing rather than the version in the path.
`scripts/txn_data_harness/docs/contracts-*.md` carry the worked wording.

### Adding one product touches many plans

A single new SKU fans out across every plan that carries it — catalog, pricing,
images, rating, rates, tax. Each of those plans has a README with record counts.
Missing one is silent until the consistency check runs, so **always run it repo-wide
rather than on the plan you were editing**:

```bash
python scripts/ai/check_plan_readme_consistency.py    # no argument = all plans
```

⚠ The checker validates **object tables and file-tree listings only** — it does
**not** read counts written in prose or headings. Those you must update by hand.

---

## Doc Layers in This Repo

Understanding where truth lives prevents duplication drift.

| Layer | Location | How to keep current |
| ----- | -------- | ------------------- |
| Generated CCI refs | `.cursor/skills/cci-orchestration/tasks-reference.md`, `.cursor/skills/cci-orchestration/flows-reference.md`, `.cursor/skills/cci-orchestration/feature-flags.md` | `python scripts/ai/generate_cci_reference.py` |
| SFDMU plan READMEs | `datasets/sfdmu/**/README.md` (e.g. `datasets/sfdmu/qb/en-US/*/README.md`, `datasets/sfdmu/mfg/README.md`, `datasets/sfdmu/procedure-plans/README.md`) | Must match the plan's `export.json` + CSVs — enforce with `python scripts/ai/check_plan_readme_consistency.py` (counts, operations, externalIds, object presence) |
| Agent instructions | `AGENTS.md` (`CLAUDE.md` is a symlink) | Single source; edit `AGENTS.md` only |
| Human setup / reference | `README.md` | Manual — task tables, flag tables, troubleshooting |
| Skill files | `.cursor/skills/*/SKILL.md` + sub-files | Manual — cross-references to task names, paths |
| Guides and features | `docs/guides/`, `docs/features/`, `docs/references/` | Manual prose; watch for stale task/flow names |
| Copilot instructions | `.github/copilot-instructions.md` | Pointer only — keep thin, link to `AGENTS.md` |

---

## Verification Commands

```bash
python scripts/ai/generate_cci_reference.py              # regenerate references
git diff .cursor/skills/cci-orchestration/               # should show only intended changes
python scripts/validate_sfdmu_v5_datasets.py             # plan v5 compliance — should pass
python scripts/ai/check_plan_readme_consistency.py       # plan README ↔ export.json/CSVs — should PASS (0 errors)
```

If the diff shows unintended changes, investigate before committing. To commit the regenerated files:

```bash
python scripts/ai/generate_cci_reference.py
git add .cursor/skills/cci-orchestration/tasks-reference.md \
       .cursor/skills/cci-orchestration/flows-reference.md \
       .cursor/skills/cci-orchestration/feature-flags.md
```

---

## Related Skills

- **CCI Orchestration** — `.cursor/skills/cci-orchestration/SKILL.md`
- **SFDMU Data Plans** — `.cursor/skills/sfdmu-data-plans/SKILL.md`
- **Repository Integration** — `.cursor/skills/repo-integration/SKILL.md`
- **Robot Testing** — `.cursor/skills/robot-testing/SKILL.md`
- **Release Enablement** — `.cursor/skills/release-enablement/SKILL.md`
- **Revenue Cloud Docs** — `.cursor/skills/revenue-cloud-docs/SKILL.md`
- **Revenue Cloud Data Model** — `.cursor/skills/revenue-cloud-data-model/SKILL.md`
- **Usage & Consumption** — `.cursor/skills/usage-consumption/SKILL.md`
- **Troubleshooting** — `.cursor/skills/troubleshooting/SKILL.md`
