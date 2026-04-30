# Documentation Consistency — Pre-Merge Doc Review

Use this skill **before marking a PR ready** to verify that all affected
documentation stays aligned with code changes. It replaces multi-round
review-loop fixes ("fix stale description", "update README task name",
"regenerate CCI reference") with a single lookup pass.

## Quick Rules

1. **If you changed `cumulusci.yml`** — run `python scripts/ai/generate_cci_reference.py` and commit the output. Verify `git diff` on `tasks-reference.md`, `flows-reference.md`, `feature-flags.md` shows only your intended changes.
2. **If you renamed or added a CCI task** — grep `README.md`, `AGENTS.md`, `docs/`, and `.cursor/skills/` for the **old name**; update or remove every stale reference.
3. **If you changed an SFDMU plan** (`export.json`, CSVs, objects, operations) — update the plan's `README.md` in the **same commit**. Run `python scripts/validate_sfdmu_v5_datasets.py`.
4. **If you changed feature flags** (added, removed, renamed, changed default) — update the flag table in `README.md` and verify `feature-flags.md` was regenerated (rule 1).
5. **If you changed a Python task class** (`tasks/*.py`) — check the task's `description` in `cumulusci.yml`, the `README.md` Custom Tasks table, and any `docs/` guide that names it.
6. **If you changed Robot test suites or resources** — check `robot-testing/SKILL.md` tables (Setup tasks / E2E tasks) and the `README.md` troubleshooting section.
7. **If you created a new skill or sub-file** — add it to: (a) the parent `SKILL.md` cross-reference, (b) `AGENTS.md` Skill Sub-Files table, (c) `.cursor/skills/README.md` Skill Router if top-level.
8. **Quick verification** — run `python scripts/ai/generate_cci_reference.py` and then `git diff` to confirm only intended changes appear. Run `python scripts/validate_sfdmu_v5_datasets.py` (should pass).

## DO NOT

- **DO NOT** duplicate procedural content across `README.md`, `AGENTS.md`, and skill files — keep one source and add pointers.
- **DO NOT** manually update `docs/references/cci-task-reference.md` if the generated `tasks-reference.md` covers the same tasks — consolidate to one.
- **DO NOT** edit `CLAUDE.md` — it is a symlink to `AGENTS.md`.
- **DO NOT** skip the plan README when changing SFDMU plan behavior.

---

## Change-Surface Map

The core lookup: **when X changes, verify Y**.

| What changed | Docs to verify or update |
| ------------ | ------------------------ |
| `cumulusci.yml` (tasks, flows, flags) | Generated refs (run script), `README.md` task/flag tables, `AGENTS.md` Common Workflows |
| `tasks/*.py` (class, options, description) | `cumulusci.yml` description, `README.md` Custom Tasks table, relevant `docs/` guide |
| `datasets/sfdmu/**/export.json` or CSVs | Plan `README.md` in same directory, run SFDMU validator |
| Feature flag add/rename/default change | `README.md` Feature Flags tables, `AGENTS.md` edition flags, generated `feature-flags.md` |
| `robot/**` (new suite, renamed keyword) | `robot-testing/SKILL.md` task tables, `patterns.md`, `README.md` troubleshooting |
| `templates/` or UX assembly logic | `ux-assembly-retrieve.md`, `docs/features/dynamic-ux-assembly.md` |
| New `.cursor/skills/` file | Parent `SKILL.md`, `AGENTS.md` Sub-Files table, `.cursor/skills/README.md` Skill Router |
| `orgs/*.json` (scratch org definitions) | `README.md` Quick Start if it names specific configs |
| `scripts/apex/*.apex` | `troubleshooting/SKILL.md` if it references the script |
| `.forceignore` | No doc update, but verify retrieve/deploy intent is consistent |
| `scripts/ai/*.py` | `AGENTS.md` AI Utility Scripts section |

---

## Doc Layers in This Repo

Understanding where truth lives prevents duplication drift.

| Layer | Location | How to keep current |
| ----- | -------- | ------------------- |
| Generated CCI refs | `.cursor/skills/cci-orchestration/tasks-reference.md`, `.cursor/skills/cci-orchestration/flows-reference.md`, `.cursor/skills/cci-orchestration/feature-flags.md` | `python scripts/ai/generate_cci_reference.py` |
| SFDMU plan READMEs | `datasets/sfdmu/qb/en-US/*/README.md` | Manual — must match `export.json` |
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
python scripts/validate_sfdmu_v5_datasets.py             # should pass
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
